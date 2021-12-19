import cv2


def opened_webcam(cam_id):
    cam = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
    if cam.isOpened():
        return cam
    else:
        return None


def release_webcam(cam):
    cam.release()