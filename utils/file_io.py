import os
import openpyxl
import pandas as pd

def data_path():
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../data/')
    return data_path

#def read_xlsx(file = os.path.join(data_path, 'bento.xlsx')):
def read_xlsx(file = '../data/machine_assistance/bento.xlsx'):
    spreadsheet = pd.read_excel(open(file, 'rb'), sheetname = 0)
    return spreadsheet

#def write_xlsx(final_df, file = os.path.join(data_path, 'output.xlsx')):
def write_xlsx(final_df, file = '../data/output.xlsx', sheet = 'Sheet1'):
    if os.path.isfile(file):
        book = openpyxl.load_workbook(file)
        writer = pd.ExcelWriter(file, engine = 'openpyxl')
        writer.book = book
        final_df.to_excel(writer, sheet_name = sheet)
        writer.save()
    else:
        writer = pd.ExcelWriter(file, engine = 'openpyxl')
        final_df.to_excel(writer, sheet_name = sheet)
        writer.save()

    writer.close
