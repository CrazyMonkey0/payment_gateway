import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestDashboardView:
    def test_dashboard_view_status_code(self, client):
        """Test that the dashboard view returns HTTP 200."""
        response = client.get(reverse('dashboard'))
        assert response.status_code == 200

    def test_dashboard_view_template(self, client):
        """Test that the dashboard view renders the correct template."""
        response = client.get(reverse('dashboard'))
        assert 'accounts/dashboard.html' in [t.name for t in response.templates]

    def test_dashboard_view_context(self, client):
        """Test that the dashboard view includes the correct context."""
        response = client.get(reverse('dashboard'))
        assert response.context['section'] == 'dashboard'

    def test_dashboard_view_url_resolution(self, client):
        """Test that the 'dashboard' URL resolves correctly."""
        url = reverse('dashboard')
        assert url == '/'

    def test_dashboard_view_post_not_allowed(self, client):
        """Test that POST method is not allowed for dashboard view."""
        response = client.post(reverse('dashboard'))
        assert response.status_code == 405

    def test_dashboard_view_put_not_allowed(self, client):
        """Test that PUT method is not allowed for dashboard view."""
        response = client.put(reverse('dashboard'))
        assert response.status_code == 405

    def test_dashboard_view_delete_not_allowed(self, client):
        """Test that DELETE method is not allowed for dashboard view."""
        response = client.delete(reverse('dashboard'))
        assert response.status_code == 405
    
    def test_dashboard_view_multiple_requests(self, client):
        """Test that the dashboard view returns consistent responses for multiple requests."""
        for _ in range(13):
            response = client.get(reverse('dashboard'))
            assert response.status_code == 200
            assert 'accounts/dashboard.html' in [t.name for t in response.templates]
            assert response.context['section'] == 'dashboard'