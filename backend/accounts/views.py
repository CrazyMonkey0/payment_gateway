from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import UserRegistrationForm, ProfileForm


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

            # Create a Profile object and associate it with a new user
            profile = Profile(user=new_user)
            profile.save()

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


@login_required
def dashboard(request):
    """
    View displaying the user's dashboard.

    Accessible only to authenticated users. Redirects to the login page
    if the user is not authenticated.

    Parameters:
    - request (HttpRequest): The request object.

    Returns:
    - HttpResponse: Rendered HTML response for the user's dashboard.
    """
    return render(request,
                  'accounts/dashboard.html',
                  {'section': 'dashboard'})


@login_required
def show_profile(request):
    """
    Display the profile information for the currently logged-in user.

    Returns:
        HttpResponse: Rendered 'accounts/profile.html' template with profile information.
    """
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'accounts/profile.html', {'section': 'show_profile',
                                                     'profile': profile})


@login_required
def edit_profile(request):
    """
    Allow the user to edit their profile information.

    Returns:
        HttpResponse: Rendered 'accounts/edit_profile.html' template with the profile edit form.
    """
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('show_profile')
    else:
        form = ProfileForm()

    return render(request, 'accounts/edit_profile.html', {'section': 'edit_profile',
                                                          'form': form})
