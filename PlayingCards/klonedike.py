import os
import random
import tkinter as tk

from base import BaseBoard, BaseCard, CardFace
from globals import *


CARD_X = 100
CARD_Y = 100
CARD_OFFSET_X = 90
CARD_OFFSET_Y = 30
SPACE_X =90
SPACE_Y = 140
STOCK_X = BOARD_WIDTH - 100
STOCK_Y = CARD_Y + 50
ACEHOLDER_X = BOARD_WIDTH - 200
ACEHOLDER_Y = 300
OPEN_STOCK_X = STOCK_X - (SPACE_X + 10)
OPEN_STOCK_Y = STOCK_Y
OPEN_TEMP_X = STOCK_X - SPACE_X
STACK_OFFSET = 0.3
RED_COLOR = {'diamond', 'heart'}
RED = 'red'
BLACK = 'black'
FIXED_POSITION = {'aceholder', 'cardholder', 'acestock'}


class Card(BaseCard):

    def __init__(self, item_id, face, status, x, y, 
            face_up=False, order=None, col=None):
        super().__init__(item_id, face, x, y, face_up)
        self.status = status
        self.order = order
        self.col = col
       

    @property
    def color(self):
        if self.mark in RED_COLOR:
            return RED
        else:
            return BLACK
        

class Holder:

    def __init__(self, item_id, x, y, status='holder', col=None):
        self.id = item_id
        self.x = x
        self.y = y
        self.status = status
        self.col = col


