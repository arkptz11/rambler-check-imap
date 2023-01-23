from dataclasses import dataclass
from loguru import logger
import sys
import base64


@dataclass
class data_cl:
    string:str
    login:str=None
    password:str=None
    new_password:str=None
    change_pass:bool = False
    on_off_imap:bool = False
    def __init__(self, string:str) -> None:
        self.string = string
        spl_string = string.split(':')
        count_true_false = ctf=  string.count('true')
        lenght = ln = len(spl_string)
        if ln == 2 +ctf:
            self.login,self.password = spl_string[:2]
            if ctf ==1:
                self.on_off_imap = True
        elif ln == 3 +ctf:
            self.login, self.password,self.new_password  = spl_string[:3]
            self.change_pass = True
            if ctf == 1:
                self.on_off_imap = True
        else:
            logger.error(f'Ошибка ввода данных: {string}')
            sys.exit()


class Statuses:
    error = 'Error'
    success = 'Success'
    nevalid = 'Невалид'
    left_captcha = 'Левая капча'