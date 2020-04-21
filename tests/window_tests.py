from nose.tools import *
import tkinter as tk

from japanese_app.app_windows import Learn
from japanese_app.main import App

root = tk.Tk()

sess_settings = {
                     "profile": {"name": "Tester"},
                     "kana": [("a", "hira")],
                     "index": 0,
                     "mode": "write"
                     }

# def learn_test():
    
    # app = App(root, sess_settings, "learn")
    # root.mainloop()
    
# def speak_test():
    
    # app = App(root, sess_settings, "speak")
    # root.mainloop()
    
# def write_test():

    # app = App(root, sess_settings, "write")
    # root.mainloop()