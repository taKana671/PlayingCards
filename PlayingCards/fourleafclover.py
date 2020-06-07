from collections import namedtuple

import os
import random
import tkinter as tk

from globals import *



CARD_X = int(BOARD_WIDTH/2) - 150
CARD_Y = int(BOARD_HEIGHT/5)
STACK_OFFSET = 0.3
SPACE = 90
STOCK_X = BOARD_WIDTH - 300 
STOCK_Y = BOARD_HEIGHT - 100
PIN_OFFSET_X = 18
PIN_OFFSET_y = 30





CardFace = namedtuple('CardFace', 'image mark value')


class Card:

    def __init__(self, item_id, face, x, y, face_up=False, order=None):
        self.id = item_id
        self.face = face 
        self.x = x
        self.y = y
        self.face_up = face_up
        self.order = order
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

    def __init__(self, master, status_text, delay=400, rows=4, columns=4):
        self.status_text = status_text
        self.rows = rows
        self.columns = columns
        self.delay = delay
        self.selected = []
        self.deck = [face for face in self.create_card()]
        self.back = tk.PhotoImage(file='images/back.png')
        self.pin = tk.PhotoImage(file='images/pin.png')
        super().__init__(master, width=BOARD_WIDTH, height=BOARD_HEIGHT, bg=BOARD_COLOR)
        self.pack(fill=tk.BOTH, expand=True)
        self.new_game()
      

    def new_game(self):
        self.delete('all')
        # config() changes attributes after creating object. 
        self.config(width=BOARD_WIDTH, height=BOARD_HEIGHT)
        random.shuffle(self.deck)
        self.playing_cards = {} 
        self.setup_cards(self.deck[:self.rows*self.columns])
        self.setup_stock(self.deck[self.rows*self.columns:])
        for name in self.playing_cards.keys():
            self.tag_bind(name, '<ButtonPress-1>', self.click)


    def create_card(self):
        image_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), CARD_ROOT)
        for path in os.listdir(image_path):
            name = os.path.splitext(path)[0]
            mark, value = name.split('_')
            if not mark.startswith('jocker') and value != '10':    
                yield CardFace(tk.PhotoImage(file=os.path.join(image_path, path)), mark, int(value))


    def setup_cards(self, cards):
        x = CARD_X
        y = CARD_Y
        for i, face in enumerate(cards, 1):
            name = 'card{}'.format(i)
            item_id = self.create_image(x, y, image=face.image, tags=name)
            card = Card(item_id, face, x, y, True, i)
            self.playing_cards[name] = card
            x += SPACE
            if i % self.columns == 0:
                x = CARD_X
                y += 130


    def setup_stock(self, cards):
        x, y = STOCK_X, STOCK_Y
        for i, face in enumerate(cards):
            name = 'stock{}'.format(i)
            item_id = self.create_image(x, y, image=self.back, tags=name)
            card = Card(item_id, face, x, y)
            self.playing_cards[name] = card
            x += STACK_OFFSET
            y -= STACK_OFFSET


    def click(self, event):
        card = self.get_card(event)
        if card.face_up:
            if not card.pin:
                self.set_pin(card)
            self.judge(card)


    def get_card(self, event):
        item_id = self.find_closest(event.x, event.y)[0]
        tag = self.gettags(item_id)[0]
        return self.playing_cards[tag]
       

    def set_pin(self, card):
        item_id = self.create_image(
            card.x + PIN_OFFSET_X, 
            card.y - PIN_OFFSET_y, 
            image=self.pin, 
            tags='pin{}'.format(card.id)
        )
        card.pin = item_id


    def judge(self, card):
        if card in self.selected:
            self.remove_pins((card,))
            self.selected.remove(card)
        else:
            self.selected.append(card)
        same = len(set(card.mark for card in self.selected)) == 1 # all marks the same?
        court_cards = sum(10 < card.value for card in self.selected) # the number of th court cards
        number_cards = sum(card.value <= 10 for card in self.selected) # the number of the number cards
        if not same or (court_cards and number_cards):
            self.undo()
        elif court_cards == 3:
            self.set_new_cards()
        elif number_cards >= 2:
            total = sum(card.value for card in self.selected)
            if total > 15:
                self.undo()
            elif total == 15:
                self.set_new_cards()
        self.update_status()
 

    def undo(self):
        cards = self.selected[0:]
        self.selected = []
        self.after(self.delay, lambda: self.remove_pins(cards))


    def set_new_cards(self):
        cards = sorted(self.selected, key=lambda x: x.order)
        self.selected = []
        self.after(self.delay, lambda: self.delete_cards(cards))
        self.after(self.delay, lambda: self.start_move(cards))


    def start_move(self, cards):
        self.destinations = [(card.x, card.y) for card in cards]
        stocks = [card for card in self.playing_cards.values() if not card.face_up]
        stocks.sort(key=lambda x: x.id, reverse=True)
        self.move_cards = []
        for i, card in enumerate(cards, 1):
            if i <= len(stocks):
                stock = stocks[i-1]
                stock.x, stock.y, stock.order = card.x, card.y, card.order
                self.move_cards.append(stock)
        if self.move_cards:
            self.destinatios = self.destinations[:len(self.move_cards)]
            self.is_moved = False
            self.idx = 0
            self.run_move_sequence()


    def run_move_sequence(self):
        if not self.is_moved:
            if not self.move_cards[self.idx].face_up:
                card = self.move_cards[self.idx]
                self.itemconfig(card.id, image=card.image)
                card.face_up = True
            self.move_card(self.move_cards[self.idx].id, self.destinations[self.idx])
            self.after(MOVE_SPEED, self.run_move_sequence)
        else:
            self.idx += 1
            if self.idx < len(self.move_cards):
                self.is_moved = False
                self.run_move_sequence()


    def move_card(self, id, destination):
        dest_x, dest_y = destination
        coords = self.coords(id)
        current_x, current_y = int(coords[0]), int(coords[1])
        offset_x = offset_y = 0
        if current_x < dest_x:
            offset_x = 1
        elif current_x > dest_x:
            offset_x = -1
        if current_y < dest_y:
            offset_y = 1
        elif current_y > dest_y:
            offset_y = -1
        if (offset_x, offset_y) != (0, 0):
            self.move(id, offset_x, offset_y)
        if (current_x, current_y) == (dest_x, dest_y):
            self.is_moved = True


    def remove_pins(self, cards):
        for card in cards:
            self.delete(card.pin)
            card.pin = None
    

    def delete_cards(self, cards):
        for card in cards:
            self.delete(card.id)
        self.remove_pins(cards)
    

    def update_status(self):
        text = ', '.join(['{} {}'.format(card.mark, card.value) for card in self.selected])
        self.status_text.set('Selected card: {}'.format(text))



if __name__ == '__main__':
    application = tk.Tk()
    application.title('FourLeafClover')
    score_text = tk.StringVar()
    board = Board(application, score_text)
    application.mainloop()


 