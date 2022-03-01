import pickle_data
import random
import string
import sys
import os
import time

from pram import DEFAULT_THRESHOLD, LOGIN_URL, LOGIN_SUCCESSFUL_URL, MENU_URL, IMAGE_CACHE_PATH
from recognize import face_recognized
from train import train_face

import cv2
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchWindowException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

threshold = DEFAULT_THRESHOLD

sys.tracebacklimit = 0

data = pickle_data.Data()

is_data_showed = False

table_selected_id = ''

original_window = None

library_window = None


def driver_options(detach):
    options = webdriver.ChromeOptions()

    if detach:
        options.add_experimental_option("detach", True)
        # 使瀏覽器不會自動關閉

    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    # 不顯示上方'Chrome正受到自動測試軟體控制'提示

    root_path = os.path.abspath("./")
    options.add_argument(f"--user-data-dir={root_path}\\data\\chrome-user-data")
    options.add_argument(f"--profile-directory=Default")

    prefs = {"credentials_enable_service": True, "profile.password_manager_enabled": True}
    options.add_experimental_option("prefs", prefs)
    # 關閉Chrome詢問是否儲存密碼選項

    options.add_argument("--use-fake-ui-for-media-stream")
    # 排除跳出視訊鏡頭權限要求

    return options


def create_web_driver(detach=False):
    service = Service(ChromeDriverManager().install())

    options = driver_options(detach)

    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()

    return driver


def login_session(driver):
    try:
        wait = WebDriverWait(driver, 30)
        if wait.until(ec.url_changes(LOGIN_URL)):
            if driver.current_url == LOGIN_SUCCESSFUL_URL:
                return
            else:
                driver.get(LOGIN_URL)
                login_session(driver)
    except TimeoutException:
        login_session(driver)
    except (NoSuchWindowException, WebDriverException):
        exit()


def wait_until_page_loaded(wait, url):
    try:
        if wait.until(ec.url_matches(url)):
            return
    except TimeoutException:
        wait_until_page_loaded(wait, url)


def load_library_page(driver, wait):
    global original_window
    global library_window

    original_window = driver.current_window_handle

    driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/a/img").click()

    library_window = driver.window_handles[-1]

    driver.switch_to.window(library_window)

    element = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".mod_box")))
    element.click()

    element = wait.until(ec.presence_of_element_located((By.LINK_TEXT, "流通管理")))
    element.click()

    element = driver.find_element(By.LINK_TEXT, "借閱流通")
    element.click()

    driver.switch_to.window(original_window)


def is_data_button_clicked(driver):
    if driver.current_window_handle == driver.window_handles[0]:
        return driver.execute_script('return tableShowed;')
    else:
        return False


def data_table_add_row(row, driver):
    input_row = [row['name'].to_string(index=False), row['id'].to_string(index=False)]
    driver.execute_script(f'let table = $(\'#data_table\').DataTable();'
                          f'table.row.add({input_row}).draw();')


def search_student_image(stu_id):
    df = data.content.loc[data.content['id'] == stu_id]
    return df['img'].iloc[0]


def data_table_process(driver, wait):
    global is_data_showed
    global table_selected_id

    if not is_data_showed:
        is_data_showed = True
        wait.until(ec.presence_of_element_located((By.ID, 'data_table')))

        if not data.content.empty:
            for i in range(data.content.index.stop):
                data_table_add_row(data.content.iloc[[i]], driver)
    else:
        table_selected_id = current_student_id(driver)
        if table_selected_id != '':
            if table_selected_id == current_student_id(driver):
                enable_button(driver, True, clear_button_massage="刪除")
                show_student_image(driver, search_student_image(table_selected_id))

                button_clicked, button_name = check_if_button_clicked(driver)

                if button_clicked:
                    if button_name == 'check_button':
                        book_borrow_process(driver, wait, table_selected_id)
                    elif button_name == 'clear_button':
                        data.remove_member_by_id(table_selected_id)
                        clear_result(driver, "辨識資料庫檢索")
                        disable_button(driver, check_button_massage="請選擇辨識資料", clear_button_massage="刪除")
            else:
                table_selected_id = current_student_id(driver)
        else:
            clear_result(driver, "辨識資料庫檢索")
            disable_button(driver, check_button_massage="請選擇辨識資料", clear_button_massage="刪除")
            time.sleep(0.1)


