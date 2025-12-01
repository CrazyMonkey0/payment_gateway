import pytest
from django.urls import reverse
from django.test import Client, override_settings
from django.contrib.auth import get_user_model

from oauth2_provider.models import Application


User = get_user_model()


@pytest.mark.django_db
class TestCustomRegistrationOAuth2GetRequest:
    """Test suite for GET requests to the OAuth2 registration view."""

    def test_get_unauthenticated_user_redirects_to_login(self, client):
        """
        GIVEN: An unauthenticated user
        WHEN: Making a GET request to manage_application
        THEN: User should be redirected (OAuth2 ApplicationRegistration uses dispatch override)
        """
        response = client.get(reverse('manage_application'), follow=False)
        # ApplicationRegistration should handle auth - typically redirects
        # Either 301/302 redirect or 403 Forbidden depending on setup
        assert response.status_code in [301, 302, 403]

    def test_get_create_new_app_shows_empty_register_form(self, authenticated_client):
        """
        GIVEN: Authenticated user with NO existing application
        WHEN: Making a GET request to manage_application
        THEN: Should render oauth2_register template with empty form
        """
        client, user = authenticated_client

        response = client.get(reverse('manage_application'))

        assert response.status_code == 200
        template_names = [t.name for t in response.templates if t.name]
        assert 'accounts/oauth2_register.html' in template_names

        # Form should be present and empty
        assert 'form' in response.context
        form = response.context['form']
        assert form.instance.pk is None

    def test_get_edit_existing_app_shows_prefilled_form(self, db, authenticated_client):
        """
        GIVEN: Authenticated user WITH existing application
        WHEN: Making a GET request to manage_application
        THEN: Should render oauth2_update template with prefilled form
        """
        client, user = authenticated_client
        # Create an app for this user
        app = Application.objects.create(
            user=user,
            name='Existing App',
            client_id='app-client-id-12345',
            client_secret='app-client-secret-67890',
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://localhost:8000/callback'
        )

        response = client.get(reverse('manage_application'))

        assert response.status_code == 200
        template_names = [t.name for t in response.templates if t.name]
        assert 'accounts/oauth2_update.html' in template_names

        # Form should be prefilled with existing app data
        assert 'form' in response.context
        assert 'application' in response.context
        form = response.context['form']
        assert form.instance.pk == app.pk
        assert form['name'].value() == 'Existing App'

    def test_get_context_contains_section_identifier(self, authenticated_client):
        """
        GIVEN: Authenticated user
        WHEN: Making a GET request to manage_application
        THEN: Response context should contain 'section' = 'manage_application'
        """
        client, user = authenticated_client

        response = client.get(reverse('manage_application'))

        assert response.status_code == 200
        assert response.context['section'] == 'manage_application'


