from kivy.app import App
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix.switch import Switch
from kivy.lang import Builder
import translater
from multiprocessing import Process
from plyer import notification
from dict_manager import update_dictionary
import os
import clipboard as clip
import keyboard
import re
import time


KV_FILE = """
<MainWindow>:
    height: 200
    width: 500
    size_hint: 1, 1
    query_input: qi
    dict_input: di
    trans_inst: ti
    hotkey: sw

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
        DictionaryInputField:
            id: di
            text: 'dictionary.txt'
            size_hint: 0.8, 1
        Switch:
            id: sw
            size_hint: 0.2, 1

<QueryInputField>:
    halign: 'center'
    font_size: 32
    size_hint: 1,0.5
    multiline: False
    background_color: 1,1,1,1

<DictionaryInputField>:
    halign: 'center'
    font_size: 14
    multiline: False
    background_color: 1,1,1,1

<TranslationField>:
    text: ''
    font_size: 20
    text_size: self.width, None
    valign: 'center'
    halign: 'center'
"""


Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '500')
Config.set('graphics', 'height', '200')


class MainWindow(BoxLayout):
    query_input = ObjectProperty(None)
    dict_input = ObjectProperty(None)
    trans_inst = ObjectProperty(None)
    hotkey = ObjectProperty(None)

    def check_hotkey(self, dt):
        if keyboard.is_pressed('ctrl+c') and self.hotkey.active:
            self.hotkey_action()
            time.sleep(1)

    def hotkey_action(self):
        word = clip.paste()
        self.query_input.text = word
        trans_tuple = translater.translate_from_str(self.query_input.text)
        if trans_tuple:
            translation = trans_tuple.translation
            update_dictionary(self.dict_input.text, trans_tuple)
        else:
            translation = 'No translation found!'
        self.trans_inst.text = translation
        notification.notify(message=translation, title=f'Перевод "{word}"', timeout=6)



class QueryInputField(TextInput):

    def on_enter(instance, value):
        trans_tuple = translater.translate_from_str(instance.text)
        if trans_tuple:
            translation = trans_tuple.translation
            update_dictionary(instance.parent.dict_input.text, trans_tuple)
        else:
            translation = 'No translation found!'
        instance.parent.trans_inst.text = translation

class DictionaryInputField(TextInput):
    pass

class TranslationField(Label):
    pass

class TranslaterApp(App):
    def build(self):
        Builder.load_string(KV_FILE)
        main = MainWindow()
        Clock.schedule_interval(main.check_hotkey, 1/60)
        return main

if __name__ == '__main__':
	TranslaterApp().run()
