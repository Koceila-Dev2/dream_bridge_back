from django.shortcuts import render
from .models import Dream
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm

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


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'dream_bridge_app/home.html')  # corrigé

@login_required
def dashboard(request):
    return render(request, 'dream_bridge_app/dashboard.html')  # corrigé

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Connexion automatique après inscription
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'dream_bridge_app/register.html', {'form': form})  # corrigé

@login_required
def narrate(request):
    return render(request, 'dream_bridge_app/narrate.html')

@login_required
def library(request):
    return render(request, 'dream_bridge_app/library.html')