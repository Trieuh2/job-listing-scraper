import os
from gui.main_frame import MainFrame

def main():
    app = MainFrame()
    os.system('cls' if os.name == 'nt' else 'clear')
    app.mainloop()

if __name__ == '__main__':
    main()