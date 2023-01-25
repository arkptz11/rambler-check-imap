from dataclasses import dataclass
import queue
from typing import Callable
import pandas as pd
import multiprocessing
from .decorators import true_false


@dataclass(repr=True)
class CsvCheck:
    name_file: str
    colums_check: list[str]
    Lock: multiprocessing.Lock = multiprocessing.Lock()
    df: pd.DataFrame = pd.DataFrame()
    type_file: str = 'csv'

    def _read_file(self):
        if self.type_file == 'csv':
            self.df = pd.read_csv(self.name_file, index_col=0)
        elif self.type_file == 'excel':
            self.df = pd.read_excel(self.name_file, index_col=0)

    @true_false
    def _check_file(self, need_lock=True) -> bool:
        if need_lock:
            self.Lock.acquire()
        self._read_file()
        if need_lock:
            self.Lock.release()

    @true_false
    def _check_columns(self) -> bool:
        for i in self.colums_check:
            if not i in self.df.columns:
                raise
        if len(self.colums_check) != len(self.df.columns):
            raise

    def _unlock(self):
        try:
            self.Lock.release()
        except:
            pass

    def check_file(self, need_lock=True):
        if not self._check_file(need_lock=need_lock) or (not self._check_columns()):
            self.create_file()

    def create_file(self):
        self.df = pd.DataFrame(columns=self.colums_check)
        self._unlock()
        self.save_file()


    def save_file(self, need_lock=True):
        if need_lock:
            self.Lock.acquire()
            print('//')
        if self.type_file == 'csv':
            self.df.to_csv(self.name_file)
        elif self.type_file == 'excel':
            self.df.to_excel(self.name_file)
        if need_lock:
            self.Lock.release()

    def add_string(self, data):
        self.Lock.acquire()
        self.check_file(need_lock=False)
        self.df = self.df.append(data, ignore_index=True)
        self.save_file(need_lock=False)
        self.Lock.release()


@dataclass(repr=True)
class Execute:
    name_file: str
    name_csv_file: str
    target_column: str
    count_args: int = 0

    def __init__(self, name_file: str,
                 name_csv_file: str, list_columns: list, target_column: str, formater=None) -> None:
        self.name_file, self.name_csv_file, self.list_columns, self.target_column = name_file, name_csv_file, list_columns, target_column
        self.formater = formater
        self.csv = CsvCheck(name_file=self.name_csv_file,
                            colums_check=self.list_columns, Lock=multiprocessing.Lock())
        self.csv.check_file()

    def get_queue(self) -> multiprocessing.Queue:
        counter = 0
        q = multiprocessing.Queue()
        with open(self.name_file, 'r', encoding='utf-8') as file:
            data = file.read().split('\n')
            data = self.clear_empty_line(data=data)
        da = self.get_list_on_df()
        for element in data:
            if not element in da:
                counter += 1
                if self.formater:
                    element = self.formater(element)
                q.put(element)
        self.count_args = counter
        return q

    def get_list_on_df(self) -> pd.DataFrame:
        self.csv.check_file()
        df = self.csv.df
        return df[self.target_column].to_list()

    @staticmethod
    def clear_empty_line(data: list) -> list:
        for line in data:
            if line in ['', ' ', '\n']:
                data.remove(line)
        return data
