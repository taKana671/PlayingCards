import os
import tkinter as tk
import tkinter.ttk as ttk

import pyramid
from globals import *


class Window(ttk.Frame):

    def __init__(self, master):
        super().__init__(master, padding=PAD)
        self.create_variables()
        self.create_images()
        self.create_ui()


    def create_variables(self):
        self.images = {}
        self.status_text = tk.StringVar()


    def create_images(self):
        image_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), IMAGE_ROOT)
        for name in (CLOSE, PYRAMID, PIN, BACK, RELOAD):
            self.images[name] = tk.PhotoImage(
                file=os.path.join(image_path, '{}.png'.format(name)))


    def create_ui(self):
        self.create_board()
        self.create_menubar()
        self.create_statusbar()


    def create_board(self):
        self.board = pyramid.Board(self.master, self.status_text, self.images[BACK], self.images[PIN])
        self.board.pack(fill=tk.BOTH, expand=True)


    def create_menubar(self):
        self.menubar = tk.Menu(self.master)
        self.master.config(menu=self.menubar)
        self.create_game_menu()
        self.create_help_menu()
        

    def create_game_menu(self):
        gamemenu = tk.Menu(self.menubar, tearoff=0, name='game')
        gamemenu.add_command(label=PYRAMID, command=self.board.new_game,
            compound=tk.LEFT, image=self.images[PYRAMID])
        gamemenu.add_command(label=CLOSE, command='',
            compound=tk.LEFT, image=self.images[CLOSE])
        self.menubar.add_cascade(label="Game", menu=gamemenu)


    def create_help_menu(self):
        helpmenu = tk.Menu(self.menubar, tearoff=0, name='help')
        helpmenu.add_command(label=PYRAMID, command='',
            compound=tk.LEFT, image=self.images[PYRAMID])
        self.menubar.add_cascade(label="Help", menu=helpmenu)


    def create_statusbar(self):
        statusbar = ttk.Frame(self.master)
        repeat_btn = ttk.Button(statusbar, image=self.images[RELOAD], width=5, command=self.board.new_game)
        repeat_btn.pack(side=tk.RIGHT, pady=PAD)
        status_label = ttk.Label(statusbar, textvariable=self.status_text, font=('', 20))
        status_label.pack(side=tk.LEFT)
        statusbar.columnconfigure(0, weight=1)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        


    def close(self, event=None):
        self.quit()


if __name__ == '__main__':
    app = tk.Tk()
    app.title('Window')
    window = Window(app)
    app.protocol('WM_DELETE_WINDOW', window.close)
    app.mainloop()