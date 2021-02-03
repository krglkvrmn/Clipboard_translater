import os
import re
import time
import clipboard as clip
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.switch import Switch
import keyboard
from plyer import notification
from dict_manager import DictManager
from translater import translate, Translation, Translation_for_render
from kivy.uix.spinner import Spinner


# Separate file was not rendered correctly
KV_FILE = """
<MainWindow>:
    height: 200
    width: 500
    size_hint: 1, 1
    query_input: qi
    trans_inst: ti
    hotkey: sw
    sett_man: sm

    orientation: 'vertical'
    QueryInputField:
        id: qi
        text: ''
        on_text_validate: self.on_enter(self.text)
    TranslationField:
        id: ti
    BoxLayout:
        orientation: 'horizontal'
        size_hint: 1,0.3
        Switch:
            id: sw
        SettingsManager:
            id: sm
            orientation: 'horizontal'
            lang_select: lang_sel
            LanguageSelectField:
                id: lang_sel
                text: 'Guess'
                values: self.AVAILABLE_LANGS
                size_hint: 1,0.45
                pos_hint: {'top':0.7}
                sync_height: True


<QueryInputField>:
    halign: 'center'
    font_size: 32
    size_hint: 1,0.5
    multiline: False
    background_color: 1,1,1,1

<TranslationField>:
    text: ''
    font_size: 20
    text_size: self.width, None
    valign: 'center'
    halign: 'center'

"""


Config.set('graphics', 'resizable', 0)
Config.set('graphics', 'width', 500)
Config.set('graphics', 'height', 200)


class MainWindow(BoxLayout):
    # Instance of input field.
    query_input = ObjectProperty(None)
    # Instance of translation field.
    trans_inst = ObjectProperty(None)
    # Instance of hotkey on/off switch.
    hotkey = ObjectProperty(None)
    # Settings manager instance
    sett_man = ObjectProperty(None)
    # Dictionary updater
    dict_manager = DictManager()

    def _check_hotkey(self, dt):
        """
        Checks hotkey condition and calls hotkey action function if hotkey mode is enabled.
        """
        if (keyboard.is_pressed('ctrl+c') or keyboard.is_pressed('ctrl+shift+c')) and self.hotkey.active:
            # Copying of text into clipboard can take great amount of time.
            # This prevents action function from reading wrong clipboard content.
            time.sleep(1.5)
            self._hotkey_action()
            time.sleep(1)

    def _hotkey_action(self):
        """
        Translate word, write results into dictionary and notify user if
        hotkey is pressed.
        """
        word = clip.paste()
        # Place requested word in input field.
        self.query_input.text = word
        # Current language
        self.dict_manager.lang = self.sett_man.lang_select.text
        # Translate word.
        for _ in range(10):
            try:
                trans_tuple = translate(word.lower(), self.dict_manager.lang.lower(), render=True)
                break
            except AttributeError:
                pass
        else:
            notification.notify(message="", title='Try again!', timeout=1)
            return
        if trans_tuple:
            translation = trans_tuple.translations
            if not (self.sett_man.lang_select.text == "Guess"):
                self.dict_manager.update_dict(trans_tuple)
        else:
            translation = 'No translation found!'
        # Show translation in GUI.
        self.trans_inst.text = translation
        # Notification containing translation results.
        notification.notify(message=translation, title=f'Перевод "{word}"', timeout=10)




class QueryInputField(TextInput):
    def on_enter(instance, value):
        """
        The function are triggered by pressing 'enter' while typing
        in input field.
        Shows translation in GUI and updates dictionary.
        """
        lang = instance.parent.sett_man.lang_select.text
        instance.parent.dict_manager.lang = lang
        for _ in range(15):
            try:
                trans_tuple = translate(instance.text.lower(), lang.lower(), render=True)
                break
            except AttributeError:
                pass
        else:
            notification.notify(message="", title='Try again!', timeout=1)
            return

        if trans_tuple:
            translation = trans_tuple.translations
            if not (instance.parent.sett_man.lang_select.text == "Guess"):
                instance.parent.dict_manager.update_dict(trans_tuple)
        else:
            translation = 'No translation found!'
        instance.parent.trans_inst.text = translation


class TranslationField(Label):
    pass


class SettingsManager(BoxLayout):
    # Instance of language select dropdown menu
    lang_select = ObjectProperty(None)


class LanguageSelectField(Spinner):
    AVAILABLE_LANGS = ("Guess", "English", "German", "French")


class DropdownCallButton(Button):
    pass


class TranslaterApp(App):
    def build(self):
        Builder.load_string(KV_FILE)
        main = MainWindow()
        # Check if hotkey was pressed.
        Clock.schedule_interval(main._check_hotkey, 1/60)
        return main

if __name__ == '__main__':
	TranslaterApp().run()