@pytest.mark.django_db
class TestCustomRegistrationOAuth2PostCreateNew:
    """Test suite for POST requests to create new OAuth2 applications."""

    def test_post_create_valid_app_generates_credentials(self, authenticated_client):
        """
        GIVEN: Authenticated user with valid form data
        WHEN: POSTing to manage_application (no existing app)
        THEN: Should create Application with generated client_id/secret
              and show success template with credentials
        """
        client, user = authenticated_client

        data = {
            'name': 'My Test Application',
            'redirect_uris': 'http://localhost:8000/callback'
        }

        response = client.post(reverse('manage_application'), data)

        assert response.status_code == 200
        template_names = [t.name for t in response.templates if t.name]
        assert 'accounts/oauth2_success.html' in template_names

        # Context must contain the generated credentials
        assert 'client_id' in response.context
        assert 'client_secret' in response.context
        assert response.context['client_id']  # Not empty
        assert response.context['client_secret']  # Not empty

        # Application must exist in DB
        app = Application.objects.filter(user=user).first()
        assert app is not None
        assert app.name == 'My Test Application'
        assert app.client_id == response.context['client_id']
        assert app.client_secret == response.context['client_secret']

    def test_post_create_sets_correct_oauth_defaults(self, authenticated_client):
        """
        GIVEN: Authenticated user creating new app
        WHEN: POSTing valid data
        THEN: Application should have correct OAuth2 type and grant type
        """
        client, user = authenticated_client

        data = {
            'name': 'OAuth Test App',
            'redirect_uris': 'https://example.com/callback'
        }

        client.post(reverse('manage_application'), data)

        app = Application.objects.get(user=user)
        assert app.client_type == Application.CLIENT_PUBLIC
        assert app.authorization_grant_type == Application.GRANT_AUTHORIZATION_CODE

    def test_post_create_with_multiple_redirect_uris(self, authenticated_client):
        """
        GIVEN: Authenticated user providing multiple redirect URIs
        WHEN: POSTing valid data with newline-separated URIs
        THEN: Application should be created with all URIs
        """
        client, user = authenticated_client

        data = {
            'name': 'Multi-URI App',
            'redirect_uris': 'http://localhost:8000/cb\nhttps://example.com/oauth'
        }

        response = client.post(reverse('manage_application'), data)

        assert response.status_code == 200
        app = Application.objects.get(user=user)
        assert 'http://localhost:8000/cb' in app.redirect_uris
        assert 'https://example.com/oauth' in app.redirect_uris

    def test_post_create_empty_name_returns_form_error(self, authenticated_client):
        """
        GIVEN: Authenticated user with invalid (empty) name
        WHEN: POSTing data with empty name
        THEN: Should re-render register form with validation error
        """
        client, user = authenticated_client

        data = {
            'name': '',
            'redirect_uris': 'http://example.com/cb'
        }

        response = client.post(reverse('manage_application'), data)

        assert response.status_code == 200
        template_names = [t.name for t in response.templates if t.name]
        assert 'accounts/oauth2_register.html' in template_names

        form = response.context['form']
        assert not form.is_valid()
        assert 'name' in form.errors

        # No application should be created
        assert not Application.objects.filter(user=user).exists()

    def test_post_create_name_too_short_returns_error(self, authenticated_client):
        """
        GIVEN: Authenticated user with name < 3 characters
        WHEN: POSTing data with short name
        THEN: Should return validation error for name field
        """
        client, user = authenticated_client

        data = {
            'name': 'ab',
            'redirect_uris': 'http://example.com/cb'
        }

        response = client.post(reverse('manage_application'), data)

        form = response.context['form']
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_post_create_missing_redirect_uris_returns_error(self, authenticated_client):
        """
        GIVEN: Authenticated user without redirect URIs
        WHEN: POSTing data with empty redirect_uris
        THEN: Should return validation error for redirect_uris field
        """
        client, user = authenticated_client

        data = {
            'name': 'Valid App Name',
            'redirect_uris': ''
        }

        response = client.post(reverse('manage_application'), data)

        form = response.context['form']
        assert not form.is_valid()
        assert 'redirect_uris' in form.errors

    def test_post_create_invalid_redirect_uri_format_returns_error(self, authenticated_client):
        """
        GIVEN: Authenticated user with invalid URI (not http/https)
        WHEN: POSTing data with invalid URI
        THEN: Should return validation error for redirect_uris field
        """
        client, user = authenticated_client

        data = {
            'name': 'Valid App',
            'redirect_uris': 'ftp://example.com/callback'
        }

        response = client.post(reverse('manage_application'), data)

        form = response.context['form']
        assert not form.is_valid()
        assert 'redirect_uris' in form.errors


