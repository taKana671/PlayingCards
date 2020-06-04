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


class Card:

    def __init__(self, item_id, face, status, x, y, left=None, right=None):
        self.id = item_id
        self.face = face 
        self.status = status
        self.x = x
        self.y = y
        self.left = left
        self.right = right
        self.pin = None


class CardFace:

    def __init__(self, img, value, up=False, dele=False):
        self.img = img 
        self.value = value
        self.up = up
        self.dele = dele


class Board(tk.Canvas):

    def __init__(self, master, status_text, back, pin, delay=400, rows=7):
        self.status_text = status_text
        self.rows = rows
        self.delay = delay
        self.stock = None
        self.discard_x = DISCARD_X
        self.discard_y = DISCARD_Y
        self.opened = []
        self.deck = [card for card in os.listdir(ROOT)]
        self.back = back
        self.pin = pin
        self.playing_cards = {} 
        super().__init__(master, width=BOARD_WIDTH, height=BOARD_HEIGHT, bg=BOARD_COLOR)
        self.pack(fill=tk.BOTH, expand=True)
        self.new_game()
      

    def new_game(self):
        self.delete('all')
        # config() changes attributes after creating object. 
        self.config(width=BOARD_WIDTH, height=BOARD_HEIGHT)
        random.shuffle(self.deck)

        cards = [face for face in self.card_face(lambda x: not x.startswith('jocker'))]
        jockers = [face for face in self.card_face(lambda x: x.startswith('jocker'))]

        self.setup_pyramid(cards)
        self.setup_stock(cards)
        self.setup_jocker(jockers)

        for name in self.playing_cards.keys():
            self.tag_bind(name, '<ButtonPress-1>', self.click)


    def card_face(self, func):
        image_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), CARD_ROOT)
        for card in self.deck:
            if func(card):
                name = os.path.splitext(card)[0]
                _, value = name.split('_')   
                yield CardFace(tk.PhotoImage(file=os.path.join(image_path, card)), int(value))


    def setup_pyramid(self, cards):
        start = 0
        x, y = PYRAMID_X, PYRAMID_Y
        for i in range(1, self.rows+1):
            for face in cards[start: start + i]: 
                index = cards.index(face)
                name = 'pyramid{}'.format(index)
                image = face.img if i == self.rows else self.back
                # x, y are the center of the image
                item_id = self.create_image(x, y, image=image, tags=name)
                face.up = True if i == self.rows else False
                left = cards[index + i] if i < self.rows else None
                right = cards[index + i + 1] if i < self.rows else None
                card = Card(item_id, face, 'pyramid', x, y, left, right)
                self.playing_cards[name] = card
                x += SPACE
            start = start + i
            x -= (SPACE * i) + 45
            y += 40


    def setup_stock(self, cards):
        start = int(self.rows * (self.rows+1) / 2)
        x, y = STOCK_X, STOCK_Y
        for i, face in enumerate(cards[start:]):
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
            item_id = self.create_image(x, y, image=face.img, tags=name)
            face.up = True
            card = Card(item_id, face, 'jocker', x, y)
            self.playing_cards[name] = card
            x += SPACE


    def click(self, event):
        card = self.get_card(event)
        if card.status == 'stock' and card.face.up == False:
            if self.stock is None:
                self.stock_face_up(card)
            else:
                self.discard_stock()
                self.stock_face_up(card)
            self.stock = card
        elif card.face.up:
            if not card.pin:
                self.set_pin(card)
            self.judge(card)


    def get_card(self, event):
        item_id = self.find_closest(event.x, event.y)[0]
        tag = self.gettags(item_id)[0]
        return self.playing_cards[tag]
       

    def stock_face_up(self, card):
        self.itemconfig(card.id, image=card.face.img)
        self.coords(card.id, OPEN_STOCK_X, OPEN_STOCK_Y)
        card.x, card.y = OPEN_STOCK_X, OPEN_STOCK_Y 
        card.face.up = True 


    def discard_stock(self):
        self.coords(self.stock.id, self.discard_x, self.discard_y)
        self.tag_raise(self.stock.id)
        self.stock.x, self.stocky = self.discard_x, self.discard_y 
        self.discard_x += STACK_OFFSET
        self.discard_y -= STACK_OFFSET
        self.stock.kind = 'discarded'


    def pyramid_face_up(self):
        cards = filter(lambda x: x.right and x.left, self.playing_cards.values())
        for card in cards:
            if card.right.dele and card.left.dele:
                self.itemconfig(card.id, image=card.face.img)
                card.face.up = True


    def set_pin(self, card):
        item_id = self.create_image(card.x + 18, card.y - 30, image=self.pin, tags='pin{}'.format(card.id))
        card.pin = item_id


    def judge(self, card):
        self.update_status(card)
        if card.face.value == 13:
            self.after(self.delay, lambda: self.delete_cards(card))
        elif len(self.opened) == 1 and self.opened[0] == card:
            self.remove_pins(card)
            self.opened = []
        else:
            self.opened.append(card)
            if len(self.opened) == 2:
                card1, card2 = self.opened[0], self.opened[1]
                if card1.face.value + card2.face.value == 13 or \
                         (card1.status == 'jocker' or card2.status == 'jocker'):
                    self.after(self.delay, lambda: self.delete_cards(card1, card2))
                else:
                    self.after(self.delay, lambda: self.remove_pins(card1, card2))
                self.opened = []
       

    def remove_pins(self, *cards):
        for card in cards:
            self.delete(card.pin)
            card.pin = None
        self.update_status()


    def delete_cards(self, *cards):
        for card in cards:
            card.face.dele = True
            self.delete(card.id)
            self.delete(card.pin)
        self.update_status()
        self.after(self.delay, self.pyramid_face_up)


    def update_status(self, card=''):
        if not card:
            status = ''
        else:
            val = card.status if card.status == 'jocker' else card.face.value
            if val == 13 or not self.opened:
                status = val
            elif len(self.opened) == 1:
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


 