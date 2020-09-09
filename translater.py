from collections import namedtuple
from bs4 import BeautifulSoup
import clipboard as clip
import requests


# Defining basic structure for translation representation.
Translation = namedtuple('Translation', ['word', 'transcription', 'translation'])
TARGET_URL = 'https://wooordhunt.ru/word/postsearch'


def _translate(word: str) -> Translation:
    """
    Translate word.

    Input:
            1. Word to translate.

    Output:
            1. Translation object, which has translation, word and
            transcription attributes.
    """

    response = requests.post(TARGET_URL, data={"word": word})
    try:
        # Encoding troubles with transcription in case of plain text
        soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
        translation = soup.find('span', class_='t_inline_en').text
        transcription = soup.find('span', class_='transcription').text
    # Translation was not found
    except AttributeError as exc:
        print(exc)
        return
    return Translation(word, transcription, translation)


def translate_from_clip() -> Translation:
    """
    Translate word in clipboard.

    Output:
            1. Translation object, which has translation, word and
            transcription attributes.
    """
    # Get text from clipboard
    clip_text = clip.paste()
    return _translate(clip_text)


def translate_from_str(word: str) -> Translation:
    return _translate(word)
translate_from_str.__doc__ = _translate.__doc__


if __name__ == '__main__':
    print(translate_from_clip())
