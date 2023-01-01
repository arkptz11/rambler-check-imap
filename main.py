# -*- coding: utf-8 -*-
import json
import traceback
import imaplib
from seleniumwire import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
import sys
import requests
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from loguru import logger
import os
import threading
import queue
import pandas as pd
from time import sleep, time
import random
import multiprocessing
from Utility.proxy import Proxy_Class
from Utility.data_class import data_cl
import warnings
ua = UserAgent()
warnings.filterwarnings("ignore")
a_z = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
homeDir = (r'\\').join(os.path.abspath(__file__).split('\\')[:-1])


class Flow_to_work():
    def __init__(self, proxy: Proxy_Class, delay_: str, Lock: multiprocessing.Lock, proxy_list: list, Logs_to_excel: list, delays: str, data: data_cl, counter, all_seeds) -> None:
        self.ip = None
        self.data = data
        self.proxy = proxy
        self.delay = delay_
        self.Lock = Lock
        self.proxy_list = proxy_list
        self.Logs_to_excel = Logs_to_excel
        self.delays = delays
        self.counter, self.all_seeds = counter, all_seeds
        try:
            # self.ads = ads(self.proxy, Lock)
            self.start_driver()
            self.zapysk()
            # self.ads.del_ads_id()
        except:
            try:
                self.Lock.release()
            except:
                pass
            print(traceback.format_exc())

    def zapysk(self):
        list_func = []
        list_func = [self.go, ]
        res = ''
        for func in list_func:
            try:
                res = func()
            except:
                res = "Ошибка"
                print(traceback.format_exc())
                break
            if res != 'Успешно':
                break
        # self.Logs_to_excel.append({'seed': self.seed,
        # 'result':res})
        if res != 'Успешно':
            self.counter.value += 1
            # logger.error(f'{self.counter.value}/{self.all_seeds}')
            self.driver.save_screenshot(
                f'{homeDir}\\Screenshots_error\\{self.data.login}.png')
        else:
            self.counter.value += 1
            # logger.success(f'{self.counter.value}/{self.all_seeds}')
        try:
            self.driver.close()
        except:
            pass
        for i in range(100):
            try:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.close()
            except:
                break
                pass
        self.proxy_list.append(self.proxy)
        self.Lock.acquire()
        df = pd.read_excel(rf'{homeDir}\\result.xlsx', index_col=0)
        _data = {'mail': self.data.string, 'ip': self.ip, }
        if self.data.on_off_imap:
            _data['imap'] = self.data.on_off_imap
        if self.data.change_pass:
            _data['pass'] = self.data.change_pass
        df = df.append(_data, ignore_index=True)
        df.to_excel(rf'{homeDir}\\result.xlsx')
        df = pd.read_csv(rf'{homeDir}\\csv\\success_regs.csv', index_col=0)
        df = df.append({'data': f'{self.data.string}'}, ignore_index=True)
        df.to_csv(rf'{homeDir}\\csv\\success_regs.csv')
        self.Lock.release()

    def start_driver(self):
        # self.ads.creade_ads_profile(cookie=self.cookie)
        # self.driver = self.ads.connect_to_ads_selenium(self.ads.start_ads_profile())
        options_c = Options()
        options_c.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 1})
        options_c.add_argument(f'--proxy-server=http://{self.proxy.url_proxy}')
        options_c.add_argument('--disable-blink-features=AutomationControlled')
        options = {'proxy':
                   {'http': f'http://{self.proxy.url_proxy}',
                    'http': f'https://{self.proxy.url_proxy}', }}
        options_c.add_argument(f"user-agent={ua.random}")
        options_c.add_extension(
            f'{homeDir}/Utility/anticaptcha-plugin_v0.63.zip')
        self.driver = webdriver.Chrome(
            options=options_c, seleniumwire_options=options)
        self.driver.set_window_size(1700, 1080)
        self.wait = WebDriverWait(self.driver, 30)
        sl = 0
        if self.delay:
            if self.delays == "0":
                sl = 0
            else:
                sl = random.randint(int(self.delays.split(
                    '-')[0])*60, int(self.delays.split('-')[1]) * 60)
            sleep(sl)
        self.proxy.change_ip()
        self.ip = self.proxy.check_connection()
        logger.success(self.ip)
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def login_rambler(self):
        self.get_new('https://mail.rambler.ru/')
        cur = self.driver.current_window_handle
        frame_path = '/html/body/div[1]/div/div[2]/div[2]/iframe'
        self.wait.until(lambda x: x.find_element(By.XPATH, frame_path))
        frame = self.driver.find_element(By.XPATH, frame_path)
        self.driver.switch_to.frame(frame)

        self.wait_send(
            '//input[@class="rui-Input-input -motrika-nokeys"]', self.data.login)
        self.wait_send(
            '//input[@class="rui-Input-input -metrika-nokeys"]', self.data.password)
        self.wait_click(
            '//button[@class="rui-Button-button rui-Button-type-primary rui-Button-size-medium rui-Button-iconPosition-left rui-Button-block"]')
        try:
            self.wait.until(lambda x: x.find_element(
                By.XPATH, '//iframe[@data-hcaptcha-widget-id]'))
            self.captcha_check()
            self.wait_click(
                '//button[@class="rui-Button-button rui-Button-type-primary rui-Button-size-medium rui-Button-iconPosition-left rui-Button-block"]')
        except:
            pass
        self.driver.switch_to.window(cur)
        self.wait.until(lambda x: x.find_element(
            By.XPATH, '//button[@data-cerber="topline::mail::user::menu_open"]'))
        sleep(5)

    def acp_api_send_request(self, message_type, data={}):
        message = {
            # всегда указывается именно этот получатель API сообщения
            'receiver': 'antiCaptchaPlugin',
            # тип запроса, например setOptions
            'type': message_type,
            # мерджим с дополнительными данными
            **data
        }
        # выполняем JS код на странице
        # а именно отправляем сообщение стандартным методом window.postMessage
        return self.driver.execute_script("""
        return window.postMessage({});
        """.format(json.dumps(message)))

    def activate_anti_captcha(self):
        self.get_new('https://httpbin.org/ip')
        for i in range(3):
            self.acp_api_send_request(
                'setOptions',
                {'options': {'antiCaptchaApiKey': 'e36b5b6d9bfc7b4ca2bba2e6c5fd0e38'}}
            )

    def go_setting(self):
        self.wait_click('//a[@data-list-view="settings"]')

    def captcha_check(self, xpath_check=False):
        xpath_change_pass = '/html/body/div[4]/div/div/div/form/section[4]/div/div/div/div/div/div/a[1]'
        if not xpath_check:
            try:
                self.wait.until(lambda x: x.find_element(
                    By.XPATH, '//a[@class="status" and contains(.,"Solving is")]'))
                logger.success('Капчу увидел')
            except:
                return False
            while True:
                try:
                    self.driver.find_element(
                        By.XPATH, '//a[@class="status" and contains(.,"Solving is")]')
                except:
                    break
            try:
                WebDriverWait(self.driver, 5).until(lambda x: x.find_element(
                    By.XPATH, '//a[@class="status" and .="Solved"]'))
                logger.success('Капчу решил')
            except:
                return False
            return True
        else:
            try:
                self.wait.until(lambda x: x.find_element(
                    By.XPATH, xpath_change_pass))
                logger.success('Капчу увидел')
            except:
                # traceback.print_exc()
                return False
            while True:
                try:
                    elem = self.driver.find_element(
                        By.XPATH, xpath_change_pass)
                    assert "Solving is" in elem.text
                except:
                    break
            for i in range(5):
                try:
                    elem = self.driver.find_element(
                        By.XPATH, xpath_change_pass)
                    assert "Solved" in elem.text
                except:
                    sleep(1)
                    if i == 4:
                        return False
            return True

    def switch_imap(self):
        self.go_setting()
        self.wait_click('//a[@href="/settings/mailapps"]')
        elem = self.wait_and_return_elem(
            '//button[contains(@class, "rui-ToggleOption-toggleOption") and @value="true"]', sleeps=5)
        val = elem.get_attribute('aria-pressed')
        print(elem.get_attribute('value'), val)
        if val == 'true':
            return True
        else:
            elem.click()
            if not self.captcha_check():
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
        if not self.captcha_check():
            return False
        else:
            old_pass.send_keys(self.data.password)
            self.wait_send(
                '/html/body/div[4]/div/div/div/form/section[3]/div/div/div[1]/input', self.data.new_password)
            self.wait_click(
                '/html/body/div[4]/div/div/div/form/footer/button[1]')
            sleep(2)
            return True

    def go(self):

        try:
            self.activate_anti_captcha()
            self.login_rambler()
            if self.data.on_off_imap:
                try:
                    mail = imaplib.IMAP4_SSL('imap.rambler.ru')
                    mail.login(self.data.login, self.data.password)
                    self.data.on_off_imap = 'Уже был включен'
                except:
                    for i in range(3):
                        imap_on = self.switch_imap()
                        if imap_on:
                            try:
                                sleep(5)
                                mail = imaplib.IMAP4_SSL('imap.rambler.ru')
                                mail.login(self.data.login, self.data.password)
                                logger.success('imap включён')
                                self.data.on_off_imap = 'Успешно'
                                break
                            except:
                                self.data.on_off_imap = 'Ошибка'
                                imap_on = False

                        if not imap_on:
                            self.get_new(
                                'https://mail.rambler.ru/folder/INBOX')
                            sleep(10)
                    logger.success('end')
            if self.data.change_pass:
                for i in range(3):
                    change_pass = self.change_pass()
                    if change_pass:
                        try:
                            sleep(5)
                            mail = imaplib.IMAP4_SSL('imap.rambler.ru')
                            mail.login(self.data.login, self.data.new_password)
                            logger.success('пас поменяли')
                            self.data.change_pass = 'Успешно'
                            break
                        except:
                            logger.error('Пас не сменился')
                            self.data.change_pass = 'Ошибка'
                            # traceback.print_exc()
                            change_pass = False
        except:
            return 'Ошибка'
        return 'Успешно'

    def get_new(self, link):
        c = 0
        start_time = time()
        while True:
            if time() - start_time:
                raise
            c += 1
            try:
                self.driver.get(link)
                break
            except:
                if c > 10:
                    c = 0
                    print(traceback.format_exc(), f"\n\n{link}")
                    pass

    def wait_and_return_elem(self, xpath, sec=30, sleeps=None):
        self.wait = WebDriverWait(self.driver, sec)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        if sleeps:
            sleep(sleeps)
        return self.driver.find_element(By.XPATH, xpath)

    def wait_click(self, xpath, sleeps=None, sec=30):
        self.wait = WebDriverWait(self.driver, sec)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        if sleeps:
            sleep(sleeps)
        self.driver.find_element(By.XPATH, xpath).click()
        self.wait = WebDriverWait(self.driver, 30)

    def wait_send(self, xpath, keys):
        self.wait.until(lambda x: x.find_element(By.XPATH, xpath))
        self.driver.find_element(By.XPATH, xpath).send_keys(keys)


