class Start(AppWindow):
    """The start screen, where a user profile is selected, or no profile.
    Profile dictionary is retrieved from db or created and passed to Setup
    window."""
    
    instructions = "Choose an existing profile, or create a new one."    
    
    def __init__(self, app, **kwargs):
    
        super().__init__(app, **kwargs)
        
    def _get_profile_names(self):
        """Called in load_widgets() to get profiles from the database."""
        
        self.profile_names = []
        with dbm.open(PROFILE_DATABASE, "c") as db:
            for name in db.keys():
                self.profile_names.append(name)
                
    def _make_new_profile_dict(self, name):
        """Called in next()."""
        
        # TODO: make the variables for this
        self.app.sess_settings["profile"] = {"name": name}
        
    def _dropdown_callback(self, *args):
        
        if self.profile_var.get() == "Create New":
            self.widgets["entry"].config(state="normal")
        else:
            self.widgets["entry"].delete(0, tk.END)
            self.widgets["entry"].config(state="disabled")
            
    def load_widgets(self):
        """Create and configure all of this frame's widgets."""

        self.rowconfigure(2, weight=1) # for the filler below entry widget
        
        # dropdown menu
        self._get_profile_names()
        self.profile_var = tk.StringVar()
        self.profile_var.set("Select Profile")
        self.profile_var.trace("w", self._dropdown_callback)
        options = ["Create New"] + self.profile_names        
        dropdown = tk.OptionMenu(self, self.profile_var, *options)
        dropdown.configure(font=FONT, takefocus=True)
        # Get the actual options menu from the dropdown and config its font
        dropdown_opts = self.nametowidget(dropdown.menuname)
        dropdown_opts.config(font=FONT)
        
        entry = tk.Entry(self, font=FONT, width=20,
            bg="lightgray")
        entry.config(state="disabled", bg="white")
        
        padding1 = tk.Label(self)

        next_button = tk.Button(self, text="Next", command=self.next,
            font=FONT)
        
        dropdown.grid(sticky="w", padx=4, pady=4)
        entry.grid(sticky="w", padx=4, pady=4)
        padding1.grid(sticky="ns")
        next_button.grid(sticky="w", padx=4, pady=4)
        
        self.widgets["dropdown"] = dropdown
        self.widgets["entry"] = entry
        self.widgets["padding1"] = padding1 # Might not need to access again?
        self.widgets["next_button"] = next_button
        
    def take_focus(self):
        
        self.app.pack_slaves()[-1].pack_forget() # forget the previous window
        self.app.ins_var.set(self.instructions)
        self.app.sess_settings["profile"] = None
        self._get_profile_names()
        self.profile_var.set("Select Profile")
        self.pack(fill=tk.BOTH, expand=1)
        
    def next(self):
        """Makes sure the user selected a profile option and passes
        it to the setup screen"""    
        
        saved_profile = self.profile_var.get()
        new_profile = self.widgets["entry"].get()
        
        if saved_profile == "Select Profile":
            Popup(self, "Select a profile, or create a new one!")
        elif saved_profile == "Create New":
            if new_profile:
                if new_profile not in self.profile_names:  #TODO: TEST THIS
                    # Create profile data dict for new profile and pass along.
                    self._make_new_profile_dict(new_profile)
                    self.app.windows["setup"].take_focus()
                else:
                    Popup(self, "Profile already exists!")
            else:
                Popup(self, "Enter a new profile name!")
        else:
            # Existing profile was selected, get profile's data from the db,
            # set profile variable and then pass it to the setup window.
            with dbm.open(PROFILE_DATABASE, "c") as db:
                self.app.sess_settings["profile"] = db[saved_profile]
            self.app.windows["setup"].take_focus()