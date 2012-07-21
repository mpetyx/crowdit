from award.models import Award
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


def image(request, award_id):
    award = get_object_or_404(Award, pk=award_id)
    response = HttpResponse(award.image, 'image/jpeg')
    response['Cache-Control'] = 'max-age=7200'
    return response
