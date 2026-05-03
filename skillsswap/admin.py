from django.contrib import admin
from .models import Skill

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_free', 'price', 'user', 'created_at')
    list_filter = ('category', 'is_free')
    search_fields = ('title', 'description')