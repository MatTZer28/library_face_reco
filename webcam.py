import base64

import cv2
import numpy as np
from selenium.webdriver.common.by import By


def read_frame(driver):
    canvas = driver.find_element(By.ID, 'canvas')

    frame_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)

    frame = base64_to_cv2(frame_base64)

    return frame


def base64_to_cv2(frame):
    img_string = base64.b64decode(frame)
    frame = cv2.imdecode(np.fromstring(img_string, np.uint8), cv2.IMREAD_COLOR)
    return frame