def show_result_student_name(driver, stu_name):
    driver.execute_script(f'document.getElementsByName("student_name")[0].value = "{stu_name}";')


def show_result_student_id(driver, stu_id):
    driver.execute_script(f'document.getElementsByName("student_id")[0].value = "{stu_id}";')


def show_student_image(driver, stu_img):
    file_name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    cv2.imwrite(IMAGE_CACHE_PATH + f'{file_name}.png', stu_img)
    driver.execute_script(f'document.getElementById("student_face").src = "cache/{file_name}.png"')
    image_path = IMAGE_CACHE_PATH + file_name + '.png'
    os.remove(image_path)


def show_result_has_match_message(driver):
    driver.execute_script('progressIndicator = document.getElementsByClassName("progress_indicator")[0];'
                          'progressIndicator.innerHTML = "辨識成功";'
                          'progressIndicator.style.animation = "none";')


def enable_student_name_input(driver):
    driver.execute_script('studentNameInput = document.getElementsByName("student_name")[0];'
                          'studentNameInput.disabled = false;'
                          'studentNameInput.placeholder = "請在此輸入姓名";')


def enable_student_id_input(driver):
    driver.execute_script('studentIdInput = document.getElementsByName("student_id")[0];'
                          'studentIdInput.disabled = false;'
                          'studentIdInput.placeholder = "請在此輸入證號";')


def enable_input(driver):
    enable_student_name_input(driver)
    enable_student_id_input(driver)


def show_result_no_match_message(driver):
    driver.execute_script('progressIndicator = document.getElementsByClassName("progress_indicator")[0];'
                          'progressIndicator.innerHTML = "無資料<br />'
                          '<span style=\\"font-size: xx-large;\\">建議建立個人辨識資料</span>";'
                          'progressIndicator.style.animation = "none";')


def enable_check_button(driver, has_match):
    if has_match:
        driver.execute_script('checkButton = document.getElementsByClassName("check_button")[0];'
                              'checkButton.innerHTML = "確認資料，進行借閱";'
                              'checkButton.disabled = false;')
    else:
        driver.execute_script('checkButton = document.getElementsByClassName("check_button")[0];'
                              'checkButton.innerHTML = "建立個人辨識資料";'
                              'checkButton.disabled = false;')


def enable_clear_button(driver, message):
    driver.execute_script(f'clearButton = document.getElementsByClassName("clear_button")[0];'
                          f'clearButton.innerHTML = "{message}";'
                          f'clearButton.disabled = false;')


def enable_button(driver, has_match, clear_button_massage="清除"):
    enable_check_button(driver, has_match)
    enable_clear_button(driver, clear_button_massage)


def show_result(driver, result):
    if not result.empty:
        stu_name = result.iloc[0, 1]
        show_result_student_name(driver, stu_name)

        stu_id = result.iloc[0, 0]
        show_result_student_id(driver, stu_id)

        stu_img = result.iloc[0, 2]
        show_student_image(driver, stu_img)

        show_result_has_match_message(driver)

        enable_button(driver, has_match=True)
    else:
        enable_input(driver)

        show_result_no_match_message(driver)

        enable_button(driver, has_match=False)


def face_recognition_process(driver):
    global is_data_showed
    is_data_showed = False

    result = face_recognized(driver, data, threshold)

    show_result(driver, result)


