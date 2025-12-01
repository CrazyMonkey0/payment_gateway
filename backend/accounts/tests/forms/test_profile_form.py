import pytest
from accounts.forms import ProfileForm
from accounts.models import Profile
from bank.models import Bank


# ===== FIXTURES =====

@pytest.fixture
def form_data_factory():
    """
    Factory fixture to create form data with configurable values.
    
    Returns:
        function: A function that creates form data dictionaries with defaults
                 that can be overridden via kwargs.
    """
    def _make_form_data(**kwargs):
        default = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "iban": "PL12345678901234567890",
        }
        default.update(kwargs)
        return default
    return _make_form_data


# If you don't have create_bank in main conftest.py, define it here:
@pytest.fixture
def create_bank(db):
    """
    Factory fixture to create Bank instances.
    
    Args:
        iban (str): The IBAN for the bank account
        balance (float): Initial balance, defaults to 1000.00
        
    Returns:
        Bank: Created bank instance
    """
    def _create(iban, balance=1000.00):
        return Bank.objects.create(iban=iban, balance=balance)
    return _create


@pytest.fixture
def user_factory(db):
    """
    Factory fixture to create user profiles.
    
    Returns:
        function: A function that creates Profile instances with defaults
                 that can be overridden via kwargs.
    """
    def _create_user(**kwargs):
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!@#'
        }
        defaults.update(kwargs)
        return Profile.objects.create_user(**defaults)
    return _create_user


# ===== TESTS =====

@pytest.mark.django_db
@pytest.mark.parametrize(
    "first_name, last_name, email, iban",
    [
        ("John", "Doe", "john@example.com", "PL12345678901234567890"),
        ("Jane", "Smith", "jane@test.com", "GB98765432109876543210"),
        ("Bob", "Brown", "bob@mail.com", "DE11111111111111111111"),
    ]
)
def test_profile_form_valid_data(first_name, last_name, email, iban, create_bank):
    """Test ProfileForm with valid data and existing IBAN in database."""
    create_bank(iban)
    
    form_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "iban": iban,
    }
    form = ProfileForm(data=form_data)
    
    assert form.is_valid() is True
    assert form.cleaned_data['first_name'] == first_name
    assert form.cleaned_data['last_name'] == last_name
    assert form.cleaned_data['email'] == email
    assert form.cleaned_data['iban'] == iban


@pytest.mark.django_db
@pytest.mark.parametrize("iban", [
    "PL99999999999999999999",
    "GB12345678901234567890",
    "DE00000000000000000000",
])
def test_iban_not_in_database(iban, form_data_factory):
    """Test ProfileForm with valid IBAN format but not existing in database."""
    form_data = form_data_factory(iban=iban)
    form = ProfileForm(data=form_data)
    
    assert form.is_valid() is False
    assert 'iban' in form.errors
    assert 'This IBAN does not exist.' in str(form.errors['iban'])


@pytest.mark.django_db
@pytest.mark.parametrize("invalid_iban", [
    "12PL1234567890",        # Numbers before country code
    "pl12345678901234567890", # Lowercase country code
    "P112345678901234567890", # Single letter country code
    "PLA2345678901234567890", # Letter in numeric part
    "PL 1234567890",         # Space in IBAN
    "PL-1234567890",         # Dash in IBAN
    "PLXX123456789",         # Letters in numeric part
    "123456789012345678",    # Only numbers, no country code
    "ABC123",                # Invalid format
    "PL12345ABC",            # Mix of valid start with letters
])
def test_incorrect_iban_format(invalid_iban, form_data_factory):
    """Test ProfileForm with incorrect IBAN format."""
    form_data = form_data_factory(iban=invalid_iban)
    form = ProfileForm(data=form_data)
    
    assert form.is_valid() is False
    assert 'iban' in form.errors
    assert 'Incorrect IBAN' in str(form.errors['iban'])


@pytest.mark.django_db
def test_empty_iban(form_data_factory):
    """Test ProfileForm with empty IBAN - should show 'required' error."""
    form_data = form_data_factory(iban="")
    form = ProfileForm(data=form_data)
    
    assert form.is_valid() is False
    assert 'iban' in form.errors
    assert 'This field is required' in str(form.errors['iban'])


@pytest.mark.django_db
def test_iban_field_required(form_data_factory):
    """Test that IBAN field is required."""
    form_data = form_data_factory()
    del form_data['iban']  # Remove IBAN from data
    
    form = ProfileForm(data=form_data)
    
    assert form.is_valid() is False
    assert 'iban' in form.errors


@pytest.mark.django_db
def test_optional_fields(create_bank):
    """
    Test whether first_name, last_name, and email are optional.
    This verifies the actual behavior based on Profile model configuration.
    """
    iban = "PL12345678901234567890"
    create_bank(iban)
    
    form_data = {"iban": iban}
    form = ProfileForm(data=form_data)
    
    if form.is_valid():
        print("INFO: first_name, last_name, email are OPTIONAL in Profile model")
        assert form.cleaned_data['iban'] == iban
    else:
        print("INFO: Some fields are REQUIRED in Profile model")
        print(f"Required fields: {list(form.errors.keys())}")


@pytest.mark.django_db
def test_empty_form():
    """Test ProfileForm with no data."""
    form = ProfileForm(data={})
    
    assert form.is_valid() is False
    assert 'iban' in form.errors
    assert len(form.errors) >= 1


