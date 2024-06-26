from django.contrib import admin
from friendships.models import Friendship
# Register your models here.

@admin.register(Friendship)
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'id',
        'from_user',
        'to_user',
        'created_at',
    )