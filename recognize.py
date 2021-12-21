import pandas as pd

import csv_data
import calculate
from capture import face_frame
from head_pose import head_pose_not_correct


def face_recognized(driver, data: csv_data.Data, threshold):

    face = face_frame(driver)

    while head_pose_not_correct(face):  # 頭沒有擺正
        face = face_frame(driver)

    recog_face = [face]

    if not data.content.empty:
        for i in data.content.index:
            data_feature = data.content['feature'][i]
            curr_feature = calculate.features_mean(recog_face)

            euclidean_distance = calculate.euclidean_distance(data_feature, curr_feature)

            if euclidean_distance < float(threshold / 100):
                return data.content.iloc[[i]]
            else:
                return pd.DataFrame()
    else:
        return pd.DataFrame()
