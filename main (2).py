from Selen_utils import data_cl, Proxy_Class, Captcha, Flow
import multiprocessing
from loguru import logger as log
from seleniumwire import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from dataclasses import dataclass

import os
import pandas as pd
from time import sleep, time
import random
import warnings
ua = UserAgent()
warnings.filterwarnings("ignore")
a_z = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
homeDir = (r'\\').join(os.path.abspath(__file__).split('\\')[:-1])


class Rambler(Flow):
    def go_setting(self):
        self.wait_click('//a[@data-list-view="settings"]')

    def login_rambler(self):
        self.get_new('https://id.rambler.ru/account/change-password')
        self.wait_send(
            '//input[@class="rui-Input-input -motrika-nokeys"]', self.data.login)
        self.wait_send(
            '//input[@class="rui-Input-input -metrika-nokeys"]', self.data.password)
        self.wait_click(
            '//button[@data-cerber-id="login_form::main::login_button"]')
        try:
            ans = self.wait_2_elements(
                '//iframe[@data-hcaptcha-widget-id]', '//div[@class="rui-FieldStatus-message"]')
            if ans == 2:
                return 'Невалид'
            ans = self.wait_2_elements('//button[@class="rui-Button-button rui-Button-type-primary rui-Button-size-medium rui-Button-iconPosition-left rui-Button-block"]',
                                       Captcha.captcha_xpath)
            if ans == 2:
                Captcha.captcha_check(self.driver)
            self.wait_click(
                '//button[@data-cerber-id="login_form::main::login_button"]')
        except:
            pass
        sleep(5)

    def switch_imap(self):
        self.go_setting()
        self.wait_click('//a[@href="/settings/mailapps"]')
        elem = self.wait_and_return_elem(
            '//button[contains(@class, "rui-ToggleOption-toggleOption") and @value="true"]', sleeps=5)
        val = elem.get_attribute('aria-pressed')
        if val == 'true':
            return True
        else:
            elem.click()
            if not Captcha.captcha_check(self.driver):
                return False
            else:
                self.wait_click(
                    '//button[@class="rui-Button-button rui-Button-type-primary rui-Button-size-small rui-Button-iconPosition-left MailAppsChange-submitButton-S7"]', sleeps=3)  # отправить
                return True

    def change_pass(self):
        self.get_new(
            'https://id.rambler.ru/account/change-password?back=https://mail.rambler.ru/settings/security')
        old_pass = self.wait_and_return_elem(
            '/html/body/div[4]/div/div/div/form/section[2]/div/div/div[1]/input')
        if not Captcha.captcha_check(self.driver):
            return False
        else:
            old_pass.send_keys(self.data.password)
            self.wait_send(
                '/html/body/div[4]/div/div/div/form/section[3]/div/div/div[1]/input', self.data.new_password)
            self.wait_click(
                '/html/body/div[4]/div/div/div/form/footer/button[1]')
            sleep(2)
            return True
Rambler(data_cl('2:2'), Proxy_Class('ro.dc.smartproxy.com:20001:user-sp34092641:123456789xXxX|google.com'), multiprocessing.Lock(), []).start_driver(anticaptcha_on=True)
sleep(10000)