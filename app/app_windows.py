"""
Tkinter frames that act as the apps windows..
"""

import os
from random import choice, shuffle
from threading import Thread
import tkinter as tk

from PIL import Image, ImageTk
from playsound import playsound, PlaysoundException

import app.app_widgets as aw

# Path to app images and sounds.
ASSET_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "..", "assets")
FONT = ("Helvetica", 20)
SESS_SETTINGS = {
    "index": 0,     # Index of the kana being quizzed/learned.
    "kana": None,   # Kana currently being quizzed/learned.
    "mode": ""}     # Session mode, determines quizzing or learning.

class App(tk.Frame):
    """Object that runs the app."""
    
    def __init__(self, root):  
        super().__init__(root)
        self.root = root
        self.bind("<Configure>", self._resize_callback)
        self.root.title("Kana Learning")
        self.load_frames()
        self.pack(fill=tk.BOTH, expand=1)

    def _resize_callback(self, event):
        self.ins_label.config(wraplength=self.root.winfo_width() - 8)

    def _msg_var_callback(self, *args):
        self.ins_label.config(text=self.ins_var.get())

    def load_frames(self):
        # Args for ins_label.
        self.ins_var = tk.StringVar()
        self.ins_var.trace("w", self._msg_var_callback)
        
        self.ins_label = tk.Label(
            self, text="", font=FONT, textvariable=self.ins_var, bg="khaki2")
        sep_frame = tk.Frame(self, height=6, bd=3, relief=tk.SUNKEN)
        
        self.ins_label.pack(fill=tk.X, padx=4)
        sep_frame.pack(fill=tk.X, padx=5)
        
        self.windows = {
            "setup": Setup(self),
            "learn": Learn(self),
            "speak": Speak(self),
            "write": Write(self)}
                        
        self.windows["setup"].take_focus()
        

class Popup(tk.Toplevel):
    """Toplevel to message the user. Set timed to False to force user
    to close this window before moving on.
    """
    
    wait_time = 2000
    
    def __init__(self, parent, msg, timed=True, **kwargs):
        super().__init__(parent)
        self.title("!!!")
        
        # Offset popup from topleft of parent slightly.
        x = parent.root.winfo_x() + 5
        y = parent.root.winfo_y() + 5
        self.geometry(f"+{x}+{y}")

        m = tk.Message(self, text=msg, aspect=300, font=FONT)
        b = tk.Button(
            self, text="OK", command=self.destroy, bg="palevioletred1",
            font=FONT)

        m.pack(fill=tk.X, expand=1)
        b.pack(side=tk.BOTTOM, pady=4)
        
        if timed:
            self.after(Popup.wait_time, self.destroy)
        else:
            self.grab_set()
            parent.wait_window()


class AppWindow(tk.Frame):
    """Base class for all the app's windows."""
    
    instructions = ""
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.app = app
        self.root = app.root
        self.widgets = {}
        self.load_widgets()
    
    def load_widgets(self):
        pass
  
        
