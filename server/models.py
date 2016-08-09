from django.contrib.auth.models import User
from django.db import models

class Board(models.Model):
	abbr = models.CharField(max_length=10)
	name = models.CharField(max_length=50)

class Post(models.Model):
	user = models.ForeignKey(User, null=True, default=None, related_name='post_user')
	board = models.ForeignKey(Board)
	text = models.TextField(max_length=5000)
	extension = models.CharField(max_length=10, null=True)
	reply = models.ForeignKey('self', null=True, related_name='post_reply')
	date = models.DateTimeField()
	ip = models.CharField(max_length=20)
	reply_count = models.IntegerField(default=0)
	last_modified = models.DateTimeField(null=True)

class Quote(models.Model):
	post = models.ForeignKey(Post, related_name='quote_post')
	quote = models.ForeignKey(Post, related_name='quote_quote')

class Notification(models.Model):
	user = models.ForeignKey(User, related_name='notif_user')
	text = models.CharField(max_length=100)
	url = models.CharField(max_length=100)
	date = models.DateTimeField(null=True)

class Ban(models.Model):
	ip = models.CharField(max_length=50, default=0)
	exp_date = models.DateTimeField()

class Profile(models.Model):
	user = models.ForeignKey(User, related_name='prof_user')
	date_registered = models.DateTimeField()
	last_notif_seen = models.IntegerField(default=0)
