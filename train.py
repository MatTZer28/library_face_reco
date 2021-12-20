import webcam
from capture import face_frame

import cv2
import dlib
import numpy as np
import math

CAMERA_ID = 0
POINTS_NUM_LANDMARK = 68


def train_face():
    cam = webcam.opened_webcam(CAMERA_ID)

    face = face_frame(cam)

    while head_pose_not_correct(face):
        face = face_frame(cam)

    train_faces = [face_frame(cam) for i in range(5)]


def head_pose_not_correct(face):
    pitch, yaw, roll = detect_head_pose(face)
    return True


def detect_head_pose(frame):
    retval, points = get_image_points(frame)
    if retval != 0:
        print('get_image_points failed')
        return

    ret, rotation_vector, translation_vector = get_pose_estimation(frame.shape, points)
    if not ret:
        print('get_pose_estimation failed')
        return

    return get_euler_angle(rotation_vector)


def get_image_points(frame):
    detector = face_detector()
    predictor = face_predictor()

    face_rect = detector(frame, 0)

    if not face_rect:
        print("ERROR: found no face")
        return -1, None

    largest_index = _largest_face(face_rect)
    face_rectangle = face_rect[largest_index]

    landmark_shape = predictor(frame, face_rectangle)

    return get_image_points_from_landmark_shape(landmark_shape)


def face_detector():
    return dlib.get_frontal_face_detector()


def face_predictor():
    return dlib.shape_predictor("dlib_model/shape_predictor_68_face_landmarks.dat")


def _largest_face(face_rect):
    if len(face_rect) == 1:
        return 0

    face_areas = [(rect.right() - rect.left()) * (rect.bottom() - rect.top()) for rect in face_rect]

    largest_area = face_areas[0]
    largest_index = 0
    for index in range(1, len(face_rect)):
        if face_areas[index] > largest_area:
            largest_index = index
            largest_area = face_areas[index]

    return largest_index


def get_image_points_from_landmark_shape(landmark_shape):
    if landmark_shape.num_parts != POINTS_NUM_LANDMARK:
        print("ERROR:landmark_shape.num_parts-{}".format(landmark_shape.num_parts))
        return -1, None

    # 2D image points. If you change the image, you need to change vector
    image_points = np.array([
        (landmark_shape.part(30).x, landmark_shape.part(30).y),     # Nose tip
        (landmark_shape.part(8).x, landmark_shape.part(8).y),       # Chin
        (landmark_shape.part(36).x, landmark_shape.part(36).y),     # Left eye left corner
        (landmark_shape.part(45).x, landmark_shape.part(45).y),     # Right eye right corne
        (landmark_shape.part(48).x, landmark_shape.part(48).y),     # Left Mouth corner
        (landmark_shape.part(54).x, landmark_shape.part(54).y)      # Right mouth corner
    ], dtype="double")

    return 0, image_points


def get_pose_estimation(frame_size, image_points):
    # 3D model points.
    model_points = np.array([
        (0.0, 0.0, 0.0),            # Nose tip
        (0.0, -330.0, -65.0),       # Chin
        (-225.0, 170.0, -135.0),    # Left eye left corner
        (225.0, 170.0, -135.0),     # Right eye right corne
        (-150.0, -150.0, -125.0),   # Left Mouth corner
        (150.0, -150.0, -125.0)     # Right mouth corner

    ])

    focal_length = frame_size[1]
    center = (frame_size[1] / 2, frame_size[0] / 2)

    camera_matrix = np.array(
        [[focal_length, 0, center[0]],
         [0, focal_length, center[1]],
         [0, 0, 1]], dtype="double"
    )

    dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion

    (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points,
                                                                  image_points,
                                                                  camera_matrix,
                                                                  dist_coeffs,
                                                                  flags=cv2.SOLVEPNP_ITERATIVE)

    return success, rotation_vector, translation_vector


def get_euler_angle(rotation_vector):
    # calculate rotation angles
    theta = cv2.norm(rotation_vector, cv2.NORM_L2)

    # transformed to quaterniond
    w = math.cos(theta / 2)
    x = math.sin(theta / 2) * rotation_vector[0][0] / theta
    y = math.sin(theta / 2) * rotation_vector[1][0] / theta
    z = math.sin(theta / 2) * rotation_vector[2][0] / theta

    y_square = y * y
    # pitch (x-axis rotation)
    t0 = 2.0 * (w * x + y * z)
    t1 = 1.0 - 2.0 * (x * x + y_square)
    print('t0:{}, t1:{}'.format(t0, t1))
    pitch = math.atan2(t0, t1)

    # yaw (y-axis rotation)
    t2 = 2.0 * (w * y - z * x)
    if t2 > 1.0:
        t2 = 1.0
    if t2 < -1.0:
        t2 = -1.0
    yaw = math.asin(t2)

    # roll (z-axis rotation)
    t3 = 2.0 * (w * z + x * y)
    t4 = 1.0 - 2.0 * (y_square + z * z)
    roll = math.atan2(t3, t4)

    print('pitch:{}, yaw:{}, roll:{}'.format(pitch, yaw, roll))

    y = int((pitch / math.pi) * 180)
    x = int((yaw / math.pi) * 180)
    z = int((roll / math.pi) * 180)

    return y, x, z