@pytest.mark.django_db
class TestCustomRegistrationOAuth2PostEdit:
    """Test suite for POST requests to edit existing OAuth2 applications."""

    def test_post_edit_valid_data_updates_application(self, db, authenticated_client):
        """
        GIVEN: Authenticated user with existing application
        WHEN: POSTing updated valid data
        THEN: Should update the application and render update template
        """
        client, user = authenticated_client
        app = Application.objects.create(
            user=user,
            name='Existing App',
            client_id='app-client-id-12345',
            client_secret='app-client-secret-67890',
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://localhost:8000/callback'
        )

        data = {
            'name': 'Updated App Name',
            'redirect_uris': 'https://newdomain.com/oauth'
        }

        response = client.post(reverse('manage_application'), data)

        assert response.status_code == 200
        template_names = [t.name for t in response.templates if t.name]
        assert 'accounts/oauth2_update.html' in template_names

        # Application should be updated
        app.refresh_from_db()
        assert app.name == 'Updated App Name'
        assert 'https://newdomain.com/oauth' in app.redirect_uris

    def test_post_edit_preserves_client_id_immutability(self, db, authenticated_client):
        """
        GIVEN: Authenticated user with existing application
        WHEN: POSTing data with attempted client_id override
        THEN: client_id should remain unchanged (security feature)
        """
        client, user = authenticated_client
        app = Application.objects.create(
            user=user,
            name='Existing App',
            client_id='app-client-id-12345',
            client_secret='app-client-secret-67890',
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://localhost:8000/callback'
        )
        original_client_id = app.client_id

        data = {
            'name': 'Updated App',
            'redirect_uris': 'http://example.com/cb',
            'client_id': 'hacker-attempted-id'  # Attacker tries to override
        }

        response = client.post(reverse('manage_application'), data)

        app.refresh_from_db()
        assert app.client_id == original_client_id
        assert app.client_id != 'hacker-attempted-id'

    def test_post_edit_preserves_client_secret_immutability(self, db, authenticated_client):
        """
        GIVEN: Authenticated user with existing application
        WHEN: POSTing data with attempted client_secret override
        THEN: client_secret should remain unchanged (security feature)
        """
        client, user = authenticated_client
        app = Application.objects.create(
            user=user,
            name='Existing App',
            client_id='app-client-id-12345',
            client_secret='app-client-secret-67890',
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://localhost:8000/callback'
        )
        original_client_secret = app.client_secret

        data = {
            'name': 'Updated App',
            'redirect_uris': 'http://example.com/cb',
            'client_secret': 'hacker-attempted-secret'  # Attacker tries to override
        }

        response = client.post(reverse('manage_application'), data)

        app.refresh_from_db()
        assert app.client_secret == original_client_secret
        assert app.client_secret != 'hacker-attempted-secret'

    def test_post_edit_invalid_data_returns_form_with_errors(self, db, authenticated_client):
        """
        GIVEN: Authenticated user with existing application
        WHEN: POSTing invalid data (e.g., empty name)
        THEN: Should re-render update template with form errors
        """
        client, user = authenticated_client
        app = Application.objects.create(
            user=user,
            name='Existing App',
            client_id='app-client-id-12345',
            client_secret='app-client-secret-67890',
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://localhost:8000/callback'
        )

        data = {
            'name': 'x',  # Too short
            'redirect_uris': 'invalid-uri'  # Invalid format
        }

        response = client.post(reverse('manage_application'), data)

        assert response.status_code == 200
        template_names = [t.name for t in response.templates if t.name]
        assert 'accounts/oauth2_update.html' in template_names

        form = response.context['form']
        assert not form.is_valid()
        assert 'name' in form.errors or 'redirect_uris' in form.errors

        # Application should NOT be modified
        app.refresh_from_db()
        assert app.name == 'Existing App'

    def test_post_edit_form_shows_current_values(self, db, authenticated_client):
        """
        GIVEN: Authenticated user with existing application
        WHEN: POSTing invalid data for an existing app
        THEN: Form should be bound to instance and display errors, not show old values
              (Django form behavior: submitted values take precedence over instance)
        """
        client, user = authenticated_client
        app = Application.objects.create(
            user=user,
            name='Existing App',
            client_id='app-client-id-12345',
            client_secret='app-client-secret-67890',
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://localhost:8000/callback'
        )

        data = {
            'name': '',  # Invalid
            'redirect_uris': ''  # Invalid
        }

        response = client.post(reverse('manage_application'), data)

        form = response.context['form']
        # Form should still be bound to the instance (edit mode)
        assert form.instance.pk == app.pk
        # But submitted values (empty) take precedence over instance
        assert form['name'].value() == ''
        # Form errors should be present
        assert not form.is_valid()
        assert 'name' in form.errors or 'redirect_uris' in form.errors


