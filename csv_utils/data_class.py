from dataclasses import dataclass
from loguru import logger
import sys
import base64


@dataclass
class data_cl:
    string:str
    login:str=None
    password:str=None
    def __init__(self, string:str) -> None:
        self.string = string
        spl_string = string.split(':')
        lenght = ln = len(spl_string)
        if ln == 2:
            self.login,self.password = spl_string[:2]
        else:
            logger.error(f'Ошибка ввода данных: {string}')
            sys.exit()


class Statuses:
    error = 'Error'
    success = 'Success'
    nevalid = 'Невалид'
    left_captcha = 'Левая капча'