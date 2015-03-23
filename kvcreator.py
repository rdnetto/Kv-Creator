#!/usr/bin/env python2

from kivy.app import App
from kivy.uix.label import Label
from kivy.adapters.dictadapter import DictAdapter


class CreatorApp(App):
    pass


if(__name__ == "__main__"):
    app = CreatorApp()
    # app.build()
    # app.root.ids.settingsList.adapter = DictAdapter(cls=Label, data = {"one" : "foo", "two" : "bar", "baz" : "three"})
    app.run()

