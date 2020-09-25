from multiprocessing import Process
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
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.switch import Switch
import keyboard
from plyer import notification
from dict_manager import update_dictionary
import translater


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
            trans_select: trans_sel
            call_ls: call_ls
            call_tr: call_tr
            DropdownCallButton:
                id: call_ls
            LanguageSelectField:
                id: lang_sel
            DropdownCallButton:
                id: call_tr
            TranslaterSelectField:
                id: trans_sel

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

<DropdownCallButton>:
    size_hint: 1,0.4
    pos_hint: {'top':0.5}
"""

AVAILABLE_LANGS = ["English", "Deutsch", "Guess"]
AVAILABLE_TRANSLATERS = {"English": ["wooordhunt", "yandex"],
                         "Deutsch": ["yandex"],
                         "Guess": [""]}


Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '500')
Config.set('graphics', 'height', '200')


class MainWindow(BoxLayout):
    # Instance of input field.
    query_input = ObjectProperty(None)
    # Instance of translation field.
    trans_inst = ObjectProperty(None)
    # Instance of hotkey on/off switch.
    hotkey = ObjectProperty(None)
    # Settings manager instance
    sett_man = ObjectProperty(None)

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
        # Translate word.
        trans_tuple = translater.translate_from_str(self.query_input.text)
        if trans_tuple:
            translation = trans_tuple.translation
            # Write result in HTML dictionary.
            update_dictionary('dictionary.html', trans_tuple)
        else:
            translation = 'No translation found!'
        # Show translation in GUI.
        self.trans_inst.text = translation
        # Notification containing translation results.
        notification.notify(message=translation, title=f'Перевод "{word}"', timeout=6)




class QueryInputField(TextInput):
    def on_enter(instance, value):
        """
        The function are triggered by pressing 'enter' while typing
        in input field.
        Shows translation in GUI and updates dictionary.
        """
        trans_tuple = translater.translate_from_str(instance.text)
        if trans_tuple:
            translation = trans_tuple.translation
            update_dictionary('dictionary.html', trans_tuple)
        else:
            translation = 'No translation found!'
        instance.parent.trans_inst.text = translation


class TranslationField(Label):
    pass


class SettingsManager(BoxLayout):
    # Instance of language select dropdown menu
    lang_select = ObjectProperty(None)
    # Instance of translater select dropdown menu
    trans_select = ObjectProperty(None)
    # Main button for language dropdown
    call_ls = ObjectProperty(None)
    # Main button for translater dropdown
    call_tr = ObjectProperty(None)

    def setup_language_dropdown(self):
        def __on_select(inst, data):
            self.call_ls.text = data
            self.setup_trans_dropdown()
        dropdown = self.lang_select              # Alias
        self.call_ls.text = "English"
        for lang in AVAILABLE_LANGS:
            btn = Button(text=lang, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)
        self.call_ls.bind(on_release=dropdown.open)
        dropdown.bind(on_select=__on_select)

    def setup_trans_dropdown(self):
        current_lang = self.call_ls.text
        dropdown = self.trans_select
        dropdown.clear_widgets()
        tr_list =  AVAILABLE_TRANSLATERS[current_lang]
        self.call_tr.text = tr_list[0]
        for trans in tr_list:
            btn = Button(text=trans, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)
        self.call_tr.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda inst, data: setattr(self.call_tr, "text", data))


class LanguageSelectField(DropDown):
    pass


class TranslaterSelectField(DropDown):
    pass


class DropdownCallButton(Button):
    pass


class TranslaterApp(App):
    def build(self):
        Builder.load_string(KV_FILE)
        main = MainWindow()
        main.sett_man.setup_language_dropdown()
        main.sett_man.setup_trans_dropdown()
        # Check if hotkey was pressed.
        Clock.schedule_interval(main._check_hotkey, 1/60)
        return main

if __name__ == '__main__':
	TranslaterApp().run()
