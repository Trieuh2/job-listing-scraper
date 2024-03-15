import os
from gui.main_frame import MainFrame

if __name__ == '__main__':
    app = MainFrame()

    # Clear console
    os.system('cls' if os.name == 'nt' else 'clear')
    app.mainloop()