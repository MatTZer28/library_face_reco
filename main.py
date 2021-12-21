import csv_data
from pram import DEFAULT_THRESHOLD, LOGIN_URL, LOGIN_SUCCESSFUL_URL, MENU_URL, CAMERA_ID
from recognize import face_recognized

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchWindowException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

threshold = DEFAULT_THRESHOLD
data = csv_data.Data()


def driver_options():
    options = webdriver.ChromeOptions()

    # options.add_experimental_option("detach", True)
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
        wait = WebDriverWait(driver, 1)
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


def show_result_student_name(driver, stu_name):
    driver.execute_script(f'document.getElementsByName("student_name")[0].value = "{stu_name}";')


def show_result_student_id(driver, stu_id):
    driver.execute_script(f'document.getElementsByName("student_id")[0].value = "{stu_id}";')


def show_result(driver, result):
    if not result.empty:
        stu_name = result.iloc[0, 0]
        show_result_student_name(driver, stu_name)
        stu_id = result.iloc[0, 1]
        show_result_student_id(driver, stu_id)
    else:
        show_result_student_name(driver, '無資料')
        show_result_student_id(driver, '無資料')


def start_face_recognition_process(driver):
    result = face_recognized(driver, data, threshold)

    show_result(driver, result)


def wait_until_page_loaded(wait, url):
    try:
        if wait.until(ec.url_matches(url)):
            return
    except TimeoutException:
        wait_until_page_loaded(wait, url)


def menu_session(driver):
    try:
        wait = WebDriverWait(driver, 1)
        wait_until_page_loaded(wait, MENU_URL)

        start_face_recognition_process(driver)

        if wait.until(ec.url_changes(MENU_URL)):
            return
    except TimeoutException:
        menu_session(driver)
    except (NoSuchWindowException, WebDriverException):
        exit()


def main():
    driver = create_web_driver()

    # driver.get(LOGIN_URL)
    # login_session(driver)

    driver.get(MENU_URL)
    menu_session(driver)


if __name__ == '__main__':
    main()
