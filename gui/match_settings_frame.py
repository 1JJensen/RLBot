import tkinter as tk
from tkinter import ttk


class SettingsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        ttk.Label(self, text="Match settings").pack()
