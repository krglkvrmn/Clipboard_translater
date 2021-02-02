from googletrans import Translator, LANGUAGES
from collections import namedtuple


LANGCODES = dict(map(reversed, LANGUAGES.items()))

# Defining basic structure for translation representation.
Translation = namedtuple('Translation', ['word', 'translations', 'examples'])
Translation_for_render = namedtuple('Translation', ['word', 'translations', 'trigger', 'examples'])


def translate(word, language, render=False):
    """
        Translate word from input language to russian.
        Render argument defines special output format, which is
        convenient to be used in dropdown menu.
    """
    translator = Translator()
    # Select language code
    lang = "auto" if language == "guess" else LANGCODES[language]
    raw_translation = translator.translate(word, dest="ru", src=lang)
    json_data = raw_translation.extra_data
    all_translations = []
    all_examples = []
    try:
        for word_type in json_data["all-translations"]:
            all_translations.extend(word_type[1])
    # Translation does not exists
    except IndexError:
        print(1, json_data)
        return None
    # ????
    except TypeError:
        all_translations = [json_data["translation"][0][0]]
    all_translations = ", ".join(all_translations)
    try:
        for example in json_data["examples"][0]:
            all_examples.append(example[0])
    # No examples for this word
    except TypeError:
        all_examples = ['', '']
    if ''.join(all_translations.split()) == ''.join(word.split()):
        return None
    if render:
        return Translation_for_render(word, all_translations, all_examples[0], all_examples[1:])
    elif not render:
        return Translation(word, all_translations, all_examples)


if __name__ == '__main__':
    print(translate("example", "english"))
