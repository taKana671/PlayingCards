from collections import namedtuple
import os
import tkinter as tk

from globals import *


CardFace = namedtuple('CardFace', 'image mark value')


class BaseCard:

    def __init__(self, item_id, face, x, y, face_up):
        self.id = item_id
        self.face = face
        self.x = x
        self.y = y
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


class BaseBoard(tk.Canvas):

    def __init__(self, master, status_text, delay):
        self.status_text = status_text
        self.delay = delay
        self.deck = [face for face in self.create_card()]
        self.back = self.get_image(BACK)
        self.pin = self.get_image(PIN)
        super().__init__(master, width=BOARD_WIDTH, height=BOARD_HEIGHT, bg=BOARD_COLOR)
        self.pack(fill=tk.BOTH, expand=True)
        self.new_game()


    def new_game(self):
        """
        Override this method in subclasses to 
        create instance of BaseCard subclasses.
        """
        raise NotImplementedError()


    def create_card(self):
        """
        Override this method in subclasses to 
        yield CardFace instance.
        """
        raise NotImplementedError()


    def get_image(self, file):
        image_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), IMAGE_ROOT)
        return tk.PhotoImage(
                file=os.path.join(image_path, '{}.png'.format(file)))


    def get_tag(self, event):
        item_id = self.find_closest(event.x, event.y)[0]
        tag = self.gettags(item_id)[0]
        return tag 


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


    def set_pin(self, card):
        item_id = self.create_image(
            card.x + PIN_OFFSET_X, 
            card.y - PIN_OFFSET_y, 
            image=self.pin, 
            tags='pin{}'.format(card.id)
        )
        card.pin = item_id
        

    def remove_pins(self, cards):
        for card in cards:
            self.delete(card.pin)
            card.pin = None
       

    def delete_cards(self, cards):
        for card in cards:
            card.dele = True
            self.delete(card.id)
        self.remove_pins(cards)
        self.count_rest_cards()


    def finish(self):
        self.ribbon = self.get_image(RIBBON)
        self.create_image(BOARD_WIDTH/2, BOARD_HEIGHT/2, 
            image=self.ribbon, tags=RIBBON)