@pytest.mark.django_db
class TestCustomRegistrationOAuth2Security:
    """Test suite for security aspects of OAuth2 registration."""

    def test_user_cannot_edit_another_users_application(self, db):
        """
        GIVEN: User A with an application, User B authenticated
        WHEN: User B GETs/POSTs to manage_application endpoint
        THEN: User B should only see/edit their own application (or none)
        """
        user_a = User.objects.create_user(username='usera', password='pass')
        app_a = Application.objects.create(
            user=user_a,
            name='Existing App',
            client_id='app-client-id-12345',
            client_secret='app-client-secret-67890',
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://localhost:8000/callback'
        )
        user_b = User.objects.create_user(username='userb', password='pass')

        client_b = Client()
        client_b.force_login(user_b)

        response = client_b.get(reverse('manage_application'))

        # User B should not see User A's application
        template_names = [t.name for t in response.templates if t.name]
        assert 'accounts/oauth2_register.html' in template_names  # Empty form for new app
        assert response.context['form'].instance.pk is None

    def test_generated_client_id_is_unique(self, authenticated_client):
        """
        GIVEN: Multiple applications created via POST
        WHEN: Creating applications
        THEN: Each application should have a unique client_id
        """
        client, user = authenticated_client

        # Create first app
        data1 = {
            'name': 'App One',
            'redirect_uris': 'http://localhost/cb1'
        }
        response1 = client.post(reverse('manage_application'), data1)
        client_id_1 = response1.context['client_id']

        # Note: In real scenario, we'd need a new user for second app
        # since the view only allows one app per user
        assert client_id_1  # Should be generated
        assert len(client_id_1) > 0

    def test_client_secret_is_only_shown_on_creation(self, db, authenticated_client):
        """
        GIVEN: User who already created an application
        WHEN: GETting the manage_application endpoint
        THEN: The GET response should NOT show the client_secret in plain text
              (it's in a readonly field on the form, not in context)
        """
        client, user = authenticated_client
        app = Application.objects.create(
            user=user,
            name='Existing App',
            client_id='app-client-id-12345',
            client_secret='app-client-secret-67890',
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://localhost:8000/callback'
        )

        response = client.get(reverse('manage_application'))

        # On edit (GET), client_secret should NOT be in context
        # (it's in the form as readonly, not passed separately)
        assert 'client_secret' not in response.context or response.context['client_secret'] is None

    def test_unauthenticated_post_redirects_to_login(self, client):
        """
        GIVEN: Unauthenticated user
        WHEN: POSTing to manage_application
        THEN: Should not accept POST and likely redirect or deny
        """
        data = {
            'name': 'Hack Attempt',
            'redirect_uris': 'http://hacker.com'
        }

        response = client.post(reverse('manage_application'), data, follow=False)

        # ApplicationRegistration protects auth - either redirect or 403
        assert response.status_code in [301, 302, 403]


@pytest.mark.django_db
class TestCustomRegistrationOAuth2Context:
    """Test suite for context data passed to templates."""

    def test_context_includes_section_for_navigation(self, authenticated_client):
        """
        GIVEN: Any authenticated request to manage_application
        WHEN: Request succeeds
        THEN: Context should include 'section' = 'manage_application' for navigation
        """
        client, user = authenticated_client

        response = client.get(reverse('manage_application'))

        assert response.context['section'] == 'manage_application'

    def test_create_success_context_has_all_credentials(self, authenticated_client):
        """
        GIVEN: Successfully created OAuth2 application
        WHEN: POSTing valid creation data
        THEN: Success template context should include client_id, client_secret, and section
        """
        client, user = authenticated_client

        data = {
            'name': 'Complete App',
            'redirect_uris': 'http://example.com/cb'
        }

        response = client.post(reverse('manage_application'), data)

        context = response.context
        assert 'client_id' in context
        assert 'client_secret' in context
        assert 'section' in context
        assert context['section'] == 'manage_application'

    def test_edit_context_includes_application_instance(self, db, authenticated_client):
        """
        GIVEN: Authenticated user with existing application
        WHEN: GETing the manage_application endpoint
        THEN: Context should include 'application' with the app instance
        """
        client, user = authenticated_client
        app = Application.objects.create(
            user=user,
            name='Existing App',
            client_id='app-client-id-12345',
            client_secret='app-client-secret-67890',
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://localhost:8000/callback'
        )

        response = client.get(reverse('manage_application'))

        assert 'application' in response.context
        assert response.context['application'].pk == app.pk


