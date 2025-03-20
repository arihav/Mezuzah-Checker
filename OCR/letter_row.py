import cv2
import numpy as np

from enum import IntEnum


num_to_let = {1: 'א', 2: 'ב', 3: 'ג', 4: 'ד', 5: 'ה', 6: 'ו', 7: 'ז', 8: 'ח', 9: 'ט', 10: 'י', 20: 'כ', 30: 'ל',
              40: 'מ', 50: 'נ', 60: 'ס', 70: 'ע', 80: 'פ', 90: 'צ', 100: 'ק', 200: 'ר', 300: 'ש', 400: 'ת',
              21: 'ך', 41: 'ם', 51: 'ן', 81: 'ף', 91: 'ץ'}

class Diff(IntEnum):
    EQUAL = 0
    WRONG = 1
    MISSING = 2
    EXTRA = 3
    SUSPICIOUS = 4


class Letter:

    def __init__(self, letter):
        self.letter = np.array(letter)
        self.x, self.y, self.w, self.h = cv2.boundingRect(letter)

        self.prediction = None
        self.expected_character = None
        self.confidence = 0
        self.mez_let = None
        self.increment = 0
        self.rownum = None
        self.letnum = None
        self.match = None
        self.wordnum = 0

        self.status: Diff = Diff.EQUAL

    def __add__(self, other):
        if type(other) is not Letter:
            raise Exception("Invalid argument, must be Letter ")

        return Letter(np.concatenate([self.letter, other.letter]))

    def __str__(self):
        return f"Letter: {num_to_let[self.prediction]}, expected: {self.expected_character}, x: {self.x}, y: {self.y}, w: {self.w}, h: {self.h}, row: {self.rownum}, let: {self.letnum}, match: {self.match}"

    def to_dict(self):
        return {
            'id': self.letnum,
            'word_id': self.wordnum,
            'x': self.x,
            'y': self.y,
            'width': self.w,
            'height': self.h,
            'character': num_to_let.get(self.prediction, None),
            'expected_character': self.expected_character,
            'confidence': self.confidence,
            'status': self.status
        }

    def show_let(self, img):
        cv2.rectangle(img, (self.x, self.y), (self.x + self.w, self.y + self.h), (0, 255, 0), 1)
        img = cv2.resize(img, (0, 0), fx=0.6, fy=0.6)
        # img = img[max(self.y-5, 0): min(self.y + self.h + 5, len(img)),
        #       max(self.x-200, 0): min(self.x + self.w+200, len(img[0]))]
        cv2.imshow('letter', img)
        cv2.waitKey(0)


class Row:
    def __init__(self, letter=None):
        self.letter_list = []

        self.top_avr = 0
        self.bottom_avr = 0

        if letter is not None:
            self.add_let(letter)

    def __len__(self):
        return len(self.letter_list)

    def add_let(self, letter):
        self.top_avr = (self.top_avr * self.__len__() + letter.y) / (self.__len__() + 1)
        self.bottom_avr = (self.bottom_avr * self.__len__() + letter.y + letter.h) / (self.__len__() + 1)

        self.letter_list.append(letter)

    def replace_let(self, letter, index):
        self.letter_list[index] = letter

    def get_let(self, index):
        return self.letter_list[index]

    def get_matching_rate(self, letter):
        if self.top_avr >= letter.y:
            if self.bottom_avr > letter.y + letter.h:
                return letter.y + letter.h - self.top_avr
            else:
                return self.bottom_avr - self.top_avr
        elif self.bottom_avr > letter.y > self.top_avr:
            if self.bottom_avr > letter.y + letter.h:
                return letter.h
            else:
                return self.bottom_avr - letter.y
        else:
            return 0
