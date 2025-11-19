from django.forms import ValidationError
import pytest
from bank.models import Visa, MasterCard, default_valid_until
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
def test_default_valid_until_format_and_range():
    result = default_valid_until()

    # Check format
    assert len(result) == 7
    assert result[2] == "/"

    month, year = map(int, result.split("/"))
    assert 1 <= month <= 12
    assert len(str(year)) == 4

    expected_date = timezone.now() + timedelta(days=730)
    assert year == expected_date.year
    assert month == expected_date.month


@pytest.mark.django_db
def test_visa_card_creation(create_bank):
    bank_instance = create_bank("Alice", "Smith", "PL")
    visa_card = Visa.objects.create(
        bank=bank_instance, id_card="1234567890123456", cvc="123"
    )
    assert str(visa_card) == "Alice Smith"
    assert visa_card.is_valid is True
    assert visa_card.logo == "Visa"
    assert len(visa_card.id_card) == 16
    assert len(visa_card.cvc) == 3


@pytest.mark.django_db
def test_mastercard_creation(create_bank):
    bank_instance = create_bank("Bob", "Johnson", "GB")
    mc_card = MasterCard.objects.create(
        bank=bank_instance, id_card="6543210987654321", cvc="321"
    )
    assert str(mc_card) == "Bob Johnson"
    assert mc_card.is_valid is True


@pytest.mark.django_db
@pytest.mark.parametrize(
    "id_card",
    [
        "1234",
        "123x4",
        "123456789012121x",
        "123456711289012121",
        "123456711ada289012121",
    ],
)
def test_invalid_id_card(create_bank, id_card):
    bank_instance = create_bank("Bob", "Johnson", "GB")

    card = MasterCard(
        bank=bank_instance,
        id_card=id_card,
        cvc="321",
    )

    with pytest.raises(ValidationError) as excinfo:
        card.full_clean()

    assert "id_card" in excinfo.value.message_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "cvc",
    [
        "12",
        "1a",
        "12x",
        "123456711289012121",
        "123456711ada289012121",
    ],
)
def test_invalid_cvc(create_bank, cvc):
    bank_instance = create_bank("Bob", "Johnson", "GB")

    card = MasterCard(
        bank=bank_instance,
        id_card="6543211987654321",
        cvc=cvc,
    )

    with pytest.raises(ValidationError) as excinfo:
        card.full_clean()

    assert "cvc" in excinfo.value.message_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "valid_until",
    [
        "1234",
        "123.4",
        "12.2000",
        "1212000",
        "12345671128/9012121",
        "123456711ad.289012121",
    ],
)
def test_invalid_valid_until(create_bank, valid_until):
    bank_instance = create_bank("Bob", "Johnson", "GB")

    card = MasterCard(
        bank=bank_instance,
        id_card="6543211987654321",
        cvc="321",
        valid_until=valid_until,
    )

    with pytest.raises(ValidationError) as excinfo:
        card.full_clean()

    assert "valid_until" in excinfo.value.message_dict


@pytest.mark.django_db
def test_is_valid_field(create_bank):
    bank_instance = create_bank("Alice", "Smith", "PL")

    visa_card = Visa.objects.create(
        bank=bank_instance, id_card="1234567890123456", cvc="123"
    )

    assert visa_card.is_valid is True

    visa_card.is_valid = False
    visa_card.save()
    visa_card.refresh_from_db()

    assert visa_card.is_valid is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    "is_valid",
    [
        None,
        "invalid_string",
        123,
        45.67,
        [],
        {},
    ],
)
def test_invalid_is_valid(create_bank, is_valid):
    bank_instance = create_bank("Bob", "Johnson", "GB")

    card = MasterCard(
        bank=bank_instance,
        id_card="6543211987654321",
        cvc="321",
        is_valid=is_valid,
    )

    with pytest.raises(ValidationError) as excinfo:
        card.full_clean()

    assert "is_valid" in excinfo.value.message_dict
