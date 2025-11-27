import pytest
from accounts.forms import UserRegistrationForm
from accounts.models import Profile


@pytest.fixture
def create_registration_form():
    """
    Factory fixture to create UserRegistrationForm instances with default valid data.
    It returns a factory function that accepts keyword arguments (**kwargs) to override
    the default data when called inside a test.
    
    Usage in test: form = create_registration_form(email='new@test.com', password='new_pass')
    """
    def _factory(**kwargs):
        data = {
            "username": "testuser_base",
            "first_name": "John",
            "last_name": "Doe",
            "email": "base_test@test.com",
            "password": "SecurePass123!@#",
            "password2": "SecurePass123!@#",
        }
        # Override default data with arguments passed during the call
        data.update(kwargs)

        return UserRegistrationForm(data=data)
    
    # The fixture returns the factory function
    return _factory


@pytest.fixture
def valid_form_data():
    """
    Fixture providing complete valid data specifically for save tests,
    ensuring they use unique, predictable data. (Kept for compatibility with save tests).
    """
    return {
        "username": "save_testuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "save_test@test.com",
        "password": "SecurePass123!@#",
        "password2": "SecurePass123!@#",
    }


# This test still uses direct form_data because it relies on @parametrize for full data sets.
@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, first_name, last_name, email, password, password2",
    [
        ("testuser", "John", "Doe", "test@gmail.com", "SecurePass123!@#", "SecurePass123!@#"),
        ("testuser2", "Jane", "Smith", "test2@gmail.com", "AnotherPass456$%", "AnotherPass456$%"),
        ("user_123", "Bob", "Brown", "bob@example.com", "ComplexP@ssw0rd!", "ComplexP@ssw0rd!"),
    ]
)
def test_user_registration_form_valid_data(username, first_name, last_name, email, password, password2):
    """Test UserRegistrationForm with various valid data sets."""
    form_data = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "password2": password2,
    }
    form = UserRegistrationForm(data=form_data)
    
    if not form.is_valid():
        print(f"Form errors: {form.errors}")
    
    assert form.is_valid() is True
    # Check if the email has been correctly cleaned (lowercased by clean_email)
    assert form.cleaned_data['email'] == email.lower() 
    assert form.cleaned_data['username'] == username


@pytest.mark.django_db
@pytest.mark.parametrize(
    "password, password2",
    [
        ("SecurePass123!@#", "DifferentPass456"),  
        ("test123", "test124"),                  
        ("Pass@123", "Pass@12"),                   
    ]
)
def test_password_mismatch(password, password2, create_registration_form):
    """Test UserRegistrationForm with mismatched passwords using the factory fixture."""
    # Use create_registration_form directly with kwargs for overrides
    form = create_registration_form(
        username="unique_user_for_mismatch", 
        email="unique_mismatch@test.com",
        password=password,
        password2=password2,
    )
    
    assert form.is_valid() is False
    assert 'password2' in form.errors
    assert 'Passwords are not identical.' in str(form.errors['password2'])


@pytest.mark.django_db
@pytest.mark.parametrize(
    "password, password2",
    [
        ("", "somepassword"),       # Empty password field
        ("somepassword", ""),       # Empty password2 field
    ]
)
def test_empty_password_fields(password, password2, create_registration_form):
    """Test UserRegistrationForm with empty password fields, checking for 'required' error."""
    # Use create_registration_form directly with kwargs for overrides
    form = create_registration_form(
        username="unique_user_for_empty",
        email="unique_empty@test.com",
        password=password,
        password2=password2,
    )
    
    assert form.is_valid() is False
    assert ('password' in form.errors or 'password2' in form.errors)
    
    # Check for the "required" error message
    if not password:
        assert 'This field is required' in str(form.errors.get('password', ''))
    if not password2:
        assert 'This field is required' in str(form.errors.get('password2', ''))


