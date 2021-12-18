import os

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

LOGIN_URL = 'https://one.cy.edu.tw/web-sso/rest/Redirect/login/page/normal?returnUrl=https://one.cy.edu.tw/WebAuth.do'
LOGIN_SUCCESSFUL_URL = 'https://one.cy.edu.tw/web-module_list/rest/service/main'
MENU_URL = 'file://' + os.path.abspath('web/menu.html')


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
    except NoSuchWindowException:
        exit()


def wait_until_page_loaded(wait, url):
    try:
        wait.until(ec.url_to_be(url))
    except TimeoutException:
        wait_until_page_loaded(wait, url)


def menu_session(driver):
    try:
        wait = WebDriverWait(driver, 1)
        wait_until_page_loaded(wait, MENU_URL)
        if wait.until(ec.url_changes(MENU_URL)):
            return
    except TimeoutException:
        menu_session(driver)
    except NoSuchWindowException:
        exit()


def main():
    driver = create_web_driver()

    driver.get(LOGIN_URL)
    login_session(driver)

    driver.get(MENU_URL)
    menu_session(driver)


if __name__ == '__main__':
    main()
