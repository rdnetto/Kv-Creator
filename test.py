#!/usr/bin/python2

import kivy.lang
from kivy.app import App


class TestApp(App):
    def build(self):
        return kivy.lang.Builder.load_file("test.kv")


if(__name__ == "__main__"):
    TestApp().run()


