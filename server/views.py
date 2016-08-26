import re
import os
import json
import datetime
from PIL import Image
from ipware.ip import get_ip
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from server.models import *

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

admins = ('madprops',)

def log(s):
	with open(BASE_DIR + '/log', 'a') as log:
		log.write(str(s) + '\n\n')

def now():
	return datetime.datetime.now()

def is_banned(request):
	ip = get_ip(request)
	if ip:
		bans = Ban.objects.filter(ip=ip)
		for b in bans:
			if b.exp_date > now():	
				return True
		return False

def boards_to_html():
	s = ""
	s += "<div id='board_list'>"
	boards = Board.objects.all().order_by('abbr')
	s += "<a class='board_link' href='/all/'>/all/</a> <span class='h10'></span>"
	for b in boards:
		s += "<a class='board_link' href='/" + b.abbr + "/'>/" + b.abbr + "/</a> <span class='h10'></span>"
	s += "</div>"
	return s

def get_random_board():
	return Board.objects.order_by('?')[0]

def main(request):
	# board = get_random_board()
	# return HttpResponseRedirect('/' + board.abbr + '/')
	return HttpResponseRedirect('/all/')

def board(request, board):

	if board != 'all':
		board = Board.objects.get(abbr=board)

	if request.method == 'POST':
		if board == 'all':
			return HttpResponseRedirect('/all/')
		if is_banned(request):
			return HttpResponseRedirect('/error/7')
		text = request.POST['text'].strip()
		status = check_thread(request)
		if status == 'ok':
			try:
				file = request.FILES['file']
			except:
				return HttpResponseRedirect('/error/4')
			ip = get_ip(request)
			if not ip:
				ip = 0
			p = Post(board=board, text=text, date=now(), last_modified=now(), ip=ip)
			if request.user.is_authenticated():
				p.user = request.user
			p.save()
			handle_uploaded_file(file, p)
			return HttpResponseRedirect('/' + board.abbr + '/' + str(p.id))
		elif status == 'mustwait':
			return HttpResponseRedirect('/error/1')
		elif status == 'toolong':
			return HttpResponseRedirect('/error/2')
		elif status == 'empty':
			return HttpResponseRedirect('/error/3')
		elif status == 'linebreaks':
			return HttpResponseRedirect('/error/6')
		else:
			return HttpResponseRedirect('/')
	else:
		c = {}
		fobs = []

		if board == 'all':
			c['board_name'] = 'All'
			c['board_abbr'] = 'all'
			posts = Post.objects.filter(reply__isnull=True).order_by('-last_modified')[:50]
		else:
			c['board_name'] = board.name
			c['board_abbr'] = board.abbr
			posts = Post.objects.filter(board=board, reply__isnull=True).order_by('-last_modified')[:50]

		for p in posts:
			fobitem = {}
			fobitem['thread'] = p
			fobs.append(fobitem)
		c['fobs'] = fobs
		if request.user.is_authenticated():
			num_notifs = num_new_notifs(request)
			if num_notifs == 1:
				c['notifs'] = '1 notification'
			else:
				c['notifs'] = str(num_notifs) + ' notifications'
		c['boards_html'] = boards_to_html()
		if request.user.username in admins:
			c['is_admin'] = 'yes'
		else:
			c['is_admin'] = 'no'
		return render(request, 'main.html', c)