def check_if_button_clicked(driver):
    if driver.current_window_handle == driver.window_handles[0]:
        check_button_clicked = driver.execute_script('return checkButtonClicked;')
        clear_button_clicked = driver.execute_script('return clearButtonClicked;')
        data_button_clicked = driver.execute_script('return tableShowed;')

        if check_button_clicked is True or clear_button_clicked is True or data_button_clicked is True:
            if check_button_clicked:
                driver.execute_script('checkButtonClicked = false;')
                return True, 'check_button'

            if clear_button_clicked:
                driver.execute_script('clearButtonClicked = false;')
                return True, 'clear_button'

            if data_button_clicked:
                return True, 'data_button'
        else:
            return False, 'none'
    else:
        return False, 'none'


def is_train_process(driver):
    check_button_content = driver.execute_script('checkButton = document.getElementsByClassName("check_button")[0];'
                                                 'return checkButton.innerHTML;')
    if check_button_content == '建立個人辨識資料':
        return True
    else:
        return False


def is_student_input_ok(driver):
    is_student_name_input_ok = driver.execute_script('studentNameInput = document.getElementsByName("student_name")[0];'
                                                     'if (studentNameInput.value == "") return false;'
                                                     'else return true;')

    is_student_id_input_ok = driver.execute_script('studentNameInput = document.getElementsByName("student_id")[0];'
                                                   'if (studentNameInput.value == "") return false;'
                                                   'else return true;')

    if not is_student_name_input_ok or not is_student_id_input_ok:
        if not is_student_name_input_ok:
            driver.execute_script('studentNameInput = document.getElementsByName("student_name")[0];'
                                  'studentNameInput.classList.add("bad_input");'
                                  'studentNameInput.classList.remove("vibrate_animation");'
                                  'studentNameInput.offsetWidth;'
                                  'studentNameInput.classList.add("vibrate_animation");')

        if not is_student_id_input_ok:
            driver.execute_script('studentIdInput = document.getElementsByName("student_id")[0];'
                                  'studentIdInput.classList.add("bad_input");'
                                  'studentIdInput.classList.remove("vibrate_animation");'
                                  'studentIdInput.offsetWidth;'
                                  'studentIdInput.classList.add("vibrate_animation");')

        return False

    return True


def show_train_success_message(driver):
    driver.execute_script('progressIndicator = document.getElementsByClassName("progress_indicator")[0];'
                          'progressIndicator.innerHTML = "建立成功";'
                          'progressIndicator.style.animation = "none";')


def face_train_process(driver):
    stu_img = train_face(driver, data)

    show_train_success_message(driver)

    show_student_image(driver, stu_img)

    enable_button(driver, has_match=True)


def current_student_id(driver):
    return driver.execute_script('studentIdInput = document.getElementsByName("student_id")[0];'
                                 'return studentIdInput.value')


def open_and_switch_to_new_tab(driver):
    driver.execute_script("window.open()")
    driver.switch_to.window(driver.window_handles[1])


def disable_data_button(driver):
    driver.execute_script('dataButton = document.getElementById("data_button");'
                          'dataButton.setAttribute(\'onclick\', \'\')')


def show_book_lending_message(driver):
    driver.execute_script('progressIndicator = document.getElementsByClassName("progress_indicator")[0];'
                          'progressIndicator.innerHTML = "借閱程序進行中";'
                          'progressIndicator.style.animation = "breath 3s infinite";')


def enable_data_button(driver):
    driver.execute_script('dataButton = document.getElementById("data_button");'
                          'dataButton.setAttribute(\'onclick\', \'data_button_clicked()\')')


def show_book_has_lent_message(driver):
    driver.execute_script('progressIndicator = document.getElementsByClassName("progress_indicator")[0];'
                          'progressIndicator.innerHTML = "借閱完成";'
                          'progressIndicator.style.animation = "none";')


