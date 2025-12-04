from django.test import TestCase
from django.contrib.auth import get_user_model
from oauth2_provider.models import Application
from accounts.forms import CustomRegistrationFormOAuth2
from django.contrib.auth.hashers import check_password

User = get_user_model()


class CustomRegistrationFormOAuth2CreateModeTests(TestCase):
    """Tests for CREATE mode (new application)."""
    
    def setUp(self):
        """Preparing the user for testing."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_mode_client_id_and_secret_fields_are_hidden(self):
        """
        In CREATE mode, the client_id and client_secret fields should be hidden
        (HiddenInput widget).
        """
        # Arrange & Act
        form = CustomRegistrationFormOAuth2()
        
        # Assert
        self.assertEqual(
            form.fields['client_id'].widget.__class__.__name__,
            'HiddenInput'
        )
        self.assertEqual(
            form.fields['client_secret'].widget.__class__.__name__,
            'HiddenInput'
        )
    
    def test_create_mode_sets_default_client_type_and_grant_type(self):
        """
        The new instance should have the following default values set:
        - client_type = PUBLIC
        - authorization_grant_type = AUTHORIZATION_CODE
        """
        # Arrange & Act
        form = CustomRegistrationFormOAuth2()
        
        # Assert
        self.assertEqual(
            form.instance.client_type,
            Application.CLIENT_PUBLIC
        )
        self.assertEqual(
            form.instance.authorization_grant_type,
            Application.GRANT_AUTHORIZATION_CODE
        )
    
    def test_valid_form_with_minimal_data(self):
        """The form should be correct with the minimum required data."""
        # Arrange
        form_data = {
            'name': 'Test App',
            'redirect_uris': 'http://localhost:8000/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_valid_form_with_multiple_redirect_uris(self):
        """The form should accept multiple redirect URIs (each on a new line)."""
        # Arrange
        form_data = {
            'name': 'Multi URI App',
            'redirect_uris': 'http://localhost:8000/callback\nhttps://example.com/oauth/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_invalid_name_too_short(self):
        """Application names shorter than 3 characters should be rejected."""
        # Arrange
        form_data = {
            'name': 'Ab',  # 2 characters
            'redirect_uris': 'http://localhost:8000/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('at least 3 characters', str(form.errors['name']))
    
    def test_invalid_name_empty(self):
        """An empty application name should be rejected."""
        # Arrange
        form_data = {
            'name': '',
            'redirect_uris': 'http://localhost:8000/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_invalid_name_only_whitespace(self):
        """Name consisting only of whitespace should be rejected."""
        # Arrange
        form_data = {
            'name': '   ',
            'redirect_uris': 'http://localhost:8000/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_invalid_redirect_uris_empty(self):
        """An empty redirect_uris field should be rejected."""
        # Arrange
        form_data = {
            'name': 'Test App',
            'redirect_uris': ''
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('redirect_uris', form.errors)
        self.assertIn('At least one redirect URI is required', str(form.errors['redirect_uris']))
    
    def test_invalid_redirect_uris_only_whitespace(self):
        """Redirect_uris with only whitespace should be rejected."""
        # Arrange
        form_data = {
            'name': 'Test App',
            'redirect_uris': '   \n   \n   '
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('redirect_uris', form.errors)
    
    def test_invalid_redirect_uri_without_protocol(self):
        """URI without http/https protocol should be rejected."""
        # Arrange
        form_data = {
            'name': 'Test App',
            'redirect_uris': 'localhost:8000/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('redirect_uris', form.errors)
        self.assertIn('Must start with http:// or https://', str(form.errors['redirect_uris']))
    
    def test_invalid_redirect_uri_with_ftp_protocol(self):
        """URI with unsupported ftp:// protocol should be rejected."""
        # Arrange
        form_data = {
            'name': 'Test App',
            'redirect_uris': 'ftp://example.com/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('redirect_uris', form.errors)
    
    def test_mixed_valid_and_invalid_uris(self):
        """If one of multiple URIs is invalid, the form should be rejected."""
        # Arrange
        form_data = {
            'name': 'Test App',
            'redirect_uris': 'http://localhost:8000/callback\ninvalid-uri\nhttps://example.com/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('redirect_uris', form.errors)
    
    def test_redirect_uris_with_empty_lines_are_ignored(self):
        """Empty lines in redirect_uris should be ignored."""
        # Arrange
        form_data = {
            'name': 'Test App',
            'redirect_uris': 'http://localhost:8000/callback\n\n\nhttps://example.com/callback\n\n'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_name_is_trimmed(self):
        """Leading and trailing whitespace in name should be trimmed."""
        # Arrange
        form_data = {
            'name': '  Test App  ',
            'redirect_uris': 'http://localhost:8000/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['name'], 'Test App')


class CustomRegistrationFormOAuth2EditModeTests(TestCase):
    """Tests for EDIT mode (existing application)."""
    
    def setUp(self):
        """Preparing a user and an existing application for testing."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.app = Application.objects.create(
            name='Existing App',
            user=self.user,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://localhost:8000/callback',
            client_id='test-client-id-12345',
            client_secret='test-client-secret-67890'
        )
    
    def test_edit_mode_client_id_and_secret_fields_are_readonly(self):
        """
        In EDIT mode, the client_id and client_secret fields should be disabled
        (read-only).
        """
        # Arrange & Act
        form = CustomRegistrationFormOAuth2(instance=self.app)
        
        # Assert
        self.assertTrue(form.fields['client_id'].disabled)
        self.assertTrue(form.fields['client_secret'].disabled)
    
    def test_edit_mode_displays_existing_client_id_and_secret(self):
        """
        In EDIT mode, the form should display the existing client_id and client_secret values.
        """
        # Arrange & Act
        form = CustomRegistrationFormOAuth2(instance=self.app)
        
        # Assert
        self.assertEqual(
            form.fields['client_id'].initial,
            'test-client-id-12345'
        )
        self.assertTrue(check_password('test-client-secret-67890', form.fields['client_secret'].initial))
    
    def test_edit_mode_name_can_be_updated(self):
        """Name should be updatable in EDIT mode."""
        # Arrange
        form_data = {
            'name': 'Updated App Name',
            'redirect_uris': 'http://localhost:8000/callback',
            'client_id': self.app.client_id,
            'client_secret': self.app.client_secret
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data, instance=self.app)
        
        # Assert
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['name'], 'Updated App Name')
    
    def test_edit_mode_redirect_uris_can_be_updated(self):
        """Redirect URIs should be updatable in EDIT mode."""
        # Arrange
        form_data = {
            'name': 'Existing App',
            'redirect_uris': 'https://newdomain.com/callback',
            'client_id': self.app.client_id,
            'client_secret': self.app.client_secret
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data, instance=self.app)
        
        # Assert
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.cleaned_data['redirect_uris'],
            'https://newdomain.com/callback'
        )
    
    def test_edit_mode_client_id_cannot_be_changed_by_user(self):
        """
        Security: client_id cannot be changed by the user,
        even if they try to submit a different value.
        """
        # Arrange
        malicious_client_id = 'hacked-client-id'
        form_data = {
            'name': 'Existing App',
            'redirect_uris': 'http://localhost:8000/callback',
            'client_id': malicious_client_id,  # Próba zmiany
            'client_secret': self.app.client_secret
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data, instance=self.app)
        
        # Assert
        self.assertTrue(form.is_valid())
        # Should return the ORIGINAL client_id, not the one from the form
        self.assertEqual(
            form.cleaned_data['client_id'],
            'test-client-id-12345'
        )
        self.assertNotEqual(
            form.cleaned_data['client_id'],
            malicious_client_id
        )
    
    def test_edit_mode_client_secret_cannot_be_changed_by_user(self):
        """
        Security: client_secret cannot be changed by the user,
        even if they try to submit a different value.
        """
        # Arrange
        malicious_client_secret = 'hacked-client-secret'
        form_data = {
            'name': 'Existing App',
            'redirect_uris': 'http://localhost:8000/callback',
            'client_id': self.app.client_id,
            'client_secret': malicious_client_secret  # Próba zmiany
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data, instance=self.app)
        
        # Assert
        self.assertTrue(form.is_valid())
        # It should return the ORIGINAL client_secret, not the one from the form.
        self.assertTrue(check_password('test-client-secret-67890', form.instance.client_secret))
        self.assertNotEqual(
            form.cleaned_data['client_secret'],
            malicious_client_secret
        )
    
    def test_edit_mode_with_invalid_name(self):
        """In EDIT mode, name validation should still work."""
        # Arrange
        form_data = {
            'name': 'Ab',  # Za krótka
            'redirect_uris': 'http://localhost:8000/callback',
            'client_id': self.app.client_id,
            'client_secret': self.app.client_secret
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data, instance=self.app)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_edit_mode_with_invalid_redirect_uris(self):
        """In EDIT mode, redirect_uris validation should still work."""
        # Arrange
        form_data = {
            'name': 'Existing App',
            'redirect_uris': 'invalid-uri',
            'client_id': self.app.client_id,
            'client_secret': self.app.client_secret
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data, instance=self.app)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('redirect_uris', form.errors)


class CustomRegistrationFormOAuth2SecurityTests(TestCase):
    """Tests for security-related aspects of the form."""
    
    def setUp(self):
        """Preparing a user and an existing application for testing."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.app = Application.objects.create(
            name='Secure App',
            user=self.user,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://localhost:8000/callback',
            client_id='secure-client-id',
            client_secret='secure-client-secret'
        )
    
    def test_xss_attempt_in_name_field(self):
        """
        SECURITY: Attempted XSS in the name field should be handled safely.
        """
        # Arrange
        xss_payload = '<script>alert("XSS")</script>'
        form_data = {
            'name': xss_payload,
            'redirect_uris': 'http://localhost:8000/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        # The form should be technically valid (Django escapes in templates)
        self.assertTrue(form.is_valid())
        # But the value should be stored as-is (escaping happens in the template)
        self.assertEqual(form.cleaned_data['name'], xss_payload)
    
    def test_sql_injection_attempt_in_name_field(self):
        """
        SECURITY: SQL injection attempt in the name field.
        Django ORM protects against this automatically.
        """
        # Arrange
        sql_payload = "Test'; DROP TABLE oauth2_provider_application;--"
        form_data = {
            'name': sql_payload,
            'redirect_uris': 'http://localhost:8000/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        # The form should be valid (Django ORM protects against SQL injection).
        self.assertTrue(form.is_valid())
    
    def test_redirect_uri_with_javascript_protocol(self):
        """
        SECURITY: URI with javascript: protocol should be rejected.
        """
        # Arrange
        form_data = {
            'name': 'Test App',
            'redirect_uris': 'javascript:alert("XSS")'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('redirect_uris', form.errors)
    
    def test_redirect_uri_with_data_protocol(self):
        """
        SECURITY: URI with data: protocol should be rejected.
        """
        # Arrange
        form_data = {
            'name': 'Test App',
            'redirect_uris': 'data:text/html,<script>alert("XSS")</script>'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('redirect_uris', form.errors)
    
    def test_very_long_name_field(self):
        """
        Test handling of very long names in the application name field.
        """
        # Arrange
        very_long_name = 'A' * 10000
        form_data = {
            'name': very_long_name,
            'redirect_uris': 'http://localhost:8000/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        # The Model Application has max_length on the name field (usually 255)
        # The form should be valid, but the database will truncate the value
        # or throw an exception when saving (depending on the configuration)
        self.assertFalse(form.is_valid()) 
        self.assertIn('name', form.errors)
    
    def test_unicode_characters_in_name(self):
        """Test handling of Unicode characters in the application name."""
        # Arrange
        unicode_name = 'Тестовое приложение 测试应用 🚀'
        form_data = {
            'name': unicode_name,
            'redirect_uris': 'http://localhost:8000/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['name'], unicode_name)


class CustomRegistrationFormOAuth2EdgeCasesTests(TestCase):
    """Tests for edge cases in the form."""
    
    def test_redirect_uris_with_trailing_whitespace(self):
        """Trailing and leading whitespace in redirect URIs should be trimmed."""
        # Arrange
        form_data = {
            'name': 'Test App',
            'redirect_uris': 'http://localhost:8000/callback   \n   https://example.com/callback   '
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_redirect_uris_with_query_parameters(self):
        """URIs with query parameters should be accepted."""
        # Arrange
        form_data = {
            'name': 'Test App',
            'redirect_uris': 'http://localhost:8000/callback?param=value&other=123'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_redirect_uris_with_fragments(self):
        """URIs with fragments should be accepted."""
        # Arrange
        form_data = {
            'name': 'Test App',
            'redirect_uris': 'http://localhost:8000/callback#section'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid()) 
        self.assertIn('__all__', form.errors) 
        self.assertIn('Redirect URIs must not contain fragments', str(form.errors))
    
    def test_redirect_uri_with_port_number(self):
        """URIs with explicit port numbers should be accepted."""
        # Arrange
        form_data = {
            'name': 'Test App',
            'redirect_uris': 'http://localhost:3000/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_redirect_uri_localhost_vs_127001(self):
        """Both localhost and 127.0.0.1 should be accepted."""
        # Arrange
        form_data = {
            'name': 'Test App',
            'redirect_uris': 'http://localhost:8000/callback\nhttp://127.0.0.1:8000/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_name_with_special_characters(self):
        """Name with special characters should be accepted."""
        # Arrange
        form_data = {
            'name': "Test-App_2024 (v1.0)",
            'redirect_uris': 'http://localhost:8000/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_name_exactly_3_characters(self):
        """Name with exactly 3 characters should be accepted."""
        # Arrange
        form_data = {
            'name': 'App',
            'redirect_uris': 'http://localhost:8000/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_multiple_identical_redirect_uris(self):
        """Duplicate redirect URIs should be accepted."""
        # Arrange
        form_data = {
            'name': 'Test App',
            'redirect_uris': 'http://localhost:8000/callback\nhttp://localhost:8000/callback'
        }
        
        # Act
        form = CustomRegistrationFormOAuth2(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid(), form.errors)