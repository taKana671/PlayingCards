import os
import random
import tkinter as tk

from base import BaseBoard, BaseCard, CardFace
from Globals import BOARD_WIDTH, BOARD_HEIGHT, CARD_ROOT, MOVE_SPEED


PYRAMID_X = int(BOARD_WIDTH / 2)
PYRAMID_Y = int(BOARD_HEIGHT / 5)
PYRAMID_OFFSET_X = 45
PYRAMID_OFFSET_Y = 40
STACK_OFFSET = 0.3
SPACE = 90
JOCKER_X = 50
JOCKER_Y = 100
STOCK_X = int(BOARD_WIDTH * 3 / 4)
STOCK_Y = BOARD_HEIGHT - 80
OPEN_STOCK_X = STOCK_X - SPACE
OPEN_STOCK_Y = STOCK_Y
DISCARD_TEMP_X = OPEN_STOCK_X - 300
DISCARD_X = int(BOARD_WIDTH / 4)
DISCARD_Y = STOCK_Y
DISCARDED = 'discarded'
JOCKER = 'jocker'
STOCK = 'stock'


class Deck:

    def __init__(self, cards_dir):
        self.cards_dir = cards_dir
        self._cards = [card for card in self.get_cards() if not card.mark.startswith(JOCKER)]
        self.jockers = [card for card in self.get_cards() if card.mark.startswith(JOCKER)]

    def get_cards(self):
        for path in self.cards_dir.iterdir():
            name = path.stem
            mark, value = name.split('_')
            yield CardFace(tk.PhotoImage(file=path), mark, int(value))

    def __getitem__(self, position):
        return self._cards[position]

    def __len__(self):
        return len(self._cards)

    def shuffle(self):
        random.shuffle(self._cards)


class CardOnBoard(BaseCard):

    __slots__ = ('status', 'left', 'right')

    def __init__(self, item_id, face, status, x, y,
                 face_up=False, left=None, right=None):
        super().__init__(item_id, face, x, y, face_up)
        self.status = status
        self.left = left
        self.right = right


