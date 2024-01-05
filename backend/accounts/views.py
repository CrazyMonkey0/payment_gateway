from django.shortcuts import render
from .models import Profile
from .forms import UserRegistrationForm


def register(request):
    """
    View for user registration.

    Attributes:
    - request (HttpRequest): HTTP request object.
    """

    if request.method == 'POST':
        # If the form is submitted with POST data
        user_form = UserRegistrationForm(request.POST)

        if user_form.is_valid():
            # If the form is valid
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()

            # Create user profile
            Profile.objects.create(user=new_user)

            # Render the registration success page
            return render(request,
                          'accounts/register_done.html',
                          {'new_user': new_user})
    else:
        # If the form is not submitted (GET request)
        user_form = UserRegistrationForm()

    # Render the registration form page
    return render(request,
                  'accounts/register.html',
                  {'user_form': user_form})
