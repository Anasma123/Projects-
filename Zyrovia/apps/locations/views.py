from django.http import JsonResponse
from django.db.models.functions import Lower
from django.views.decorators.http import require_GET

from .models import District, Locality, State


def _int_param(request, key):
    value = request.GET.get(key)
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


@require_GET
def states_api(request):
    country_id = _int_param(request, 'country_id')
    if not country_id:
        return JsonResponse({'items': []})

    items = list(State.objects.filter(country_id=country_id).values('id', 'name').order_by(Lower('name'), 'name'))
    return JsonResponse({'items': items})


@require_GET
def districts_api(request):
    state_id = _int_param(request, 'state_id')
    if not state_id:
        return JsonResponse({'items': []})

    items = list(District.objects.filter(state_id=state_id).values('id', 'name').order_by(Lower('name'), 'name'))
    return JsonResponse({'items': items})


@require_GET
def localities_api(request):
    district_id = _int_param(request, 'district_id')
    state_id = _int_param(request, 'state_id')
    query = request.GET.get('q', '').strip()
    if not district_id and not state_id:
        return JsonResponse({'items': []})

    if district_id:
        queryset = Locality.objects.filter(district_id=district_id)
    else:
        queryset = Locality.objects.filter(district__state_id=state_id)
    if query:
        queryset = queryset.filter(name__icontains=query)

    items = list(
        queryset.values('id', 'name', 'pincode', 'district__name')
        .order_by(Lower('district__name'), 'district__name', Lower('name'), 'name', 'pincode')
    )
    for item in items:
        item['district_name'] = item.pop('district__name')
    return JsonResponse({'items': items})
