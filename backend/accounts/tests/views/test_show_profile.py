import pytest
from decimal import Decimal
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from accounts.models import Profile
from bank.models import Bank, Transaction


@pytest.mark.django_db
class TestShowProfileAuthentication:
    """Test authentication and access control for show_profile view."""

    def test_unauthenticated_user_redirected_to_login(self, client):
        """Test that unauthenticated users are redirected to login page."""
        response = client.get(reverse("show_profile"))
        assert response.status_code == 302
        assert reverse("login") in response.url

    def test_authenticated_user_returns_200(self, authenticated_client, create_bank):
        """Test that authenticated users can access the show_profile view."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        if not profile.iban:
            profile.iban = "PL12345678901234567890123456"
            profile.save()
        create_bank(iban=profile.iban, balance=Decimal("1000.00"))
        response = client.get(reverse("show_profile"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestShowProfileContext:
    """Test context data passed to the template."""

    def test_profile_in_context(self, authenticated_client, create_bank):
        """Test that user's profile is in the context."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        if not profile.iban:
            profile.iban = "PL12345678901234567890123456"
            profile.save()
        create_bank(iban=profile.iban, balance=Decimal("1000.00"))
        response = client.get(reverse("show_profile"))
        assert "profile" in response.context
        assert response.context["profile"].id == profile.id
        assert response.context["profile"].username == profile.username

    def test_bank_in_context(self, authenticated_client, create_bank):
        """Test that user's bank account is in the context."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        bank = create_bank(balance="5000.00")
        profile.iban = bank.iban
        profile.save()
        response = client.get(reverse("show_profile"))
        assert "bank" in response.context
        assert response.context["bank"].id == bank.id
        assert response.context["bank"].iban == profile.iban

    def test_section_in_context(self, authenticated_client, create_bank):
        """Test that the correct section identifier is in the context."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        if not profile.iban:
            profile.iban = "PL12345678901234567890123456"
            profile.save()
        create_bank(iban=profile.iban, balance=Decimal("1000.00"))
        response = client.get(reverse("show_profile"))
        assert "section" in response.context
        assert response.context["section"] == "show_profile"

    def test_transaction_data_in_context(self, authenticated_client, create_bank):
        """Test that transaction_data is present in context."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        if not profile.iban:
            profile.iban = "PL12345678901234567890123456"
            profile.save()
        create_bank(iban=profile.iban, balance=Decimal("1000.00"))
        response = client.get(reverse("show_profile"))
        assert "transaction_data" in response.context
        assert isinstance(response.context["transaction_data"], list)


@pytest.mark.django_db
class TestShowProfileTransactionAggregation:
    """Test transaction aggregation logic."""

    def test_no_transactions(self, authenticated_client, create_bank):
        """Test show_profile when user has no transactions."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        if not profile.iban:
            profile.iban = "PL12345678901234567890123456"
            profile.save()
        create_bank(iban=profile.iban, balance=Decimal("1000.00"))
        response = client.get(reverse("show_profile"))
        transaction_data = response.context["transaction_data"]
        assert transaction_data == []

    def test_single_deposit_transaction(self, authenticated_client, create_bank):
        """Test aggregation of a single deposit transaction."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        if not profile.iban:
            profile.iban = "PL12345678901234567890123456"
            profile.save()
        bank = create_bank(iban=profile.iban, balance=Decimal("1000.00"))
        today_str = timezone.now().strftime("%Y-%m-%d")

        Transaction.objects.create(
            bank=bank,
            first_name="John",
            last_name="Doe",
            transaction_type="DEPOSIT",
            amount=Decimal("500.00"),
            iban=bank.iban,
        )
        response = client.get(reverse("show_profile"))
        transaction_data = response.context["transaction_data"]
        assert len(transaction_data) == 1
        assert transaction_data[0]["date"] == today_str
        assert float(transaction_data[0]["total"]) == 500.00

    def test_multiple_deposits_same_day_aggregated(self, authenticated_client, create_bank):
        """Test that multiple deposits on the same day are aggregated."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        if not profile.iban:
            profile.iban = "PL12345678901234567890123456"
            profile.save()
        bank = create_bank(iban=profile.iban, balance=Decimal("1000.00"))
        today_str = timezone.now().strftime("%Y-%m-%d")

        amounts = [Decimal("200.00"), Decimal("300.00"), Decimal("150.00")]
        for amount in amounts:
            Transaction.objects.create(
                bank=bank,
                first_name="John",
                last_name="Doe",
                transaction_type="DEPOSIT",
                amount=amount,
                iban=bank.iban,
            )
        response = client.get(reverse("show_profile"))
        transaction_data = response.context["transaction_data"]
        assert len(transaction_data) == 1
        assert transaction_data[0]["date"] == today_str
        assert float(transaction_data[0]["total"]) == 650.00

    def test_only_deposits_included_in_aggregation(self, authenticated_client, create_bank):
        """Test that only DEPOSIT transactions are included in aggregation."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        if not profile.iban:
            profile.iban = "PL12345678901234567890123456"
            profile.save()
        bank = create_bank(iban=profile.iban, balance=Decimal("1000.00"))
        bank2 = create_bank(iban="PL12345678901234567890123451", balance=Decimal("1000.00"))

        Transaction.objects.create(
            bank=bank,
            first_name="John",
            last_name="Doe",
            transaction_type="DEPOSIT",
            amount=Decimal("500.00"),
            iban=bank.iban,
        )
        Transaction.objects.create(
            bank=bank,
            first_name="John",
            last_name="Doe",
            transaction_type="TRANSFER",
            amount=Decimal("200.00"),
            iban=bank2.iban,
        )
        Transaction.objects.create(
            bank=bank,
            first_name="John",
            last_name="Doe",
            transaction_type="WITHDRAWAL",
            amount=Decimal("200.00"),
            iban=bank.iban,
        )
        response = client.get(reverse("show_profile"))
        transaction_data = response.context["transaction_data"]
        assert len(transaction_data) == 1
        assert float(transaction_data[0]["total"]) == 500.00

    def test_transaction_date_format(self, authenticated_client, create_bank):
        """Test that transaction dates are formatted correctly as YYYY-MM-DD."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        if not profile.iban:
            profile.iban = "PL12345678901234567890123456"
            profile.save()
        bank = create_bank(iban=profile.iban, balance=Decimal("1000.00"))

        Transaction.objects.create(
            bank=bank,
            first_name="John",
            last_name="Doe",
            transaction_type="DEPOSIT",
            amount=Decimal("500.00"),
            iban=bank.iban,
        )
        response = client.get(reverse("show_profile"))
        transaction_data = response.context["transaction_data"]
        assert len(transaction_data) > 0
        assert isinstance(transaction_data[0]["date"], str)
        import re
        assert re.match(r"\d{4}-\d{2}-\d{2}", transaction_data[0]["date"])

    def test_transaction_data_structure(self, authenticated_client, create_bank):
        """Test that transaction_data items have correct structure."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        if not profile.iban:
            profile.iban = "PL12345678901234567890123456"
            profile.save()
        bank = create_bank(iban=profile.iban, balance=Decimal("1000.00"))

        Transaction.objects.create(
            bank=bank,
            first_name="John",
            last_name="Doe",
            transaction_type="DEPOSIT",
            amount=Decimal("500.00"),
            iban=bank.iban,
        )
        response = client.get(reverse("show_profile"))
        transaction_data = response.context["transaction_data"]
        assert len(transaction_data) > 0
        assert len(transaction_data[0]) == 2
        assert "date" in transaction_data[0]
        assert "total" in transaction_data[0]


@pytest.mark.django_db
class TestShowProfileTemplate:
    """Test template rendering."""

    def test_correct_template_used(self, authenticated_client, create_bank):
        """Test that the correct template is used."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        if not profile.iban:
            profile.iban = "PL12345678901234567890123456"
            profile.save()
        create_bank(iban=profile.iban, balance=Decimal("1000.00"))
        response = client.get(reverse("show_profile"))
        assert "accounts/profile.html" in [t.name for t in response.templates]


