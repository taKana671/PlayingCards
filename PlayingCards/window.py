import os
import tkinter as tk
import tkinter.ttk as ttk

import fourleafclover
import pyramid
from globals import *


class Window(ttk.Frame):

    def __init__(self, master):
        super().__init__(master, padding=PAD)
        self.create_variables()
        self.create_images()
        self.create_ui()


    def create_variables(self):
        self.games = {}
        self.images = {}
        self.status_text = tk.StringVar()


    def create_images(self):
        image_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), IMAGE_ROOT)
        for name in (CLOSE, PYRAMID, RELOAD, CLOVER, RULES):
            self.images[name] = tk.PhotoImage(
                file=os.path.join(image_path, '{}.png'.format(name)))


    def create_ui(self):
        self.create_board()
        self.create_menubar()
        self.create_statusbar()
        self.change_board(PYRAMID)


    def create_board(self):
        container = tk.Frame(self.master)
        container.pack(fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        for name, module in zip((PYRAMID, CLOVER), (pyramid, fourleafclover)):
            frame = tk.Frame(container) 
            frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            game = module.Board(frame, self.status_text)
            game.pack(fill=tk.BOTH, expand=True)
            self.games[name] = (frame, game)


    def create_menubar(self):
        self.menubar = tk.Menu(self.master)
        self.master.config(menu=self.menubar)
        self.create_game_menu()
        self.create_help_menu()
        

    def create_game_menu(self):
        gamemenu = tk.Menu(self.menubar, tearoff=0, name='game')
        gamemenu.add_command(label=PYRAMID, command=lambda: self.change_board(PYRAMID),
            compound=tk.LEFT, image=self.images[PYRAMID])
        gamemenu.add_command(label=CLOVER, command=lambda: self.change_board(CLOVER),
            compound=tk.LEFT, image=self.images[CLOVER])
        gamemenu.add_command(label=CLOSE, command=self.close,
            compound=tk.LEFT, image=self.images[CLOSE])
        self.menubar.add_cascade(label="Game", menu=gamemenu)


    def create_help_menu(self):
        helpmenu = tk.Menu(self.menubar, tearoff=0, name='help')
        helpmenu.add_command(label=RULES, command='',
            compound=tk.LEFT, image=self.images[RULES])
        self.menubar.add_cascade(label="Help", menu=helpmenu)


    def create_statusbar(self):
        statusbar = ttk.Frame(self.master)
        repeat_btn = ttk.Button(statusbar, image=self.images[RELOAD], width=5, command=self.new_game)
        repeat_btn.pack(side=tk.RIGHT, pady=PAD)
        status_label = ttk.Label(statusbar, textvariable=self.status_text, font=('', 20))
        status_label.pack(side=tk.LEFT)
        statusbar.columnconfigure(0, weight=1)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        

    def change_board(self, board_name):
        flame, board = self.games[board_name]
        flame.tkraise()
        self.board = board
        self.new_game()


    def new_game(self):
        self.status_text.set('')
        self.board.new_game()


    def close(self, event=None):
        self.quit()



if __name__ == '__main__':
    app = tk.Tk()
    app.title('Window')
    window = Window(app)
    app.protocol('WM_DELETE_WINDOW', window.close)
    app.mainloop()