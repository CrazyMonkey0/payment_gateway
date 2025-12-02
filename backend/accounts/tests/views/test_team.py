import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestTeamView:
    def test_team_view_status_code(self, client):
        """Test that the team view returns HTTP 200."""
        response = client.get(reverse('team'))
        assert response.status_code == 200

    def test_team_view_template(self, client):
        """Test that the team view renders the correct template."""
        response = client.get(reverse('team'))
        assert 'accounts/team.html' in [t.name for t in response.templates]

    def test_team_view_context(self, client):
        """Test that the team view includes the correct context."""
        response = client.get(reverse('team'))
        assert response.context['section'] == 'team'

    def test_team_view_url_resolution(self, client):
        """Test that the 'team' URL resolves correctly."""
        url = reverse('team')
        assert url == '/team/'

    def test_team_view_post_not_allowed(self, client):
        """Test that POST method is not allowed for team view."""
        response = client.post(reverse('team'))
        assert response.status_code == 405

    def test_team_view_put_not_allowed(self, client):
        """Test that PUT method is not allowed for team view."""
        response = client.put(reverse('team'))
        assert response.status_code == 405

    def test_team_view_delete_not_allowed(self, client):
        """Test that DELETE method is not allowed for team view."""
        response = client.delete(reverse('team'))
        assert response.status_code == 405