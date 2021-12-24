import pickle_data
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

threshold = DEFAULT_THRESHOLD

data = pickle_data.Data()


def driver_options():
    options = webdriver.ChromeOptions()

    options.add_experimental_option("detach", True)
    # 使瀏覽器不會自動關閉(僅測試用)

    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    # 不顯示上方'Chrome正受到自動測試軟體控制'提示

    prefs = {"credentials_enable_service": False, "profile.password_manager_enabled": False}
    options.add_experimental_option("prefs", prefs)
    # 關閉Chrome詢問是否儲存密碼選項

    options.add_argument("--use-fake-ui-for-media-stream")

    return options


def create_web_driver():
    service = Service(ChromeDriverManager().install())

    options = driver_options()

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


def show_result_student_name(driver, stu_name):
    driver.execute_script(f'document.getElementsByName("student_name")[0].value = "{stu_name}";')


def show_result_student_id(driver, stu_id):
    driver.execute_script(f'document.getElementsByName("student_id")[0].value = "{stu_id}";')


def show_student_image(driver, stu_img):
    cv2.imwrite(IMAGE_CACHE_PATH + 'stu_img.png', stu_img)
    driver.execute_script('document.getElementById("student_face").src = "cache/stu_img.png"')


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


def enable_clear_button(driver):
    driver.execute_script('clearButton = document.getElementsByClassName("clear_button")[0];'
                          'clearButton.disabled = false;')


def enable_button(driver, has_match):
    enable_check_button(driver, has_match)
    enable_clear_button(driver)


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
    result = face_recognized(driver, data, threshold)

    show_result(driver, result)


def check_if_button_clicked(driver):
    check_button_clicked = driver.execute_script('return checkButtonClicked;')
    clear_button_clicked = driver.execute_script('return clearButtonClicked;')

    if check_button_clicked is True or clear_button_clicked is True:
        if check_button_clicked:
            driver.execute_script('checkButtonClicked = false;')
            return True, 'check_button'

        if clear_button_clicked:
            driver.execute_script('clearButtonClicked = false;')
            return True, 'clear_button'
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

    enable_button(driver, True)


def book_borrow_process(driver):
    driver.execute_script("window.open()")
    driver.switch_to.window(driver.window_handles[1])
    driver.get('https://one.cy.edu.tw/web-module_list/rest/service/main#')


def clear_result_student_image(driver):
    driver.execute_script('document.getElementById("student_face").src = "src/pic/user.png"')


def clear_result_student_name(driver):
    driver.execute_script('studentNameInput = document.getElementsByName("student_name")[0];'
                          'studentNameInput.disabled = true;'
                          'studentNameInput.classList.remove("bad_input");'
                          'studentNameInput.value = "";'
                          'studentNameInput.placeholder = "";')


def clear_result_student_id(driver):
    driver.execute_script('studentIdInput = document.getElementsByName("student_id")[0];'
                          'studentIdInput.disabled = true;'
                          'studentIdInput.classList.remove("bad_input");'
                          'studentIdInput.value = "";'
                          'studentIdInput.placeholder = "";')


def clear_result(driver):
    clear_result_student_image(driver)
    clear_result_student_name(driver)
    clear_result_student_id(driver)


def disable_check_button(driver, massage):
    driver.execute_script(f'checkButton = document.getElementsByClassName("check_button")[0];'
                          f'checkButton.innerHTML = "{massage}";'
                          f'checkButton.disabled = true;')


def disable_clear_button(driver):
    driver.execute_script('clearButton = document.getElementsByClassName("clear_button")[0];'
                          'clearButton.disabled = true;')


def disable_button(driver, check_button_massage="請完成辨識程序"):
    disable_check_button(driver, check_button_massage)
    disable_clear_button(driver)


def wait_for_user_to_make_decision(driver):
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
                    book_borrow_process(driver)
            elif button_name == 'clear_button':
                clear_result(driver)
                disable_button(driver)
                break


def menu_session(driver):
    try:
        wait = WebDriverWait(driver, 30)
        wait_until_page_loaded(wait, MENU_URL)

        while True:
            face_recognition_process(driver)

            wait_for_user_to_make_decision(driver)

    except TimeoutException:
        menu_session(driver)
    except (NoSuchWindowException, WebDriverException):
        exit()


def main():
    driver = create_web_driver()

    #driver.get(LOGIN_URL)
    #login_session(driver)

    driver.get(MENU_URL)
    menu_session(driver)


if __name__ == '__main__':
    main()
