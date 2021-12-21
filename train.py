import calculate
import csv_data
from capture import face_frame
from head_pose import head_pose_not_correct


def face_training(driver, data: csv_data.Data):

    face = face_frame(driver)

    while head_pose_not_correct(face):  # 頭沒有擺正
        face = face_frame(driver)

    train_faces = [face_frame(driver) for i in range(5)]

    feature = calculate.features_mean(train_faces)

    data
