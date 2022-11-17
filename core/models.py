from django.db import models

SMS = 1
IMAGE = 2
VIDEO = 3
GIF = 4
VOCAL = 5
OTHER = 0

USER = 1
GROUP = 2


class Conversation(models.Model):
    CONV_TYPE = (
        (USER, "user"),
        (GROUP, "group"),
    )
    conv_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    color = models.CharField(max_length=200, default="blue")
    avatar = models.ImageField(
        upload_to="media/avatar/", default="media/avatar/default.png")
    type = models.IntegerField(choices=CONV_TYPE, default=USER)
    members = models.ManyToManyField("User", null=True, blank=True)
    thread_id = models.IntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class User(models.Model):
    user_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=200)
    phone_num = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.name


class Message(models.Model):
    MESSAGE_TYPES = (
        (SMS, "sms"),
        (IMAGE, "image"),
        (VIDEO, "video"),
        (GIF, "gif"),
        (VOCAL, "vocal"),
    )
    sms_id = models.IntegerField(null=True, blank=True)
    mms_id = models.IntegerField(null=True, blank=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=10000, null=True, blank=True)
    send_date = models.DateTimeField()
    type = models.IntegerField(choices=MESSAGE_TYPES, default=SMS)
    reaction = models.CharField(max_length=10, null=True, blank=True)
    reply = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True)
    media_path = models.CharField(max_length=10000, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.body)
