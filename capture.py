import dlib
import cv2
import numpy as np


def face_frame(cam):
    frame, faces = detect_faces(cam)

    while no_faces_detected(faces):
        frame, faces = detect_faces(cam)

    face = pick_one_from_faces(faces)

    cropped_frame = crop_frame_with_only_face(frame, face)

    return cropped_frame


def detect_faces(cam):
    detector = face_detector()

    frame = webcam_frame(cam)
    frame_gray = cvt_gray(frame)

    faces_coordinate = detector(frame_gray, 0)
    return frame, faces_coordinate


def face_detector():
    return dlib.get_frontal_face_detector()


def webcam_frame(cam):
    if cam.isOpened():
        frame_ready, frame = cam.read()
        if frame_ready:
            return frame
    return np.array([0, 0, 0]).reshape([3, 1, 1])


def cvt_gray(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def no_faces_detected(faces):
    if faces:
        return False
    else:
        return True


def pick_one_from_faces(faces):
    return faces[0]


def crop_frame_with_only_face(frame, face):
    cropped_frame = frame[face.top():face.bottom(), face.left():face.right()]
    return cropped_frame
