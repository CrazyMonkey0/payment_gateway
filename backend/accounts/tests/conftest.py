import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from oauth2_provider.models import Application
from accounts.models import Profile
from accounts.forms import UserRegistrationForm, ProfileForm
from bank.models import Bank

User = get_user_model()


# PROFILE / USER CREATION FIXTURES


@pytest.fixture
def create_profile():
    """
    Factory fixture to create Profile instances with customizable attributes.
    
    Usage:
        profile = create_profile(username='testuser', password='pass123')
        profile = create_profile(email='new@test.com', iban='DE89370400440532013000')
    
    Returns:
        function: Factory function that creates Profile instances
    """
    def _factory(**kwargs):
        password = kwargs.pop("password", "testpass123")
        defaults = {
            "username": "testuser",
            "first_name": "John",
            "last_name": "Doe",
            "email": "test@example.com",
            "iban": "DE89370400440532013000",
            "url_feedback": "default-feedback",
        }
        defaults.update(kwargs)
        
        profile = Profile.objects.create_user(password=password, **defaults)
        return profile
    
    return _factory


@pytest.fixture
def user_factory(db):
    """
    Factory fixture to create user profiles with minimal required fields.
    
    Usage:
        user = user_factory(username='customuser', email='custom@test.com')
    
    Returns:
        function: Factory function that creates Profile instances
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


# FORM DATA FACTORIES


@pytest.fixture
def valid_registration_data():
    """
    Fixture providing valid registration form data for successful registration.
    
    Returns:
        dict: Dictionary with all required fields for UserRegistrationForm
    """
    return {
        "username": "testuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "testuser@example.com",
        "password": "SecurePass123!@#",
        "password2": "SecurePass123!@#",
    }


@pytest.fixture
def create_registration_form():
    """
    Factory fixture to create UserRegistrationForm instances with configurable data.
    
    Usage:
        form = create_registration_form(email='new@test.com', password='newpass')
        form = create_registration_form(username='alice', first_name='Alice')
    
    Returns:
        function: Factory function that creates UserRegistrationForm instances
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
        data.update(kwargs)
        return UserRegistrationForm(data=data)
    
    return _factory


@pytest.fixture
def valid_form_data():
    """
    Fixture providing complete valid registration data.
    
    Used primarily for form save tests to ensure unique, predictable data.
    
    Returns:
        dict: Dictionary with valid user registration data
    """
    return {
        "username": "save_testuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "save_test@test.com",
        "password": "SecurePass123!@#",
        "password2": "SecurePass123!@#",
    }


@pytest.fixture
def invalid_registration_data_mismatched_passwords():
    """
    Fixture providing registration data with mismatched passwords for error testing.
    
    Returns:
        dict: Dictionary with mismatched password fields
    """
    return {
        "username": "testuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "testuser@example.com",
        "password": "SecurePass123!@#",
        "password2": "DifferentPass456",
    }


@pytest.fixture
def invalid_registration_data_duplicate_email(create_profile):
    """
    Fixture providing registration data with an email that already exists in database.
    
    This fixture automatically creates a user with the conflicting email.
    
    Args:
        create_profile: The create_profile fixture (auto-injected)
    
    Returns:
        dict: Dictionary with registration data using duplicate email
    """
    create_profile(email="existing@example.com")
    
    return {
        "username": "newuser",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "existing@example.com",
        "password": "SecurePass123!@#",
        "password2": "SecurePass123!@#",
    }


@pytest.fixture
def form_data_factory():
    """
    Factory fixture to create ProfileForm data with configurable values.
    
    Usage:
        data = form_data_factory(first_name='Alice', email='alice@test.com')
        form = ProfileForm(data=data)
    
    Returns:
        function: Factory function that creates form data dictionaries
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


# BANK / IBAN FIXTURES


@pytest.fixture
def create_bank(db):
    """
    Factory fixture to create Bank instances with IBAN.
    
    Usage:
        bank = create_bank(iban='DE89370400440532013000', balance=5000.00)
    
    Args:
        db: pytest-django database access fixture (auto-injected)
    
    Returns:
        function: Factory function that creates Bank instances
    """
    def _create(iban, balance=1000.00):
        return Bank.objects.create(iban=iban, balance=balance)
    
    return _create


# CLIENT / AUTHENTICATION FIXTURES


@pytest.fixture
def client():
    """
    Fixture providing a Django test client for making HTTP requests.
    
    Usage:
        response = client.get('/accounts/register/')
        response = client.post('/accounts/register/', data={...})
    
    Returns:
        Client: Django test client instance
    """
    return Client()


@pytest.fixture
def authenticated_client(db):
    """
    Fixture providing an authenticated test client with a logged-in test user.
    
    Usage:
        client, user = authenticated_client
        response = client.get('/dashboard/')  # User is authenticated
    
    Returns:
        tuple: (client, user) - Client object and associated User instance
    """
    user = User.objects.create_user(username='testuser', password='testpass123')
    client = Client()
    client.force_login(user)
    return client, user


# OAUTH2 FIXTURES


@pytest.fixture
def user_with_application(db):
    """
    Fixture providing a user with an existing OAuth2 application.
    
    Usage:
        user, app = user_with_application
        assert app.user == user
        assert app.name == 'Existing App'
    
    Returns:
        tuple: (user, application) - User instance and associated Application
    """
    user = User.objects.create_user(username='appuser', password='apppass123')
    app = Application.objects.create(
        user=user,
        name='Existing App',
        client_id='app-client-id-12345',
        client_secret='app-client-secret-67890',
        client_type=Application.CLIENT_PUBLIC,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        redirect_uris='http://localhost:8000/callback'
    )
    return user, app


@pytest.fixture
def authenticated_user_with_app(db):
    """
    Fixture providing an authenticated client for a user with an OAuth2 application.
    
    Usage:
        client, user, app = authenticated_user_with_app
        response = client.get(reverse('manage_application'))
    
    Returns:
        tuple: (client, user, application) - Authenticated client, user, and app
    """
    user = User.objects.create_user(username='appuser', password='apppass123')
    app = Application.objects.create(
        user=user,
        name='Test App',
        client_id='test-client-id',
        client_secret='test-client-secret',
        client_type=Application.CLIENT_PUBLIC,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        redirect_uris='http://localhost:8000/callback'
    )
    client = Client()
    client.force_login(user)
    return client, user, app