class Board(BaseBoard):

    def __init__(self, master, status_text, sounds, delay=400, rows=7):
        super().__init__(master, status_text, delay, sounds)
        self.rows = rows
        self.selected = []
        self.now_moving = False
        self.deck = Deck(self.cards_dir)

    def new_game(self):
        self.delete('all')
        self.discard_x = DISCARD_X
        self.discard_y = DISCARD_Y
        # config() changes attributes after creating object.
        self.config(width=BOARD_WIDTH, height=BOARD_HEIGHT)
        self.deck.shuffle()
        self.playing_cards = {}
        # the number of pyramit cards
        limit = int(self.rows * (self.rows + 1) / 2)
        self.setup_pyramid(self.deck[:limit])
        self.setup_stock(self.deck[limit:])
        self.setup_jocker(self.deck.jockers)

        for name in self.playing_cards.keys():
            self.tag_bind(name, '<ButtonPress-1>', self.click)

    def setup_pyramid(self, pyramid_cards):
        # make array as [[1 element], [2 elements], [3 elements],...]
        start = 0
        cards = []
        for i in range(1, self.rows + 1):
            cards.append(pyramid_cards[start:start + i])
            start = start + i
        # layout pyramid
        x, y = PYRAMID_X, PYRAMID_Y
        for i, row in enumerate(cards, 1):
            for j, face in enumerate(row, 1):
                name = f'pyramid{i}{j}'
                item_id = self.create_image(
                    x, y,
                    image=face.image if i == self.rows else self.back,
                    tags=name
                )
                face_up = True if i == self.rows else False
                card = CardOnBoard(item_id, face, 'pyramid', x, y, face_up)
                self.playing_cards[name] = card
                x += SPACE
            x -= (SPACE * i) + PYRAMID_OFFSET_X
            y += PYRAMID_OFFSET_Y
        # set left and right cards
        for i, row in enumerate(cards[:-1], 1):
            for j, _ in enumerate(row, 1):
                card = self.playing_cards[f'pyramid{i}{j}']
                card.left = self.playing_cards[f'pyramid{i + 1}{j}']
                card.right = self.playing_cards[f'pyramid{i + 1}{j + 1}']

    def setup_stock(self, cards):
        x, y = STOCK_X, STOCK_Y
        for i, face in enumerate(cards):
            name = f'{STOCK}{i}'
            item_id = self.create_image(x, y, image=self.back, tags=name)
            card = CardOnBoard(item_id, face, STOCK, x, y)
            self.playing_cards[name] = card
            x += STACK_OFFSET
            y -= STACK_OFFSET

    def setup_jocker(self, jockers):
        x, y = JOCKER_X, JOCKER_Y
        for i, face in enumerate(jockers):
            name = f'{JOCKER}{i}'
            item_id = self.create_image(x, y, image=face.image, tags=name)
            card = CardOnBoard(item_id, face, JOCKER, x, y, True)
            self.playing_cards[name] = card
            x += SPACE

    def click(self, event):
        if not self.now_moving:
            card = self.playing_cards[self.get_tag(event)]
            if card.status == STOCK and not card.face_up:
                if not [card for card in self.playing_cards.values() if card.status == STOCK and card.pin]:
                    self.start_move(card)
            elif card.face_up:
                if not card.pin:
                    self.set_pins(card)
                    self.judge(card)
                else:
                    self.remove_pins(card)
                    self.selected = []

    def start_move(self, card):
        self.destinations = []
        self.move_cards = []
        if stocks := [stock for stock in self.playing_cards.values() \
                        if stock.status == STOCK and stock.face_up and not stock.dele]:
            stock = stocks[0]
            stock.x, stock.y = self.discard_x, self.discard_y
            self.discard_x += STACK_OFFSET
            self.discard_y -= STACK_OFFSET
            stock.status = DISCARDED
            self.destinations.append((DISCARD_TEMP_X, OPEN_STOCK_Y))
            self.move_cards.append(stock)
        card.x, card.y = OPEN_STOCK_X, OPEN_STOCK_Y
        self.destinations.append((OPEN_STOCK_X, OPEN_STOCK_Y))
        self.move_cards.append(card)
        self.is_moved = False
        self.idx = 0
        self.now_moving = True
        self.run_move_sequence()

    def run_move_sequence(self):
        if not self.is_moved:
            self.move_card(self.move_cards[self.idx].id, self.destinations[self.idx])
            self.after(MOVE_SPEED, self.run_move_sequence)
        else:
            self.after_move_sequence(self.move_cards[self.idx])
            self.idx += 1
            if self.idx < len(self.move_cards):
                self.is_moved = False
                self.run_move_sequence()
            else:
                self.now_moving = False

    def after_move_sequence(self, card):
        if not card.face_up:
            self.sounds.open.play()
            self.turn_card(card, True)
        if card.status == DISCARDED:
            self.coords(card.id, card.x, card.y)
            self.tag_raise(card.id)

    def judge(self, card):
        self.update_status(card)
        self.selected.append(card)
        if len(self.selected) == 1 and card.value == 13:
            self.break_foundation(card)
            self.selected = []
        elif len(self.selected) == 2:
            cards = self.selected[0:]
            if sum(card.value == 14 for card in self.selected) >= 1 or \
                    sum(card.value for card in self.selected) == 13:
                self.break_foundation(*cards)
            else:
                self.after(self.delay, lambda: self.bad_choices(cards))
            self.selected = []

    def break_foundation(self, *cards):
        self.after(self.delay, lambda: self.delete_cards(*cards))
        self.after(self.delay + 200, self.pyramid_face_up)

    def pyramid_face_up(self):
        cards = filter(lambda x: x.right and x.left, self.playing_cards.values())
        for card in cards:
            if card.right.dele and card.left.dele and not card.face_up:
                self.sounds.open.play()
                self.turn_card(card, True)

    def update_status(self, card=None):
        val = card.status if card.status == JOCKER else card.value
        if val == 13 or not self.selected:
            status = val
        elif len(self.selected) == 1:
            try:
                text = self.status_text.get()
                status = f'{text} + {val} = {int(text) + int(val)}'
            except ValueError:
                status = f'{text} + {val} = {13}'
        self.status_text.set(status)

    def is_game_end(self):
        if not [card for card in self.playing_cards.values() \
                    if card.status[:7] == 'pyramid' and not card.dele]:
            self.sounds.fanfare.play()


# if __name__ == '__main__':
#     application = tk.Tk()
#     application.title('Pyramid')
#     score_text = tk.StringVar()
#     # board = Board(application, print, score)
#     board = Board(application, score_text)
#     application.mainloop()
