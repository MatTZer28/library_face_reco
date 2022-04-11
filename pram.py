import os

import dlib

LOGIN_URL = 'https://one.cy.edu.tw/web-sso/rest/Redirect/login/page/normal?returnUrl=https://one.cy.edu.tw/WebAuth.do'

LOGIN_SUCCESSFUL_URL = 'https://one.cy.edu.tw/web-module_list/rest/service/main'

LIBRARY_URL = 'https://one.cy.edu.tw/web-module_list/rest/service/main#!/'

menu_html_path = os.path.abspath('web/menu.html').replace('\\', '/')

MENU_URL = 'file:///' + menu_html_path

COOKIE_PATH = 'data/cookie.pkl'

DATA_PATH = 'data/student_info.pkl'

DETECTOR = dlib.get_frontal_face_detector()

PREDICTOR = dlib.shape_predictor('dlib_model/shape_predictor_68_face_landmarks.dat')

RECOGNITION = dlib.face_recognition_model_v1('dlib_model/dlib_face_recognition_resnet_model_v1.dat')

POINTS_NUM_LANDMARK = 68

DEFAULT_THRESHOLD = 65

IMAGE_CACHE_PATH = 'web/cache/'
