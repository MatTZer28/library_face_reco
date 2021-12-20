from pram import DETECTOR

import cv2
import numpy as np


def face_frame(cam):
    frame, faces = detect_faces(cam)

    while no_faces_detected(faces):  # 沒有偵測到人臉
        frame, faces = detect_faces(cam)

    largest_face = pick_largest_face(faces)

    cropped_frame = crop_frame_with_only_face(frame, largest_face)

    resized_frame = resize(cropped_frame)

    return resized_frame


def detect_faces(cam):
    frame = webcam_frame(cam)

    faces_coordinate = DETECTOR(frame, 0)
    return frame, faces_coordinate


def webcam_frame(cam):
    if cam.isOpened():
        frame_ready, frame = cam.read()
        if frame_ready:
            return frame
    return np.array([0, 0, 0]).reshape([3, 1, 1])


def no_faces_detected(faces):
    if faces:
        return False
    else:
        return True


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
