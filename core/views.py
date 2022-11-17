from django.shortcuts import render
from django.http import HttpResponse

from .models import Conversation, Message


def convs(request):
    convs = Conversation.objects.all()
    context = {
        'convs': convs,
    }
    return render(request, 'core/index.html', context)

def conv(request, conv_id):
    messages = Conversation.objects.get(conv_id=conv_id).message_set.all().order_by('send_date')
    context = {
        'messages': messages,
    }
    return render(request, 'conv/index.html', context)