class Setup(AppWindow):
    """Window where settings are chosen before kicking off learning or
    quizzes.  Settings are saved to SESS_SETTINGS.
    """
    
    instructions = "Choose kana, and choose learning or quizzing."
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        
    def _get_selected_kana(self):
        """Return a list of all kana highlighted from both charts."""
        kana = []
        for w in self.widgets["hira_chart"].grid_slaves():
            if not isinstance(w, tk.Checkbutton):
                if w.cget("bg") != "white":
                    kana.append((w.romaji, "hira"))
        for w in self.widgets["kata_chart"].grid_slaves():
            if not isinstance(w, tk.Checkbutton):
                if w.cget("bg") != "white":
                    kana.append((w.romaji, "kata"))
        
        shuffle(kana)
        return kana
        
    def load_widgets(self):
        # Args and variables for the radio_buttons.
        self.radio_var = tk.StringVar()
        radio_buttons = []
        modes = [
            ("Learn", "learn"),
            ("Speaking Quiz", "speak"),
            ("Writing Quiz", "write"),
            ("Both Quizzes", "both")]
    
        self.rowconfigure(2, weight=1)
        self.rowconfigure(6, weight=1)
        
        # The charts and their checkbuttons.
        kata_chart = aw.KanaChart(self, "kata")
        hira_chart = aw.KanaChart(self, "hira")
        self.off_chart = hira_chart
        self.on_chart = kata_chart
        
        chart_name_label = tk.Label(
            self, text=self.on_chart.name, font=FONT)
        select_all_button = tk.Button(
            self, text="Select All", font=FONT,
            command=self.select_all)      
        deselect_all_button = tk.Button(
            self, text="Deselect All", font=FONT,
            command=self.deselect_all)
        switch_button = tk.Button(
            self, text="Switch Kana", font=FONT,
            command=self.switch_chart)
        padding1 = tk.Label(self)
        # The radio buttons.
        for text, mode in modes:
            rb = tk.Radiobutton(
                self, text=text, font=FONT, var=self.radio_var, value=mode)
            radio_buttons.append(rb)
        padding2 = tk.Label(self)
        start_button = tk.Button(
            self, text="Start", font=FONT, command=self.start)
        
        self.on_chart.grid(columnspan=5, pady=4, padx=4)
        chart_name_label.grid(row=1, column=0)
        select_all_button.grid(row=1, column=2)
        deselect_all_button.grid(row=1, column=3)
        switch_button.grid(row=1, column=4)
        padding1.grid(row=2, sticky="ns")
        radio_buttons[0].grid(row=4, column=1)
        for i in range(len(radio_buttons[1:])):
            radio_buttons[(i + 1)].grid(row=(i + 3), column=3)
        padding2.grid(row=6, sticky="ns")
        start_button.grid(row=7, column=4, padx=4, pady=4, sticky="e")
        
        self.widgets["kata_chart"] = kata_chart
        self.widgets["hira_chart"] = hira_chart
        self.widgets["chart_name_label"] = chart_name_label
        self.widgets["select_all_button"] = select_all_button
        self.widgets["deselect_all_button"] = deselect_all_button
        self.widgets["switch_button"] = switch_button
        self.widgets["padding1"] = padding1
        self.widgets["radio_buttons"] = radio_buttons
        self.widgets["padding2"] = padding2
        self.widgets["start_button"] = start_button
        
    def take_focus(self):      
        self.app.pack_slaves()[-1].pack_forget() # unpack the previous window
        self.app.ins_var.set(self.instructions)
        # self.deselect_all(both=True) # better to leave previous selection?
        self.pack(fill=tk.BOTH, expand=1)
        
    def select_all(self):
        """Highlight all chart cells and select all checkbuttons."""
        buttons = self.on_chart.grid_slaves(row=0)
        buttons.extend(self.on_chart.grid_slaves(column=0))
        for b in buttons:
            if b.cget("bg") == "SystemButtonFace":
                b.invoke()
                    
    def deselect_all(self, both=False):
        """Unhighlight all chart cells and deselect all checkbuttons."""
        buttons = self.on_chart.grid_slaves(row=0)
        buttons.extend(self.on_chart.grid_slaves(column=0))
        if both:
            buttons.extend(self.off_chart.grid_slaves(row=0))
            buttons.extend(self.off_chart.grid_slaves(column=0))
        for b in buttons:
            if b.cget("bg") != "SystemButtonFace":
                b.invoke()
            
    def switch_chart(self):
        """Switch between displaying the kata and hira charts."""
        self.on_chart, self.off_chart = self.off_chart, self.on_chart
        self.off_chart.grid_remove()
        self.widgets["chart_name_label"].config(text=self.on_chart.name)
        self.on_chart.grid(row=0, column=0, columnspan=5)
        
    def start(self):
        """Get user selected settings and start quizzing/teaching."""
        
        kana = self._get_selected_kana()
        if not kana:
            Popup(self, "You must select some hiragana or katakana!")
            return
        SESS_SETTINGS["kana"] = kana
        
        mode = self.radio_var.get()
        if not mode:
            Popup(self, "You must select a mode!")
            return
        SESS_SETTINGS["mode"] = mode
        
        if SESS_SETTINGS["mode"] == "both":
            next_window = choice(["speak", "write"])
            self.app.windows[next_window].take_focus()
        else:
            self.app.windows[SESS_SETTINGS["mode"]].take_focus()
        
        
