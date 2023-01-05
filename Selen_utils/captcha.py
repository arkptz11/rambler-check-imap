from seleniumwire import webdriver
import json
from loguru import logger as log
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


class Captcha:
    captcha_xpath = '//a[@class="status" and contains(.,"Solving is")]'
    @staticmethod
    def activate_anti_captcha(driver: webdriver.Chrome):
        for i in range(3):
            try:
                message = {
                    # всегда указывается именно этот получатель API сообщения
                    'receiver': 'antiCaptchaPlugin',
                    # тип запроса, например setOptions
                    'type': 'setOptions',
                    # мерджим с дополнительными данными
                    'options': {'antiCaptchaApiKey': 'e36b5b6d9bfc7b4ca2bba2e6c5fd0e38'}
                }
                # выполняем JS код на странице
                # а именно отправляем сообщение стандартным методом window.postMessage
                return driver.execute_script("""
                return window.postMessage({});
                """.format(json.dumps(message)))
            except Exception as e:
                pass
        return None

    @staticmethod
    def captcha_check(driver: webdriver.Chrome) -> bool:
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(lambda x: x.find_element(
                By.XPATH, '//a[@class="status" and contains(.,"Solving is")]'))
            log.success('Капчу увидел')
        except:
            return False
        while True:
            try:
                driver.find_element(
                    By.XPATH, '//a[@class="status" and contains(.,"Solving is")]')
            except:
                break
        try:
            WebDriverWait(driver, 5).until(lambda x: x.find_element(
                By.XPATH, '//a[@class="status" and .="Solved"]'))
            log.success('Капчу решил')
        except:
            return False
        return True