if __name__ == '__main__':
    regs_queue = queue.Queue()
    seeds = multiprocessing.Queue()
    proxy_q = queue.Queue()
    m = multiprocessing.Manager()
    Logs_to_excel = m.list()
    counter = multiprocessing.Value('i', 0)
    proxy_list = m.list()
    all_seeds = 0
    try:
        df = pd.read_excel(rf'{homeDir}\\result.xlsx', index_col=0)
    except:
        df = pd.DataFrame(columns=['mail', 'ip', 'pass', 'imap'])
        df.to_excel(rf'{homeDir}\\result.xlsx')
    with open(rf'{homeDir}\\txt\\ramblers.txt', 'r') as file:
        df = pd.read_csv(rf'{homeDir}\\csv\\success_regs.csv', index_col=0)[
            'data'].to_list()
        seeds_imp = file.read().split('\n')
        for data in seeds_imp:
            if not (data in df) and data != '' and data != '\n':
                regs_queue.put(data_cl(data))
    with open(f'{homeDir}\\txt\\proxy.txt') as file:
        for i in file.read().split('\n'):
            prox = Proxy_Class(i)
            proxy_list.append(prox)
    with open(f'{homeDir}\\stop.txt', 'w') as file:
        pass
    Lock = multiprocessing.Lock()
    threads_count = int(input(f"Сколько потоков требуется?"))
    delays = input('Задержка(либо 1-2, либо 0)')
    flow = 0
    delay = False
    while True:
        while (not regs_queue.empty()):
            while len(multiprocessing.active_children())-1 >= threads_count:
                sleep(1)
            for i in range(threads_count-len(multiprocessing.active_children())+1):
                if (not regs_queue.empty()):
                    with open(f'{homeDir}\\stop.txt', 'r') as file:
                        if 'true' in file.read():
                            continue
                    data = regs_queue.get()
                    proxx = random.choice(proxy_list)
                    # proxx.change_ip()
                    proxy_list.remove(proxx)
                    t = multiprocessing.Process(target=Flow_to_work, args=[
                                                proxx, delay, Lock, proxy_list, Logs_to_excel, delays, data, counter, all_seeds])
                    t.start()
                    flow += 1
        while len(multiprocessing.active_children()) != 1:
            sleep(1)
        break
