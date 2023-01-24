from Selen_utils import data_cl, Proxy_Class, Captcha, Flow, Statuses
from csv_utils import Execute, CsvCheck
import config as cf
import multiprocessing
from loguru import logger as log
import imaplib
import queue
from seleniumwire import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import ElementClickInterceptedException
from dataclasses import dataclass
import traceback
import os
import pandas as pd
from time import sleep, time
import random
import warnings
ua = UserAgent()
warnings.filterwarnings("ignore")
a_z = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
homeDir = (r'\\').join(os.path.abspath(__file__).split('\\')[:-1])

datas = cf.datas
csv = cf.csv


class Rambler(Flow):
    def go_setting(self):
        try:
            self.wait_click('//a[@data-list-view="settings"]')
        except ElementClickInterceptedException:
            for i in range(3):
                self.click_for_x_y(1542, 77)
                sleep(0.3)
            self.go_setting()

    def login_rambler(self):
        self.get_new('https://mail.rambler.ru/settings/mailapps')
        frame = self.driver.find_element(
            By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/iframe')
        cur = self.driver.current_window_handle
        self.driver.switch_to.frame(frame)
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
                return Statuses.nevalid
            ans = self.wait_2_elements('//a[@href="/settings/accounts"]',
                                       Captcha.captcha_xpath)
            if ans == 2:
                Captcha.captcha_check(self.driver)
                self.wait_click(
                    '//button[@data-cerber-id="login_form::main::login_button"]')
        except Exception as e:
            pass
        ans = self.check_frame_and_window(
            frame, '//div[@class="rui-FieldStatus-message"]', cur, '//a[@data-list-view="settings"]')
        if ans == 1:
            elem = self.driver.find_element(
                By.XPATH, '//div[@class="rui-FieldStatus-message"]').text
            if 'Неправильная почта' in elem:
                return Statuses.nevalid
            else:
                return Statuses.left_captcha
        self.driver.switch_to.window(cur)

    def switch_imap(self):
        self.go_setting()
        self.log_debug_with_lock(f'{self.data} -- go_setting')
        self.wait_click('//a[@href="/settings/mailapps"]')
        self.log_debug_with_lock(f'{self.data} -- mailapps')
        elem = self.wait_and_return_elem(
            '//button[contains(@class, "rui-ToggleOption-toggleOption") and @value="true"]', sleeps=5)
        self.log_debug_with_lock(f'{self.data} -- ищем элем вкл')
        val = elem.get_attribute('aria-pressed')
        if val == 'true':
            self.log_debug_with_lock(f'{self.data} -- imap уже включён')
            return True
        else:
            elem.click()
            self.log_debug_with_lock(f'{self.data} -- кликнули по элементу, ждём капчу')
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
            '//input[@class="rui-Input-input -metrika-nokeys" and @id="password"]')
        if not Captcha.captcha_check(self.driver):
            return False
        else:
            old_pass.send_keys(self.data.password)
            self.wait_send(
                '//input[@class="rui-Input-input -metrika-nokeys" and @id="newPassword"]', self.data.new_password)
            self.wait_click(
                '//button[@data-cerber-id="profile::change_password::save_password_button"]')
            sleep(5)
            return True

    def check_imap(self, log, pas):
        try:
            mail = imaplib.IMAP4_SSL('imap.rambler.ru')
            mail.login(log, pas)
            return True
        except Exception as e:
            return False

    def restart_driver(self):
        self.log_debug_with_lock(f'{self.data} -- restart_driver')
        self.close_driver()
        self.start_driver(
            anticaptcha_on=True, anticaptcha_path=f'{homeDir}\\files\\anticaptcha-plugin_v0.63.zip')
        self.activate_anti_captcha()

    def go(self,):
        self.log_debug_with_lock(f'Старт потока {self.data}')
        self.restart_driver()
        self.log_debug_with_lock('activate anti-captcha')
        for i in range(3):
            try:
                _login = self.login_rambler()
                if _login in [Statuses.nevalid, Statuses.left_captcha]:
                    return _login
                break
            except:
                self.log_error(desc='Ошибка во время логина')
                if i == 2:
                    return Statuses.error
                self.restart_driver()
        self.log_debug_with_lock(f'{self.data} -- login rambler')
        if self.data.on_off_imap:
            if self.check_imap(self.data.login, self.data.password):
                self.data.on_off_imap = 'Уже был включен'
            else:
                for i in range(3):
                    imap_on = self.switch_imap()
                    if imap_on:
                        sleep(5)
                        if self.check_imap(self.data.login, self.data.password):
                            log.success(f'{self.data} -- imap включён')
                            self.data.on_off_imap = Statuses.success
                            break
                        else:
                            self.data.on_off_imap = Statuses.error
                            imap_on = False

                    else:
                        self.get_new(
                            'https://mail.rambler.ru/folder/INBOX')
                        sleep(5)
                log.success(f'{self.data} -- end switch imap')
        if self.data.change_pass and self.check_imap(self.data.login, self.data.password):
            for i in range(3):
                change_pass = self.change_pass()
                if change_pass:
                    sleep(5)
                    if self.check_imap(self.data.login, self.data.new_password):
                        log.success(f'{self.data} -- пас поменяли')
                        self.data.change_pass = Statuses.success
                        break
                    else:
                        log.error(f'{self.data} -- Пас не сменился')
                        self.data.change_pass = Statuses.error
                        change_pass = False
                else:
                    self.get_new('https://mail.rambler.ru/settings/mailapps')
        return Statuses.success

    def start(self,):
        self.zapysk([self.go])


if __name__ == '__main__':
    proxy_q = queue.Queue()
    m = multiprocessing.Manager()
    Logs_to_excel = m.list()
    counter = multiprocessing.Value('i', 0)
    proxy_list = m.list()
    excel_file = CsvCheck(name_file=rf'{homeDir}\\result.xlsx', colums_check=[
                          'mail', 'pass', 'imap', 'result'], type_file='excel')
    excel_file.check_file()
    data_q = datas.get_queue()
    with open(f'{homeDir}\\txt\\proxy.txt') as file:
        for i in file.read().split('\n'):
            prox = Proxy_Class(i)
            proxy_list.append(prox)
    with open(f'{homeDir}\\stop.txt', 'w') as file:
        pass
    Lock = multiprocessing.Lock()
    threads_count = int(input(f"Сколько потоков требуется? - "))
    delay = input('Задержка(либо 1-2, либо 0) - ')
    flow = 0
    while True:
        while (not data_q.empty()):
            while len(multiprocessing.active_children())-1 >= threads_count:
                sleep(1)
            for i in range(threads_count-len(multiprocessing.active_children())+1):
                if (not data_q.empty()) and len(proxy_list) > 0:
                    with open(f'{homeDir}\\stop.txt', 'r') as file:
                        if 'true' in file.read():
                            continue
                    data = data_q.get()
                    proxx = random.choice(proxy_list)
                    # proxx.change_ip()
                    proxy_list.remove(proxx)
                    t = multiprocessing.Process(
                        target=Rambler(data, proxx, Lock, proxy_list, delay, csv=csv, count_accs=datas.count_args, count_make_accs=counter, excel_file=excel_file).start)
                    t.start()
                    flow += 1
        while len(multiprocessing.active_children()) != 1:
            sleep(1)
        break
