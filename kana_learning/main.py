"""
App for learning to speak and write Japanese katakana and
hiragana.  Implements tkinter for the GUI.
"""

import tkinter as tk

from kana_learning.app_windows import App

def main():    

    root = tk.Tk()
    app = App(root)
    root.mainloop()
    
if __name__ == "__main__":

    main()