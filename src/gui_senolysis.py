from dataclasses import dataclass
import tkinter as tk
from tkinter.filedialog import askdirectory
import os


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # Create Frame
        self.frame = tk.Frame()
        self.frame.pack(fill="both", expand=1)
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

        # Set Red Channel Threshold for senescent classification
        self.red_threshhold_label = tk.Label(
            self.frame,
            text=f"Enter the red-channel threshold (0-65,536) used for senescent classification",
        )
        self.red_threshhold_label.pack()
        self.red_threshold_entry = tk.Entry(self.frame, textvariable=tk.StringVar())
        self.red_threshold_entry.insert(tk.END, "100")
        self.red_threshold_entry.pack()

        # Get Number of jobs
        self.num_jobs_label = tk.Label(
            self.frame,
            text=f"Enter number of images to run in parallel (max: {os.cpu_count()})",
        )
        self.num_jobs_label.pack()
        self.num_jobs_entry = tk.Entry(self.frame, textvariable=tk.StringVar())
        self.num_jobs_entry.insert(tk.END, "1")
        self.num_jobs_entry.pack()

        # Run Analysis Button
        run_text = tk.StringVar()
        run_text.set("Run Analysis")
        run_btun = tk.Button(
            self.frame,
            textvariable=run_text,
            command=lambda: self.quit(),
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
    def quit(self):
        self.num_jobs = int(self.num_jobs_entry.get())
        self.red_threshold = int(self.num_jobs_entry.get())
        self.after(100, self.destroy())

