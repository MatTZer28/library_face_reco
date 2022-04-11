import pickle_data
import calculate
from capture import face_frame
from head_pose import recognize_head_pose_not_correct

import pandas as pd


def face_recognized(driver, data: pickle_data.Data, threshold):
    fail_count = 0

    face, is_face_gone = face_frame(driver)

    if is_data_button_clicked(driver):
        return pd.DataFrame()

    show_face_detected_message(driver)

    while recognize_head_pose_not_correct(face):  # 頭沒有擺正
        fail_count = fail_count + 1
        if fail_count == 5:
            show_head_pose_not_correct_message(driver)

        face, is_face_gone = face_frame(driver)

        if is_face_gone:
            fail_count = 0
            show_face_detected_message(driver)

        if is_data_button_clicked(driver):
            return pd.DataFrame()

    show_recognizing_message(driver)

    recog_face = [face]

    if not data.content.empty:
        curr_feature = calculate.features_mean(recog_face)
        euclidean_distances = []

        for i in range(data.content.index.start, data.content.index.stop, data.content.index.step):
            data_feature = data.content['feature'][i]
            euclidean_distance = calculate.euclidean_distance(data_feature, curr_feature)
            euclidean_distances.append(euclidean_distance)

        if len(euclidean_distances) > 0:
            lowest_euclidean_distance = min(euclidean_distances)
            if lowest_euclidean_distance < 1 - float(threshold / 100):
                return data.content.iloc[[euclidean_distances.index(lowest_euclidean_distance)]]
        return pd.DataFrame()
    else:
        return pd.DataFrame()


def is_data_button_clicked(driver):
    if driver.current_window_handle == driver.window_handles[0]:
        return driver.execute_script('return tableShowed;')
    else:
        return False


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
