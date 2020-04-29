"""
App for learning to speak and write Japanese katakana and
hiragana.  Implements tkinter for the GUI.
"""

import sys
import tkinter as tk

from kana_teacher.windows import App

def main():    
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()