def thread(request, board, id):
	board = Board.objects.get(abbr=board)
	if request.method == 'POST':
		if is_banned(request):
			return HttpResponseRedirect('/error/7')
		text = request.POST['text'].strip()
		status = check_post(request)
		if status == 'ok':
			thread = Post.objects.get(id=id)
			if thread.reply_count >= 300:
				return HttpResponseRedirect('/error/8')
			ip = get_ip(request)
			if not ip:
				ip = 0
			p = Post(board=board, text=text, date=now(), reply=thread, ip=ip)
			if request.user.is_authenticated():
				p.user = request.user
			p.save()
			pid = p.id
			try:
				file = request.FILES['file']
				handle_uploaded_file(file, p)
			except:
				pass
			try:
				post = Post.objects.get(id=pid)
				thread.reply_count += 1
				thread.last_modified = now()
				thread.save()
				save_quotes(post, thread)
			except:
				pass
			return HttpResponseRedirect('/' + board.abbr + '/' + id + '/#bottom')
		elif status == 'mustwait':
			return HttpResponseRedirect('/error/1')
		elif status == 'toolong':
			return HttpResponseRedirect('/error/2')
		elif status == 'linebreaks':
			return HttpResponseRedirect('/error/6')
		else:
			return HttpResponseRedirect('/' + board.abbr + '/' + id + '/#bottom')
	else:
		c = {}
		c['board_name'] = board.name
		c['board_abbr'] = board.abbr
		fobs = {}
		fobs['thread'] = Post.objects.get(id=id)
		fobs['thread_quotes'] = Quote.objects.filter(quote=fobs['thread'])
		fobs['posts'] = []
		posts = Post.objects.filter(reply=fobs['thread']).order_by('id')
		for p in posts:
			fobitem = {}
			fobitem['post'] = p
			fobitem['quotes'] = Quote.objects.filter(quote=p)
			fobs['posts'].append(fobitem)
		c['fobs'] = fobs
		if request.user.is_authenticated():
			num_notifs = num_new_notifs(request)
			if num_notifs == 1:
				c['notifs'] = '1 notification'
			else:
				c['notifs'] = str(num_notifs) + ' notifications'
		c['boards_html'] = boards_to_html()
		if request.user.username in admins:
			c['is_admin'] = 'yes'
		else:
			c['is_admin'] = 'no'
		return render(request, 'thread.html', c)

def error(request, code):
	code = int(code)
	c = {}
	if code == 1:
		c['message'] = "error: you must wait 30 seconds after your last post"
	elif code == 2:
		c['message'] = "error: text can't exceed 4000 characters"
	elif code == 3:
		c['message'] = "error: you didn't write any text"
	elif code == 4:
		c['message'] = "error: you didn't upload a file"
	elif code == 5:
		c['message'] = "error: you didn't upload a proper file"
	elif code == 6:
		c['message'] = "error: too many linebreaks"
	elif code == 7:
		c['message'] = "error: you were banned for 30 days"
	elif code == 8:
		c['message'] = "error: unable to make post, thread is full"
	return render(request, 'message.html', c)

def save_quotes(post, thread):
	pattern = re.compile('>>(\d+)')
	search = re.findall(pattern, post.text)
	qids = []
	for qid in search:
		if qid not in qids:
			qids.append(qid)
			quote = Post.objects.get(id=qid)
			q = Quote(post=post, quote=quote)
			q.save()
			if quote.user.is_authenticated() and quote.user != post.user:
				text = "someone replied to you in a thread"
				url = "/" + thread.board.abbr + "/" + str(thread.id) + "#" + str(post.id)
				notif = Notification(user=quote.user, text=text, url=url, date=now())
				notif.save()
	if len(qids) == 0:
		if post.user != thread.user:
			text = "someone posted in your thread"
			url = "/" + thread.board.abbr + "/" + str(thread.id) + "#" + str(post.id)
			notif = Notification(user=thread.user, text=text, url=url, date=now())
			notif.save()

def check_thread(request):
	text = request.POST['text'].strip()
	if len(text) == 0:
		return 'empty'
	if len(text) > 4000:
		return 'toolong'
	if text.count('\n') > 80:
		return 'linebreaks'
	try:
		if request.user.username not in admins:
			ip = get_ip(request)
			last_post = Post.objects.filter(ip=ip).last()
			if now() - last_post.date < datetime.timedelta(seconds=30):
				return 'mustwait'
	except:
		pass
	return 'ok'

