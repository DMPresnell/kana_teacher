import os
import pytest
import tkinter as tk

from app.app_widgets import *


def test_kanachart():
    root = tk.Tk()
    hc = KanaChart(root, "hira")
    kc = KanaChart(root, "kata")
    
    root.destroy()
    
def test_drawingcanvas():
    root = tk.Tk()
    c = DrawingCanvas(root)
    
    root.destroy()
    
def test_imagelabel():
    root = tk.Tk()
    l = ImageLabel(root)
    
    l.load(os.path.join("tests", "test_gif.gif"))
    assert len(l.frames) > 1
    
    l.unload()
    assert [l.cget("text"), l.cget("image")] == ["", ""]
    
    l.load(os.path.join("tests", "test_gif.gif"), frame=-1)
    
    l.unload()
    
    l.load(os.path.join("hira", "a.gif"))
    assert l.cget("text") != ""
    assert l.cget("image") == ""
    
    root.destroy()