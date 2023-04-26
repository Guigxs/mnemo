import sqlite3
import os
from distutils.dir_util import copy_tree
from datetime import datetime


DB_FILE = "out/signal_backup.db"
FILE_EXT = {"image/jpeg": {"ext": "jpg", "id": "2"}, "image/png": {"ext": "png", "id": "2"}, "image/webp": {"ext": "jpg", "id": "2"}, "image/gif": {"ext": "gif", "id": "4"},
            "video/mp4": {"ext": "mp4", "id": "3"}, "application/pdf": {"ext": "pdf", "id": "0"}, "audio/aac": {"ext": "aac", "id": "5"}, "text/x-signal-plain": {"ext": "", "id": "0"}}


def copy_files():
    copy_tree("out/avatar", "media/avatar")
    copy_tree("out/attachment", "media/attachment")


def connect_db(db):
    conn = sqlite3.connect(db)
    print(f"Connected to '{db}' with SQLite version {sqlite3.version}")
    return conn


def fetch_db(conn, query):
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    return rows


def get_users(conn):
    query_user_conv = "SELECT _id,uuid,group_id,group_type,phone,color,profile_joined_name,system_display_name from recipient"
    data_user_conv = fetch_db(conn, query_user_conv)

    return data_user_conv


def get_conversations(conn):
    query_user_conv = "SELECT _id,uuid,group_id,group_type,phone,color,profile_joined_name,system_display_name from recipient"
    data_user_conv = fetch_db(conn, query_user_conv)
    query_groups_conv = "SELECT recipient_id as _id,title,members from groups"
    data_groups_conv = fetch_db(conn, query_groups_conv)
    query_threads_conv = "select _id,thread_recipient_id,snippet from thread"
    data_threads_conv = fetch_db(conn, query_threads_conv)

    return {"convs": data_user_conv, "groups": data_groups_conv, "threads": data_threads_conv}


def get_messages(conn):
    query_sms = "SELECT _id,address,date_sent,body,type,thread_id from sms"
    data_sms = fetch_db(conn, query_sms)
    query_mms = "SELECT _id,date,msg_box,body,address,m_type,quote_body,quote_author,thread_id from mms"
    data_mms = fetch_db(conn, query_mms)
    query_mention = "SELECT message_id,recipient_id as user_id,range_start as position,thread_id from mention"
    data_mention = fetch_db(conn, query_mention)
    query_media = "SELECT _id,mid as message_id,ct,unique_id as type from part"
    data_media = fetch_db(conn, query_media)
    query_reaction = "select message_id,author_id,emoji,date_sent from reaction"
    data_reaction = fetch_db(conn, query_reaction)

    return {"sms": data_sms, "mms": data_mms, "mention": data_mention, "media": data_media, "reaction": data_reaction}


def create_users(users):
    from core.models import User

    for user in users:
        if user[4] != "":
            User.objects.create(user_id=user[0], name=user[7] if user[7] else user[6]
                                if user[6] else "Unknown user", phone_num=str(user[2]))


def create_conversations(conversations):
    from core.models import User, Conversation

    for thread in conversations["threads"]:
        if thread[2] != "":
            Conversation.objects.create(conv_id=thread[1], thread_id=thread[0])

    for conv in conversations["convs"]:
        try:
            obj = Conversation.objects.get(conv_id=conv[0])
            obj.name = conv[7] if conv[7] else conv[6] if conv[6] else "Unknown user"
            obj.color = conv[5]
            obj.type = 1 if conv[3] == 0 else 2
            obj.save()

        except Conversation.DoesNotExist or User.DoesNotExist:
            print(
                f"[CONV] Conversation/User {conv[0]} does not exist! Skipping...")

    for group in conversations["groups"]:
        conv = Conversation.objects.get(conv_id=group[0])
        conv.name = group[1]
        for id in group[2].split(","):
            u = User.objects.get(user_id=id)
            conv.members.add(u)
        conv.save()


def create_messages(messages, owner):
    from core.models import User, Conversation, Message

    for sms in messages["sms"]:
        try:
            conv = Conversation.objects.get(thread_id=sms[5])
            user = User.objects.get(user_id=sms[1])
            Message.objects.create(sms_id=sms[0], conversation=conv, sender=user if sms[4] ==
                                   10485780 else owner, body=sms[3], send_date=datetime.fromtimestamp(sms[2]/1000), type=1)

        except Conversation.DoesNotExist or User.DoesNotExist:
            print(
                f"[SMS] Conversation/User {sms[1]} does not exist! Skipping...")

    for mms in messages["mms"]:
        try:
            conv = Conversation.objects.get(thread_id=mms[8])
            user = User.objects.get(user_id=mms[4])
            Message.objects.create(mms_id=mms[0], conversation=conv, sender=user if mms[5] ==
                                   132 else owner, body=mms[3], send_date=datetime.fromtimestamp(mms[1]/1000), type=2, )

        except Conversation.DoesNotExist or User.DoesNotExist:
            print(
                f"[MMS] Conversation/User {mms[4]} does not exist! Skipping...")

    for media in messages["media"]:
        try:
            mess = Message.objects.get(mms_id=media[1])
            mess.type = FILE_EXT[media[2]]["id"] if media[2] in FILE_EXT else 0
            ext = FILE_EXT[media[2]]['ext'] if media[2] in FILE_EXT else ""
            mess.media_path = f"media/attachment/{media[3]}_{media[0]}.{ext}"
            mess.save()

        except Message.DoesNotExist:
            print(f"[Media] Message {media[0]} does not exist! Skipping...")

    for mention in messages["mention"]:
        try:
            user = User.objects.get(user_id=mention[1])
            message = Message.objects.get(mms_id=mention[0])
            original = message.body
            message.body = f"{original[:mention[2]]}@{user.name}{original[mention[2]+1:]}"
            message.save()

        except User.DoesNotExist or Message.DoesNotExist:
            print(
                f"[Mention] Message {mention[0]} does not exist! Skipping...")

def run_script(db_file, delete=False):
    from core.models import User, Conversation, Message, Server

    print("Running script...")
    print("Delete:", delete)
    
    conn = connect_db(db_file)
    copy_files()

    if delete:
        Conversation.objects.all().delete()
        User.objects.all().delete()
        Message.objects.all().delete()

    users = get_users(conn)
    convs = get_conversations(conn)
    messages = get_messages(conn)

    create_users(users)
    create_conversations(convs)
    create_messages(messages, User.objects.get(user_id=1))

    conn.close()

    server = Server.objects.get_or_create()[0]
    server.process_state = Server.TERMINATED
    server.process_end_date = datetime.now()
    server.save()
    

def run_migrations(db_file, delete):
    os.environ.setdefault(f"DJANGO_SETTINGS_MODULE", "mnemo.settings")
    import django
    django.setup()

    run_script(db_file, delete=delete)

if __name__ == "__main__":
    os.environ.setdefault(f"DJANGO_SETTINGS_MODULE", "mnemo.settings")
    import django
    django.setup()

    run_script(DB_FILE, delete=True)