import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestWhyUsView:
    def test_why_us_view_status_code(self, client):
        """Test that the why_us view returns HTTP 200."""
        response = client.get(reverse('why_us'))
        assert response.status_code == 200

    def test_why_us_view_template(self, client):
        """Test that the why_us view renders the correct template."""
        response = client.get(reverse('why_us'))
        assert 'accounts/why.html' in [t.name for t in response.templates]

    def test_why_us_view_context(self, client):
        """Test that the why_us view includes the correct context."""
        response = client.get(reverse('why_us'))
        assert response.context['section'] == 'why_us'

    def test_why_us_view_url_resolution(self):
        """Test that the 'why_us' URL resolves correctly."""
        url = reverse('why_us')
        assert url == '/why-us/'

    def test_why_us_view_post_not_allowed(self, client):
        """Test that POST method is not allowed for why_us view."""
        response = client.post(reverse('why_us'))
        assert response.status_code == 405

    def test_why_us_view_put_not_allowed(self, client):
        """Test that PUT method is not allowed for why_us view."""
        response = client.put(reverse('why_us'))
        assert response.status_code == 405

    def test_why_us_view_delete_not_allowed(self, client):
        """Test that DELETE method is not allowed for why_us view."""
        response = client.delete(reverse('why_us'))
        assert response.status_code == 405

    def test_why_us_view_multiple_requests(self, client):
        """Test that the why_us view returns consistent responses for multiple requests."""
        for _ in range(13):
            response = client.get(reverse('why_us'))
            assert response.status_code == 200
            assert 'accounts/why.html' in [t.name for t in response.templates]
            assert response.context['section'] == 'why_us'