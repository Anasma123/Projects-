from django.db import migrations


def add_peruvayal_to_kozhikode(apps, schema_editor):
    Country = apps.get_model("locations", "Country")
    State = apps.get_model("locations", "State")
    District = apps.get_model("locations", "District")
    Locality = apps.get_model("locations", "Locality")

    india = Country.objects.filter(name__iexact="India").first()
    if not india:
        india = Country.objects.filter(code="IN").first()
    if not india:
        return

    state = State.objects.filter(country_id=india.id, name__iexact="Kerala").first()
    if not state:
        state = State.objects.create(country_id=india.id, name="Kerala")

    district = District.objects.filter(state_id=state.id, name__iexact="Kozhikode").first()
    if not district:
        district = District.objects.create(state_id=state.id, name="Kozhikode")

    if not Locality.objects.filter(district_id=district.id, name__iexact="Peruvayal").exists():
        Locality.objects.create(
            district_id=district.id,
            name="Peruvayal",
            pincode="",
        )


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0003_remove_locality_unique_locality_per_district"),
    ]

    operations = [
        migrations.RunPython(add_peruvayal_to_kozhikode, migrations.RunPython.noop),
    ]

