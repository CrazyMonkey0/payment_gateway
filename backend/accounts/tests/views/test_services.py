import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestServicesView:
    def test_services_view_status_code(self, client):
        """Test that the services view returns HTTP 200."""
        response = client.get(reverse('services'))
        assert response.status_code == 200

    def test_services_view_template(self, client):
        """Test that the services view renders the correct template."""
        response = client.get(reverse('services'))
        assert 'accounts/services.html' in [t.name for t in response.templates]

    def test_services_view_context(self, client):
        """Test that the services view includes the correct context."""
        response = client.get(reverse('services'))
        assert response.context['section'] == 'services'

    def test_services_view_url_resolution(self, client):
        """Test that the 'services' URL resolves correctly."""
        url = reverse('services')
        assert url == '/services/'

    def test_services_view_post_not_allowed(self, client):
        """Test that POST method is not allowed for services view."""
        response = client.post(reverse('services'))
        assert response.status_code == 405

    def test_services_view_put_not_allowed(self, client):
        """Test that PUT method is not allowed for services view."""
        response = client.put(reverse('services'))
        assert response.status_code == 405

    def test_services_view_delete_not_allowed(self, client):
        """Test that DELETE method is not allowed for services view."""
        response = client.delete(reverse('services'))
        assert response.status_code == 405
    
    def test_services_view_multiple_requests(self, client):
        """Test that the services view returns consistent responses for multiple requests."""
        for _ in range(13):
            response = client.get(reverse('services'))
            assert response.status_code == 200
            assert 'accounts/services.html' in [t.name for t in response.templates]
            assert response.context['section'] == 'services'