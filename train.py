import calculate
import pickle_data
from capture import face_frame
from head_pose import train_head_pose_not_correct


def train_face(driver, data: pickle_data.Data):
    fail_count = 0

    face, is_face_gone = face_frame(driver)

    show_face_detected_message(driver)

    while train_head_pose_not_correct(face):  # 頭沒有擺正
        fail_count = fail_count + 1
        if fail_count == 5:
            show_head_pose_not_correct_message(driver)

        face, is_face_gone = face_frame(driver)

        if is_face_gone:
            fail_count = 0
            show_face_detected_message(driver)

    train_faces = []
    for i in range(5):
        face, is_face_gone = face_frame(driver)
        train_faces.append(face)

    show_training_message(driver)

    feature = calculate.features_mean(train_faces)

    middle_face = train_faces[2]

    data.add_new_member(student_id(driver), student_name(driver), middle_face, feature)

    return middle_face


def show_face_detected_message(driver):
    driver.execute_script('progressIndicator = document.getElementsByClassName("progress_indicator")[0];'
                          'progressIndicator.innerHTML = "開始建立<br />請正臉面向鏡頭";'
                          'progressIndicator.style.animation = "none";')


def show_head_pose_not_correct_message(driver):
    driver.execute_script('progressIndicator = document.getElementsByClassName("progress_indicator")[0];'
                          'progressIndicator.innerHTML = "臉未擺正<br />請正臉面向鏡頭";'
                          'progressIndicator.style.animation = "none";')


def show_training_message(driver):
    driver.execute_script('progressIndicator = document.getElementsByClassName("progress_indicator")[0];'
                          'progressIndicator.innerHTML = "建立中，請稍後";'
                          'progressIndicator.style.animation = "breath 3s infinite";')


def student_id(driver):
    return driver.execute_script('return document.getElementsByName("student_id")[0].value;')


def student_name(driver):
    return driver.execute_script('return document.getElementsByName("student_name")[0].value;')
