import pytest
from decimal import Decimal
from django.urls import reverse
from django.utils import timezone
from accounts.models import Profile
from bank.models import Bank, Transaction


@pytest.fixture
def profile_with_bank(authenticated_client, create_bank, db):
    """Fixture: creates a logged-in user, profile, and bank account."""
    client, user = authenticated_client
    bank = create_bank(iban="PL12345678901234567890123456", balance=1000)
    profile = Profile.objects.get(id=user.id)
    profile.iban = bank.iban
    profile.save()
    return client, profile, bank


@pytest.mark.django_db
class TestEditProfileView:
    """Tests for edit_profile view."""

    def test_get_authenticated(self, profile_with_bank):
        client, profile, bank = profile_with_bank
        response = client.get(reverse("edit_profile"))
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].instance.id == profile.id
        assert response.context["section"] == "show_profile"

    def test_post_valid_iban_only(self, profile_with_bank):
        client, profile, bank = profile_with_bank
        # only IBAN is in the form; url_feedback not used in your forms
        data = {"iban": bank.iban}
        response = client.post(reverse("edit_profile"), data)
        profile.refresh_from_db()
        assert profile.iban == bank.iban
        assert response.status_code == 302

    def test_post_updates_iban(self, profile_with_bank, create_bank):
        client, profile, bank = profile_with_bank
        new_iban = "PL12345678901234567890123457"
        create_bank(iban=new_iban, balance=500)
        data = {"iban": new_iban}
        response = client.post(reverse("edit_profile"), data)
        profile.refresh_from_db()
        assert profile.iban == new_iban
        assert response.status_code == 302

    def test_post_invalid_iban(self, profile_with_bank):
        client, profile, bank = profile_with_bank
        data = {"iban": "INVALID"}
        response = client.post(reverse("edit_profile"), data)
        profile.refresh_from_db()
        form = response.context["form"]
        assert response.status_code == 200
        assert not form.is_valid()
        assert "iban" in form.errors

    def test_csrf_protection(self, authenticated_client, create_bank, db):
        client, user = authenticated_client
        client_enforce = client.__class__(enforce_csrf_checks=True)
        bank = create_bank(iban="PL12345678901234567890123456", balance=1000)
        profile = Profile.objects.get(id=user.id)
        profile.iban = bank.iban
        profile.save()
        response = client_enforce.post(
            reverse("edit_profile"),
            {"iban": bank.iban},
            HTTP_X_CSRFTOKEN="invalid",
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestShowProfileTransactions:
    """Tests transaction aggregation on show_profile."""

    def test_no_transactions(self, profile_with_bank):
        client, profile, bank = profile_with_bank
        response = client.get(reverse("show_profile"))
        tx_data = response.context.get("transaction_data", [])
        assert tx_data == []

    def test_single_deposit(self, profile_with_bank):
        client, profile, bank = profile_with_bank
        Transaction.objects.create(
            bank=bank,
            first_name="John",
            last_name="Doe",
            transaction_type="DEPOSIT",
            amount=Decimal("500.00"),
            iban=bank.iban,
        )
        response = client.get(reverse("show_profile"))
        tx_data = response.context.get("transaction_data", [])
        assert len(tx_data) == 1
        assert float(tx_data[0]["total"]) == 500.00

    def test_multiple_deposits_same_day_aggregated(self, profile_with_bank):
        client, profile, bank = profile_with_bank
        amounts = [Decimal("200"), Decimal("300"), Decimal("150")]
        for amt in amounts:
            Transaction.objects.create(
                bank=bank,
                first_name="John",
                last_name="Doe",
                transaction_type="DEPOSIT",
                amount=amt,
                iban=bank.iban,
            )
        response = client.get(reverse("show_profile"))
        tx_data = response.context.get("transaction_data", [])
        assert len(tx_data) == 1
        assert float(tx_data[0]["total"]) == sum(amounts)

    def test_only_deposits_aggregated(self, profile_with_bank, create_bank):
        client, profile, bank = profile_with_bank
        bank2 = create_bank(iban="PL99999999999999999999999999", balance=100)
        Transaction.objects.create(
            bank=bank, first_name="John", last_name="Doe", transaction_type="DEPOSIT", amount=500, iban=bank.iban
        )
        Transaction.objects.create(
            bank=bank, first_name="John", last_name="Doe", transaction_type="TRANSFER", amount=200, iban=bank2.iban
        )
        Transaction.objects.create(
            bank=bank, first_name="John", last_name="Doe", transaction_type="WITHDRAWAL", amount=200, iban=bank.iban
        )
        response = client.get(reverse("show_profile"))
        tx_data = response.context.get("transaction_data", [])
        assert float(tx_data[0]["total"]) == 500.00

    def test_decimal_precision(self, profile_with_bank):
        client, profile, bank = profile_with_bank
        amounts = [Decimal("10.5"), Decimal("20.25"), Decimal("30.125"), Decimal("40.01")]
        for amt in amounts:
            Transaction.objects.create(
                bank=bank,
                first_name="John",
                last_name="Doe",
                transaction_type="DEPOSIT",
                amount=amt,
                iban=bank.iban,
            )
        response = client.get(reverse("show_profile"))
        tx_data = response.context.get("transaction_data", [])
        total = float(tx_data[0]["total"])
        expected = float(sum(amounts))
        assert abs(total - expected) < 0.01
