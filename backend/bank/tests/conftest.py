import pytest
from bank.models import Bank, Transaction


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