class Learn(AppWindow):
    """Window that is meant to teach the kana, as opposed to quiz."""
    
    instructions = "Practice brush strokes and speaking."
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)

    def _load_next_kana(self):
        """Load the next kana's media."""
        try:
            kana = SESS_SETTINGS["kana"][SESS_SETTINGS["index"]]
        except IndexError:
            popup = Popup(
                self, "You've looped through all the kana! Starting again...")
            shuffle(SESS_SETTINGS["kana"])
            SESS_SETTINGS["index"] = 0
            kana = SESS_SETTINGS["kana"][SESS_SETTINGS["index"]]
        
        self.widgets["stroke_gif"].destroy()
        self.widgets["stroke_gif"] = aw.ImageLabel(self)
        self.widgets["stroke_gif"].load(os.path.join(
            ASSET_PATH, "images", kana[1], kana[0] + ".gif"))
        self.widgets["stroke_gif"].grid(row=0, column=2, padx=4)
        
        self.widgets["char_still"].unload()
        self.widgets["char_still"].load(os.path.join(
            ASSET_PATH, "images", kana[1], kana[0] + ".gif"), frame=-1)
            
        self.audio_path = os.path.join(
            ASSET_PATH, "sounds", "kana", kana[0] + ".wav")
        t = Thread(target=playsound, args=(self.audio_path,))
        try:
            t.start()
        except PlaysoundException:
            print(">>> No audio for '{}'".format(
                SESS_SETTINGS['kana'][SESS_SETTINGS['index']][0]))

    def _cleanup(self):
        """Prevent the gif from looping when out of sight."""
        self.widgets["stroke_gif"].destroy()

    def load_widgets(self):
        # Variables for the audio_button.
        path = os.path.join(ASSET_PATH, "images", "sound.png")
        self.audio_image = ImageTk.PhotoImage(file=path)
    
        canvas = aw.DrawingCanvas(self)
        stroke_gif = aw.ImageLabel(self) 
        char_still = aw.ImageLabel(self) 
        audio_button = tk.Button(
            self, image=self.audio_image, command=self.play_audio) 
        quit_button = tk.Button(
            self, text="Quit", font=FONT, command=self.quit)
        quiz_button = tk.Button(
            self, text="Quiz Me!", font=FONT, command=self.quiz)
        next_button = tk.Button(
            self, text="Next", font=FONT, comman=self.next)
        
        canvas.grid(columnspan=2, rowspan=2, padx=4, sticky="nsew")
        stroke_gif.grid(row=0, column=2, padx=4)
        char_still.grid(row=1, column=2, padx=4)
        audio_button.grid(row=2, column=2, padx=4, pady=4)
        quit_button.grid(row=3, column=0, padx=4, pady=4, sticky="w")
        quiz_button.grid(row=3, column=1, pady=4)
        next_button.grid(row=3, column=2, padx=4, pady=4, sticky="e")
        
        self.widgets["canvas"] = canvas
        self.widgets["stroke_gif"] = stroke_gif
        self.widgets["char_still"] = char_still
        self.widgets["audio_button"] = audio_button
        self.widgets["quit_button"] = quit_button
        self.widgets["quiz_button"] = quiz_button
        self.widgets["next_button"] = next_button
    
    def take_focus(self):
        self.app.pack_slaves()[-1].pack_forget()
        self.app.ins_var.set(self.instructions)
        self._load_next_kana()
        self.pack(fill=tk.BOTH, expand=1)
        
    def play_audio(self):
        t = Thread(target=playsound, args=(self.audio_path,))
        try:
            t.start()
        except PlaysoundException:
            print(">>> No audio for '{}'".format(
                SESS_SETTINGS['kana'][SESS_SETTINGS['index']][0]))
        
    def quit(self):
        self._cleanup()
        self.app.windows["setup"].take_focus()
        
    def quiz(self):
        """Change the session from learning to quizzing."""
        self._cleanup()
        SESS_SETTINGS["index"] = 0
        SESS_SETTINGS["mode"] = "both"
        next_window = choice(["speak", "write"])
        self.app.windows[next_window].take_focus()
        
    def next(self):
        """Move on to the next kana."""
        self._cleanup()
        SESS_SETTINGS["index"] += 1
        self._load_next_kana()
        
    
