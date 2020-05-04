import requests
from bs4 import BeautifulSoup
from plyer import notification
import plyer.platforms.win.notification
import win32clipboard as wclip
import keyboard
import time


form_url = 'https://wooordhunt.ru/word/postsearch'

def translate():
	wclip.OpenClipboard()
	try:
		clip_text = wclip.GetClipboardData()
	except TypeError:
		#wclip.CloseClipboard()
		return None
	data = {'word':clip_text}
	responce = requests.post(form_url, data=data)
	try:
		soup = BeautifulSoup(responce.content.decode('utf-8'), 'lxml')
		translation = soup.find('span', class_='t_inline_en').text
	except AttributeError:
		translation = 'No translation found'
	wclip.CloseClipboard()
	return translation
		
while True:
	keyboard.wait('ctrl+c')
	time.sleep(0.1)
	trans = translate()
	notification.notify(message=trans, timeout=3)
	c = trans

