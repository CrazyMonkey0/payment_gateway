from math import e
import pytest
from bank.models import Bank


@pytest.fixture
def create_bank():
    """
    Fixture for creating a Bank instance with the specified parameters.
    """
    def _create_bank(first_name, last_name, country, iban="", balance=1000):
        return Bank.objects.create(
            first_name=first_name,
            last_name=last_name,
            country=country,
            iban=iban,
            balance=balance
        )
    return _create_bank


@pytest.mark.django_db
@pytest.mark.parametrize("country, prefix, length", [
    ("PL", "PL", 28),
    ("DE", "DE", 22),
    ("GB", "GB", 22),
])
def test_iban_generation(create_bank, country, prefix, length):
    bank_instance = create_bank('Test', 'User', country, iban="")
    assert bank_instance.iban.startswith(prefix), f"The IBAN should start with {prefix}"
    assert len(bank_instance.iban) == length, f"The length of the IBAN should be {length}"

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
    found_instance = Bank.find_by_iban(iban_value)
    if exists:
        assert found_instance == bank_instance, "The found instance should match the created instance"
    else:
        assert found_instance is None, "The found instance should be None for non-existent IBAN"

@pytest.mark.django_db
def test_str_representation(create_bank):
    bank_instance = create_bank('Alice', 'Smith', 'GB', balance=2500.75)
    expected_str = "Alice Smith | Balance: 2500.75$"
    assert str(bank_instance) == expected_str, "The string representation does not match the expected format"

