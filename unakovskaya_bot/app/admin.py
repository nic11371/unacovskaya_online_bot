from django.contrib import admin
from .models import User, VideoLink


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'first_name', 'last_name',
        'tg_id', 'vk_id', 'created_at')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('created_at',)


@admin.register(VideoLink)
class VideoLinkAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'delay_minutes', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('title', 'message_text')
    ordering = ('order',)
