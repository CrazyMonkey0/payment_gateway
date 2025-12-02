import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestAboutView:
    def test_about_view_status_code(self, client):
        """Test that the about view returns HTTP 200."""
        response = client.get(reverse('about'))
        assert response.status_code == 200

    def test_about_view_template(self, client):
        """Test that the about view renders the correct template."""
        response = client.get(reverse('about'))
        assert 'accounts/about.html' in [t.name for t in response.templates]

    def test_about_view_context(self, client):
        """Test that the about view includes the correct context."""
        response = client.get(reverse('about'))
        assert response.context['section'] == 'about'

    def test_about_view_url_resolution(self, client):
        """Test that the 'about' URL resolves correctly."""
        url = reverse('about')
        assert url == '/about/'

    def test_about_view_post_not_allowed(self, client):
        """Test that POST method is not allowed for about view."""
        response = client.post(reverse('about'))
        assert response.status_code == 405

    def test_about_view_put_not_allowed(self, client):
        """Test that PUT method is not allowed for about view."""
        response = client.put(reverse('about'))
        assert response.status_code == 405

    def test_about_view_delete_not_allowed(self, client):
        """Test that DELETE method is not allowed for about view."""
        response = client.delete(reverse('about'))
        assert response.status_code == 405

    def test_about_view_multiple_requests(self, client):
        """Test that the about view returns consistent responses for multiple requests."""
        for _ in range(13):
            response = client.get(reverse('about'))
            assert response.status_code == 200
            assert 'accounts/about.html' in [t.name for t in response.templates]
            assert response.context['section'] == 'about'