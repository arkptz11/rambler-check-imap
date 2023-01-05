import logging
import requests
from dataclasses import dataclass
from requests.auth import HTTPProxyAuth
from time import sleep
from loguru import logger as log


@dataclass(repr=True)
class Proxy_Class:
    ip: str
    port: str
    login: str
    password: str
    proxy_link: str

    def __init__(self, proxy: str, logging: str = False) -> None:
        self.ip, self.port, self.login, self.password, self.proxy_link = self.proxy_reorganize(
            proxy)
        self.list_data = [self.ip, self.port,
                          self.login, self.password, self.proxy_link]
        self.proxy_default_format = f'{self.ip}:{self.port}:{self.login}:{self.password}'
        self.proxy_default_format_with_url = f'{self.ip}:{self.port}:{self.login}:{self.password}|{self.proxy_link}'
        self.url_proxy = f'{self.login}:{self.password}@{self.ip}:{self.port}'
        self.logging = logging

    def proxy_reorganize(self, proxy: str) -> list[str] or None:
        if proxy == None:
            return None, None, None, None, None
        if '|' in proxy:
            proxy, proxy_link = proxy.split('|')
            proxy_link = proxy_link.replace(
                'http://', '').replace('https://', '')
        else:
            proxy_link = None
        if "http" in proxy:
            proxy = proxy.replace('http://', '').replace('https://', '')
        if '@' in proxy:
            log_pas, ip_port = proxy.split('@')
            login, password = log_pas.split(':')
            ip, port = ip_port.split(':')
        else:
            ip, port, login, password = proxy.split(':')
        return ip, port, login, password, proxy_link

    def change_ip(self, only_check_inet=False):
        s = self.get_session()
        if not only_check_inet:
            s.get('http://' + self.proxy_link)
            sleep(3)
        for cycle_index in range(10):
            if cycle_index == 10:
                raise Exception('Proxy connection error')

            try:
                response = s.get(url='https://httpbin.org/ip', timeout=5)
                if self.logging:
                    log.success(
                        f'{self.logging}Новый айпи - {response.json()["origin"]}')
                if response.status_code == 200:
                    return True
            except requests.ConnectionError as ex:
                log.debug(f'{s.proxies} \n {ex}')

            sleep(2)
        return False

    def check_connection(self):
        s = self.get_session()
        for i in range(3):
            try:
                return s.get('https://httpbin.org/ip').json()['origin']
            except:
                sleep(5)
        return None

    def get_session(self):
        ip, port, log, pas, proxy_link = self.list_data
        auth = HTTPProxyAuth(log, pas)
        s = requests.Session()
        s.proxies = {'https': f'http://{self.url_proxy}',
                     'http': f'http://{self.url_proxy}'}
        s.auth = auth
        return s
