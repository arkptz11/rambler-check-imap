import os
from csv_utils import Execute
from Selen_utils import data_cl
homeDir = (r'\\').join(os.path.abspath(__file__).split('\\')[:-1])


txt_file_ramblers = homeDir + '\\txt\\ramblers.txt'
name_csv_file = homeDir + '\\csv\\regs.csv'
csv_columns = ['data']

datas = Execute(name_file=txt_file_ramblers, name_csv_file=name_csv_file, list_columns=csv_columns, target_column='data', formater=data_cl)
csv = datas.csv