class Speak(AppWindow):
    """Window that quizzes by having the user speak."""
    
    instructions = "Say the character shown."
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)

    def _load_next_kana(self):
        """Load the next kana's media."""
        try:
            kana = SESS_SETTINGS["kana"][SESS_SETTINGS["index"]]
        except IndexError:
            popup = Popup(
                self, "You've looped through all the kana! Starting again...")
            shuffle(SESS_SETTINGS["kana"])
            SESS_SETTINGS["index"] = 0
            kana = SESS_SETTINGS["kana"][SESS_SETTINGS["index"]]
        
        self.widgets["stroke_gif"].destroy()
        self.widgets["stroke_gif"] = aw.ImageLabel(self)
        self.widgets["stroke_gif"].load(os.path.join(
            ASSET_PATH, "images", kana[1], kana[0] + ".gif"))
        self.widgets["stroke_gif"].grid(row=0, column=2, padx=4)
        
        self.audio_path = os.path.join(
            ASSET_PATH, "sounds", "kana", kana[0] + ".wav")
        
    def _cleanup(self):
        """Prevent the gif from looping when out of sight."""
        self.widgets["stroke_gif"].destroy()
    
    def load_widgets(self):
        # Args for the audio_button.
        path = os.path.join(ASSET_PATH, "images", "sound.png")
        self.audio_image = ImageTk.PhotoImage(file=path)
        
        stroke_gif = aw.ImageLabel(self)
        audio_button = tk.Button(
            self, image=self.audio_image, command=self.play_audio)
        quit_button = tk.Button(
            self, text="Quit", font=FONT, command=self.quit)
        learn_button = tk.Button(
            self, text="Learn", font=FONT, command=self.learn)
        next_button = tk.Button(
            self, text="Next", font=FONT, command=self.next)
        
        stroke_gif.grid(columnspan=3, padx=4, pady=4)
        audio_button.grid(row=0, column=0, pady=4)
        quit_button.grid(row=2, column=0, padx=4, pady=4, sticky="w")
        learn_button.grid(row=2, column=1, pady=4)
        next_button.grid(row=2, column=2, padx=4, pady=4, sticky="e")
        
        self.widgets["stroke_gif"] = stroke_gif
        self.widgets["audio_button"] = audio_button
        self.widgets["quit_button"] = quit_button
        self.widgets["learn_button"] = learn_button
        self.widgets["next_button"] = next_button
        
    def take_focus(self):
        self.app.pack_slaves()[-1].pack_forget()
        self.app.ins_var.set(self.instructions)
        self._load_next_kana()
        self.pack(fill=tk.BOTH, expand=1)
        
    def play_audio(self):
        t = Thread(target=playsound, args=(self.audio_path,))
        try:
            t.start()
        except PlaysoundException:
            print(">>> No audio for '{}'".format(
                SESS_SETTINGS['kana'][SESS_SETTINGS['index']][0]))
        
    def quit(self):
        self._cleanup()
        self.app.windows["setup"].take_focus()
        
    def learn(self):
        """Switch session from quizzing to learning."""
        self._cleanup()
        SESS_SETTINGS["mode"] = "learn"
        self.app.windows["learn"].take_focus()
        
    def next(self):
        """Move on to the next kana."""
        self._cleanup()
        SESS_SETTINGS["index"] += 1
        if SESS_SETTINGS["mode"] == "both":
            next_window = choice(["speak", "write"])
        else:
            next_window = "speak"
        if next_window == "speak":
            self._load_next_kana()
        else:
            self.app.windows[next_window].take_focus()
    
    
