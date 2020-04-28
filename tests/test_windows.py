import pytest
import tkinter as tk

from kana_teacher.windows import *
from kana_teacher.kana import KANA


def test_app():
    root = tk.Tk()
    app = App(root)
    assert root.pack_slaves()[0] == app
    assert app.pack_slaves()[0] == app.ins_label
    assert app.pack_slaves()[-1] in app.windows.values()
    
    app.ins_var.set("test")
    assert app.ins_label.cget("text") == "test"
    
    app.destroy()
    root.destroy()

def test_popup():
    root = tk.Tk()
    app = App(root)
    popup = Popup(app, "test")
    widgets = popup.pack_slaves()
    assert widgets[0].cget("text") == "test"
    assert widgets[1].cget("text") == "OK"
    
    app.destroy()
    popup.destroy()
    root.destroy()
    
def test_appwindow():
    root = tk.Tk()
    app = App(root)
    aw = AppWindow(app)
    assert aw.root == root
    
    app.destroy()
    root.destroy()
    
def test_setup():
    root = tk.Tk()
    app = App(root)
    setup = app.windows["setup"]
    setup.take_focus()
    assert app.pack_slaves()[-1] == setup
    
    setup.select_all()
    setup.deselect_all()
    
    on = setup.on_chart
    off = setup.off_chart
    setup.switch_chart()
    assert on == setup.off_chart
    assert off == setup.on_chart
    
    setup.start()
    assert app.pack_slaves()[-1] == setup
    setup.select_all()
    setup.widgets["radio_buttons"][0].invoke()
    setup.start()
    assert app.pack_slaves()[-1] != setup
    assert len(SESS_SETTINGS["kana"]) == 71
    
    app.destroy()
    root.destroy()
    SESS_SETTINGS["kana"] == None
    SESS_SETTINGS["index"] == 0
    
def test_learn():
    root = tk.Tk()
    app = App(root)
    SESS_SETTINGS["kana"] = [(KANA[0][0], "hira")]
    SESS_SETTINGS["mode"] = "learn"
    learn = app.windows["learn"]
    
    learn.take_focus()
    learn.quit()
    assert app.pack_slaves()[-1] == app.windows["setup"]
    
    learn.take_focus()
    learn.quiz()
    assert app.pack_slaves()[-1] in [app.windows["speak"], app.windows["write"]]
    
    learn.take_focus()
    learn.next()
    assert app.pack_slaves()[-1] == learn
    
    app.destroy()
    root.destroy()
    SESS_SETTINGS["kana"] = None
    SESS_SETTINGS["mode"] = ""
    SESS_SETTINGS["index"] = 0
    
def test_speak():
    root = tk.Tk()
    app = App(root)
    SESS_SETTINGS["kana"] = [(KANA[0][0], "hira"), (KANA[1][0], "kata")]
    SESS_SETTINGS["mode"] = "speak"
    speak = app.windows["speak"]
    
    speak.take_focus()
    speak.play_audio()
    
    speak.quit()
    assert app.pack_slaves()[-1] == app.windows["setup"]
    
    speak.take_focus()
    speak.learn()
    assert app.pack_slaves()[-1] == app.windows["learn"]
    
    speak.take_focus()
    i = SESS_SETTINGS["index"]
    speak.next()
    assert i != SESS_SETTINGS["index"]
    
    app.destroy()
    root.destroy()
    SESS_SETTINGS["kana"] = None
    SESS_SETTINGS["mode"] = ""
    
def test_write():
    root = tk.Tk()
    app = App(root)
    SESS_SETTINGS["kana"] = [(KANA[0][0], "hira"), (KANA[1][0], "kata")]
    SESS_SETTINGS["mode"] = "write"
    write = app.windows["write"]
    
    assert write.widgets["stroke_gif"] not in write.grid_slaves()
    assert write.widgets["char_still"] not in write.grid_slaves()
    
    write.take_focus()
    write.show()
    assert write.widgets["stroke_gif"] in write.grid_slaves()
    assert write.widgets["char_still"] in write.grid_slaves()
    
    write.take_focus()
    write.play_audio()
    
    write.quit()
    assert app.pack_slaves()[-1] == app.windows["setup"]
    
    write.take_focus()
    write.learn()
    assert app.pack_slaves()[-1] == app.windows["learn"]
    
    write.take_focus()
    i = SESS_SETTINGS["index"]
    write.next()
    assert i != SESS_SETTINGS["index"]
    
    app.destroy()
    root.destroy()
    SESS_SETTINGS["kana"] = None
    SESS_SETTINGS["mode"] = ""