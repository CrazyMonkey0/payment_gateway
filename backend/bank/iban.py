import random


def pl_iban():
    x = ''.join(str(random.randrange(0, 9)) for _ in range(2))
    y = ''.join(str(random.randrange(0, 9)) for _ in range(16))

    # Poland - PLkk BBBB BBBB MMMM MMMM MMMM MMMM MMMM.
    # The first 2 digits are check digits. The next 8 digits are the bank-branch identifier. The last 16 are the account number.
    return f"PL{x}12345678{y}"


def de_iban():
    x = ''.join(str(random.randrange(0, 9)) for _ in range(2))
    y = ''.join(str(random.randrange(0, 9)) for _ in range(10))

    # Poland - PLkk BBBB BBBB MMMM MMMM MMMM MMMM MMMM.
    # The first 2 digits are check digits. The next 8 digits are the bank-branch identifier. The last 16 are the account number.
    return f"DE{x}87654321{y}"


def gb_iban():
    x = ''.join(str(random.randrange(0, 9)) for _ in range(2))
    y = ''.join(str(random.randrange(0, 9)) for _ in range(8))

    # United Kingdom - GBkk BBBB SSSS SSCC CCCC CC.
    # The first 2 digits are check digits. The bank's four-digit ID, followed by the branch code (usually) and account number.
    return f"GB{x}3123222222{y}"
