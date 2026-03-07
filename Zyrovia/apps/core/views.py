from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

PROTECTED_ACTIONS = {'booking', 'chat', 'calling', 'rating'}


def dashboard(request):
    cards = [
        {'name': 'NearRide', 'description': 'Book nearby drivers with transparent pricing and live ETA.', 'actions': ['booking', 'chat', 'calling', 'rating']},
        {'name': 'NearShop', 'description': 'Discover shops around you and request quick delivery support.', 'actions': ['booking', 'chat', 'calling', 'rating']},
        {'name': 'NearService', 'description': 'Connect with verified local service providers in minutes.', 'actions': ['booking', 'chat', 'calling', 'rating']},
    ]
    return render(request, 'core/dashboard.html', {'cards': cards})


@login_required
def protected_action(request, action: str):
    if action not in PROTECTED_ACTIONS:
        raise Http404('Action not found.')
    return render(request, 'core/action.html', {'action': action})


def bad_request_view(request, exception):
    return render(request, 'errors/400.html', status=400)


def permission_denied_view(request, exception):
    return render(request, 'errors/403.html', status=403)


def not_found_view(request, exception):
    return render(request, 'errors/404.html', status=404)


def server_error_view(request):
    return render(request, 'errors/500.html', status=500)