class Board(BaseBoard):

    def __init__(self, master, status_text, delay=400, rows=7):
        self.rows = rows
        self.open_stock_x = OPEN_STOCK_X
        self.open_stock_y = OPEN_STOCK_Y
        self.stock_x = STOCK_X
        self.stock_y = STOCK_Y
        self.selected = []
        self.now_moving = False
        self.holder = self.get_image('holder')
        super().__init__(master, status_text, delay)
        
      
    def create_card(self):
        image_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), CARD_ROOT)
        for path in os.listdir(image_path):
            name = os.path.splitext(path)[0]
            mark, value = name.split('_')
            if not mark.startswith('jocker'):  
                yield CardFace(tk.PhotoImage(
                    file=os.path.join(image_path, path)), mark, int(value))


    def new_game(self):
        self.delete('all')
        self.playing_cards = {} 
        self.holders = {}
        # config() changes attributes after creating object. 
        self.config(width=BOARD_WIDTH, height=BOARD_HEIGHT)
        random.shuffle(self.deck)
        limit = int(self.rows * (self.rows+1) / 2) # the number of klondike cards
        self.setup_holder()
        self.setup_cards(self.deck[:limit])
        self.setup_stock(self.deck[limit:])
        for card in self.playing_cards.values():
            self.tag_bind(card.id, '<ButtonPress-1>', self.click_card)
        for holder in self.holders.values():
            self.tag_bind(holder.id, '<ButtonPress-1>', self.click_holder)


    def setup_holder(self):
        x, y = CARD_X, CARD_Y
        for i in range(1, 8):
            name = 'cardholder{}'.format(i)
            item_id = self.create_image(x, y, image=self.holder, tags=name)
            self.holders[name] = Holder(item_id, x, y, status='cardholder', col='col{}1'.format(i))
            x += SPACE_X
        name = 'stockholder'
        item_id = self.create_image(STOCK_X, STOCK_Y, image=self.holder, tags=name)
        self.tag_bind(name, '<ButtonPress-1>', self.start_stock_back)
      
        x, y = ACEHOLDER_X, ACEHOLDER_Y 
        for i in range(1, 3):
            for j in range(1, 3):
                name = 'aceholder{}{}'.format(i, j) 
                item_id = self.create_image(x, y, image=self.holder, tags=name)
                self.holders[name] = Holder(item_id, x, y, status='aceholder')
                x += SPACE_X
            x = ACEHOLDER_X
            y = ACEHOLDER_Y + SPACE_Y


    def setup_cards(self, klondike_cards):
        # make array as [[1 element], [2 elements], [3 elements],...]
        start = 0
        cards = []
        for i in range(1, self.rows+1):
            cards.append(klondike_cards[start:start + i])
            start = start + i
        x, y = CARD_X, CARD_Y
        for i, row in enumerate(cards, 1):
            for j, face in enumerate(row, 1):
                face_up = True if j ==len(row) else False
                col = 'col{}{}'.format(i, int(face_up))
                item_id = self.create_image(
                    x, y,
                    image=face.image if j == len(row) else self.back, 
                    tags= col
                )
                card = Card(item_id, face, 'card', x, y, face_up, col=col)
                self.playing_cards[item_id] = card
                y += CARD_OFFSET_Y
            x += SPACE_X
            y = CARD_Y
        

    def setup_stock(self, cards):
        x, y = STOCK_X, STOCK_Y
        for i, face in enumerate(cards, 1):
            name = 'stock{}1'.format(i)
            item_id = self.create_image(x, y, image=self.back, tags=name)
            card = Card(item_id, face, 'stock', x, y, order=i, col=name)
            self.playing_cards[item_id] = card
            x += STACK_OFFSET
            y -= STACK_OFFSET


    def click_holder(self, event):
        holder = self.holders[self.get_tag(event)]
        self.after(self.delay, lambda: self.judge(holder))


    def click_card(self, event):
        card = self.playing_cards[self.get_id(event)]
        if card.status == 'card' and card.face_up:
            cards = [c for c in self.playing_cards.values() if c.col == card.col]
            if card.pin:
                self.remove_pins(cards)
                self.selected = []
            else:
                for c in cards:
                    self.set_pin(c)
                self.after(self.delay, lambda: self.judge(cards))
        elif card.status == 'stock' and not card.face_up:
            self.start_move_stock(card)
        elif card.status in {'openedstock', 'acestock'}:
            if card.pin:
                self.remove_pins((card,))
                self.selected = []
            else:
                self.set_pin(card)
                self.after(self.delay, lambda: self.judge(card))
        

    def start_stock_back(self, event):
        cards = [card for card in self.playing_cards.values() \
            if card.status == 'openedstock']
        if cards:
            self.open_stock_x = OPEN_STOCK_X
            cards.sort(key=lambda x: x.order)
            self.open_stock_y = OPEN_STOCK_Y
            x, y = STOCK_X, STOCK_Y
            for card in cards:
                card.x, card.y = x, y
                x += STACK_OFFSET
                y -= STACK_OFFSET
            self.move_start(cards, (OPEN_TEMP_X, STOCK_Y))


    def start_move_stock(self, card):
        card.x, card.y = self.open_stock_x, self.open_stock_y
        self.turn_card(card, True)
        self.open_stock_x += STACK_OFFSET
        self.open_stock_y -= STACK_OFFSET
        self.move_start([card], (OPEN_TEMP_X, STOCK_Y))


    def start_horizontal_move(self, start, goal):
        destinations = (goal.x, goal.y) if goal.status in FIXED_POSITION \
            else (goal.x, goal.y + CARD_OFFSET_Y)
        self.goal_col = 'acestock{}1'.format(start.id) if start.status == 'acestock' \
            else goal.col
        self.tag_raise(start.col)
        self.move_start([start], destinations)


    def move_start(self, move_cards, destinations):
        self.move_cards = move_cards
        self.destinations = destinations
        self.is_moved = False
        self.idx = 0
        self.run_move_sequence()


    def run_move_sequence(self):
        if not self.is_moved:
            self.move_card(self.move_cards[self.idx].col, self.destinations)
            self.after(MOVE_SPEED, self.run_move_sequence)
        else:
            if self.move_cards[self.idx].status in {'openedstock', 'stock'}:
                self.after_stock_moved(self.move_cards[self.idx])
            else:
                self.after_card_moved(self.move_cards[self.idx])
            self.idx += 1
            if self.idx < len(self.move_cards):
                self.is_moved = False
                self.run_move_sequence()


    def after_card_moved(self, start):
        col = start.col[:-1]
        cards = [card for card in self.playing_cards.values() \
            if card.col == start.col]
        self.itemconfig(start.col, tag=self.goal_col)
        for card in sorted(cards, key=lambda x: x.y):
            coords = self.coords(card.id)
            card.x, card.y = int(coords[0]), int(coords[1])
            card.col = self.goal_col
        cards = [card for card in self.playing_cards.values() \
            if card.col == col + '0']
        if cards:
            new = max(cards, key=lambda x: x.y)
            self.itemconfig(new.id, tag=col+'1')
            new.col = col+'1'
            self.turn_card(new, True)


    def after_stock_moved(self, card):
        if card.status == 'openedstock':
            self.turn_card(card, False)
            card.status = 'stock'
        else:
            card.status = 'openedstock' 
        self.coords(card.id, card.x, card.y)
        self.tag_raise(card.id)


    def judge(self, target):
        # self.update_status(card)
        self.selected.append(target)
        if len(self.selected) == 2:
            obj1, obj2 = self.selected[0], self.selected[1]
            self.selected = []
            if isinstance(obj1, list): 
                start = min(obj1, key=lambda x: x.y)
                if isinstance(obj2, list): # card  => card
                    goal = max(obj2, key=lambda x: x.y)
                    if goal.value - 1 == start.value and goal.color != start.color:
                        self.start_horizontal_move(start, goal)
                    self.remove_pins(obj1 + obj2)
                # card with value 13 or 1 => cardholder or aceholder
                elif isinstance(obj2, Holder):
                    if (start.value == 13 and obj2.status == 'cardholder') \
                            or (start.value == 1 and obj2.status == 'aceholder'):
                        if obj2.status == 'aceholder':
                            start.status = 'acestock'
                        self.start_horizontal_move(start, obj2)
                    self.remove_pins(obj1)
                # list => onto acestock 
                elif isinstance(obj2, Card) and obj2.status == 'acestock' and len(obj1) == 1:
                    if start.value - 1 == obj2.value and start.mark == obj2.mark:
                        start.status = 'acestock'
                        self.start_horizontal_move(start, obj2)
                    self.remove_pins((start, obj2))
            elif isinstance(obj1, Card) and obj1.status == 'openedstock':
                # openedstock => card
                if isinstance(obj2, list):
                    goal = max(obj2, key=lambda x: x.y)
                    if goal.value - 1 == obj1.value and goal.color != obj1.color:
                        obj1.status = 'card'
                        self.start_horizontal_move(obj1, goal)
                    self.remove_pins((obj2 + [obj1]))
                # openedstock with value 13 or 1 => cardholder or aceholder
                elif isinstance(obj2, Holder):
                    if (obj1.value == 13 and obj2.status == 'cardholder') \
                            or (obj1.value == 1 and obj2.status == 'aceholder'):
                        obj1.status = 'card' if obj2.status == 'cardholder' else 'acestock'
                        self.start_horizontal_move(obj1, obj2)
                    self.remove_pins((obj1,))
                # openedstock => onto acestock
                elif isinstance(obj2, Card) and obj2.status == 'acestock':
                    if obj1.value - 1 == obj2.value and obj1.mark == obj2.mark:
                        obj1.status = 'acestock'
                        self.start_horizontal_move(obj1, obj2)
                    self.remove_pins((obj1, obj2))
            elif isinstance(obj1, Card) and obj1.status == 'acestock':
                # acestock => card
                if isinstance(obj2, list):
                    goal = max(obj2, key=lambda x: x.y)
                    if goal.value - 1 == obj1.value and goal.color != obj1.color:
                        obj1.status = 'card'
                        self.start_horizontal_move(obj1, goal)
                    self.remove_pins((obj2 + [obj1]))
                # acestock with value 13 => cardholder
                elif isinstance(obj2, Holder) and obj2.status == 'cardholder': 
                    if obj1.value == 13:
                        obj1.status = 'card'
                        self.start_horizontal_move(obj1, obj2)
                    self.remove_pins((obj1,))
           

    def update_status(self, card=None):
        val = card.status if card.status == 'jocker' else card.value
        if val == 13 or not self.selected:
            status = val
        elif len(self.selected) == 1:
            try:
                text = self.status_text.get()
                status = '{} + {} = {}'.format(text, val, int(text) + int(val))
            except ValueError:
                status = '{} + {} = {}'.format(text, val, 13)
        self.status_text.set(status)


    def count_rest_cards(self):
        cards = [card for card in self.playing_cards.values() if \
            card.status == 'pyramid' and not card.dele]
        if not cards:
            self.after(self.delay, self.finish)



if __name__ == '__main__':
    application = tk.Tk()
    application.title('Pyramid')
    score_text = tk.StringVar()
    # board = Board(application, print, score)
    board = Board(application, score_text)
    application.mainloop()


 