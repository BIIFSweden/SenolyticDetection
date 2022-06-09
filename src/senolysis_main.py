from functions import main_analysis
from gui import GUI

def main():
    print("Select Directory in GUI and press Run Analysis")
    gui = GUI()
    gui.mainloop()
    user_parameters = gui.get_user_parameters()
    print("Directory chosen.")
    main_analysis(user_parameters)
    return None

if __name__ == "__main__":
    main()
    
