import array

import cv2
import numpy as np
from PIL import Image
from selenium.webdriver.common.by import By


def read_frame(driver):
    canvas = driver.find_element(By.ID, 'canvas')

    width = int(canvas.get_attribute('width'))
    height = int(canvas.get_attribute('height'))

    frame_data = driver.execute_script(
        "var context = arguments[0].getContext(\"2d\");"
        "var data = context.getImageData(arguments[1], arguments[2], arguments[3], arguments[4]).data;"
        "return data;",
        canvas, 0, 0, width, height)

    data_bytes = array.array('B', frame_data).tobytes()

    frame = np.array(Image.frombytes('RGBA', (width, height), data_bytes))

    frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)

    return frame