@pytest.mark.django_db
def test_duplicate_email(create_registration_form):
    """Test UserRegistrationForm with a duplicate email, checking the custom validation (clean_email)."""
    duplicate_email = 'existing@test.com'
    
    # 1. Create an existing user
    Profile.objects.create_user(
        username='existinguser',
        email=duplicate_email,
        password='ExistingPass123!@#'
    )
    
    # 2. Attempt to register a new user with the same email
    form = create_registration_form(
        username="newuser",
        email=duplicate_email,
    )
    
    assert form.is_valid() is False
    assert 'email' in form.errors
    assert 'An account with such an email already exists.' in str(form.errors['email'])


@pytest.mark.django_db
def test_case_insensitive_email_duplicate(create_registration_form):
    """Test that email comparison is case-insensitive (using iexact in clean_email)."""
    # Create an existing user with lowercase email
    Profile.objects.create_user(
        username='existinguser2',
        email='test@example.com',
        password='ExistingPass123!@#'
    )
    
    # Try to register with uppercase email (same email, different case)
    form = create_registration_form(
        username="newuser2",
        email="TEST@EXAMPLE.COM",
    )
    
    # Should be invalid due to case-insensitive check
    assert form.is_valid() is False
    assert 'email' in form.errors
    assert 'An account with such an email already exists.' in str(form.errors['email'])


@pytest.mark.django_db
@pytest.mark.parametrize(
    "missing_field",
    ["username", "password", "password2"]
)
# Reverts to a non-factory approach as kwargs usage would make it complex here
def test_required_fields(missing_field, valid_form_data): 
    """Test UserRegistrationForm with explicitly missing required fields."""
    # Using valid_form_data as a base for easy removal
    form_data = valid_form_data.copy()
    
    # Remove the specified field
    del form_data[missing_field]
    
    form = UserRegistrationForm(data=form_data)
    assert form.is_valid() is False
    assert missing_field in form.errors


@pytest.mark.django_db
# Uses valid_form_data as a base since it's cleaner for field deletion
def test_optional_fields_can_be_empty(valid_form_data):
    """Test that first_name and last_name can be omitted (assuming blank=True in Profile model)."""
    # Create a copy and remove the optional fields
    form_data = valid_form_data.copy()
    del form_data['first_name']
    del form_data['last_name']
    
    form = UserRegistrationForm(data=form_data)
    
    # It should still be valid if the model supports empty fields
    assert form.is_valid() is True
    assert 'first_name' not in form.errors
    assert 'last_name' not in form.errors


@pytest.mark.django_db
def test_empty_form():
    """Test empty UserRegistrationForm. All required fields must have errors."""
    form = UserRegistrationForm(data={})
    assert form.is_valid() is False
    assert len(form.errors) > 0
    assert 'username' in form.errors
    assert 'password' in form.errors
    assert 'password2' in form.errors


@pytest.mark.django_db
def test_very_long_strings(create_registration_form):
    """Test UserRegistrationForm with very long strings, checking max_length constraints."""
    # Use create_registration_form directly with kwargs for overrides
    form = create_registration_form(
        username="a" * 400,  # Exceeds typical max_length
        first_name="b" * 400,
        last_name="c" * 400,
        email="long_string@test.com",
    )
    assert form.is_valid() is False
    assert len(form.errors) > 0
    # At least one field should fail due to length constraints
    assert ('username' in form.errors or 'first_name' in form.errors or 'last_name' in form.errors)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "invalid_email",
    [
        "invalid-email",            # No @ symbol
        "@example.com",             # Missing local part
        "user@",                    # Missing domain
        "user @example.com",        # Space in local part
        "user@example",             # Missing TLD
    ]
)
def test_various_invalid_email_formats(invalid_email, create_registration_form):
    """Test UserRegistrationForm with various invalid email formats, checking Django's built-in validation."""
    # Use create_registration_form directly with kwargs for overrides
    form = create_registration_form(
        username="user_for_invalid_email",
        email=invalid_email,
    )
    assert form.is_valid() is False
    assert 'email' in form.errors