@pytest.mark.django_db
class TestShowProfileEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_balance(self, authenticated_client, create_bank):
        """Test show_profile with zero balance."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        bank = create_bank(iban="DE89370400440532013000", balance=Decimal("0.00"))
        profile.iban = bank.iban
        profile.save()
        response = client.get(reverse("show_profile"))
        assert response.status_code == 200
        assert response.context["bank"] is not None
        assert float(response.context["bank"].balance) == 0.00

    def test_large_balance(self, authenticated_client, create_bank):
        """Test show_profile with a very large balance."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        bank = create_bank(iban="GB82WEST12345698765432", balance=Decimal("999999999.99"))
        profile.iban = bank.iban
        profile.save()
        response = client.get(reverse("show_profile"))
        assert response.status_code == 200
        assert response.context["bank"].balance == Decimal("999999999.99")

    def test_decimal_precision_maintained(self, authenticated_client, create_bank):
        """Test that decimal precision is maintained in transaction totals."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        if not profile.iban:
            profile.iban = "PL12345678901234567890123456"
            profile.save()
        bank = create_bank(iban=profile.iban, balance=Decimal("1000.00"))

        Transaction.objects.create(
            bank=bank,
            first_name="John",
            last_name="Doe",
            transaction_type="DEPOSIT",
            amount=Decimal("100.50"),
            iban=bank.iban,
        )
        Transaction.objects.create(
            bank=bank,
            first_name="John",
            last_name="Doe",
            transaction_type="DEPOSIT",
            amount=Decimal("200.75"),
            iban=bank.iban,
        )
        response = client.get(reverse("show_profile"))
        transaction_data = response.context["transaction_data"]
        assert len(transaction_data) > 0
        total = float(transaction_data[0]["total"])
        assert abs(total - 301.25) < 0.01

    def test_multiple_deposits_with_mixed_precision(self, authenticated_client, create_bank):
        """Test aggregation with multiple deposits of varying decimal precision."""
        client, user = authenticated_client
        profile = Profile.objects.get(id=user.id)
        if not profile.iban:
            profile.iban = "PL12345678901234567890123456"
            profile.save()
        bank = create_bank(iban=profile.iban, balance=Decimal("1000.00"))

        amounts = [
            Decimal("10.5"),
            Decimal("20.25"),
            Decimal("30.125"),
            Decimal("40.01"),
        ]
        for amount in amounts:
            Transaction.objects.create(
                bank=bank,
                first_name="John",
                last_name="Doe",
                transaction_type="DEPOSIT",
                amount=amount,
                iban=bank.iban,
            )
        response = client.get(reverse("show_profile"))
        transaction_data = response.context["transaction_data"]
        assert len(transaction_data) > 0
        total = float(transaction_data[0]["total"])
        expected_total = float(sum(amounts))
        assert abs(total - expected_total) < 0.01
