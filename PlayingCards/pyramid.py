from collections import namedtuple

import os
import random
import tkinter as tk

from globals import *


PYRAMID_X = int(BOARD_WIDTH/2)
PYRAMID_Y = int(BOARD_HEIGHT/3)
STACK_OFFSET = 0.3
SPACE = 90
STOCK_X = BOARD_WIDTH - 200 
STOCK_Y = BOARD_HEIGHT - 100
JOCKER_X  = 200
JOCKER_Y = 100
OPEN_STOCK_X = STOCK_X - SPACE 
OPEN_STOCK_Y = STOCK_Y
DISCARD_X = JOCKER_X
DISCARD_Y = STOCK_Y
STATUS_MESSAGE = 'No cards selected.'


CardFace = namedtuple('CardFace', 'image mark value')


class Card:

    def __init__(self, item_id, face, status, x, y, face_up=False, left=None, right=None):
        self.id = item_id
        self.face = face 
        self.status = status
        self.x = x
        self.y = y
        self.face_up = face_up
        self.left = left
        self.right = right
        self.face_up = face_up
        self.dele = False
        self.pin = None


    @property
    def value(self):
        return self.face.value

    
    @property
    def mark(self):
        return self.face.mark


    @property
    def image(self):
        return self.face.image



class Board(tk.Canvas):

    def __init__(self, master, status_text, delay=400, rows=7):
    # def __init__(self, master, status_text, back, pin, delay=400, rows=7):
        self.status_text = status_text
        self.rows = rows
        self.delay = delay
        self.stock = None
        self.discard_x = DISCARD_X
        self.discard_y = DISCARD_Y
        self.selected = []
        self.deck = [face for face in self.create_card()]
        self.back = tk.PhotoImage(file='images/back.png')
        self.pin = tk.PhotoImage(file='images/pin.png')
        # self.back = back
        # self.pin = pin
        self.playing_cards = {} 
        super().__init__(master, width=BOARD_WIDTH, height=BOARD_HEIGHT, bg=BOARD_COLOR)
        self.pack(fill=tk.BOTH, expand=True)
        self.new_game()
      

    def create_card(self):
        image_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), CARD_ROOT)
        for path in os.listdir(image_path):
            name = os.path.splitext(path)[0]
            mark, value = name.split('_')    
            yield CardFace(tk.PhotoImage(file=os.path.join(image_path, path)), mark, int(value))


    def new_game(self):
        self.delete('all')
        # config() changes attributes after creating object. 
        self.config(width=BOARD_WIDTH, height=BOARD_HEIGHT)
        random.shuffle(self.deck)
        cards = [face for face in self.deck if not face.mark.startswith('jocker')]
        jockers = [face for face in self.deck if face.mark.startswith('jocker')]    
        limit = int(self.rows * (self.rows+1) / 2) # the number of pyramit cards
        self.setup_pyramid(cards[:limit])
        self.setup_stock(cards[limit:])
        self.setup_jocker(jockers)
        for name in self.playing_cards.keys():
            self.tag_bind(name, '<ButtonPress-1>', self.click)


    def setup_pyramid(self, pyramid_cards):
        start = 0
        cards = []
        for i in range(1, self.rows+1):
            cards.append(pyramid_cards[start:start + i])
            start = start + i

        x, y = PYRAMID_X, PYRAMID_Y
        for i, row in enumerate(cards, 1):
            for j, face in enumerate(row, 1):
                name = 'pyramid{}{}'.format(i, j)
                item_id = self.create_image(
                    x, y,
                    image=face.image if i == self.rows else self.back, 
                    tags=name
                )
                face_up = True if i == self.rows else False
                card = Card(item_id, face, 'pyramid', x, y, face_up)
                self.playing_cards[name] = card
                x += SPACE
            x -= (SPACE * i) + 45
            y += 40
        for i, row in enumerate(cards[:-1], 1):
            for j, _ in enumerate(row, 1):
                card = self.playing_cards['pyramid{}{}'.format(i, j)]
                card.left = self.playing_cards['pyramid{}{}'.format(i+1, j)]
                card.right = self.playing_cards['pyramid{}{}'.format(i+1, j+1)]
              

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
        card = self.get_card(event)
        if card.status == 'stock' and card.face_up == False:
            if self.stock is None:
                self.stock_face_up(card)
            else:
                self.discard_stock()
                self.stock_face_up(card)
            self.stock = card
        elif card.face_up:
            if not card.pin:
                self.set_pin(card)
            self.judge(card)


    def get_card(self, event):
        item_id = self.find_closest(event.x, event.y)[0]
        tag = self.gettags(item_id)[0]
        return self.playing_cards[tag]
       

    def stock_face_up(self, card):
        self.itemconfig(card.id, image=card.image)
        self.coords(card.id, OPEN_STOCK_X, OPEN_STOCK_Y)
        card.x, card.y = OPEN_STOCK_X, OPEN_STOCK_Y 
        card.face_up = True 


    def discard_stock(self):
        self.coords(self.stock.id, self.discard_x, self.discard_y)
        self.tag_raise(self.stock.id)
        self.stock.x, self.stocky = self.discard_x, self.discard_y 
        self.discard_x += STACK_OFFSET
        self.discard_y -= STACK_OFFSET
        self.stock.status = 'discarded'


    def pyramid_face_up(self):
        cards = filter(lambda x: x.right and x.left, self.playing_cards.values())
        for card in cards:
            if card.right.dele and card.left.dele:
                self.itemconfig(card.id, image=card.image)
                card.face_up = True


    def set_pin(self, card):
        item_id = self.create_image(card.x + 18, card.y - 30, image=self.pin, tags='pin{}'.format(card.id))
        card.pin = item_id


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

 

    def remove_pins(self, cards):
        for card in cards:
            self.delete(card.pin)
            card.pin = None
       

    def delete_cards(self, cards):
        for card in cards:
            card.dele = True
            self.delete(card.id)
        self.remove_pins(cards)


    def update_status(self, card=''):
        if not card:
            status = ''
        else:
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



if __name__ == '__main__':
    application = tk.Tk()
    application.title('Pyramid')
    score_text = tk.StringVar()
    # board = Board(application, print, score)
    board = Board(application, score_text)
    application.mainloop()


 