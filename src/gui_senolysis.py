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
            width=30,
        )
        browse_btun.grid(row=0, column=1)

        # Set Red Channel Threshold for senescent classification
        self.red_threshhold_label = tk.Label(
            self.frame,
            text=f"Senescent threshold (0-65,536)",
        )
        self.red_threshhold_label.grid(row=1, column=0)
        self.red_threshold_entry = tk.Entry(
            self.frame, textvariable=tk.IntVar(value=300)
        )
        self.red_threshold_entry.insert(tk.END, "")
        self.red_threshold_entry.grid(row=2, column=0)

        # Set Minumum Nuclei size
        self.nuclei_min_label = tk.Label(
            self.frame,
            text=f"Minimum Nuclei Area (pixels)",
        )
        self.nuclei_min_label.grid(row=1, column=1)
        self.nuclei_min_entry = tk.Entry(self.frame, textvariable=tk.IntVar(value=100))
        self.nuclei_min_entry.insert(tk.END, "")
        self.nuclei_min_entry.grid(row=2, column=1)

        # Set Maximum Nuclei size
        self.nuclei_max_label = tk.Label(
            self.frame,
            text=f"Maximum Nuclei Area (pixels)",
        )
        self.nuclei_max_label.grid(row=1, column=2)
        self.nuclei_max_entry = tk.Entry(
            self.frame, textvariable=tk.IntVar(value=10000)
        )
        self.nuclei_max_entry.insert(tk.END, "")
        self.nuclei_max_entry.grid(row=2, column=2)

        # Set Channel Order
        self.scenescent_channel_label = tk.Label(
            self.frame,
            text=f"Scenescent Channel #",
        )
        self.scenescent_channel_label.grid(row=3, column=0)
        self.scenescent_channel_entry = tk.Entry(
            self.frame, textvariable=tk.IntVar(value=0)
        )
        self.scenescent_channel_entry.insert(tk.END, "")
        self.scenescent_channel_entry.grid(row=4, column=0)

        # Set Channel Order
        self.quiescent_channel_label = tk.Label(
            self.frame,
            text=f"Quiescent Channel #",
        )
        self.quiescent_channel_label.grid(row=3, column=1)
        self.quiescent_channel_entry = tk.Entry(
            self.frame, textvariable=tk.IntVar(value=1)
        )
        self.quiescent_channel_entry.insert(tk.END, "")
        self.quiescent_channel_entry.grid(row=4, column=1)

        # Set Channel Order
        self.nuclei_chanel_label = tk.Label(
            self.frame,
            text=f"Nuclei Channel #",
        )
        self.nuclei_chanel_label.grid(row=3, column=2)
        self.nuclei_chanel_entry = tk.Entry(self.frame, textvariable=tk.IntVar(value=2))
        self.nuclei_chanel_entry.insert(tk.END, "")
        self.nuclei_chanel_entry.grid(row=4, column=2)

        # Get Number of jobs
        self.num_jobs_label = tk.Label(
            self.frame,
            text=f"Enter number of images to run in parallel (max: {os.cpu_count()})",
        )
        self.num_jobs_label.grid(row=5, column=1)
        self.num_jobs_entry = tk.Entry(self.frame, textvariable=tk.IntVar(value=1))
        self.num_jobs_entry.insert(tk.END, "")
        self.num_jobs_entry.grid(row=6, column=1)

        # Remove Well-Ring option
        self.remove_well_ring = tk.IntVar()
        self.well_ring_checkbox = tk.Checkbutton(
            self.frame,
            text="Remove well slide outline from images",
            variable=self.remove_well_ring,
        )
        self.well_ring_checkbox.select()
        self.well_ring_checkbox.grid(row=7, column=1)

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
        run_btun.grid(row=8, column=1)

    # Choose Image Directory
    def select_directory(self):
        browse_text = tk.StringVar()
        browse_text.set("loading...")
        self.directory = askdirectory(parent=self.frame)

    # Save inputs and close GUI
    def quit(self):
        self.num_jobs = int(self.num_jobs_entry.get())
        self.scenescent_threshold = int(self.red_threshold_entry.get())
        self.remove_well_ring = int(self.remove_well_ring.get())
        self.min_nuclei_size = int(self.nuclei_min_entry.get())
        self.max_nuclei_size = int(self.nuclei_max_entry.get())
        self.scenescent_channel = int(self.scenescent_channel_entry.get())
        self.quiescent_channel = int(self.quiescent_channel_entry.get())
        self.nuclei_chanel = int(self.nuclei_chanel_entry.get())
        self.after(100, self.destroy())
