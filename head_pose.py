from pram import PREDICTOR,  POINTS_NUM_LANDMARK

import math

import cv2
import dlib
import numpy as np


def head_pose_not_correct(face_frame):

    pitch, yaw, roll = detect_head_pose(face_frame)

    if (165 <= pitch <= 179) or (-179 <= pitch <= -165):
        if -10 <= yaw <= 10:
            if -10 <= roll <= 10:
                return False
    return True


def detect_head_pose(frame):
    ret, points = get_image_points(frame)
    if ret != 0:
        print('get_image_points failed')
        return -1, -1, -1

    ret, rotation_vector, translation_vector = get_pose_estimation(frame.shape, points)
    if not ret:
        print('get_pose_estimation failed')
        return -1, -1, -1

    pitch, yaw, roll = get_euler_angle(rotation_vector)

    return pitch, yaw, roll


def get_image_points(frame):
    frame_width = frame.shape[0]
    frame_height = frame.shape[1]

    face_rect = dlib.rectangle(0, 0, frame_width, frame_height)

    landmark_shape = PREDICTOR(frame, face_rect)

    return get_image_points_from_landmark_shape(landmark_shape)


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

    y = int((pitch / math.pi) * 180)
    x = int((yaw / math.pi) * 180)
    z = int((roll / math.pi) * 180)

    return y, x, z
