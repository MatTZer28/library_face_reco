import webcam
from capture import face_frame

CAMERA_ID = 0


def train_face():
    cam = webcam.opened_webcam(CAMERA_ID)

    face = face_frame(cam)

    while head_pose_not_correct(face):
        face = face_frame(cam)

    train_faces = [face_frame(cam) for i in range(5)]


def head_pose_not_correct(face):
    return True