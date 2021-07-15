import os
import sys
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')))
import tkinter as tk

import window
from globals import APP_NAME


def main():
    application = tk.Tk()
    application.withdraw()
    application.title(APP_NAME)
    application.option_add('tearOff', False)
    win = window.Window(application)
    application.protocol('WM_DELETE_WINDOW', win.close)
    application.deiconify()
    application.mainloop()


main()
