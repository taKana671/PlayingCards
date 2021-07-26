import os
import tkinter as tk
import tkinter.ttk as ttk

import pygame

import couple
import fourleafclover
import klonedike
import pyramid
import rules
from Globals import (PAD, IMAGE_ROOT, CLOSE, PYRAMID, RELOAD, CLOVER, RULES,
    KLONEDIKE, COUPLE, DISAPPEAR, LINEUP, MISTAKE, SHUFFLE, OPEN, CHANGE, FANFARE)


pygame.init()


class Sounds:

    def __init__(self):
        self.create_sound_effect()

    def create_sound_effect(self):
        self.disappear = pygame.mixer.Sound(DISAPPEAR)
        self.lineup = pygame.mixer.Sound(LINEUP)
        self.mistake = pygame.mixer.Sound(MISTAKE)
        self.shuffle = pygame.mixer.Sound(SHUFFLE)
        self.open = pygame.mixer.Sound(OPEN)
        self.change = pygame.mixer.Sound(CHANGE)
        self.fanfare = pygame.mixer.Sound(FANFARE)


class Window(ttk.Frame):

    def __init__(self, master):
        super().__init__(master, padding=PAD)
        self.sounds = Sounds()
        self.create_variables()
        self.create_images()
        self.create_ui()

    def create_variables(self):
        self.games = {}
        self.images = {}
        self.status_text = tk.StringVar()
        self.rule = None

    def create_images(self):
        image_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), IMAGE_ROOT)
        for name in (CLOSE, PYRAMID, RELOAD, CLOVER, RULES, KLONEDIKE, COUPLE):
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
        # sounds = Sounds()
        for name, module in zip((PYRAMID, CLOVER, KLONEDIKE, COUPLE),
                                (pyramid, fourleafclover, klonedike, couple)):
            frame = tk.Frame(container)
            frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            game = module.Board(frame, self.status_text, self.sounds)
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
        gamemenu.add_command(label=KLONEDIKE, command=lambda: self.change_board(KLONEDIKE),
                             compound=tk.LEFT, image=self.images[KLONEDIKE])
        gamemenu.add_command(label=COUPLE, command=lambda: self.change_board(COUPLE),
                             compound=tk.LEFT, image=self.images[COUPLE])
        gamemenu.add_command(label=CLOSE, command=self.close,
                             compound=tk.LEFT, image=self.images[CLOSE])
        self.menubar.add_cascade(label="Game", menu=gamemenu)

    def create_help_menu(self):
        helpmenu = tk.Menu(self.menubar, tearoff=0, name='help')
        helpmenu.add_command(
            label=RULES, command=self.show_rules, compound=tk.LEFT, image=self.images[RULES])
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
        if self.rule:
            self.rule.switch_text(self.board.__module__)

    def new_game(self):
        self.sounds.change.play()
        self.status_text.set('')
        self.board.new_game()

    def show_rules(self):
        if self.rule is None:
            self.rule = rules.Window(self, self.board.__module__)
        else:
            self.rule.deiconify()

    def close(self, event=None):
        self.quit()


if __name__ == '__main__':
    app = tk.Tk()
    app.title('Window')
    window = Window(app)
    app.protocol('WM_DELETE_WINDOW', window.close)
    app.mainloop()