class Write(AppWindow):
    """Window that quizzes by having the user write.""" 

    instructions = "Write the character spoken."

    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)

    def _load_next_kana(self):
        try:
            kana = SESS_SETTINGS["kana"][SESS_SETTINGS["index"]]
        except IndexError:
            popup = Popup(
                self, "You've looped through all the kana! Starting again...")
            shuffle(SESS_SETTINGS["kana"])
            SESS_SETTINGS["index"] = 0
            kana = SESS_SETTINGS["kana"][SESS_SETTINGS["index"]]
        
        self.widgets["canvas"].erase()
        
        self.widgets["stroke_gif"].destroy()
        self.widgets["stroke_gif"] = aw.ImageLabel(self)
        self.widgets["stroke_gif"].load(os.path.join(
            ASSET_PATH, "images", kana[1], kana[0] + ".gif"))
        self.widgets["stroke_gif"].grid(row=0, column=2, padx=4)
        
        self.widgets["char_still"].unload()
        self.widgets["char_still"].load(os.path.join(
            ASSET_PATH, "images", kana[1], kana[0] + ".gif"), frame=-1)
            
        self.widgets["show_button"].grid(row=0, column=2, padx=4, pady=4)
        self.widgets["stroke_gif"].grid_forget()
        self.widgets["char_still"].grid_forget()
        
        self.audio_path = os.path.join(
            ASSET_PATH, "sounds", "kana", kana[0] + ".wav")
        t = Thread(target=playsound, args=(self.audio_path,))
        try:
            t.start()
        except PlaysoundException:
            print(">>> No audio for '{}'...".format(
                SESS_SETTINGS['kana'][SESS_SETTINGS['index']][0]))
    
    def _cleanup(self):
        """Prevent the gif from looping when out of sight."""
        self.widgets["stroke_gif"].destroy()
    
    def load_widgets(self):
        # Args for the audio_button.
        path = os.path.join(ASSET_PATH, "images", "sound.png")
        self.audio_image = ImageTk.PhotoImage(file=path)
        
        canvas = aw.DrawingCanvas(self)
        show_button = tk.Button(
            self, text="Show Answer", font=FONT, command=self.show)
        stroke_gif = aw.ImageLabel(self)
        char_still = aw.ImageLabel(self)
        audio_button = tk.Button(
            self, image=self.audio_image, command=self.play_audio)
        quit_button = tk.Button(
            self, text="Quit", font=FONT, command=self.quit)
        learn_button = tk.Button(
            self, text="Learn", font=FONT, command=self.learn)
        next_button = tk.Button(
            self, text="Next", font=FONT, command=self.next)
        
        canvas.grid(rowspan=2, columnspan=2, padx=4, pady=4, sticky="nsew")
        show_button.grid(row=0, column=2, padx=4, pady=4)
        audio_button.grid(row=2, column=0, padx=4, pady=4)
        quit_button.grid(row=3, column=0, padx=4, pady=4, sticky="w")
        learn_button.grid(row=3, column=1, padx=4, pady=4)
        next_button.grid(row=3, column=2, padx=4, pady=4, sticky="e")
        
        self.widgets["canvas"] = canvas
        self.widgets["show_button"] = show_button
        self.widgets["stroke_gif"] = stroke_gif
        self.widgets["char_still"] = char_still
        self.widgets["audio_button"] = audio_button
        
    def take_focus(self):
        self.app.pack_slaves()[-1].pack_forget()
        self.app.ins_var.set(self.instructions)
        self._load_next_kana()
        self.pack(fill=tk.BOTH, expand=1)
        
    def show(self):
        """Displays the character gif and still image."""
        self.widgets["show_button"].grid_remove()
        self.widgets["stroke_gif"].grid(row=0, column=2, padx=4, pady=4)
        self.widgets["char_still"].grid(row=1, column=2, padx=4, pady=4)
        
    def play_audio(self):
        t = Thread(target=playsound, args=(self.audio_path,))
        try:
            t.start()
        except PlaysoundException:
            print(f">>> No audio for "
                "'{SESS_SETTINGS['kana'][SESS_SETTINGS['index']][0]}'...")
        
    def quit(self):
        self._cleanup()
        self.app.windows["setup"].take_focus()
        
    def learn(self):
        """Switch session from quizzing to learning."""
        self._cleanup()
        SESS_SETTINGS["mode"] = "learn"
        self.app.windows["learn"].take_focus()
        
    def next(self):
        """Move on to the next kana."""
        self._cleanup()
        SESS_SETTINGS["index"] += 1
        if SESS_SETTINGS["mode"] == "both":
            next_window = choice(["speak", "write"])
        else:
            next_window = "write"
        if next_window == "write":
            self._load_next_kana()
        else:
            self.app.windows[next_window].take_focus()