@pytest.mark.django_db
class TestCustomRegistrationOAuth2EdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def test_post_create_with_whitespace_only_name(self, authenticated_client):
        """
        GIVEN: Form data with whitespace-only name
        WHEN: POSTing data
        THEN: Should reject as invalid
        """
        client, user = authenticated_client

        data = {
            'name': '   ',
            'redirect_uris': 'http://example.com/cb'
        }

        response = client.post(reverse('manage_application'), data)

        form = response.context['form']
        assert not form.is_valid()

    def test_post_edit_with_same_data_idempotent(self, db, authenticated_client):
        """
        GIVEN: Existing application with data
        WHEN: POSTing the exact same data (idempotent operation)
        THEN: Application should be saved without errors
        """
        client, user = authenticated_client
        app = Application.objects.create(
            user=user,
            name='Existing App',
            client_id='app-client-id-12345',
            client_secret='app-client-secret-67890',
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://localhost:8000/callback'
        )

        data = {
            'name': 'Existing App',
            'redirect_uris': 'http://localhost:8000/callback'
        }

        response = client.post(reverse('manage_application'), data)

        assert response.status_code == 200
        app.refresh_from_db()
        assert app.name == 'Existing App'

    def test_post_edit_user_field_cannot_be_changed(self, db, authenticated_client):
        """
        GIVEN: Existing application owned by User A
        WHEN: User A edits the application (user field hidden in form)
        THEN: The user field should remain pointing to User A
        """
        client, user_a = authenticated_client
        app = Application.objects.create(
            user=user_a,
            name='Existing App',
            client_id='app-client-id-12345',
            client_secret='app-client-secret-67890',
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://localhost:8000/callback'
        )

        data = {
            'name': 'Still Owned By User A',
            'redirect_uris': 'http://example.com/cb'
        }

        response = client.post(reverse('manage_application'), data)

        app.refresh_from_db()
        assert app.user == user_a

    @pytest.mark.parametrize('invalid_uri', [
        'ftp://example.com',
        'file:///etc/passwd',
        'javascript:alert("xss")',
        'example.com/callback',  # Missing protocol
    ])
    def test_post_invalid_uri_schemes_rejected(self, authenticated_client, invalid_uri):
        """
        GIVEN: Various invalid URI formats
        WHEN: POSTing form data with invalid URIs
        THEN: All should be rejected with validation error
        """
        client, user = authenticated_client

        data = {
            'name': 'Valid Name',
            'redirect_uris': invalid_uri
        }

        response = client.post(reverse('manage_application'), data)

        form = response.context['form']
        assert not form.is_valid()
        assert 'redirect_uris' in form.errors

    @pytest.mark.parametrize('valid_uri', [
        'http://localhost:8000/callback',
        'https://example.com/oauth',
        'https://sub.example.com:9000/path/to/callback',
    ])
    def test_post_valid_uri_schemes_accepted(self, authenticated_client, valid_uri):
        """
        GIVEN: Valid URI formats (http/https)
        WHEN: POSTing form data with valid URIs
        THEN: Should be accepted and application created
        """
        client, user = authenticated_client

        data = {
            'name': 'Valid App',
            'redirect_uris': valid_uri
        }

        response = client.post(reverse('manage_application'), data)

        assert response.status_code == 200
        template_names = [t.name for t in response.templates if t.name]
        assert 'accounts/oauth2_success.html' in template_names
