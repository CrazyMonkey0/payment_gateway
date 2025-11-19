import pytest
from bank.models import Bank


@pytest.mark.django_db
@pytest.mark.parametrize("country, prefix, length", [
    ("PL", "PL", 28),
    ("DE", "DE", 22),
    ("GB", "GB", 22),
])
def test_iban_generation(create_bank, country, prefix, length):
    bank_instance = create_bank('Test', 'User', country, iban="")
    assert bank_instance.iban.startswith(prefix)
    assert len(bank_instance.iban) == length


@pytest.mark.django_db
@pytest.mark.parametrize("iban_value, exists", [
    ("PL12345678901234567890123456", True),
    ("DE87654321876543218765", True),
    ("GB31232222221234567890", True),
    ("NONEXISTENTIBAN", False),
    ("PL12345678900987654321123456", False),
])
def test_find_by_iban(create_bank, iban_value, exists):
    bank_instance = create_bank('John', 'Doe', 'PL', iban=iban_value) if exists else None
    found = Bank.find_by_iban(iban_value)
    if exists:
        assert found == bank_instance
    else:
        assert found is None


@pytest.mark.django_db
def test_str_representation(create_bank):
    bank = create_bank('Alice', 'Smith', 'GB', balance=2500.75)
    assert str(bank) == "Alice Smith | Balance: 2500.75$"
