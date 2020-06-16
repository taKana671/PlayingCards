# from collections import namedtuple

import os
import random
import tkinter as tk

from base import BaseBoard, BaseCard, CardFace
from globals import *


PYRAMID_X = int(BOARD_WIDTH/2)
PYRAMID_Y = int(BOARD_HEIGHT/5)
PYRAMID_OFFSET_X = 45
PYRAMID_OFFSET_Y = 40
STACK_OFFSET = 0.3
SPACE = 90
JOCKER_X  = 50
JOCKER_Y = 100
STOCK_X = int(BOARD_WIDTH*3/4) 
STOCK_Y = BOARD_HEIGHT - 80
OPEN_STOCK_X = STOCK_X - SPACE 
OPEN_STOCK_Y = STOCK_Y
DISCARD_TEMP_X = OPEN_STOCK_X - 300
DISCARD_X = int(BOARD_WIDTH/4)
DISCARD_Y = STOCK_Y


class Card(BaseCard):

    def __init__(self, item_id, face, status, x, y, 
            face_up=False, left=None, right=None):
        super().__init__(item_id, face, x, y, face_up)
        self.status = status
        self.left = left
        self.right = right
        

class Board(BaseBoard):

    def __init__(self, master, status_text, delay=400, rows=7):
        # self.status_text = status_text
        self.rows = rows
        # self.delay = delay
        self.discard_x = DISCARD_X
        self.discard_y = DISCARD_Y
        self.selected = []
        self.now_moving = False
        super().__init__(master, status_text, delay)
        
      
    def create_card(self):
        image_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), CARD_ROOT)
        for path in os.listdir(image_path):
            name = os.path.splitext(path)[0]
            mark, value = name.split('_')    
            yield CardFace(tk.PhotoImage(
                file=os.path.join(image_path, path)), mark, int(value))


    def new_game(self):
        self.delete('all')
        # config() changes attributes after creating object. 
        self.config(width=BOARD_WIDTH, height=BOARD_HEIGHT)
        random.shuffle(self.deck)
        self.playing_cards = {} 
        cards = [face for face in self.deck if not face.mark.startswith('jocker')]
        jockers = [face for face in self.deck if face.mark.startswith('jocker')]    
        limit = int(self.rows * (self.rows+1) / 2) # the number of pyramit cards
        self.setup_pyramid(cards[:limit])
        self.setup_stock(cards[limit:])
        self.setup_jocker(jockers)
        for name in self.playing_cards.keys():
            self.tag_bind(name, '<ButtonPress-1>', self.click)


    def setup_pyramid(self, pyramid_cards):
        # make array as [[1 element], [2 elements], [3 elements],...]
        start = 0
        cards = []
        for i in range(1, self.rows+1):
            cards.append(pyramid_cards[start:start + i])
            start = start + i
        # layout pyramid
        template = 'pyramid{}{}'
        x, y = PYRAMID_X, PYRAMID_Y
        for i, row in enumerate(cards, 1):
            for j, face in enumerate(row, 1):
                name = template.format(i, j)
                item_id = self.create_image(
                    x, y,
                    image=face.image if i == self.rows else self.back, 
                    tags=name
                )
                face_up = True if i == self.rows else False
                card = Card(item_id, face, 'pyramid', x, y, face_up)
                self.playing_cards[name] = card
                x += SPACE
            x -= (SPACE * i) + PYRAMID_OFFSET_X
            y += PYRAMID_OFFSET_Y
        # set left and right cards
        for i, row in enumerate(cards[:-1], 1):
            for j, _ in enumerate(row, 1):
                card = self.playing_cards[template.format(i, j)]
                card.left = self.playing_cards[template.format(i+1, j)]
                card.right = self.playing_cards[template.format(i+1, j+1)]
              

    def setup_stock(self, cards):
        x, y = STOCK_X, STOCK_Y
        for i, face in enumerate(cards):
            name = 'stock{}'.format(i)
            item_id = self.create_image(x, y, image=self.back, tags=name)
            card = Card(item_id, face, 'stock', x, y)
            self.playing_cards[name] = card
            x += STACK_OFFSET
            y -= STACK_OFFSET


    def setup_jocker(self, jockers):
        x, y = JOCKER_X, JOCKER_Y
        for i, face in enumerate(jockers):
            name = 'jocker{}'.format(i)
            item_id = self.create_image(x, y, image=face.image, tags=name)
            card = Card(item_id, face, 'jocker', x, y, True)
            self.playing_cards[name] = card
            x += SPACE


    def click(self, event):
        card = self.playing_cards[self.get_tag(event)]
        if card.status == 'stock' and card.face_up == False:
            if not self.now_moving:
                self.start_move(card)
                self.now_moving = True
        elif card.face_up:
            if not card.pin:
                self.set_pins((card,))
            self.judge(card)


    def start_move(self, card):
        stock = [card for card in self.playing_cards.values() \
            if card.status == 'stock' and card.face_up and not card.dele]
        self.destinations = []
        self.move_cards = []
        if stock:
            stock = stock[0]  
            stock.x, stock.y = self.discard_x, self.discard_y 
            self.discard_x += STACK_OFFSET
            self.discard_y -= STACK_OFFSET
            stock.status = 'discarded'
            self.destinations.append((DISCARD_TEMP_X, OPEN_STOCK_Y))
            self.move_cards.append(stock)
        card.x, card.y = OPEN_STOCK_X, OPEN_STOCK_Y
        self.destinations.append((OPEN_STOCK_X, OPEN_STOCK_Y))
        self.move_cards.append(card)
        self.is_moved = False
        self.idx = 0
        self.run_move_sequence()
       

    def run_move_sequence(self):
        if not self.is_moved:
            self.move_card(self.move_cards[self.idx].id, self.destinations[self.idx])
            self.after(MOVE_SPEED, self.run_move_sequence)
        else:
            card = self.move_cards[self.idx]
            if not card.face_up:
                self.itemconfig(card.id, image=card.image)
                card.face_up = True    
            if card.status == 'discarded':
                self.coords(card.id, card.x, card.y)
                self.tag_raise(card.id)
            self.idx += 1
            if self.idx < len(self.move_cards):
                self.is_moved = False
                self.run_move_sequence()
            else:
                self.now_moving = False

        
    def pyramid_face_up(self):
        cards = filter(lambda x: x.right and x.left, self.playing_cards.values())
        for card in cards:
            if card.right.dele and card.left.dele:
                self.itemconfig(card.id, image=card.image)
                card.face_up = True


    def judge(self, card):
        self.update_status(card)
        if card.value == 13:
            self.after(self.delay, lambda: self.delete_cards((card,)))
            self.after(self.delay, self.pyramid_face_up)
        elif len(self.selected) == 1 and self.selected[0] == card:
            self.remove_pins((card,))
            self.selected = []
        else:
            self.selected.append(card)
            if len(self.selected) == 2:
                cards = self.selected[0:]
                if sum(card.value == 14 for card in self.selected) >= 1 or \
                        sum(card.value for card in self.selected) == 13:
                    self.after(self.delay, lambda: self.delete_cards(cards))
                    self.after(self.delay, self.pyramid_face_up)
                else:
                    self.after(self.delay, lambda: self.remove_pins(cards))
                self.selected = []


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


 