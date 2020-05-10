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
import translater
from multiprocessing import Process
from plyer import notification
import os
import clipboard as clip
import keyboard
import re
import time


Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '500')
Config.set('graphics', 'height', '200')

def update_dictionary(path, tt):
    filename = re.search(r'/?(\w+\..{3})', path).group(1)
    directory = re.search(r'.*/', path)
    if directory:
        directory = directory.group(0)
    else:
        directory = '.'
    if filename not in os.listdir(directory):
        with open(path, 'w') as file:
            pass
    to_write_str = f'{tt.word.lower()} {tt.transcription} - {tt.translation}\n'
    with open(path, 'r') as file:
        if to_write_str in file.read():
            return
    with open(path, 'a') as file:
        file.write(to_write_str)

class MainWindow(BoxLayout):
    query_input = ObjectProperty(None)
    dict_input = ObjectProperty(None)
    trans_inst = ObjectProperty(None)
    hotkey = ObjectProperty(None)
    enable_hotkey = BooleanProperty(False)

    def switch_callback(self, active):
        if not active:
            self.enable_hotkey = True
        else:
            self.enable_hotkey = False

    def check_hotkey(self, dt):
        if keyboard.is_pressed('ctrl+c') and self.enable_hotkey:
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
        notification.notify(message=translation, title=f'Перевод {word}', timeout=6)



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

class ClipTransApp(App):
    def build(self):
        self.load_kv('clipTrans.kv')
        main = MainWindow()
        Clock.schedule_interval(main.check_hotkey, 1/60)
        return main

if __name__ == '__main__':
	ClipTransApp().run()
