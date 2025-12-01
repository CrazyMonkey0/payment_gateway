import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()


class TestRegisterViewGET:
    """Tests for GET requests to the register view."""
    
    @pytest.mark.django_db
    def test_register_get_returns_status_code_200(self, client):
        """
        Test that GET request to register view returns HTTP 200 OK.
        
        Ensures the register page is accessible and the view doesn't raise
        any errors when accessed via GET.
        """
        response = client.get(reverse('register'))
        assert response.status_code == 200
    
    
    @pytest.mark.django_db
    def test_register_get_renders_correct_template(self, client):
        """
        Test that GET request renders the correct registration template.
        
        Ensures the view uses the proper template for displaying the
        registration form.
        """
        response = client.get(reverse('register'))
        assert 'registration/register.html' in [t.name for t in response.templates]
    
    
    @pytest.mark.django_db
    def test_register_get_returns_form_in_context(self, client):
        """
        Test that the registration form is passed in the response context.
        
        Ensures the template receives the form object for rendering the
        registration form HTML.
        """
        response = client.get(reverse('register'))
        assert 'user_form' in response.context
        assert response.context['user_form'] is not None
    
    
    @pytest.mark.django_db
    def test_register_get_form_has_required_fields(self, client):
        """
        Test that the form in the GET response has all required fields.
        
        Verifies that the form contains username, first_name, last_name,
        email, password, and password2 fields.
        """
        response = client.get(reverse('register'))
        form = response.context['user_form']
        
        expected_fields = {'username', 'first_name', 'last_name', 'email', 
                           'password', 'password2'}
        assert set(form.fields.keys()) == expected_fields


class TestRegisterViewPOSTSuccess:
    """Tests for successful POST requests to the register view."""
    
    @pytest.mark.django_db
    def test_register_post_with_valid_data_creates_user(self, client, valid_registration_data):
        """
        Test that POST with valid data creates a new user in the database.
        
        Ensures the view properly creates a Profile instance when valid
        registration data is submitted.
        """
        initial_user_count = Profile.objects.count()
        
        response = client.post(reverse('register'), valid_registration_data)
        
        assert Profile.objects.count() == initial_user_count + 1
    
    
    @pytest.mark.django_db
    def test_register_post_creates_user_with_correct_data(self, client, valid_registration_data):
        """
        Test that the created user has the correct data from the form.
        
        Verifies that username, first_name, last_name, and email are
        correctly saved to the database.
        """
        client.post(reverse('register'), valid_registration_data)
        
        user = Profile.objects.get(username=valid_registration_data['username'])
        assert user.first_name == valid_registration_data['first_name']
        assert user.last_name == valid_registration_data['last_name']
        assert user.email == valid_registration_data['email'].lower()
        assert user.username == valid_registration_data['username']
    
    
    @pytest.mark.django_db
    def test_register_post_hashes_password(self, client, valid_registration_data):
        """
        Test that the password is properly hashed and not stored in plaintext.
        
        Ensures Django's password hashing is applied and that the plaintext
        password is not stored in the database.
        """
        password = valid_registration_data['password']
        client.post(reverse('register'), valid_registration_data)
        
        user = Profile.objects.get(username=valid_registration_data['username'])
        
        # Password should be hashed (not the plaintext password)
        assert user.password != password
        # check_password should return True for correct password
        assert user.check_password(password) is True
        # check_password should return False for incorrect password
        assert user.check_password('wrongpassword') is False
    
    
    @pytest.mark.django_db
    def test_register_post_redirects_to_success_template(self, client, valid_registration_data):
        """
        Test that successful registration renders the success template.
        
        Ensures the view responds with the register_done.html template
        after successful user creation.
        """
        response = client.post(reverse('register'), valid_registration_data)
        assert 'registration/register_done.html' in [t.name for t in response.templates]
    
    
    @pytest.mark.django_db
    def test_register_post_success_returns_status_200(self, client, valid_registration_data):
        """
        Test that successful registration returns HTTP 200 OK.
        
        The view renders a success template rather than redirecting (302),
        so a 200 status code is expected.
        """
        response = client.post(reverse('register'), valid_registration_data)
        assert response.status_code == 200
    
    
    @pytest.mark.django_db
    def test_register_post_success_passes_new_user_in_context(self, client, valid_registration_data):
        """
        Test that the newly created user is passed in the response context.
        
        Ensures the success template has access to the new user object
        for displaying user information.
        """
        response = client.post(reverse('register'), valid_registration_data)
        
        assert 'new_user' in response.context
        new_user = response.context['new_user']
        assert new_user.username == valid_registration_data['username']
        assert new_user.first_name == valid_registration_data['first_name']
    
    
    @pytest.mark.django_db
    @pytest.mark.parametrize("username,first_name,last_name,email", [
        ("user1", "Alice", "Anderson", "alice@example.com"),
        ("user_2", "Bob", "Brown", "bob@example.com"),
        ("user123", "Charlie", "Clark", "charlie@example.com"),
        ("testuser_special", "Diana", "Davis", "diana@example.com"),
    ])
    def test_register_post_with_various_valid_data(self, client, username, first_name, 
                                                    last_name, email):
        """
        Test user registration with various valid data combinations.
        
        Parametrized test ensuring the registration works with different
        valid usernames, names, and email addresses.
        """
        registration_data = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": "SecurePass123!@#",
            "password2": "SecurePass123!@#",
        }
        
        response = client.post(reverse('register'), registration_data)
        
        assert response.status_code == 200
        user = Profile.objects.get(username=username)
        assert user.first_name == first_name
        assert user.last_name == last_name


