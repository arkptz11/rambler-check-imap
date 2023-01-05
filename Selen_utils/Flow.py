from .data_class import data_cl
from .proxy import Proxy_Class
from .captcha import Captcha
from config import csv
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
homeDir = (r'\\').join(os.path.abspath(__file__).split('\\')[:-2])


@dataclass
class Flow:
    data: data_cl
    proxy: Proxy_Class
    Lock: multiprocessing.Lock
    proxy_list: list
    delay: str
    driver: webdriver.Chrome = None
    wait: WebDriverWait = None
    ip: str = None

    def start_driver(self, anticaptcha_on=False, anticaptcha_path=None):
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
        if anticaptcha_on:
            options_c.add_extension(
                anticaptcha_path)
        self.driver = webdriver.Chrome(
            options=options_c, seleniumwire_options=options)
        self.driver.set_window_size(1700, 1080)
        self.wait = WebDriverWait(self.driver, 30)
        self.proxy.change_ip()
        self.ip = self.proxy.check_connection()
        log.success(self.ip)
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def activate_delay(self):
        d = self.delay
        if d == '0':
            return ''
        elif '-' in d:
            first, two = map(float, d.split('-'))
            sleep(random.randint(int(round(first*60,0)), int(round(two*60,0))))
        else:
            sleep(int(round(float(d)*60,0)))

    def activate_anti_captcha(self,):
        self.get_new('https://httpbin.org/ip')
        Captcha.activate_anti_captcha(self.driver)

    def get_new(self, link):
        for num, i in enumerate(range(15)):
            try:
                self.driver.get(link)
                return True
            except Exception as e:
                log.debug(f'get_new -- {e}')
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

    def zapysk(self, list_func):
        res = ''
        for func in list_func:
            try:
                res = func()
            except Exception as e:
                res = "Error"
                log.debug(e)
                break
            if res != 'Success':
                break
        # self.Logs_to_excel.append({'seed': self.seed,
        # 'result':res})
        if res != 'Success':
            # logger.error(f'{self.counter.value}/{self.all_seeds}')
            self.driver.save_screenshot(
                f'{homeDir}\\Screenshots_error\\{self.data.login}.png')
        for _ in range(100):
            try:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.close()
            except:
                break
                pass
        self.proxy_list.append(self.proxy)
        self.Lock.acquire()
        df = pd.read_excel(rf'{homeDir}\\result.xlsx', index_col=0)
        _data = {'mail': self.data.string, 'result': res}

        if self.data.on_off_imap:
            _data['imap'] = self.data.on_off_imap
        if self.data.change_pass:
            _data['pass'] = self.data.change_pass
        df = df.append(_data, ignore_index=True)
        df.to_excel(rf'{homeDir}\\result.xlsx')
        self.Lock.release()
        csv.add_string({'data': f'{self.data.string}'})
        csv.save_csv()
