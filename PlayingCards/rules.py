import os
import tkinter as tk
import tkinter.ttk as ttk

from globals import *


class Window(tk.Toplevel):

    def __init__(self, master, game):
        super().__init__(master)
        self.withdraw()
        self.title('Rules')
        self.create_ui(game)
        self.reposition()
        self.resizable(False, False)
        self.deiconify()
        self.wait_visibility()


    def create_ui(self, game):
        title, rule = rules[game]
        self.title_label = ttk.Label(self, text=title, anchor="c", 
            foreground='blue', background='white', font=("",18))
        self.body_label = ttk.Label(self, text=rule, background='white')
        self.close_button = ttk.Button(self, text='Close', command=self.close)
        self.title_label.pack(side='top', expand=True, fill=tk.BOTH)
        self.body_label.pack(side='top', expand=True, fill=tk.BOTH)
        self.close_button.pack(anchor=tk.S)
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.bind('<Escape>', self.close)
        self.bind('<Expose>', self.reposition)


    def reposition(self, event=None):
        if self.master is not None:
            self.geometry('+{}+{}'.format(self.master.winfo_rootx() + BOARD_WIDTH,
                self.master.winfo_rooty() + 50))


    def switch_text(self, game):
        title, rule = rules[game]
        self.title_label.config(text=title)
        self.body_label.config(text=rule)


    def close(self, event=None):
        self.withdraw()


PYRAMID_RULES = """
  - Discard exposed pairs of cards that add up to 13 
    until pyramid is cleared or you're out of cards.
  - Exposed cards in the pyramid that are not overlapping
    or come from the top or the draw pile.
  - Draw 1 card at a time, which can be used for a pair
    until the next draw.
  - Aces = 1, J = 11, Q = 12, K = 13
  
  """

KLONEDIKE_RULES = """
  - The object of the game is to build all the cards face up
    on the foundations. Each foundation builds upward, 
    in sequence, from the ace to the king. 
  - Only aces may be moved to an empty foundation, and only 
    the next higher card of the same suit can be added to 
    the foundation.
  - You advance the game by building on the face-up cards in 
    the tableau in descending sequence of alternating colors. 
    For example, only the 9 of hearts or diamonds (red suits) 
    may play on the 10 of spades (a black suit). 
  - Cards can be built on the tableau piles by moving them from 
    another tableau pile or the top of the turned up cards from
    the deck.
  - Whenever the face-up cards in a column are moved, the 
    uncovered face-down card becomes available to turn up. 
    Only a king, or a sequence headed by a king, may be moved 
    to an empty column.

"""

CLOVERS_RULES = """
  - Find a combination of cards with the same mark for a 
    total of 15. Such cards can be removed.
  - J, Q, and K are not numbers, and when J, Q, and K are 
    the same mark, all the three can be removed.
  - Aces = 1

"""

rules = {
    PYRAMID.lower(): (PYRAMID, PYRAMID_RULES),
    CLOVER.lower(): ('Four Leaf Clovers', CLOVERS_RULES),
    KLONEDIKE.lower(): (KLONEDIKE, KLONEDIKE_RULES),
}


if __name__ == '__main__':
    application = tk.Tk()
    window = Window(application, 'pyramid')
    application.bind("<Control-q>", lambda *args: application.quit())
    window.bind("<Control-q>", lambda *args: application.quit())
    application.mainloop()



