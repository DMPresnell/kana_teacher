"""
Custom widgets used in the app windows.
"""

from itertools import count
import tkinter as tk

from PIL import Image, ImageTk

from kana_learning.kana import KANA

FONT = ("Helvetica", 20)
KANA_CHART_HIGH_BG = "green"

class KanaChart(tk.Frame):
    """Builds a frame that displays either a chart of katakana or
    hiragana.  Also has checkbuttons that will select columns/rows of
    kana.
    """
    
    def __init__(self, master, kana_type, **kwargs):
        
        super().__init__(master, **kwargs)
        self.build_chart(kana_type)
        
    def _checkb_wrapper(self, rc, index, var):
        """'rc' should be either 'r' or 'c' (row or column).
        'index' is the index of the row or column.
        'var' is the variable associated with the checkbutton.
        """

        def _checkb_callback(*args):
            
            if rc == "r":
                widgets = self.grid_slaves(row=index)
            elif rc == "c":
                widgets = self.grid_slaves(column=index)
                
            for w in widgets:
                if var.get():
                    # Highlight row/column
                    w.config(bg=KANA_CHART_HIGH_BG)
                elif not var.get():
                    # Unhighlight row/column
                    if isinstance(w, tk.Checkbutton):
                        # Checkbutton's unhilight to default color
                        w.config(bg="SystemButtonFace")
                    else:
                        # Don't unhighlight if selected by other 
                        # column/row
                        info = w.grid_info()
                        r, c = info["row"], info["column"]
                        if rc == "r":
                            cb_r, cb_c = 0, c
                        else:
                            cb_r, cb_c = r, 0
                        cb = self.grid_slaves(row=cb_r, column=cb_c)[0]
                        if cb.cget("bg") == KANA_CHART_HIGH_BG:
                            continue
                        w.config(bg="white")
        
        return _checkb_callback
        
    def build_chart(self, kana_type):
        
        vowels = list("AIUEO")
        consonants = list(" KSTNHMYRWnGZDBP")
        
        # Digraphs not implemented yet, need solution for j digraphs...
        # digraphs = [
            #"ky", "sh", "ch", "ny", "hy", "my", "ry", "gy", "by", "py"]
        
        let_var_dict = {}
        for letter in vowels + consonants:
            var = tk.BooleanVar()
            let_var_dict[letter] = var
        
        for i in range(len(vowels) + 1):
            self.grid_rowconfigure(i, weight=1)
        for i in range(len(consonants) + 1):
            self.grid_columnconfigure(i, weight=1)
        
        # Build the checkbuttons around the chart.
        for i in range(len(vowels)):
            letter = vowels[i]
            row = i + 1
            var = let_var_dict[letter]
            b = tk.Checkbutton(
                self, text=letter, relief=tk.GROOVE, var=var,
                command=self._checkb_wrapper("r", row, var),
                font=FONT)
            b.grid(row=row, column=0, sticky="nsew")
        for i in range(len(consonants)):
            letter = consonants[i]
            column = i + 1
            var = let_var_dict[letter]
            b = tk.Checkbutton(
                self, text=letter, relief=tk.GROOVE, var=var,
                command=self._checkb_wrapper("c", column, var),
                font=FONT)
            b.grid(row=0, column=column, sticky="nsew")
                
        # Build the label objects for each cell.
        if kana_type == "hira":
            self.name = "Hiragana"
            k = 1
        else:
            self.name = "Katakana"
            k = 2
        
        # The coords of the chart cells that should be left blank.
        blank_coords = [(8, 2), (8, 4), (10, 2), (10, 3), (10, 4), (11, 1),
            (11, 2), (11, 3), (11, 4)]
        counter = 0
        for x in range(1, 17):
            for y in range(1, 6):
                if (x, y) not in blank_coords:
                    l = tk.Label(
                        self, text=KANA[counter][k], font=FONT, bg="white")
                    l.romaji = KANA[counter][0]
                    l.grid(row=y, column=x, sticky="nsew")
                    counter += 1


class DrawingCanvas(tk.Frame):
    """A tkinter Canvas/Button combo.  Is a basic sketch pad with a
    button on the bottom that erases the entire canvas.
    """
    
    def __init__(self, master, **kwargs):
        
        super().__init__(master, bd=4, **kwargs)
        self.prev_pos = None 
        self.load_widgets()
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        
    def load_widgets(self):
        
        self.canvas = tk.Canvas(
            self, cursor="dot", bg="white", bd=4, relief=tk.SUNKEN)
        
        self.erase_button = tk.Button(
            self, text="Erase", font=FONT, command=self.erase)
            
        self.canvas.pack(expand=1, fill="y")
        self.erase_button.pack(fill="x")
        
    def start_draw(self, event):
    
        self.prev_pos = (event.x, event.y)
        
    def draw(self, event):
    
        coords = (self.prev_pos[0], self.prev_pos[1], event.x, event.y)
        self.prev_pos = (event.x, event.y)
        self.canvas.create_line(coords, width=5)
        
    def erase(self):

        for item in self.canvas.find_all():
            self.canvas.delete(item)   


class ImageLabel(tk.Label):
    """Displays a still image, text, or loops through multiple frames.
    Can be passed either a filepath string or a PIL Image object.
    Optional keyword 'frame' is the index of the frame to display as a
    still.
    """
    
    # TODO: handle resizing
    
    def _next_frame(self):
        """Loops through frames."""
        
        self.config(image=self.frames[self.loc])
        self.loc += 1
        self.loc %= len(self.frames)
        self.after(self.delay, self._next_frame)

    def load(self, im, frame=None):
        """Loads up the passed Image object or filename.  If the
        filename doesn't exist, uses text instead.
        """
        
        # im can be either str or a PIL Image object
        if isinstance(im, str):
            try:    
                im = Image.open(im)
            except:
                # If no gif or image file for the kana exists, just use
                # text.
                l = im.split("/")
                k_type = l[-2]
                if k_type == "hira":
                    k_index = 1
                if k_type == "kata":
                    k_index = 2
                k = l[-1].split(".")[0]
                for x in KANA:
                    if k in x:
                        char = x[k_index]
                        self.config(text=char, font=("Helvetica", 100))
                        return
        
        self.loc = 0
        self.frames = []
        
        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass
        
        if not self.frames:
            return
        # If only one frame, return as a still image.
        elif len(self.frames) == 1:
            self.config(image=self.frames[0])
            return
        
        # If a frame index was passed, set that frame as the still.
        if frame:
            try:
                self.config(image=self.frames[frame])
            except IndexError:
                self.config(image=self.frames[-1])
            return
        
        try:
            self.delay = im.info["duration"]
        except KeyError:
            self.delay = 100                         
                        
        self._next_frame()    
            
    def unload(self):
        
        self.config(image=None, text=None)
        self.frames = None
        