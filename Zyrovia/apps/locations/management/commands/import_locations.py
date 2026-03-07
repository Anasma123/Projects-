import json
import csv
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.locations.models import Country, District, Locality, State


class Command(BaseCommand):
    help = 'Import location hierarchy from data/locations/*.json files.'
    STATE_NAME_ALIASES = {
        'nct of delhi': 'delhi',
        'dadra and nagar haveli': 'dadra and nagar haveli and daman and diu',
        'daman and diu': 'dadra and nagar haveli and daman and diu',
    }

    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=5000)
        parser.add_argument('--min-states', type=int, default=30)
        parser.add_argument('--min-districts', type=int, default=700)
        parser.add_argument('--min-localities', type=int, default=10000)
        parser.add_argument(
            '--allow-incomplete',
            action='store_true',
            help='Allow import even if dataset size is below full-India thresholds.',
        )

    def _load_json(self, path: Path):
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding='utf-8-sig'))
        except json.JSONDecodeError as exc:
            raise CommandError(f'Invalid JSON in {path}: {exc}') from exc
        if not isinstance(data, list):
            raise CommandError(f'Expected list in {path}')
        return data

    def _load_csv(self, path: Path):
        if not path.exists():
            return None
        try:
            with path.open('r', encoding='utf-8', newline='') as fh:
                reader = csv.DictReader(fh)
                return [row for row in reader]
        except Exception as exc:  # pragma: no cover
            raise CommandError(f'Invalid CSV in {path}: {exc}') from exc

    def _load_dataset(self, data_dir: Path, base_name: str):
        json_path = data_dir / f'{base_name}.json'
        csv_path = data_dir / f'{base_name}.csv'
        data = self._load_json(json_path)
        if data is not None and len(data) > 0:
            return data
        csv_data = self._load_csv(csv_path)
        if csv_data is not None and len(csv_data) > 0:
            return csv_data
        if data is not None:
            return data
        if csv_data is not None:
            return csv_data
        raise CommandError(f'Missing dataset for {base_name}. Provide {base_name}.json or {base_name}.csv in {data_dir}.')

    @staticmethod
    def _pick(record, keys, default=''):
        for key in keys:
            value = record.get(key)
            if value is not None and str(value).strip() != '':
                return value
        return default

    @staticmethod
    def _normalize_row_keys(row):
        normalized = {}
        for key, value in row.items():
            if key is None:
                continue
            clean_key = re.sub(r'[^a-z0-9]+', '_', str(key).strip().lower()).strip('_')
            normalized[clean_key] = value
        return normalized

    @staticmethod
    def _norm_name(value):
        text = str(value or '').strip().lower()
        text = text.replace('&', ' and ')
        text = re.sub(r'[^a-z0-9]+', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _country_ref(self, row, by_ext, by_code, by_name):
        ref_ext = str(self._pick(row, ['country_external_id', 'country_id'], '')).strip()
        ref_code = str(self._pick(row, ['country_code'], '')).strip().upper()
        ref_name = str(self._pick(row, ['country_name'], '')).strip().lower()
        if ref_ext and ref_ext in by_ext:
            return by_ext[ref_ext]
        if ref_code and ref_code in by_code:
            return by_code[ref_code]
        if ref_name and ref_name in by_name:
            return by_name[ref_name]
        return None

    def _state_ref(self, row, by_ext, by_name_country, by_name_only, by_norm_name_only):
        ref_ext = str(self._pick(row, ['state_external_id', 'state_id'], '')).strip()
        if ref_ext and ref_ext in by_ext:
            return by_ext[ref_ext]

        state_name = str(self._pick(row, ['state_name'], '')).strip().lower()
        country_id = row.get('_country_id')
        if state_name and country_id:
            return by_name_country.get((country_id, state_name))
        if state_name:
            direct = by_name_only.get(state_name)
            if direct:
                return direct
            norm_name = self._norm_name(state_name)
            alias = self.STATE_NAME_ALIASES.get(norm_name)
            if alias:
                norm_name = self._norm_name(alias)
            return by_norm_name_only.get(norm_name)
        return None

    def _district_ref(self, row, by_ext, by_name_state, by_norm_name_state):
        ref_ext = str(self._pick(row, ['district_external_id', 'district_id'], '')).strip()
        if ref_ext and ref_ext in by_ext:
            return by_ext[ref_ext]

        district_name = str(self._pick(row, ['district_name'], '')).strip().lower()
        state_id = row.get('_state_id')
        if district_name and state_id:
            direct = by_name_state.get((state_id, district_name))
            if direct:
                return direct
            return by_norm_name_state.get((state_id, self._norm_name(district_name)))
        return None

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        data_dir = settings.BASE_DIR / 'data' / 'locations'

        countries_data = self._load_dataset(data_dir, 'countries')
        states_data = self._load_dataset(data_dir, 'states')
        districts_data = self._load_dataset(data_dir, 'districts')
        localities_data = self._load_dataset(data_dir, 'localities')

        if not options['allow_incomplete']:
            if len(states_data) < options['min_states']:
                raise CommandError(
                    f'Incomplete states dataset: {len(states_data)} found, need at least {options["min_states"]}.'
                )
            if len(districts_data) < options['min_districts']:
                raise CommandError(
                    f'Incomplete districts dataset: {len(districts_data)} found, need at least {options["min_districts"]}.'
                )
            if len(localities_data) < options['min_localities']:
                raise CommandError(
                    f'Incomplete localities dataset: {len(localities_data)} found, need at least {options["min_localities"]}.'
                )

        with transaction.atomic():
            self.stdout.write('Importing countries...')
            existing_countries = list(Country.objects.all().only('id', 'name', 'code', 'external_id'))
            by_ext = {c.external_id: c.id for c in existing_countries if c.external_id}
            by_code = {c.code.upper(): c.id for c in existing_countries if c.code}
            by_name = {c.name.strip().lower(): c.id for c in existing_countries}

            to_create = []
            for row in countries_data:
                row = self._normalize_row_keys(row)
                name = str(self._pick(row, ['name', 'country_name'])).strip()
                if not name:
                    continue
                ext = str(self._pick(row, ['external_id', 'id'], '')).strip() or None
                code = str(self._pick(row, ['code', 'iso2', 'iso3'], '')).strip().upper() or None

                if (ext and ext in by_ext) or (code and code in by_code) or (name.lower() in by_name):
                    continue
                to_create.append(Country(name=name, code=code, external_id=ext))

            Country.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=batch_size)
            existing_countries = list(Country.objects.all().only('id', 'name', 'code', 'external_id'))
            by_ext = {c.external_id: c.id for c in existing_countries if c.external_id}
            by_code = {c.code.upper(): c.id for c in existing_countries if c.code}
            by_name = {c.name.strip().lower(): c.id for c in existing_countries}

            self.stdout.write('Importing states...')
            existing_states = list(State.objects.all().only('id', 'name', 'country_id', 'external_id'))
            state_by_ext = {s.external_id: s.id for s in existing_states if s.external_id}
            state_by_name_country = {(s.country_id, s.name.strip().lower()): s.id for s in existing_states}
            state_name_counts = {}
            for s in existing_states:
                key = s.name.strip().lower()
                state_name_counts[key] = state_name_counts.get(key, 0) + 1
            state_by_name_only = {
                s.name.strip().lower(): s.id
                for s in existing_states
                if state_name_counts.get(s.name.strip().lower()) == 1
            }
            state_norm_counts = {}
            for s in existing_states:
                key = self._norm_name(s.name)
                state_norm_counts[key] = state_norm_counts.get(key, 0) + 1
            state_by_norm_name_only = {
                self._norm_name(s.name): s.id
                for s in existing_states
                if state_norm_counts.get(self._norm_name(s.name)) == 1
            }
            to_create = []
            for row in states_data:
                row = self._normalize_row_keys(row)
                name = str(self._pick(row, ['name', 'state_name'])).strip()
                if not name:
                    continue
                country_id = self._country_ref(row, by_ext, by_code, by_name)
                if not country_id:
                    continue
                ext = str(self._pick(row, ['external_id', 'id'], '')).strip() or None
                code = str(self._pick(row, ['code', 'state_code'], '')).strip() or None

                if (ext and ext in state_by_ext) or ((country_id, name.lower()) in state_by_name_country):
                    continue
                to_create.append(State(country_id=country_id, name=name, code=code, external_id=ext))

            State.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=batch_size)
            existing_states = list(State.objects.all().only('id', 'name', 'country_id', 'external_id'))
            state_by_ext = {s.external_id: s.id for s in existing_states if s.external_id}
            state_by_name_country = {(s.country_id, s.name.strip().lower()): s.id for s in existing_states}
            state_name_counts = {}
            for s in existing_states:
                key = s.name.strip().lower()
                state_name_counts[key] = state_name_counts.get(key, 0) + 1
            state_by_name_only = {
                s.name.strip().lower(): s.id
                for s in existing_states
                if state_name_counts.get(s.name.strip().lower()) == 1
            }
            state_norm_counts = {}
            for s in existing_states:
                key = self._norm_name(s.name)
                state_norm_counts[key] = state_norm_counts.get(key, 0) + 1
            state_by_norm_name_only = {
                self._norm_name(s.name): s.id
                for s in existing_states
                if state_norm_counts.get(self._norm_name(s.name)) == 1
            }

            self.stdout.write('Importing districts...')
            existing_districts = list(District.objects.all().only('id', 'name', 'state_id', 'external_id'))
            district_by_ext = {d.external_id: d.id for d in existing_districts if d.external_id}
            district_by_name_state = {(d.state_id, d.name.strip().lower()): d.id for d in existing_districts}
            district_by_norm_name_state = {(d.state_id, self._norm_name(d.name)): d.id for d in existing_districts}
            to_create = []
            for row in districts_data:
                row = self._normalize_row_keys(row)
                name = str(self._pick(row, ['name', 'district_name'])).strip()
                if not name:
                    continue
                row['_country_id'] = self._country_ref(row, by_ext, by_code, by_name)
                state_id = self._state_ref(row, state_by_ext, state_by_name_country, state_by_name_only, state_by_norm_name_only)
                if not state_id:
                    continue
                ext = str(self._pick(row, ['external_id', 'id'], '')).strip() or None
                code = str(self._pick(row, ['code', 'district_code'], '')).strip() or None

                if (ext and ext in district_by_ext) or ((state_id, name.lower()) in district_by_name_state):
                    continue
                to_create.append(District(state_id=state_id, name=name, code=code, external_id=ext))

            District.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=batch_size)
            existing_districts = list(District.objects.all().only('id', 'name', 'state_id', 'external_id'))
            district_by_ext = {d.external_id: d.id for d in existing_districts if d.external_id}
            district_by_name_state = {(d.state_id, d.name.strip().lower()): d.id for d in existing_districts}
            district_by_norm_name_state = {(d.state_id, self._norm_name(d.name)): d.id for d in existing_districts}

            self.stdout.write('Importing localities...')
            existing_localities = list(Locality.objects.all().only('id', 'name', 'district_id', 'pincode', 'external_id'))
            locality_by_ext = {l.external_id: l.id for l in existing_localities if l.external_id}
            locality_by_key = {(l.district_id, l.name.strip().lower(), (l.pincode or '').strip()): l.id for l in existing_localities}
            to_create = []
            for row in localities_data:
                row = self._normalize_row_keys(row)
                name = str(self._pick(row, ['name', 'locality_name', 'town', 'village'])).strip()
                if not name:
                    continue
                row['_country_id'] = self._country_ref(row, by_ext, by_code, by_name)
                row['_state_id'] = self._state_ref(
                    row, state_by_ext, state_by_name_country, state_by_name_only, state_by_norm_name_only
                )
                district_id = self._district_ref(row, district_by_ext, district_by_name_state, district_by_norm_name_state)
                district_name_value = str(self._pick(row, ['district_name'], '')).strip()
                if not district_id and row.get('_state_id') and district_name_value:
                    fallback_key = (row['_state_id'], district_name_value.lower())
                    district_id = district_by_name_state.get(fallback_key)
                    if not district_id:
                        district_obj, _ = District.objects.get_or_create(
                            state_id=row['_state_id'],
                            name=district_name_value,
                        )
                        district_id = district_obj.id
                        district_by_name_state[(row['_state_id'], district_name_value.lower())] = district_id
                        district_by_norm_name_state[(row['_state_id'], self._norm_name(district_name_value))] = district_id
                if not district_id:
                    continue
                ext = str(self._pick(row, ['external_id', 'id'], '')).strip() or None
                pincode = str(self._pick(row, ['pincode', 'postal_code', 'pin'], '')).strip()
                key = (district_id, name.lower(), pincode)

                if ext and ext in locality_by_ext:
                    continue
                if not ext and key in locality_by_key:
                    continue
                to_create.append(Locality(district_id=district_id, name=name, pincode=pincode, external_id=ext))
                if ext:
                    locality_by_ext[ext] = -1
                else:
                    locality_by_key[key] = -1

            Locality.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=batch_size)

        self.stdout.write(self.style.SUCCESS('Location import completed successfully.'))
