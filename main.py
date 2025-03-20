from contextlib import contextmanager

import cv2
import imutils
from OCR import get_letters, predict_letters, get_matching, save_letters_to_json

import cProfile
import pstats


@contextmanager
def profiler_code():
    pr = cProfile.Profile()
    try:
        pr.enable()
        yield
    finally:
        pr.disable()
        pr.print_stats(sort="tottime")


def show_img(let_list, img):
    green = (0, 255, 0)
    red = (255, 0, 0)
    i = 0
    for let in let_list:
        if let.rownum is None:
            continue

        if let.rownum % 2 == 0:
            color = red
        else:
            color = green
        cv2.rectangle(img, (let.x, let.y), (let.x + let.w, let.y + let.h), color, 1)
        cv2.putText(img, str(i), (let.x, let.y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)
        i+=1

    cv2.imshow(f'letter', img)
    cv2.waitKey(0)


if '__main__' == __name__:

    # with profiler_code():
    img_path = 'images/mz2.jpg'
    image = cv2.imread(img_path)

    img_resized = imutils.resize(image, width=1200)

    letter_list = get_letters(image)

    letter_list = predict_letters(letter_list, image, cnn=True)

    letter_list = get_matching(letter_list, image)

    # save_letters_to_json(letter_list)

    # show_img(letter_list, image)




