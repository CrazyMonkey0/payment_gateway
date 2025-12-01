import pytest
from django.core.exceptions import ValidationError
from accounts.models import Profile


@pytest.mark.django_db
def test_profile_creation(create_profile):
    profile = create_profile(username="test", url_feedback="test-feedback")
    assert profile is not None
    assert profile.id is not None
    assert profile.username == "test"
    assert profile.first_name == "John"
    assert profile.last_name == "Doe"
    assert profile.iban == "DE89370400440532013000"
    assert profile.url_feedback == "test-feedback"
    assert profile.check_password("testpass123") is True


@pytest.mark.django_db
@pytest.mark.parametrize(
    "password",
    [
        ("securepass456"),
        (""),
    ],
)
def test_profile_password(create_profile, password):
    profile = create_profile(username="secureuser", password=password)
    assert profile.check_password(password) is True
    assert profile.check_password("wrongpass") is False
    assert profile.check_password("123") is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    "iban_value, is_valid",
    [
        ("DE89370400440532013000", True),
        ("GB123456789012", True),
        ("PL61109010140000071219812874", True),
        ("", False),
        ("GB291vcxcv116016116", False),
        ("GB2911[16[016116", False),
        ("INVALIDIBAN123", False),
        ("pl12345678901234", False),
        ("[]", False),
    ],
)
def test_iban_validation(create_profile, iban_value, is_valid):
    profile = create_profile(username="ibanuser", iban=iban_value)
    if is_valid:
        profile.full_clean()
        assert profile.iban == iban_value
    else:
        with pytest.raises(ValidationError) as excinfo:
            profile.full_clean()
        assert "iban" in excinfo.value.message_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "slug_value, should_raise",
    [
        ("valid-slug-123", False),
        ("another-valid", False),
        ("slug_with_underscore", False),
        ("", True),
        ("invalid slug", True),
        ("invalid@slug", True),
        ("UPPERCASE", True),
    ],
)
def test_url_feedback_slug_validation(create_profile, slug_value, should_raise):
    """Test that url_feedback follows SlugField validation rules."""
    if should_raise:
        with pytest.raises(ValidationError) as excinfo:
            profile = create_profile(
                username=f"user_{slug_value}", url_feedback=slug_value
            )
            profile.full_clean()
        assert "url_feedback" in excinfo.value.message_dict
    else:
        profile = create_profile(
            username=f"user_{slug_value or 'empty'}", url_feedback=slug_value
        )
        profile.full_clean()
        assert profile.url_feedback == slug_value
