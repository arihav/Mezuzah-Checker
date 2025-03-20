import time

import cv2
import numpy as np
from . import Letter, Row


def image_cleaner(img):
    dilated_img = cv2.dilate(img[:, :, 1], np.ones((7, 7), np.uint8))
    bg_img = cv2.medianBlur(dilated_img, 21)

    # --- finding absolute difference to preserve edges ---
    diff_img = 255 - cv2.absdiff(img[:, :, 1], bg_img)

    # --- normalizing between 0 to 255 ---
    norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    # cv2.imshow('norm_img', imutils.resize(norm_img, width=700))

    th = cv2.threshold(norm_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    return th


def detect_letters(img):
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img = image_cleaner(img)

    bit_img = cv2.bitwise_not(img)

    cnts, hierarchy = cv2.findContours(bit_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    let_list = [Letter(c) for c in cnts]

    width_average = np.average([let.w for let in let_list])
    height_average = np.average([let.h for let in let_list])
    let_list = [let for let in let_list
                if width_average * 10 > let.w > width_average * 0.20
                and height_average * 3 > let.h]

    let_list.sort(key=lambda let: let.x + let.w, reverse=True)
    return let_list


def detect_rows(letters):
    rows = []
    for let in letters:
        if len(rows) == 0:
            rows.append(Row(let))
            continue
        matching = np.array([row.get_matching_rate(let) for row in rows])
        best_row = np.argmax(matching)
        if matching[best_row] > 0:
            rows[int(best_row)].add_let(let)
        else:
            rows.append(Row(let))

    # delete small rows
    average = np.average([(row.bottom_avr - row.top_avr)for row in rows])
    rows = [row for row in rows if row.bottom_avr - row.top_avr > average * 0.66]
    # soring the rows
    rows.sort(key=lambda row: row.letter_list[0].y)

    return rows


def combine_letters(rows):
    new_rows_list = []
    for row in rows:
        new_row = Row(row.get_let(0))
        for let in range(1, len(row)):
            old = new_row.get_let(-1)
            new = row.get_let(let)
            if new.x + new.w - old.x > old.w * 0.66 or new.w * 0.66 + new.x > old.x:
                new_row.replace_let((old + new), -1)
            else:
                new_row.add_let(new)
        new_rows_list.append(new_row)
    return new_rows_list


def get_letters(img):
    start = time.process_time()

    let_list = detect_letters(img)

    rows_list = detect_rows(let_list)
    rows_list = combine_letters(rows_list)

    let_list = list()
    for r_num, row in enumerate(rows_list):
        for l_num, let in enumerate(row.letter_list):
            let.rownum = r_num + 1
            let.letnum = l_num + 1
            let_list.append(let)

    # let_list = list()
    # for row in rows_list:
    #     let_list.extend(let for let in row.letter_list)

    print('Letter finder process took:', time.process_time() - start)

    return let_list




