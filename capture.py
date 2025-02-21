import webcam
from pram import DETECTOR

import cv2


def face_frame(driver):
    is_face_gone = False

    frame, faces = detect_faces(driver)

    if is_data_button_clicked(driver):
        return frame, is_face_gone

    while no_faces_detected(faces):  # 沒有偵測到人臉
        show_no_faces_message(driver)

        is_face_gone = True

        frame, faces = detect_faces(driver)

        if is_data_button_clicked(driver):
            return frame, is_face_gone

    largest_face = pick_largest_face(faces)

    cropped_frame = crop_frame_with_only_face(frame, largest_face)

    resized_frame = resize(cropped_frame)

    return resized_frame, is_face_gone


def detect_faces(driver):
    frame = webcam.read_frame(driver)
    faces_coordinate = DETECTOR(frame, 0)
    return frame, faces_coordinate


def is_data_button_clicked(driver):
    if driver.current_window_handle == driver.window_handles[0]:
        return driver.execute_script('return tableShowed;')
    else:
        return False


def no_faces_detected(faces):
    if faces:
        return False
    else:
        return True


def show_no_faces_message(driver):
    driver.execute_script('progressIndicator = document.getElementsByClassName("progress_indicator")[0];'
                          'progressIndicator.innerText = "尚未偵測到人臉";'
                          'progressIndicator.style.animation = "breath 3s infinite";')


def pick_largest_face(faces):
    if len(faces) == 1:
        return faces[0]

    face_areas = [(rect.right() - rect.left()) * (rect.bottom() - rect.top()) for rect in faces]

    largest_area = face_areas[0]
    largest_index = 0
    for index in range(1, len(faces)):
        if face_areas[index] > largest_area:
            largest_index = index
            largest_area = face_areas[index]

    return faces[largest_index]


def crop_frame_with_only_face(frame, face):
    cropped_frame = frame[face.top():face.bottom(), face.left():face.right()]
    return cropped_frame


def resize(frame):
    size = frame.shape
    if size[0] > 700:
        h = size[0] / 3
        w = size[1] / 3
        return cv2.resize(frame, (int(w), int(h)), interpolation=cv2.INTER_CUBIC)
    else:
        return frame
