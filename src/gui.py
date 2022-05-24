from sqlite3 import Row
import tkinter as tk
from tkinter.filedialog import askdirectory
from tkinter.tix import COLUMN, ROW


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # Create Frame
        self.frame = tk.Frame()
        self.frame.grid(columnspan=1,rowspan=4,sticky=tk.W+tk.E)
        self.title("Scenescent Analysis")
        self.frame.grid_rowconfigure((0,2),weight=1)

        # Get Directory Input Button
        directory_text = tk.StringVar()
        directory_text.set("Select directory containing image(s)")
        browse_btun = tk.Button(
            self.frame,
            textvariable=directory_text,
            command=lambda: self.select_directory(),
            height=2,
            width=50,
        )
        browse_btun.grid(column=0, row=0,padx=10, pady=10)

        #Take maximum quiescent size
        var = tk.StringVar()
        max_quiescent_area_label = tk.Label(self.frame,text="Maximum area (pixels\u00b2) of quiescent nuclei ")
        max_quiescent_area_label.grid(column=0, row=1,padx=5, pady=0)
        self.max_quiescent_area_entry = tk.Entry(self.frame, textvariable=var)
        self.max_quiescent_area_entry.insert(tk.END, "3000")
        self.max_quiescent_area_entry.grid(column=0, row=2,padx=5, pady=0)

        # Run Analysis Button
        run_text = tk.StringVar()
        run_text.set("Run Analysis")
        run_btun = tk.Button(
            self.frame,
            textvariable=run_text,
            command=lambda: self.getInputs(),
            height=2,
            width=10,
        )
        run_btun.grid(column=0, row=3,padx=10, pady=10)

    # Choose Image Directory
    def select_directory(self):
        browse_text = tk.StringVar()
        browse_text.set("loading...")
        self.directory = askdirectory(parent=self.frame)
        #browse_text.set(self.directory)

    # Save inputs and close GUI
    def getInputs(self):
        self.max_quiescent_area = int(self.max_quiescent_area_entry.get())
        self.after(100, self.destroy())


   
