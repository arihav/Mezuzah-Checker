import cv2
import numpy as np
from PIL import Image
import time
import sys

import tensorflow as tf


def convert_to_letters(result):
    letters = ''
    num_to_let = {1: 'א', 2: 'ב', 3: 'ג', 4: 'ד', 5: 'ה', 6: 'ו', 7: 'ז', 8: 'ח', 9: 'ט', 10: 'י', 20: 'כ', 30: 'ל',
                  40: 'מ', 50: 'נ', 60: 'ס', 70: 'ע', 80: 'פ', 90: 'צ', 100: 'ק', 200: 'ר', 300: 'ש', 400: 'ת',
                  21: 'ך', 41: 'ם', 51: 'ן', 81: 'ף', 91: 'ץ'}
    for re in result:
        letters += num_to_let[int(re)]

    return letters


def resize_image(img):
    size = (21, 28)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(img)
    image.thumbnail(size, Image.ANTIALIAS)

    cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    height, width = cv_img.shape[:2]
    top = bottom = left = right = 0
    if height < size[1]:
        h = size[1] - height
        top = bottom = h // 2
        bottom = bottom if h % 2 == 0 else bottom + 1
    if width < size[0]:
        w = size[0] - width
        left = right = w // 2
        left = left if w % 2 == 0 else left + 1
    edge_img = cv2.copyMakeBorder(cv_img.copy(), top, bottom, left, right, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    return edge_img


def load_train_data():
    # Load knn classifier
    try:
        with np.load('../ModelsAndData/letters_data.npz') as data:
            cells = data['train']
            key_images = data['train_labels']

    except FileNotFoundError:
        print(sys.exc_info()[1])
        sys.exit(1)

    return cells, key_images


def img_handler(letters, img):
    flat_letters = []

    for letter in letters:
        crop_img = img[letter.y: letter.y + letter.h, letter.x: letter.x + letter.w]
        resize_img = resize_image(crop_img)

        flat_img = resize_img.flatten()
        flat_letters.append(flat_img)

    flat_letters = np.array(flat_letters, dtype=np.float32)
    return flat_letters


def knn_classifier(test_cells):
    train_cells, key_images = load_train_data()

    knn = cv2.ml.KNearest_create()
    knn.train(train_cells, cv2.ml.ROW_SAMPLE, key_images)
    ret, result, neighbours, dist = knn.findNearest(test_cells, k=1)

    max_dist = np.max(dist)  # Maximum distance from all test cases
    confidences = 1 - (dist / max_dist)  # Convert to percentage

    predictions = [{"id": int(result[i][0]), "confidence": float(confidences[i][0])} for i in range(len(result))]

    return predictions


def keras_classifier(test_cells):
    test_cells = tf.keras.utils.normalize(test_cells, axis=1)

    model = tf.keras.models.load_model('ModelsAndData/keras_model.h5')
    predict = model.predict(test_cells)

    id_to_class = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 20: 10, 30: 11,
                   40: 12, 50: 13, 60: 14, 70: 15, 80: 16, 90: 17, 100: 18, 200: 19, 300: 20, 400: 21,
                   21: 22, 41: 23, 51: 24, 81: 25, 91: 26}
    result = []
    for i, p in enumerate(predict):
        for key, val in id_to_class.items():
            max_arg = np.argmax(p)
            if max_arg == val:
                result.append({'id': key, 'confidence': p[max_arg]})

    return result


def predict_letters(letters, img, cnn=True):
    start = time.process_time()

    test_cells = img_handler(letters, img)

    if cnn:
        result = keras_classifier(test_cells)
    else:
        result = knn_classifier(test_cells)

    # result = convert_to_letters(result)
    for key, letter in enumerate(letters):
        letter.prediction = result[key]['id']
        letter.confidence = float(result[key]['confidence'])

    print('Letter recognize process took:', time.process_time()-start)

    return letters