def check_post(request):
	text = request.POST['text'].strip()
	if len(text) == 0:
		try:
			image = request.FILES['file']
		except:
			return 'notextorimage'
	if len(text) > 4000:
		return 'toolong'
	if text.count('\n') > 80:
		return 'linebreaks'
	try:
		if request.user.username not in admins:
			ip = get_ip(request)
			last_post = Post.objects.filter(ip=ip).last()
			if now() - last_post.date < datetime.timedelta(seconds=30):
				return 'mustwait'
	except:
		pass
	return 'ok'

def handle_uploaded_file(file, post):
	extension = file.name.split('.')[-1].lower()
	if extension not in ['png', 'jpeg', 'jpg', 'gif', 'webm', 'mp4']:
		post.delete()
		return HttpResponseRedirect('/error/5')
	path_base = BASE_DIR + '/media/files/' + str(post.id)
	path =  path_base + '.' + extension
	with open(path , 'wb+') as destination:
		for chunk in file.chunks():
			destination.write(chunk)
	if extension in ['png', 'jpeg', 'jpg', 'gif']:
		thumb_path = path_base + '_thumb' + '.' + extension
		size = (250,350)
		img = Image.open(path)
		img.thumbnail(size, Image.ANTIALIAS)
		img.save(thumb_path)	
	post.extension = extension
	post.save()

def login(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				auth_login(request, user)
				return HttpResponseRedirect('/')
		else:
			c = {}
			c['error_msg'] = "username and password don't match"
			return render(request, 'login.html', c)
	c = {}
	return render(request, 'login.html', c)

def register(request):
	if request.method == 'POST':
		msg = check_register(request)
		if msg == 'ok':
			username = request.POST['username']
			password = request.POST['password']
			user = User.objects.create_user(username, 'no@email.com', password)
			p = Profile(user=user, date_registered=now())
			p.save()
			user.backend='django.contrib.auth.backends.ModelBackend'
			auth_login(request, user)
			return HttpResponseRedirect('/')
		else:
			c = {}
			c['error_msg'] = msg
			return render(request, 'login.html', c)

def check_register(request):
	username = request.POST['username']
	password = request.POST['password']
	try:
		user = User.objects.get(username=username)
		return 'username already exists'
	except:
		pass
	if len(username) > 50:
		return 'username is too long'
	if len(password) > 100:
		return 'password is too long'
	if len(username) == 0:
		return 'username is empty'
	if len(password) == 0:
		return 'password is empty'
	return 'ok'

def logout(request):
	auth_logout(request)
	return HttpResponseRedirect('/login')

def delete_thread(request, id):
	if request.user.username in admins:
		p = Post.objects.get(id=id)
		p.delete()
	return HttpResponseRedirect('/')

def delete_post(request):
	p = Post.objects.get(id=request.POST['id'])
	thread = p.reply
	if request.user.username in admins:
		p.delete()
		thread.reply_count -= 1
		try:
			last_post = Post.objects.filter(reply=thread).last()
			thread.last_modified = last_post.date
		except:
			pass
		thread.save()
	return HttpResponse('ok')

def raise_thread(request, id):
	if request.user.is_authenticated():
		p = Post.objects.get(id=id)
		p.last_modified = now()
		p.save()
	return HttpResponseRedirect('/')

def ban(request):
	id = request.POST['id']
	post = Post.objects.get(id=id)
	ban = Ban(ip=post.ip, exp_date=now() + datetime.timedelta(days=30))
	ban.save()
	return HttpResponse('ok')

def num_new_notifs(request):
	p = Profile.objects.get(user=request.user)
	notifs = Notification.objects.filter(user=request.user, id__gt=p.last_notif_seen)
	return len(notifs)

def check_notifs(request):
	num_notifs = num_new_notifs(request)
	data = {'num_notifs':num_notifs}
	return HttpResponse(json.dumps(data), content_type="application/json")

def notifications(request):
	c = {}
	c['notifs'] = Notification.objects.filter(user=request.user).order_by('-id')[:80]
	p = Profile.objects.get(user=request.user)
	p.last_notif_seen = c['notifs'].first().id
	p.save()
	return render(request, 'notifications.html', c)