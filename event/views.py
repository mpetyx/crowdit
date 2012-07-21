from event.models import Event
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


def image(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    response = HttpResponse(event.image, 'image/jpeg')
    response['Cache-Control'] = 'max-age=7200'
    return response
