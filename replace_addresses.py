#!/usr/bin/env python3

import logging, sys

import tablib

from address_regexp import clean_address

ADDRESS_COL_TITLE = 'Місце проживання (для фіз. осіб)/Юридична адреса (для юр. осіб)'

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s', filename='log.txt')
log = logging.getLogger(__name__)

def open_file(file):
    '''
    імпорт файлу у форматі датасету
    '''
    imported_file = tablib.Dataset().load(open(file).read())
    return imported_file


def substitution(imported_file):
    '''
    '''
    col_index = imported_file.headers.index(ADDRESS_COL_TITLE)

    # створюємо новий датасет, додаємо в нього заголовки з імпортованого файла
    new_data = tablib.Dataset()
    new_data.headers = imported_file.headers

    # по рядку опрацьовуємо імпортований файл
    for row_index in range(imported_file.height):
        row = list(imported_file[row_index])
        row[col_index] = clean_address(row[col_index])
        new_data.append(row)

    return new_data



def write_file(tmp, substituted_file):
    '''
    запис датасету в csv-файл
    '''
    with open(tmp, 'w') as f:
        f.write(substituted_file.export('csv'))

if __name__ == "__main__":
    filename = sys.argv[1]

    log.info('Перевірка {}'.format(filename))
    imported_file = open_file(filename)
    substituted_file = substitution(imported_file)

    log.info('Запис {}'.format(filename))
    write_file(filename, substituted_file)