@pytest.mark.django_db
def test_unicode_characters(create_registration_form):
    """Test UserRegistrationForm with Unicode characters in name fields."""
    # Use create_registration_form directly with kwargs for overrides
    form = create_registration_form(
        username="użytkownik_uni", 
        first_name="Łukasz",
        last_name="Żółkowski",
        email="unicode@test.com",
    )
    
    assert form.is_valid()
    assert form.cleaned_data['username'] == "użytkownik_uni"
    assert form.cleaned_data['first_name'] == "Łukasz"


@pytest.mark.django_db
def test_whitespace_in_username(create_registration_form):
    """Test that whitespace in the username is rejected (standard Django User validation)."""
    # Use create_registration_form directly with kwargs for overrides
    form = create_registration_form(
        username="test user with space",  
    )
    
    assert form.is_valid() is False
    assert 'username' in form.errors


@pytest.mark.django_db
def test_form_save_creates_user(valid_form_data):
    """Test that form.save() correctly creates a user and hashes the password."""
    # This test still relies on the dedicated valid_form_data fixture
    form = UserRegistrationForm(data=valid_form_data)
    assert form.is_valid()
    
    # Manual password setting and saving, as required for ModelForms with custom password fields
    user = form.save(commit=False)
    user.set_password(form.cleaned_data['password'])
    user.save()
    
    # Verification
    assert Profile.objects.filter(username=valid_form_data['username']).exists()
    saved_user = Profile.objects.get(username=valid_form_data['username'])
    assert saved_user.check_password(valid_form_data['password'])
    assert saved_user.email == valid_form_data['email']


@pytest.mark.django_db
def test_password_not_stored_in_plain_text(valid_form_data):
    """Test that passwords are correctly hashed and not stored in plaintext."""
    # This test still relies on the dedicated valid_form_data fixture
    form = UserRegistrationForm(data=valid_form_data)
    assert form.is_valid()
    
    user = form.save(commit=False)
    user.set_password(form.cleaned_data['password'])
    user.save()
    
    saved_user = Profile.objects.get(username=valid_form_data['username'])
    
    # Assert that the stored password is not equal to the plaintext
    assert saved_user.password != valid_form_data['password']
    
    # Assert that check_password works
    assert saved_user.check_password(valid_form_data['password'])


@pytest.mark.django_db
def test_duplicate_username(create_registration_form):
    """Test that attempting to register with a non-unique username is rejected."""
    # 1. Create first user
    duplicate_username = 'duplicate_username'
    Profile.objects.create_user(
        username=duplicate_username,
        email='first@test.com',
        password='Password123!@#'
    )
    
    # 2. Try to create another user with the same username
    form = create_registration_form(
        username=duplicate_username,
        email="second_unique@test.com",  # Unique email
    )
    
    assert form.is_valid() is False
    assert 'username' in form.errors


@pytest.mark.django_db
def test_email_normalization(create_registration_form):
    """Test that email addresses are normalized (lowercased) by the clean_email method."""
    # Provide an email with uppercase letters
    form = create_registration_form(
        username='normal_user',
        email='Test@EXAMPLE.COM',
    )
    assert form.is_valid()
    
    cleaned_email = form.cleaned_data['email']
    
    # Assert that the email is converted to lowercase
    assert cleaned_email == 'test@example.com'


@pytest.mark.django_db
def test_leading_trailing_whitespace_stripped(create_registration_form):
    """Test that leading/trailing whitespace is stripped from fields (default CharField behavior)."""
    # Use create_registration_form directly with kwargs for overrides
    form = create_registration_form(
        username="  stripped_user  ",
        first_name="  John  ",
        last_name="  Doe  ",
        email="  stripped@test.com  ",
    )
    
    assert form.is_valid()
    
    # Assert that whitespace was stripped
    assert form.cleaned_data['username'] == 'stripped_user'
    assert form.cleaned_data['first_name'] == 'John'
    assert form.cleaned_data['last_name'] == 'Doe'
    assert form.cleaned_data['email'] == 'stripped@test.com'