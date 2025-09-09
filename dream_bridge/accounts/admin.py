from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "birth_date", "believes_in_astrology", "zodiac_sign")
    list_filter = ("believes_in_astrology", "zodiac_sign")
    search_fields = ("user__username", "user__email")
