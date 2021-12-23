import pandas as pd

import csv_data
import calculate
from capture import face_frame
from head_pose import head_pose_not_correct


def face_recognized(driver, data: csv_data.Data, threshold):
    fail_count = 0

    face, is_face_gone = face_frame(driver)

    show_face_detected_message(driver)

    while head_pose_not_correct(face):  # 頭沒有擺正

        fail_count = fail_count + 1
        if fail_count == 5:
            show_head_pose_not_correct_message(driver)

        face, is_face_gone = face_frame(driver)

        if is_face_gone:
            fail_count = 0
            show_face_detected_message(driver)

    show_recognizing_message(driver)

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


def show_face_detected_message(driver):
    driver.execute_script('progressIndicator = document.getElementsByClassName("progress_indicator")[0];'
                          'progressIndicator.innerHTML = "發現人臉<br />請正臉面向鏡頭";'
                          'progressIndicator.style.animation = "none";')


def show_head_pose_not_correct_message(driver):
    driver.execute_script('progressIndicator = document.getElementsByClassName("progress_indicator")[0];'
                          'progressIndicator.innerHTML = "臉未擺正<br />請正臉面向鏡頭";'
                          'progressIndicator.style.animation = "none";')


def show_recognizing_message(driver):
    driver.execute_script('progressIndicator = document.getElementsByClassName("progress_indicator")[0];'
                          'progressIndicator.innerHTML = "辨識中，請稍後";'
                          'progressIndicator.style.animation = "breath 3s infinite";')
