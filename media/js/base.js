function init()
{ 
	activate_image_hover();
	activate_quote_hover();
	activate_header_quote_hover();
	if(loggedin === 'yes')
	{
		activate_check_notifs();
	}
	enable_inputs();
	title = document.title;
}

function activate_image_hover()
{
	$('body img').each(function(i) 
	{ 
		if($(this).attr('id') === 'image_hover')
		{
			return true;
		}
		if($(this).attr('class') === 'logo')
		{
			return true;
		}
		$(this).mouseover(function()
		{
			var s = $(this).attr('src');
			s = s.replace('_thumb', '');
			$('#image_hover').css('display', 'block');
			$('#image_hover').attr('src', s);
			$('#image_hover').css('max-width', $(window).width() - 300);
		})
		$(this).mouseout(function()
		{
			$('#image_hover').css('display', 'none');
			$('#image_hover').attr('src', '');
			$('#image_hover').css('max-height', $(window).height());
		})
	});
}

function respond(id)
{
	$('#popup_form').css('display', 'block');
	$('#popup_text').focus();
	var val = $('#popup_text').val();
	$('#popup_text').val(val + '>>' + id + '\n');
}

function close_popup_form()
{
	$('#popup_text').val('');
	$('#popup_form').css('display', 'none');
}

function activate_quote_hover()
{
	$('.quote').each(function(i) 
	{ 
		$(this).mouseover(function(e)
		{
			var id = $(this).html().replace('&gt;&gt;', '');
			id = id.replace('(OP)', '');
			id = $.trim(id);
			var post = $('#' + id).parent();
			var post_top = $(post).position().top;
			var window_top = $(window).scrollTop();
			if(post_top > window_top)
			{
				$(post).addClass('highlight');
			}
			else
			{
				show_popup_post($(this), id)
			}
		});
		$(this).mouseout(function()
		{
			hide_popup_post();
		});
	});
}

function activate_header_quote_hover()
{
	$('.header_quote').each(function(i) 
	{ 
		$(this).mouseover(function(e)
		{
			var id = $(this).html().replace('&gt;&gt;', '');
			id = $.trim(id);
			var post = $('#' + id).parent();
			var post_top = $(post).position().top;
			var post_bottom = $(post).position().top + $(post).outerHeight();
			var window_top = $(window).scrollTop();
			var window_bottom = window_top + $(window).height();
			if(post_bottom < window_bottom)
			{
				$(post).addClass('highlight');
			}
			else
			{
				show_popup_post($(this), id)
			}
		});
		$(this).mouseout(function()
		{
			hide_popup_post();
		});
	});
}

function show_popup_post(quote, id)
{
	var clone = $('#' + id).parent().clone();
	clone.find('.respond').remove();
	clone.find('img').css('max-width', 130);
	clone.find('img').css('max-height', 250);
	$('#popup_post').html(clone.html());
	$('#popup_post').css('display', 'inline-block');

	var x = quote.offset().left + (quote.width()) + 10;
	var y = quote.offset().top - ($('#popup_post').height() / 2);
	if($(window).width() - x < 200)
	{
		x = quote.offset().left - $('#popup_post').width() - quote.width();
	}
	$('#popup_post').css('left', x + 'px');
	$('#popup_post').css('top', y + 'px');

	var popup_top = $('#popup_post').position().top;
	var popup_bottom = popup_top + $('#popup_post').outerHeight();
	var window_top = $(window).scrollTop();
	var window_bottom = window_top + $(window).height();

	if(popup_bottom > window_bottom)
	{
		y -= popup_bottom - window_bottom;
	}
	$('#popup_post').css('left', x + 'px');
	$('#popup_post').css('top', y + 'px');

	if(popup_top < window_top)
	{	
		y = window_top;
	}
	$('#popup_post').css('left', x + 'px');
	$('#popup_post').css('top', y + 'px');
}

function hide_popup_post()
{
	$('#popup_post').css('display', 'none')
	$('.highlight').each(function()
	{
		$(this).removeClass('highlight');
	})
}

function go_to_post(id)
{
	$(window).scrollTop($('#' + id).parent().offset().top);
}

function delete_post(id)
{
	$('#' + id).parent().fadeOut();
	$.post('/delete_post/',
	{
		id: id,
		csrfmiddlewaretoken: csrf_token
	},
	function(data)
	{

	});
}

function ban(id)
{
	$.post('/ban/',
	{
		id: id,
		csrfmiddlewaretoken: csrf_token
	},
	function(data)
	{
		if(data== 'ok')
		{
			alert('ip was banned');
		}
	});
}

function activate_check_notifs()
{
	setInterval(function()
	{
		check_notifs();
	}, 30000);
}

function check_notifs()
{
	$.get('/check_notifs/',
	{
	},
	function(data) 
	{
		text = data['num_notifs'];
		if(text === 1)
		{
			text += ' notification'
		}
		else
		{
			text += ' notifications'
		}
		$('#notifs_link').html(text);
		if(data['num_notifs'] !== 0)
		{
			document.title = '(' + data['num_notifs'] + ') ' + title;
		}
	});
}

function enable_inputs()
{
	$('input').each(function()
	{
		$(this).attr('disabled', false);
	})
}