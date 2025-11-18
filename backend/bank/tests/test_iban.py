import re
from bank.iban import pl_iban, de_iban, gb_iban

def test_pl_iban():
    iban = pl_iban()
    pattern = r'^PL\d{2}12345678\d{16}$'
    assert re.fullmatch(pattern, iban), f"Incorrect PL IBAN: {iban}"

def test_de_iban():
    iban = de_iban()
    pattern = r'^DE\d{2}87654321\d{10}$'
    assert re.fullmatch(pattern, iban), f"Incorrect DE IBAN: {iban}"

def test_gb_iban():
    iban = gb_iban()
    pattern = r'^GB\d{2}3123222222\d{8}$'
    assert re.fullmatch(pattern, iban), f"Incorrect GB IBAN: {iban}"