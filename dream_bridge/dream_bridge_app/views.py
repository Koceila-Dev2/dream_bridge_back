from django.shortcuts import render

# Create your views here.
def home_page(request):
   
    return render(request, 'dream_bridge_app/base.html')