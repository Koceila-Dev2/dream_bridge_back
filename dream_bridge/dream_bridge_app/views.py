from django.shortcuts import render
from .models import Dream
from django.db.models import Q

def galerie_filtrée(request):
    emotion_filtrée = request.GET.get('emotion')
    date_filtrée = request.GET.get('date')

    images = Dream.objects.all()

    if emotion_filtrée and emotion_filtrée != "all":
        images = images.filter(emotion=emotion_filtrée)

    if date_filtrée:
        images = images.filter(date__date=date_filtrée)


    # pour la liste déroulante des émotions
    emotions_disponibles = Dream.objects.values_list('emotion', flat=True).distinct()

    return render(request, 'dream_bridge_app/galerie.html', {
        'images': images,
        'emotions': emotions_disponibles,
        'selected_emotion': emotion_filtrée,
        'selected_date': date_filtrée,
    })