def book_borrow_process(driver, wait, stu_id):
    disable_button(driver, check_button_massage="請完成借閱程序")
    disable_data_button(driver)
    show_book_lending_message(driver)

    driver.switch_to.window(library_window)

    element = wait.until(ec.presence_of_element_located((By.ID, "card_no")))
    element.send_keys(stu_id)
    element.send_keys(Keys.RETURN)

    element = wait.until(ec.presence_of_element_located((By.ID, "no_book")))

    while True:
        if element.get_attribute("value") == "AAAAAA":
            driver.execute_script("arguments[0].value='';", element)
            driver.switch_to.window(original_window)
            enable_button(driver, has_match=True)
            enable_data_button(driver)
            show_book_has_lent_message(driver)
            break


def clear_result_student_image(driver):
    driver.execute_script('document.getElementById("student_face").src = "src/pic/user.png"')


def clear_result_student_name(driver):
    driver.execute_script('studentNameInput = document.getElementsByName("student_name")[0];'
                          'studentNameInput.disabled = true;'
                          'studentNameInput.classList.remove("bad_input");'
                          'studentNameInput.value = "";'
                          'studentNameInput.placeholder = "";')


def show_progress_message(driver, message):
    driver.execute_script(f'progressIndicator = document.getElementsByClassName("progress_indicator")[0];'
                          f'progressIndicator.innerHTML = "{message}";'
                          f'progressIndicator.style.animation = "none";')


def clear_result_student_id(driver):
    driver.execute_script('studentIdInput = document.getElementsByName("student_id")[0];'
                          'studentIdInput.disabled = true;'
                          'studentIdInput.classList.remove("bad_input");'
                          'studentIdInput.value = "";'
                          'studentIdInput.placeholder = "";')


def clear_result(driver, message):
    clear_result_student_image(driver)
    clear_result_student_name(driver)
    clear_result_student_id(driver)
    show_progress_message(driver, message)


def disable_check_button(driver, massage):
    driver.execute_script(f'checkButton = document.getElementsByClassName("check_button")[0];'
                          f'checkButton.innerHTML = "{massage}";'
                          f'checkButton.disabled = true;')


def disable_clear_button(driver, massage):
    driver.execute_script(f'clearButton = document.getElementsByClassName("clear_button")[0];'
                          f'clearButton.innerHTML = "{massage}";'
                          f'clearButton.disabled = true;')


def disable_button(driver, check_button_massage="請完成辨識程序", clear_button_massage="清除"):
    disable_check_button(driver, check_button_massage)
    disable_clear_button(driver, clear_button_massage)


def wait_for_user_to_make_decision(driver, wait):
    while True:
        button_clicked, button_name = check_if_button_clicked(driver)

        if button_clicked:
            if button_name == 'check_button':
                if is_train_process(driver):
                    if not is_student_input_ok(driver):
                        continue
                    disable_button(driver, check_button_massage="請完成建立程序")
                    face_train_process(driver)
                else:
                    stu_id = current_student_id(driver)
                    book_borrow_process(driver, wait, stu_id)
            elif button_name == 'clear_button':
                clear_result(driver, "辨識系統準備中")
                disable_button(driver)
                break
            elif button_name == 'data_button':
                clear_result(driver, "辨識資料庫檢索")
                disable_button(driver, check_button_massage="請選擇辨識資料", clear_button_massage="刪除")
                break


def menu_session(driver):
    try:
        wait = WebDriverWait(driver, 30)
        wait_until_page_loaded(wait, MENU_URL)

        load_library_page(driver, wait)

        while True:
            if is_data_button_clicked(driver):
                data_table_process(driver, wait)
            else:
                clear_result(driver, "辨識系統準備中")
                disable_button(driver)

                face_recognition_process(driver)

                wait_for_user_to_make_decision(driver, wait)

    except TimeoutException:
        menu_session(driver)
    except (NoSuchWindowException, WebDriverException):
        exit()


def main():
    driver = create_web_driver()

    driver.get(LOGIN_URL)
    login_session(driver)

    driver.get(MENU_URL)
    menu_session(driver)


if __name__ == '__main__':
    main()
