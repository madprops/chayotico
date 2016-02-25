import os
import re
import datetime
from django import template
from bs4 import BeautifulSoup

register = template.Library()

op = 0

def quotes_text(value, opn):
	global op
	op = opn
	pat = "&gt;&gt;(\\d+)"
	res = re.sub(pat, check_quotes, value)
	return res

def check_quotes(match):
	g = str(match.group(1))
	if g == str(op):
	    return "<span onclick='go_to_post(" + g + ");' class='quote'> >>" + g + " (OP) </span>"
	else:
	    return "<span onclick='go_to_post(" + g + ");' class='quote'> >>" + g + "</span>" 	

def replies(value):
	if value > 1 or value == 0:
		return str(value) + ' replies'
	else:
		return str(value) + ' reply'

def arrows(value):
	soup = BeautifulSoup(value, 'html.parser')
	for item in soup.find_all(text=lambda x: x.strip().startswith('>')):
	    item.wrap(soup.new_tag("div class='arrow'"))
	return soup.prettify()

def title(value):
	return value[:236]

def radtime(time):
	now = datetime.datetime.now()
	if type(time) is int:
		diff = now - datetime.datetime.fromtimestamp(time)
	elif isinstance(time,datetime.datetime):
		diff = now - time 
	elif not time:
		diff = now - now
	second_diff = diff.seconds
	day_diff = diff.days
	if day_diff < 0:
		return ''
	if day_diff == 0:
		if second_diff < 60:
			return "less than a minute ago"
		if second_diff < 120:
			return  "1 minute ago"
		if second_diff < 3600:
			return str( second_diff / 60 ) + " minutes ago"
		if second_diff < 7200:
			return "1 hour ago"
		if second_diff < 86400:
			return str( second_diff / 3600 ) + " hours ago"
	if day_diff == 1:
		return "1 day ago"
	if day_diff < 7:
		return str(day_diff) + " days ago"
	if day_diff < 31:
		if day_diff/7 == 1:
			ago = " week ago"
		else:
			ago = " weeks ago"
		return str(day_diff/7) + ago
	if day_diff < 365:
		if day_diff/30 == 1:
			ago = " month ago"
		else:
			ago = " months ago"
		return str(day_diff/30) + ago
	if day_diff/365 == 1:
		ago = " year ago"
	else:
		ago = " years ago"
	return str(day_diff/365) + ago

register.filter('quotes_text', quotes_text, is_safe=True)
register.filter('replies', replies, is_safe=True)
register.filter('arrows', arrows, is_safe=True)
register.filter('title', title, is_safe=True)
register.filter('radtime', radtime, is_safe=True)