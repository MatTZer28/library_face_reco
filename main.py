import os

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
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
    # 使瀏覽器不會自動關閉

    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    # 不顯示上方'Chrome正受到自動測試軟體控制'提示

    return options


def create_web_driver():
    service = Service(ChromeDriverManager().install())

    options = driver_options()

    return webdriver.Chrome(service=service, options=options)


def login_successful(driver) -> bool:
    try:
        wait = WebDriverWait(driver, 600)
        if wait.until(ec.url_changes(LOGIN_URL)):
            if driver.current_url == LOGIN_SUCCESSFUL_URL:
                return True
            else:
                return login_session(driver)
    except TimeoutException:
        return False


def login_session(driver):
    driver.get(LOGIN_URL)
    if login_successful(driver):
        driver.get(MENU_URL)


def main():
    driver = create_web_driver()
    driver.maximize_window()

    login_session(driver)


if __name__ == '__main__':
    main()
