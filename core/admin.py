from django.contrib import admin

from .models import Message, Conversation, User

admin.site.register(Conversation)
admin.site.register(User)
admin.site.register(Message)