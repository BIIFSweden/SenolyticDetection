import tkinter as tk
from tkinter.filedialog import askdirectory


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # Create Frame
        self.frame = tk.Frame()
        self.frame.pack()
        self.title("Scenescent Analysis")

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
        browse_btun.grid(column=1, row=0)

        # Run Analysis Button - Just closes GUI
        run_text = tk.StringVar()
        run_text.set("Run Analysis")
        run_btun = tk.Button(
            self.frame,
            textvariable=run_text,
            command=lambda: self.quit_gui(),
            height=2,
            width=10,
        )
        run_btun.grid(column=1, row=1)

    # Choose Image Directory
    def select_directory(self):
        browse_text = tk.StringVar()
        browse_text.set("loading...")
        self.directory = askdirectory(parent=self.frame)
        browse_text.set(self.directory)

    def quit_gui(self):
        self.after(100, self.destroy())
