from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement
from selenium.webdriver.common.action_chains import ActionChains
import time
from os import getenv


class ParsingResult:
    def __init__(self, result: dict) -> None:
        self.__result = result

    def get_result(self) -> dict:
        return self.__result


class WebElement:
    def __init__(self, browser: webdriver.Chrome, by: str, identifier: str, delay: float = -1) -> None:
        self.__browser = browser
        if delay > 0:
            WebDriverWait(self.__browser, delay).until(
                EC.presence_of_element_located((by, identifier)))
        self.__web_element = self.__browser.find_element(by, identifier)

    def fill_dropdown_input(self, input_value: str) -> None:
        self.fill_input(input_value)
        self.fill_input(Keys.ENTER)

    def fill_input(self, input_value: str) -> None:
        self.__web_element.send_keys(input_value)

    def select_by_value(self, value: str) -> None:
        select_el = Select(self.__web_element)
        select_el.select_by_value(value)

    def submit_button(self):
        self.__web_element.submit()

    def click(self):
        self.__web_element.click()

    def get_attribute(self, attribute: str):
        return self.__web_element.get_attribute(attribute)

    def text(self) -> str:
        return self.__web_element.text

    def element(self) -> SeleniumWebElement:
        return self.__web_element


class Parser(ABC):
    _browser: webdriver.Chrome

    def __init__(self) -> None:
        super().__init__()
        self._browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def _get_web_element(self, by: str, identifier: str, delay: float = -1) -> WebElement:
        return WebElement(self._browser, by, identifier, delay)

    def _wait_for_element(self, by: str, identifier: str, delay: float = 10) -> None:
        WebDriverWait(self._browser, delay).until(EC.presence_of_element_located((by, identifier)))

    def _move_and_click(self, el: SeleniumWebElement) -> None:
        (ActionChains(self._browser)
             .move_to_element(el)
             .click(el)
             .perform())

    def _move_and_send(self, el: SeleniumWebElement, send_keys: str = Keys.ENTER) -> None:
        (ActionChains(self._browser)
             .move_to_element(el)
             .send_keys(send_keys)
             .perform())


class ItmoAdminParser(Parser):
    __LOGIN_URL = 'https://admin.itmo.ru/login'
    __LOGIN_INPUT_ID = 'username'
    __PASSWORD_INPUT_ID = 'password'
    __LOGIN_SUBMIT_ID = 'kc-login'

    __SCHEDULE_URL = 'https://admin.itmo.ru/sport/schedule'
    __LESSON_TYPE_SPAN_XPATH = '//*[@id="__layout"]/div/div[1]/div/div[2]/div/div/div[1]/div/div[1]/div/div[2]/span'
    __LESSON_TYPE_SELECT_XPATH = '//*[@id="__layout"]/div/div[1]/div/div[2]/div/div/div[1]/div/div[1]/div/div[2]/input'

    __VISITINGS_CONTAINER_XPATH = '//*[@id="sidebar-lesson"]/div/div/div[2]'

    def __init__(self, week_day: int):
        super().__init__()
        self.__week_day = week_day  # TODO by date (may be on another week)

    # TODO by IU ID
    def fill_visitings(self, fio_list: list) -> None:
        self.__login()

        time.sleep(2)
        self._browser.get(self.__SCHEDULE_URL)
        self._get_web_element(By.XPATH, self.__LESSON_TYPE_SPAN_XPATH, delay=10).click()
        self._get_web_element(By.XPATH, self.__LESSON_TYPE_SELECT_XPATH).fill_dropdown_input('Online')

        self._wait_for_element(By.CLASS_NAME, 'sport-item')
        sport_items = self._browser.find_elements(By.CLASS_NAME, 'sport-item')
        sport_items[self.__week_day].click()

        visitings_container = self._get_web_element(By.XPATH, self.__VISITINGS_CONTAINER_XPATH, delay=10)
        student_items = visitings_container.element().find_elements(By.CLASS_NAME, 'b-overlay-wrap')

        print(len(student_items))

        self._browser.implicitly_wait(10)
        for student_item in student_items:
            isu_id, fio = student_item.text.split('\n')
            if fio in fio_list:
                input_label = student_item.find_element(By.TAG_NAME, 'label')
                """ don't know why, but need to move twice for 100% clicking """
                self._move_and_click(input_label)
                time.sleep(2)
                self._move_and_send(input_label)
                print(fio)
                time.sleep(2)

    def __login(self) -> None:
        self._browser.get(self.__LOGIN_URL)
        self._get_web_element(By.ID, self.__LOGIN_INPUT_ID, delay=10).fill_input(getenv('ADMIN_ITMO_LOGIN'))
        self._get_web_element(By.ID, self.__PASSWORD_INPUT_ID).fill_input(getenv('ADMIN_ITMO_PASSWORD'))
        self._get_web_element(By.ID, self.__LOGIN_SUBMIT_ID).submit_button()
