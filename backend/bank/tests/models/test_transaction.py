import pytest
from django.core.exceptions import ValidationError
from bank.models import Transaction


@pytest.fixture
def create_transaction():
    """
    Fixture for creating a Transaction instance with the specified parameters.
    """

    def _create_transaction(
        bank,
        transaction_type,
        amount,
        first_name="Test",
        last_name="User",
        iban="",
    ):
        return Transaction.objects.create(
            bank=bank,
            transaction_type=transaction_type,
            amount=amount,
            first_name=first_name,
            last_name=last_name,
            iban=iban,
        )

    return _create_transaction


@pytest.mark.django_db
def test_transfer_success(create_bank, create_transaction):
    # accounts setup
    sender = create_bank("John", "Doe", "PL", balance=1000)
    receiver = create_bank("Alice", "Smith", "PL", balance=200)

    # execute transfer
    transfer = create_transaction(
        bank=sender,
        transaction_type="TRANSFER",
        amount=300,
        first_name="John",
        last_name="Doe",
        iban=receiver.iban,
    )
    # refresh from db
    sender.refresh_from_db()
    receiver.refresh_from_db()

    # check balances
    assert sender.balance == 700
    assert receiver.balance == 500

    # check transaction records
    assert transfer in Transaction.objects.all()

    # check deposit record for receiver
    deposit = Transaction.objects.filter(
        bank=receiver, transaction_type="DEPOSIT", amount=300
    ).first()

    assert deposit is not None


@pytest.mark.django_db
def test_transfer_insufficient_funds(create_bank, create_transaction):
    # accounts setup
    sender = create_bank("John", "Doe", "PL", balance=100)
    receiver = create_bank("Alice", "Smith", "PL", balance=200)

    # attempt transfer with insufficient funds
    with pytest.raises(ValidationError):
        create_transaction(
            bank=sender,
            transaction_type="TRANSFER",
            amount=300,
            first_name="John",
            last_name="Doe",
            iban=receiver.iban,
        )
    # refresh from db
    sender.refresh_from_db()
    receiver.refresh_from_db()

    assert sender.balance == 100
    assert receiver.balance == 200
    assert Transaction.objects.count() == 0


@pytest.mark.django_db
def test_deposit(create_bank, create_transaction):
    acc = create_bank("John", "Doe", "PL", balance=500)

    # perform deposit
    deposit = create_transaction(
        bank=acc,
        transaction_type="DEPOSIT",
        amount=250,
        first_name="John",
        last_name="Doe",
        iban=acc.iban,
    )
    # refresh from db
    acc.refresh_from_db()

    assert acc.balance == 750
    assert deposit in Transaction.objects.all()


@pytest.mark.django_db
def test_str_representation(create_bank, create_transaction):
    bank_instance = create_bank("Alice", "Smith", "GB")
    transaction = create_transaction(
        bank=bank_instance,
        transaction_type="DEPOSIT",
        amount=150.75,
        first_name="Alice",
        last_name="Smith",
        iban=bank_instance.iban,
    )
    assert str(transaction) == (
        f"Name: {transaction.first_name} {transaction.last_name} |"
        f"ID bank: {transaction.iban} | Amount: {transaction.amount}$"
    )
