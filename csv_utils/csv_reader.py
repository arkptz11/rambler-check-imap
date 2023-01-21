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
    Lock: multiprocessing.Lock
    df: pd.DataFrame = pd.DataFrame()

    @true_false
    def _check_csv_file(self) -> bool:
        self.Lock.acquire()
        self.df = pd.read_csv(self.name_file, index_col=0)
        self.Lock.release()

    @true_false
    def _check_columns(self) -> bool:
        for i in self.colums_check:
            if not i in self.df.columns:
                raise
        if len(self.colums_check) != len(self.df.columns):
            raise

    def check_csv(self):
        if not self._check_csv_file() or (not self._check_columns()):
            self.create_csv()

    def create_csv(self):
        self.df = pd.DataFrame(columns=self.colums_check)
        self.df.to_csv(self.name_file)

    def update_df(self):
        self.check_csv()

    def save_csv(self):
        self.Lock.acquire()
        self.df.to_csv(self.name_file)
        self.Lock.release()

    def add_string(self, data):
        self.update_df()
        self.Lock.acquire()
        self.df = self.df.append(data, ignore_index=True)
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
        self.csv.check_csv()

    def get_queue(self) -> multiprocessing.Queue:
        counter = 0
        q = queue.Queue()
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
        self.csv.check_csv()
        df = self.csv.df
        return df[self.target_column].to_list()

    @staticmethod
    def clear_empty_line(data: list) -> list:
        for line in data:
            if line in ['', ' ', '\n']:
                data.remove(line)
        return data
