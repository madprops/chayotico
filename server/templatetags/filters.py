import os
import re
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

register.filter('quotes_text', quotes_text, is_safe=True)
register.filter('replies', replies, is_safe=True)
register.filter('arrows', arrows, is_safe=True)
register.filter('title', title, is_safe=True)