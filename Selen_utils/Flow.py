from .data_class import data_cl, Statuses
from .proxy import Proxy_Class
from .captcha import Captcha
from csv_utils import CsvCheck
from config import csv
import multiprocessing
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
from colorama import Fore
from loguru import logger
import os
import pandas as pd
from time import sleep, time
import random
import traceback
import warnings
ua = UserAgent()
warnings.filterwarnings("ignore")
a_z = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
homeDir = (r'\\').join(os.path.abspath(__file__).split('\\')[:-2])


@dataclass
class Flow:
    data: data_cl
    data_q: multiprocessing.Queue
    proxy: Proxy_Class
    Lock: multiprocessing.Lock
    proxy_list: list
    delay: str
    driver: webdriver.Chrome = None
    wait: WebDriverWait = None
    ip: str = None
    csv: CsvCheck = None
    count_accs: int = None
    count_make_accs: multiprocessing.Value = None
    excel_file: CsvCheck = None
    log:logger =None

    def start_driver(self, anticaptcha_on=False, anticaptcha_path=None, headless=False):
        self.activate_delay()
        # self.ads.creade_ads_profile(cookie=self.cookie)
        # self.driver = self.ads.connect_to_ads_selenium(self.ads.start_ads_profile())
        options_c = Options()
        options_c.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 1})
        options_c.add_argument(
            f'--proxy-server=http://{self.proxy.url_proxy}')
        options_c.add_argument(
            '--disable-blink-features=AutomationControlled')
        options = {'proxy':
                   {'http': f'http://{self.proxy.url_proxy}',
                    'http': f'https://{self.proxy.url_proxy}', }}
        options_c.add_argument(f"user-agent={ua.random}")
        if headless:
            options_c.add_argument("--headless")
        options_c.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        if anticaptcha_on:
            options_c.add_extension(
                anticaptcha_path)
        self.driver = webdriver.Chrome(
            options=options_c, seleniumwire_options=options, service_log_path='NUL')
        self.driver.set_window_size(1700, 1080)
        self.wait = WebDriverWait(self.driver, 30)
        if self.proxy.proxy_link:
            self.proxy.change_ip()
        self.ip = self.proxy.check_connection()
        self.log_debug_with_lock(self.ip)
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def activate_delay(self):
        d = self.delay
        if d == '0':
            return ''
        elif '-' in d:
            first, two = map(float, d.split('-'))
            sleep(random.randint(int(round(first*60, 0)), int(round(two*60, 0))))
        else:
            sleep(int(round(float(d)*60, 0)))

    def activate_anti_captcha(self,):
        self.get_new('https://httpbin.org/ip')
        Captcha.activate_anti_captcha(self.driver)

    def get_new(self, link):
        for num, i in enumerate(range(15)):
            try:
                self.driver.get(link)
                return True
            except Exception as e:
                self.log_debug_with_lock(
                    f'{self.data} -- get_new ({link}-- {traceback.format_exc()}')
            if num == 14:
                raise Exception

    def wait_2_elements(self, first_elem, second_elem) -> int:
        self.wait.until(EC.any_of(lambda x: x.find_element(
            By.XPATH, first_elem),
            lambda x: x.find_element(By.XPATH, second_elem)))
        try:
            self.driver.find_element(By.XPATH, first_elem)
            return 1
        except Exception as e:
            return 2

    def click_for_x_y(self, x, y):
        self.actions = ActionChains(self.driver)
        self.actions.move_by_offset(x, y).click().perform()
        self.actions.reset_actions()

    def close_driver(self):
        try:
            self.driver.quit()
        except:
            pass

    def check_frame_and_window(self, frame, frame_elem, window, window_elem, timeout=30):
        time_start = time()
        while time() - time_start < timeout:
            self.driver.switch_to.window(window)
            try:
                self.driver.switch_to.frame(frame)
                self.driver.find_element(By.XPATH, frame_elem)
                return 1
            except Exception as e:
                pass
            self.driver.switch_to.window(window)
            try:
                self.driver.find_element(By.XPATH, window_elem)
                return 2
            except Exception as e:
                pass
        raise

    def wait_3_elements(self, first_elem, second_elem, third_elem) -> int:
        self.wait.until(EC.any_of(lambda x: x.find_element(
            By.XPATH, first_elem),
            lambda x: x.find_element(By.XPATH, second_elem),
            lambda x: x.find_element(By.XPATH, third_elem)))
        try:
            self.driver.find_element(By.XPATH, first_elem)
            return 1
        except Exception as e:
            try:
                self.driver.find_element(By.XPATH, second_elem)
                return 2
            except Exception as e:
                return 3

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

    def log_debug_with_lock(self, text: str):
        self.Lock.acquire()
        self.log.debug(text)
        self.Lock.release()

    def wait_send(self, xpath, keys):
        self.wait.until(lambda x: x.find_element(By.XPATH, xpath))
        self.driver.find_element(By.XPATH, xpath).send_keys(keys)

    def log_error(self, desc=None):
        self.log_debug_with_lock(
            f'{self.data} -- {traceback.format_exc()}' + f' -- {desc}' if desc else '')

    def run(self, list_func, attempts=2):
        res = ''
        add_to_end = False
        for func in list_func:
            try:
                res = func()
            except Exception as e:
                res = Statuses.error
                self.log_debug_with_lock(
                    f'{self.data} -- {traceback.format_exc()}')
        if not self._check_valid_thread(res) and res != Statuses.nevalid:
            self.data_q.put(self.data)
            add_to_end = True
        if not self._check_valid_thread(res):
            if res == Statuses.success:
                return 'Error'
        return res, add_to_end

    def _check_valid_thread(self, res):
        if res != Statuses.success or self.data.change_pass == Statuses.error or self.data.on_off_imap == Statuses.error:
            return False
        return True

    def zapysk(self, list_func):
        res, add_to_end = self.run(list_func)
        self.count_make_accs.value += 1
        dop_txt = (' -- Перенос в конец очереди' if add_to_end else '')
        txt = f'{self.count_make_accs.value}/{self.count_accs}' + dop_txt
        if not self._check_valid_thread(res):
            print(Fore.RED + txt)
            self.log_debug_with_lock(f'{txt}')
            try:
                self.driver.save_screenshot(
                    f'{homeDir}\\Screenshots_error\\{self.data.login}.png')
            except Exception as e:
                self.log_debug_with_lock(
                    f'{self.data} -- {traceback.format_exc()}')
                pass
        else:
            print(Fore.GREEN + txt)
        self.close_driver()
        self.proxy_list.append(self.proxy)
        _data = {'mail': self.data.string, 'result': f'{res}{dop_txt}'}
        if self.data.on_off_imap:
            _data['imap'] = self.data.on_off_imap
        if self.data.change_pass:
            _data['pass'] = self.data.change_pass
        self.excel_file.add_string(_data)
        if not add_to_end:
            self.csv.add_string({'data': f'{self.data.string}'})
