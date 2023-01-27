from csv_utils import Execute, CsvCheck, data_cl, Statuses
import config as cf
import multiprocessing
from loguru import logger as log
import imaplib
import queue
import loguru_settings
from colorama import Fore
from dataclasses import dataclass
import traceback
import os
import pandas as pd
from time import sleep, time
import random
import warnings
warnings.filterwarnings("ignore")
a_z = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
homeDir = (r'\\').join(os.path.abspath(__file__).split('\\')[:-1])

datas = cf.datas
@dataclass
class Rambler():
    data_q: multiprocessing.Queue
    counter: multiprocessing.Value
    full:int
    lock: multiprocessing.Lock
    excel_file: CsvCheck
    csv: CsvCheck
    def check_imap(self):
        try:
            mail = imaplib.IMAP4_SSL('imap.rambler.ru')
            mail.login(self.data.login, self.data.password)
            return True
        except Exception as e:
            log.debug(f'{self.data} -- {traceback.format_exc()}')
            return False

    def start(self):
        while not self.data_q.empty():
            self.data: data_cl = self.data_q.get()
            rs = self.check_imap()
            res = Statuses.success if rs else Statuses.error
            color = Fore.GREEN if res else Fore.RED
            self.lock.acquire()
            self.counter.value += 1
            print(color + f'{self.counter.value}/{self.full}')
            self.lock.release()
            self.excel_file.add_string(
                {'mail': self.data.login, 'pass': self.data.password, 'result': res})
            self.csv.add_string({'data': self.data.string})


if __name__ == '__main__':
    counter = multiprocessing.Value('i', 0)
    counter_make_accs = multiprocessing.Value('i', 0)
    excel_file = CsvCheck(name_file=rf'{homeDir}\\result.xlsx', colums_check=[
                          'mail', 'pass', 'result'], type_file='excel')
    excel_file.check_file()
    data_q = datas.get_queue()
    Lock = multiprocessing.Lock()
    threads_count = int(input(f"Сколько потоков требуется? - "))
    flow = 0
    for i in range(threads_count):
        if (not data_q.empty()):
            # proxx.change_ip()
            t = multiprocessing.Process(
                target=Rambler(data_q, counter, datas.count_args, Lock, excel_file, cf.csv).start)
            t.start()
            flow += 1
        while len(multiprocessing.active_children()) != 1:
            sleep(1)
