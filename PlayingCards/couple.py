from collections import namedtuple
import os
import random
import tkinter as tk

from base import BaseBoard, BaseCard, CardFace
from globals import BOARD_WIDTH, BOARD_HEIGHT, CARD_ROOT, MOVE_SPEED


CARD_X = int(BOARD_WIDTH / 2) - 150
CARD_Y = 100
CARD_OFFSET_Y = 130
STACK_OFFSET = 0.3
SPACE = 90
STOCK_X = BOARD_WIDTH - 150
STOCK_Y = BOARD_HEIGHT - 100


MoveCard = namedtuple('MoveCard', ['card', 'dest_x', 'dest_y'])



class Card(BaseCard):

    __slots__ = ('order')

    def __init__(self, item_id, face, x, y, face_up=False, order=None):
        super().__init__(item_id, face, x, y, face_up)
        self.order = order


class Board(BaseBoard):

    def __init__(self, master, status_text, delay=400, rows=4, columns=4):
        self.row_position = 0
        self.col_position = 0
        self.selected = []
        self.now_moving = False
        super().__init__(master, status_text, delay)

    def new_game(self):
        self.delete('all')
        # config() changes attributes after creating object.
        self.config(width=BOARD_WIDTH, height=BOARD_HEIGHT)
        random.shuffle(self.deck)
        self.playing_cards = {}
        # sep = self.rows*self.columns
        self.setup_cards(self.deck[:12])
        self.set_stock_cards(self.deck[12:])
        for name in self.playing_cards.keys():
            self.tag_bind(name, '<ButtonPress-1>', self.click)
        self.faceup_cards = [card for name, card in self.playing_cards.items() if name.startswith('card')]

    def create_card(self):
        image_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), CARD_ROOT)
        for path in os.listdir(image_path):
            name = os.path.splitext(path)[0]
            mark, value = name.split('_')
            if not mark.startswith('jocker'):
                yield CardFace(tk.PhotoImage(
                    file=os.path.join(image_path, path)), mark, int(value))

    # def set_cards(self, cards):
    #     self.col_position, self.row_position = 0, 0
    #     for i, card in enumerate(cards):
    #         if i % 4 == 0:
    #             self.row_position += CARD_OFFSET_Y
    #             self.col_position = CARD_X
    #         else:
    #             x += SPACE
    #         card.x, card.y = self.col_position, self.row_position
    #         self.moveto(card.id, x, y)

    def setup_cards(self, cards):
        self.col_position, self.row_position = 0, 0
        for i, face in enumerate(cards):
            if i % 4 == 0:
                self.row_position += CARD_OFFSET_Y
                self.col_position = CARD_X
            else:
                self.col_position += SPACE
            name = 'card{}'.format(i)
            item_id = self.create_image(
                self.col_position, self.row_position, image=face.image, tags=name)
            card = Card(item_id, face, self.col_position, self.row_position, True, i)
            self.playing_cards[name] = card

    def set_stock_cards(self, cards):
        x, y = STOCK_X, STOCK_Y
        for i, face in enumerate(cards):
            name = 'stock{}'.format(i)
            item_id = self.create_image(x, y, image=self.back, tags=name)
            card = Card(item_id, face, x, y)
            self.playing_cards[name] = card
            x += STACK_OFFSET
            y -= STACK_OFFSET

    def click(self, event):
        if not self.now_moving:
            card = self.playing_cards[self.get_tag(event)]
            if card.face_up:
                if not card.pin:
                    self.set_pins(card)
                    self.judge(card)
                else:
                    self.remove_pins(card)
                    self.selected.remove(card)
            else:
                self.put_stock_card(card)

    def rearange_cards(self):
        self.col_position, self.row_position = 0, 0
        for i, card in enumerate(self.faceup_cards):
            if i % 4 == 0:
                self.row_position += CARD_OFFSET_Y
                self.col_position = CARD_X
            else:
                self.col_position += SPACE
            if i != card.order:
                card.order = i
                yield MoveCard(card, self.col_position, self.row_position)



    
    
    
    def judge(self, card):
        self.selected.append(card)
        if len(self.selected) == 2:
            if len(set(card.value for card in self.selected)) == 1:
                card1, card2 = self.selected
                if card2.order in {card1.order - 4, card1.order + 4, card1.order - 1, card1.order + 1,
                                   card1.order - 5, card1.order + 5, card1.order - 3, card1.order + 3}:
                    self.faceup_cards = [card for card in self.faceup_cards if card not in self.selected]
                    remove_cards = self.selected[0:]
                    self.after(self.delay, lambda: self.remove_pins(*remove_cards))
                    self.after(self.delay, lambda: self.delete_cards(*remove_cards))
                    # self.after(self.delay, lambda: self.delete_cards(*left_cards))
                    self.selected = []
                    if move_cards := [card for card in self.rearange_cards()]:
                        self.after(self.delay, lambda: self.start_move(*move_cards))
            else:
                self.after(self.delay, lambda: self.remove_pins(*self.selected))
                self.selected = []






    #     self.selected.append(card)
    #     self.update_status()
    #     # all marks the same?
    #     same = len(set(card.mark for card in self.selected)) == 1
    #     # the number of th court cards
    #     court_cards = sum(10 < card.value for card in self.selected)
    #     # the number of the number cards
    #     number_cards = sum(card.value <= 10 for card in self.selected)
    #     if not same or (court_cards and number_cards):
    #         self.undo()
    #     elif court_cards == 3:
    #         self.set_new_cards()
    #     elif number_cards >= 2:
    #         total = sum(card.value for card in self.selected)
    #         if total > 15:
    #             self.undo()
    #         elif total == 15:
    #             self.set_new_cards()
      

    # def undo(self):
    #     cards = self.selected[0:]
    #     self.selected = []
    #     self.after(self.delay, lambda: self.remove_pins(*cards))

    def put_stock_card(self, card):
        # self.faceup_cards.append(card)
        # self.idx = len(self.faceup_cards) - 1
        # self.after(self.delay, lambda: self.start_move(card))
        pass
        # cards = sorted(self.selected, key=lambda x: x.order)
        # self.selected = []
        # self.after(self.delay, lambda: self.delete_cards(*cards))
        # self.after(self.delay, lambda: self.start_move(cards))


    def start_move(self, *cards):

        # if self.idx % 4 == 0:
        #     self.row_position += CARD_OFFSET_Y
        #     self.col_position = CARD_X
        # else:
        #     self.col_position += SPACE
        self.move_items = list(cards)
        self.idx = 0
        self.is_moved = False
        self.now_moving = True
        self.run_move_sequence()


        # stocks = [card for card in self.playing_cards.values() if not card.face_up]
        # self.move_cards = sorted(stocks,
        #     key=lambda x: x.id, reverse=True)[:len(selected_cards)]
        # self.destinations = []
        # if self.move_cards:
        #     cnt = len(self.move_cards)
        #     for stock, card in zip(self.move_cards, selected_cards[:cnt]):
        #         stock.x, stock.y, stock.order = card.x, card.y, card.order
        #         self.destinations.append((card.x, card.y))       
        #     self.is_moved = False
        #     self.idx = 0
        #     self.now_moving = True
        #     self.run_move_sequence()

    def run_move_sequence(self):
        if not self.is_moved:
            item = self.move_items[self.idx]
            if not item.card.face_up:
                self.turn_card(item.card, True)
                self.tag_raise(item.card.id)
            self.move_card(item.card.id, (item.dest_x, item.dest_y))
            self.after(MOVE_SPEED, self.run_move_sequence)
        else:
            item = self.move_items[self.idx]
            item.card.x = item.dest_x
            item.card.y = item.dest_y
            self.idx += 1
            if self.idx < len(self.move_items):
                self.is_moved = False
                self.run_move_sequence()
            else:
                self.now_moving = False


    #     if not self.is_moved:
    #         card = self.move_cards[self.idx]
    #         if not card.face_up:
    #             self.turn_card(card, True)
    #             self.tag_raise(card.id)
    #         self.move_card(card.id, self.destinations[self.idx])
    #         self.after(MOVE_SPEED, self.run_move_sequence)
    #     else:
    #         self.idx += 1
    #         if self.idx < len(self.move_cards):
    #             self.is_moved = False
    #             self.run_move_sequence()
    #         else:
    #             self.now_moving = False


    # def update_status(self):
    #     text = ', '.join(['{} {}'.format(card.mark, card.value) for card in self.selected])
    #     self.status_text.set(text)



if __name__ == '__main__':
    application = tk.Tk()
    application.title('FourLeafClover')
    score_text = tk.StringVar()
    board = Board(application, score_text)
    application.mainloop()