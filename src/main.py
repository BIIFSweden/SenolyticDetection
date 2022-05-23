from functions import main_analysis
from gui import GUI

def main():
    print("Select Directory in GUI and press Run Analysis")
    gui = GUI()
    gui.mainloop()
    print("Directory chosen.")
    main_analysis(gui.directory,gui.max_quiescent_area)
    return None

if __name__ == "__main__":
    main()
    
