import re

from collections import OrderedDict
from functools import lru_cache, partial


icompile = partial(re.compile, flags=re.IGNORECASE)

LSTRIP_CHARS = ' \t,-.'
RSTRIP_CHARS = ' \t,-'

PUNCTUATION_FIX = (
    re.compile(r'\s*([,.])\s*([Є-ЯҐа-їґ0-9])'),
    r'\1 \2'
)
REPEATING_PUNCTUATION_FIX = (
    re.compile(r'(\s?)([\s.,])\2+'),
    r'\2'
)
VOIDS_REMOVAL = (
    re.compile(r'(([,]+)([\s\.,]){2,})'),
    r'\2 '
)

REPLACEMENTS = (
    REPEATING_PUNCTUATION_FIX,
    PUNCTUATION_FIX,
    REPEATING_PUNCTUATION_FIX,  # TODO: спробувати оптимізувати
    (icompile(r'\bУкраїна\b'), ''),
    (icompile(r'\b\d{5}\b'), ''),  # поштовий індекс
    VOIDS_REMOVAL,
    (re.compile(  # заміна апострофів
        r'([Є-ЯҐа-їґ])([\'`’])([Є-ЯҐа-їґ])'),
        r'\1ʼ\3'),
    (icompile(r'\b(о6л|оОл|о бл)\b'), r'обл'),
    (icompile(r'\b(в\\л)\b'), r'вул'),
    (icompile(r'\b(р\-?нс)\b'), r'р-н, с'),
    (re.compile(r'\b(Оуд)\b'), r'буд'),
    (re.compile(r'([Є-ЯҐа-їґ])([0-9])'), r'\1 \2'),  # цифра одразу за буквою
    (  # НовоплатонівкаСадова
        re.compile(r'([а-їґ])([Є-ЯҐ][а-їґ])'),
        r'\1 \2'),
    (icompile(r'\bвулиця\b'), r'вул.'),
    (icompile(r'\bпровулок\b'), r'пров.'),
    (icompile(r'\bбульвар\b'), r'бульв.'),
    (icompile(r'\bпроспект\b'), r'просп.'),
    (icompile(r'\bвул\b\.?(,?)'), r'вул.\1'),
    (re.compile(r'\b(вул\.),(\s+[Є-ЯҐ])'), r'\1\2'),  # вул., Вулиця
    (icompile(r'\b(смт|селище міського типу|с\.м\.т)\b\.?,?'), r'смт'),
    (icompile(r'\bобласть\b'), r'обл.'),
    (icompile(r'\bрайон\b'), r'р-н'),
    (icompile(r'\bмісто\b'), r'м.'),
    (icompile(r'\bбудинок\b'), r'буд.'),
    (icompile(r'\bбуд\b\.?'), r'буд.'),
    (icompile(r'\bофіс\b'), r'оф.'),
    (icompile(r'\bквартира\b'), r'кв.'),
    (icompile(r'\bобл\b\.?,?\s?'), r'обл., '),
    (icompile(r'\bр\-?н\b\.?,?\s?'), r'р-н, '),
    (icompile(r'\bбуд\.,'), r'буд.'),
    (re.compile(  # додавання крапки до скорочення м. і с., але не у назвах
        r'(?<!вул\.)(?<!пров\.)(?<!бульв\.)(?<!просп\.)(?<!смт)(?<!м\.)'
        r'(\s?)\b(м|с)\.?\s'),
     lambda matched: matched.group(1) + matched.group(2).lower() + '. '),
    (re.compile(  # додавання "буд." якщо після вулиці йде число
        r'\b(вул\.|пров\.|бульв\.|просп\.|площа\b)([^,]+,)\s?([0-9])'),
        r'\1\2 буд. \3'),
    (re.compile(  # видалення пробілів навколо дефісів між буквами
        r'([Є-ЯҐа-їґ])\s*(\-)\s*([Є-ЯҐа-їґ])'),
        r'\1\2\3'),
    (re.compile(  # написання букв у номері будинку з великої без дефісу
        r'(, буд. [0-9]+)\-?([Є-ЯҐа-їґ])'),
        lambda matched: matched.group(1) + matched.group(2).upper()),
    (re.compile(  # написання букв у номері будинку після дробу
        r'(, буд. [0-9]+[Є-ЯҐ]?/[0-9]+)\-?([Є-ЯҐа-їґ])'),
        lambda matched: matched.group(1) + matched.group(2).upper()),
    (re.compile(r'([0-9])(?:\\|\|)([0-9])'), r'\1/\2'),  # дріб у номері
    # (re.compile(r'([а-їґ])\s([а-їґ])\s'), r'\1\2 '),  # ! 'приміщення з'
    (re.compile(r'([а-їґ])\s(ий|ка)\s'), r'\1\2 '),
    REPEATING_PUNCTUATION_FIX,
    PUNCTUATION_FIX,
)


def apply_replacement_rule(rule, string):
    pattern, replacement = rule
    return pattern.sub(replacement, string)


def remove_repeated_parts(address):
    uniq_parts = list(OrderedDict.fromkeys(address.split(',')))
    return ','.join(uniq_parts)


@lru_cache(maxsize=16)
def clean_address(address):
    address = address.lstrip(LSTRIP_CHARS).rstrip(RSTRIP_CHARS)
    for rule in REPLACEMENTS:
        address = apply_replacement_rule(rule, address)
    address = remove_repeated_parts(address)
    address = address.lstrip(LSTRIP_CHARS).rstrip(RSTRIP_CHARS)
    return address


# address_set
SET_CLEANER = (re.compile(r'[^a-zA-Z0-9ʼЄ-ЯҐа-їґ ]+'), ' ')

TYPE_WORDS = {
    'обл',
    'р-н',
    'м',
    'смт',
    'с',
    'вул',
    'пров',
    'бульв',
    'просп',
    'площа',
    'буд',
    'оф',
    'кв',
    'корп',
}


def address_set(address, lowercase=True):
    '''
    Перетворення адреси у множину суттєвих елементів
    '''
    words_set = set()
    if not address:
        return words_set
    if lowercase:
        address = address.lower()
    words_list = re.split(' ', apply_replacement_rule(SET_CLEANER, address))
    for word in words_list:
        if re.search('[0-9]', word):
            words_set.add(word)
        else:
            if len(word) > 3:  # FIXME: 'м. Бар', 'Ш. Лан'
                words_set.add(word)
    return words_set - TYPE_WORDS