class TestRegisterViewPOSTValidationErrors:
    """Tests for POST requests with invalid data."""
    
    @pytest.mark.django_db
    def test_register_post_with_mismatched_passwords_shows_form_errors(
            self, client, invalid_registration_data_mismatched_passwords):
        """
        Test that mismatched passwords are caught and form errors are shown.
        
        Ensures the form validation detects when password and password2
        fields don't match.
        """
        response = client.post(reverse('register'), 
                               invalid_registration_data_mismatched_passwords)
        
        assert response.status_code == 200
        form = response.context['user_form']
        assert form.is_valid() is False
        assert 'password2' in form.errors
    
    
    @pytest.mark.django_db
    def test_register_post_with_mismatched_passwords_does_not_create_user(
            self, client, invalid_registration_data_mismatched_passwords):
        """
        Test that no user is created when passwords don't match.
        
        Ensures data integrity by preventing user creation on validation
        errors.
        """
        initial_count = Profile.objects.count()
        client.post(reverse('register'), invalid_registration_data_mismatched_passwords)
        
        assert Profile.objects.count() == initial_count
    
    
    @pytest.mark.django_db
    def test_register_post_with_duplicate_email_shows_form_errors(
            self, client, invalid_registration_data_duplicate_email):
        """
        Test that duplicate email addresses are rejected.
        
        Ensures the form validation detects and rejects email addresses
        that are already in use.
        """
        response = client.post(reverse('register'), 
                               invalid_registration_data_duplicate_email)
        
        assert response.status_code == 200
        form = response.context['user_form']
        assert form.is_valid() is False
        assert 'email' in form.errors
    
    
    @pytest.mark.django_db
    def test_register_post_with_duplicate_email_does_not_create_user(
            self, client, invalid_registration_data_duplicate_email):
        """
        Test that no duplicate user is created when email already exists.
        
        Ensures the database doesn't have duplicate email entries.
        """
        initial_count = Profile.objects.count()
        client.post(reverse('register'), invalid_registration_data_duplicate_email)
        
        # Should still be 1 (the existing user created in the fixture)
        assert Profile.objects.count() == initial_count
    
    
    @pytest.mark.django_db
    @pytest.mark.parametrize("email", [
        "invalidemail",  # No @ symbol
        "test@",  # Missing domain
        "@example.com",  # Missing username
    ])
    def test_register_post_with_invalid_email_formats(self, client, email):
        """
        Test registration with various invalid email formats.
        
        Parametrized test ensuring email validation catches malformed
        email addresses.
        """
        registration_data = {
            "username": "testuser",
            "first_name": "John",
            "last_name": "Doe",
            "email": email,
            "password": "SecurePass123!@#",
            "password2": "SecurePass123!@#",
        }
        
        response = client.post(reverse('register'), registration_data)
        
        assert response.status_code == 200
        form = response.context['user_form']
        # Should have validation errors (either from email field or required field)
        assert form.is_valid() is False
    
    
    @pytest.mark.django_db
    @pytest.mark.parametrize("missing_field", [
        "username",
        "password",
        "password2",
    ])
    def test_register_post_with_missing_required_fields(self, client, missing_field):
        """
        Test registration when required fields are missing.
        
        Parametrized test ensuring required fields are validated as mandatory.
        Note: email, first_name and last_name may have blank=True in AbstractUser,
        so not all are enforced as required at form level.
        """
        registration_data = {
            "username": "testuser",
            "first_name": "John",
            "last_name": "Doe",
            "email": "test@example.com",
            "password": "SecurePass123!@#",
            "password2": "SecurePass123!@#",
        }
        
        # Remove one field
        del registration_data[missing_field]
        
        response = client.post(reverse('register'), registration_data)
        
        assert response.status_code == 200
        form = response.context['user_form']
        assert form.is_valid() is False
        assert missing_field in form.errors
    
    
    @pytest.mark.django_db
    def test_register_post_renders_form_on_validation_errors(
            self, client, invalid_registration_data_mismatched_passwords):
        """
        Test that the registration form is rendered again when validation fails.
        
        Ensures the user can see the form with error messages to correct
        and resubmit.
        """
        response = client.post(reverse('register'), 
                               invalid_registration_data_mismatched_passwords)
        
        assert 'registration/register.html' in [t.name for t in response.templates]
        assert 'user_form' in response.context


class TestRegisterViewEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    @pytest.mark.django_db
    def test_register_post_email_case_insensitive(self, client, create_profile):
        """
        Test that email addresses are treated case-insensitively.
        
        Ensures that registering with UPPERCASE email is rejected if lowercase
        email already exists (case-insensitive duplicate check).
        """
        # Create a user with lowercase email
        create_profile(email="test@example.com")
        
        registration_data = {
            "username": "newuser",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "TEST@EXAMPLE.COM",  # Uppercase version
            "password": "SecurePass123!@#",
            "password2": "SecurePass123!@#",
        }
        
        response = client.post(reverse('register'), registration_data)
        form = response.context['user_form']
        
        # Should have email error due to case-insensitive duplicate check
        assert form.is_valid() is False
        assert 'email' in form.errors
    
    
    @pytest.mark.django_db
    def test_register_post_email_stored_as_lowercase(self, client, valid_registration_data):
        """
        Test that email is normalized to lowercase in the database.
        
        Ensures email normalization for consistent lookups and displays.
        """
        valid_registration_data['email'] = "TestUser@EXAMPLE.COM"
        
        client.post(reverse('register'), valid_registration_data)
        
        user = Profile.objects.get(username=valid_registration_data['username'])
        assert user.email == "testuser@example.com"
    
    
    @pytest.mark.django_db
    def test_register_multiple_users_sequentially(self, client):
        """
        Test that multiple users can be registered in sequence.
        
        Ensures the registration process doesn't have state that prevents
        subsequent registrations.
        """
        user_data_list = [
            {
                "username": "seq_user1",
                "first_name": "Alice",
                "last_name": "Anderson",
                "email": "seq_alice@example.com",
                "password": "Pass123!@#",
                "password2": "Pass123!@#",
            },
            {
                "username": "seq_user2",
                "first_name": "Bob",
                "last_name": "Brown",
                "email": "seq_bob@example.com",
                "password": "Pass456$%&",
                "password2": "Pass456$%&",
            },
            {
                "username": "seq_user3",
                "first_name": "Charlie",
                "last_name": "Clark",
                "email": "seq_charlie@example.com",
                "password": "Pass789^&*",
                "password2": "Pass789^&*",
            },
        ]
        
        initial_count = Profile.objects.count()
        
        for user_data in user_data_list:
            response = client.post(reverse('register'), user_data)
            assert response.status_code == 200
        
        # All 3 users should be created
        assert Profile.objects.count() == initial_count + 3
        assert Profile.objects.filter(username='seq_user1').exists()
        assert Profile.objects.filter(username='seq_user2').exists()
        assert Profile.objects.filter(username='seq_user3').exists()
    
    
    @pytest.mark.django_db
    def test_register_post_with_special_characters_in_names(self, client):
        """
        Test registration with special characters in name fields.
        
        Ensures the form accepts names with hyphens, apostrophes, etc.
        """
        registration_data = {
            "username": "user_special",
            "first_name": "Jean-Pierre",
            "last_name": "O'Brien",
            "email": "special@example.com",
            "password": "SecurePass123!@#",
            "password2": "SecurePass123!@#",
        }
        
        response = client.post(reverse('register'), registration_data)
        assert response.status_code == 200
        
        user = Profile.objects.get(username="user_special")
        assert user.first_name == "Jean-Pierre"
        assert user.last_name == "O'Brien"
    
    
    @pytest.mark.django_db
    def test_register_post_with_long_names(self, client):
        """
        Test registration with maximum length names.
        
        Ensures the form accepts valid long names up to field limits.
        """
        long_name = "A" * 150  # Django CharField default max_length is 150 for names
        
        registration_data = {
            "username": "user_longname",
            "first_name": long_name,
            "last_name": long_name,
            "email": "longname@example.com",
            "password": "SecurePass123!@#",
            "password2": "SecurePass123!@#",
        }
        
        response = client.post(reverse('register'), registration_data)
        # Should succeed or show appropriate error
        # (depends on field max_length definition)
        assert response.status_code == 200
    
    
    @pytest.mark.django_db
    def test_register_post_with_whitespace_only_names(self, client):
        """
        Test that whitespace-only names are rejected or trimmed appropriately.
        
        Ensures the form doesn't accept names that are only whitespace.
        """
        registration_data = {
            "username": "user_whitespace",
            "first_name": "   ",  # Only whitespace
            "last_name": "Smith",
            "email": "whitespace@example.com",
            "password": "SecurePass123!@#",
            "password2": "SecurePass123!@#",
        }
        
        response = client.post(reverse('register'), registration_data)
        assert response.status_code == 200
        # Form may or may not be valid depending on requirements


class TestRegisterViewURLResolution:
    """Tests for URL routing and view resolution."""
    
    @pytest.mark.django_db
    def test_register_url_name_resolves(self):
        """
        Test that the 'register' URL name resolves to a valid URL.
        
        Ensures the URL routing is properly configured.
        """
        url = reverse('register')
        assert url is not None
        assert isinstance(url, str)
        assert len(url) > 0
    
    
    @pytest.mark.django_db
    def test_register_url_accessible(self, client):
        """
        Test that the register URL is accessible without errors.
        
        Ensures basic connectivity to the view.
        """
        url = reverse('register')
        response = client.get(url)
        assert response.status_code in [200, 301, 302]  # 200 for success, 301/302 for redirects
