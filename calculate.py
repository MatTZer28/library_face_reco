from pram import PREDICTOR, RECOGNITION

import dlib
import numpy as np


def features_mean(faces):
    features = []
    for frame in faces:
        face_descriptor = features_128d(frame)
        features.append(face_descriptor)
    return np.array(features).mean(axis=0)


def features_128d(frame):
    frame_width = frame.shape[0]
    frame_height = frame.shape[1]

    face_rect = dlib.rectangle(0, 0, frame_width, frame_height)

    landmark_shape = PREDICTOR(frame, face_rect)
    face_descriptor = RECOGNITION.compute_face_descriptor(frame, landmark_shape)

    return face_descriptor


def euclidean_distance(feature_1, feature_2):
    dist = np.sqrt(np.sum(np.square(np.subtract(feature_1, feature_2))))
    return dist
