from functions import main_analysis
from gui import GUI


if __name__ == "__main__":
    print("Select Directory in GUI and press Run Analysis")
    gui = GUI()
    gui.mainloop()
    print("Directory chosen.")
    main_analysis(gui.directory)
    print("Analysis Finished.")
