import requests
import clipboard as clip
from collections import namedtuple
from bs4 import BeautifulSoup

Translation = namedtuple('Translation', ['word', 'transcription', 'translation'])

def translate_from_clip():
    form_url = 'https://wooordhunt.ru/word/postsearch'
    clip_text = clip.paste()
    response = requests.post(form_url, data={"word": clip_text})
    try:
        soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
        word = clip_text
        translation = soup.find('span', class_='t_inline_en').text
        transcription = soup.find('span', class_='transcription').text
    except AttributeError:
        return
    return Translation(word, transcription, translation)

def translate_from_str(text):
    form_url = 'https://wooordhunt.ru/word/postsearch'
    response = requests.post(form_url, data={"word": text})
    try:
        soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
        word = text
        translation = soup.find('span', class_='t_inline_en').text
        transcription = soup.find('span', class_='transcription').text
    except AttributeError:
        return
    return Translation(word, transcription, translation)

if __name__ == '__main__':
    print(translate_from_clip())