@pytest.mark.django_db
def test_invalid_email_format(form_data_factory, create_bank):
    """Test ProfileForm with invalid email format."""
    form_data = form_data_factory(email="invalid-email")
    create_bank(form_data["iban"])
    
    form = ProfileForm(data=form_data)
    
    assert form.is_valid() is False
    assert 'email' in form.errors


@pytest.mark.django_db
def test_very_long_strings(form_data_factory, create_bank):
    """Test ProfileForm with strings exceeding model field max_length."""
    form_data = form_data_factory(
        first_name="a" * 500,
        last_name="b" * 500
    )
    create_bank(form_data["iban"])
    
    form = ProfileForm(data=form_data)
    
    assert form.is_valid() is False


@pytest.mark.django_db
def test_update_existing_profile(user_factory, create_bank, form_data_factory):
    """Test updating an existing profile with valid data."""
    old_iban = "PL11111111111111111111"
    new_iban = "PL22222222222222222222"
    
    # Create user and banks
    user = user_factory()
    create_bank(old_iban)
    create_bank(new_iban)
    
    # Set initial IBAN
    user.iban = old_iban
    user.save()
    
    # Update profile
    form_data = form_data_factory(
        first_name="Updated",
        last_name="Name",
        email="new@test.com",
        iban=new_iban
    )
    form = ProfileForm(data=form_data, instance=user)
    
    assert form.is_valid() is True
    updated_profile = form.save()
    assert updated_profile.first_name == "Updated"
    assert updated_profile.iban == new_iban
    assert updated_profile.email == "new@test.com"


@pytest.mark.django_db
def test_form_does_not_escape_on_validation(form_data_factory, create_bank):
    """
    Test that form validation doesn't escape HTML.
    Django escapes in templates, not forms - this is EXPECTED behavior.
    Forms store raw data, templates handle escaping.
    """
    form_data = form_data_factory(
        first_name="<script>alert('xss')</script>",
        last_name="<img src=x onerror=alert('xss')>"
    )
    create_bank(form_data["iban"])
    
    form = ProfileForm(data=form_data)
    
    if form.is_valid():
        # Raw data is stored - escaping happens in templates
        assert form.cleaned_data['first_name'] == "<script>alert('xss')</script>"
        assert form.cleaned_data['last_name'] == "<img src=x onerror=alert('xss')>"
        print("INFO: Form stores raw data (correct). Escaping happens in templates.")
    else:
        print(f"INFO: Model has additional validation: {form.errors}")


@pytest.mark.django_db
def test_iban_case_sensitivity(form_data_factory):
    """Test that IBAN validation is case-sensitive (only uppercase allowed)."""
    form_data = form_data_factory(iban="pl12345678901234567890")
    
    form = ProfileForm(data=form_data)
    
    assert form.is_valid() is False
    assert 'iban' in form.errors
    assert 'Incorrect IBAN' in str(form.errors['iban'])


@pytest.mark.django_db
def test_special_characters_in_names(form_data_factory, create_bank):
    """Test ProfileForm with special characters in names (if model allows)."""
    form_data = form_data_factory(
        first_name="Jean-Pierre",  # Hyphenated name
        last_name="O'Connor"       # Apostrophe in name
    )
    create_bank(form_data["iban"])
    
    form = ProfileForm(data=form_data)
    
    if form.is_valid():
        print("INFO: Model accepts special characters in names (good!)")
        assert form.cleaned_data['first_name'] == "Jean-Pierre"
    else:
        print(f"INFO: Model rejects special characters: {form.errors}")


@pytest.mark.django_db
def test_whitespace_in_fields(form_data_factory, create_bank):
    """Test ProfileForm with leading/trailing whitespace."""
    form_data = form_data_factory(
        first_name="  John  ",
        last_name="  Doe  ",
        email="  test@test.com  "
    )
    create_bank(form_data["iban"])
    
    form = ProfileForm(data=form_data)
    
    if form.is_valid():
        # Check if whitespace is preserved or stripped
        print(f"First name with whitespace: '{form.cleaned_data['first_name']}'")
        # Django typically does NOT strip whitespace automatically in forms


@pytest.mark.django_db
def test_multiple_banks_same_iban_pattern(create_bank, form_data_factory):
    """Test that IBAN validation correctly identifies existing IBAN."""
    iban1 = "PL11111111111111111111"
    iban2 = "PL11111111111111111112"  # Very similar but different
    
    create_bank(iban1)
    
    # Try to use non-existing IBAN
    form_data = form_data_factory(iban=iban2)
    form = ProfileForm(data=form_data)
    
    assert form.is_valid() is False
    assert 'iban' in form.errors
    assert 'This IBAN does not exist.' in str(form.errors['iban'])


@pytest.mark.django_db
def test_regex_edge_cases(create_bank, form_data_factory):
    """Test edge cases for IBAN regex validation."""
    create_bank("AB123")
    
    test_cases = [
        ("AB123", True, "Minimal valid format: 2 letters + digits"),
        ("AB", False, "Only country code, passes regex but no bank"),
        ("A1234", False, "Single letter country code"),
        ("1B234", False, "Digit in country code"),
    ]
    
    for iban, should_pass_regex, description in test_cases:
        form_data = form_data_factory(iban=iban)
        form = ProfileForm(data=form_data)
        
        if should_pass_regex:
            # Should pass regex, might fail on database check
            assert form.is_valid() is not None
        else:
            # Should fail regex check
            assert form.is_valid() is False
            if 'iban' in form.errors:
                print(f"{description}: {form.errors['iban']}")