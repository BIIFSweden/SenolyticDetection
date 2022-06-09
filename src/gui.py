from sqlite3 import Row
import tkinter as tk
from tkinter.filedialog import askdirectory
from tkinter.tix import COLUMN, ROW
from turtle import right

from numpy import place, size

class Parameters:
    def __init__(
        self,
        folder_path,
        max_quiescent_area,
        red_gamma,
        green_gamma,
    ):
        self.folder_path = folder_path
        self.max_quiescent_area = max_quiescent_area
        self.red_gamma = red_gamma
        self.green_gamma = green_gamma

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # Create Frame
        self.frame = tk.Frame()
        self.frame.pack(fill='both',expand=1)
        self.title("Senolysis Analysis")
        

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
        browse_btun.pack()

        #Take maximum quiescent size
        var = tk.StringVar()
        max_quiescent_area_label = tk.Label(self.frame,text="Maximum area (pixels\u00b2) of quiescent nuclei ")
        max_quiescent_area_label.pack()
        self.max_quiescent_area_entry = tk.Entry(self.frame, textvariable=var)
        self.max_quiescent_area_entry.insert(tk.END, "3000")
        self.max_quiescent_area_entry.pack()


        #Red Channel Gamma
        var = tk.StringVar()
        red_gamma_label = tk.Label(self.frame,text="Red Channel Gamma")
        red_gamma_label.pack()
        self.red_gamma__entry = tk.Entry(self.frame, textvariable=var)
        self.red_gamma__entry.insert(tk.END, "1")
        self.red_gamma__entry.pack()

        #Green Channel Gamma
        var = tk.StringVar()
        green_gamma_label = tk.Label(self.frame,text="Green Channel Gamma")
        green_gamma_label.pack()
        self.green_gamma__entry = tk.Entry(self.frame, textvariable=var)
        self.green_gamma__entry.insert(tk.END, "1")
        self.green_gamma__entry.pack()

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
        run_btun.pack()

    # Choose Image Directory
    def select_directory(self):
        browse_text = tk.StringVar()
        browse_text.set("loading...")
        self.directory = askdirectory(parent=self.frame)

    # Save inputs and close GUI
    def getInputs(self):
        self.max_quiescent_area = int(self.max_quiescent_area_entry.get())
        self.red_gamma = float(self.red_gamma__entry.get())
        self.green_gamma = float(self.green_gamma__entry.get())
        self.after(100, self.destroy())

    def get_user_parameters(self):
        user_parameters = Parameters(
            self.directory,
            self.max_quiescent_area,
            self.red_gamma,
            self.green_gamma
        )
        return user_parameters
