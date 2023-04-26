from time import sleep
from django.shortcuts import render
from datetime import datetime
import os
from multiprocessing import Process
import update_db

from .models import Conversation, Message, Server
from .forms import UploadForm

def convs(request):
    convs = Conversation.objects.all()
    server = Server.objects.get_or_create()[0]
    print(server.process_state)
    context = {
        'convs': convs,
        'server': server,
        "elapsed_time": server.get_elapsed_time()
    }
    return render(request, 'core/index.html', context)

def conv(request, conv_id):
    messages = Conversation.objects.get(conv_id=conv_id).message_set.all().order_by('send_date')
    context = {
        'messages': messages,
    }
    return render(request, 'conv/index.html', context)

def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            server = Server.objects.get_or_create()[0]
            server.process_state = Server.RUNNING
            server.process_start_date = datetime.now()
            server.save()

            file = handle_uploaded_file(request.FILES["file"])
            p = Process(target=update_db.run_migrations, args=(file, True))
            p.start()

            return render(request, "upload/done.html")
    else:
        form = UploadForm()

    return render(request, "upload/index.html", {"form":form})

def handle_uploaded_file(f):
    now = datetime.now()
    if not os.path.isdir("media/uploads/"):
        os.makedirs("media/uploads/")

    with open(f'media/uploads/{round(now.timestamp())}_{f.name}', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return f'media/uploads/{round(now.timestamp())}_{f.name}'