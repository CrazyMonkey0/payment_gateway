from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from oauth2_provider.views.application import ApplicationRegistration
from oauth2_provider.models import Application
from .models import Profile
from .forms import UserRegistrationForm, ProfileForm, CustomRegistrationFormOAuth2
from bank.models import Bank
from oauth2_provider.models import generate_client_id, generate_client_secret


class CustomRegistrationOAuth2(ApplicationRegistration):
    template_name_create = "accounts/oauth2_register.html"
    template_name_edit = "accounts/oauth2_update.html"

    def get(self, request, *args, **kwargs):
        app = Application.objects.filter(user=request.user).first()

        if app:
            form = CustomRegistrationFormOAuth2(instance=app)
            return render(request, self.template_name_edit, {'form': form, 'application': app, 'section': 'manage_application'})
        else:
            form = CustomRegistrationFormOAuth2()
            return render(request, self.template_name_create, {'form': form, 'section': 'manage_application'})

    def post(self, request, *args, **kwargs):
        app = Application.objects.filter(user=request.user).first()

        if app:
            form = CustomRegistrationFormOAuth2(request.POST, instance=app)
            form.instance.client_id = app.client_id  
        else:
            form = CustomRegistrationFormOAuth2(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.client_id = generate_client_id()
                instance.client_secret = generate_client_secret()
                instance.user = request.user
                instance.save()
                return render(request, self.template_name_edit, {'form': form, 'section': 'manage_application'})

        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()

        template_name = self.template_name_edit if app else self.template_name_create
        return render(request, template_name, {'form': form, 'section': 'manage_application'})



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

            # Render the registration success page
            return render(request,
                          'registration/register_done.html',
                          {'new_user': new_user})
    else:
        # If the form is not submitted (GET request)
        user_form = UserRegistrationForm()

    # Render the registration form page
    return render(request,
                  'registration/register.html',
                  {'user_form': user_form})


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


def about(request):
    return render(request,
                  'accounts/about.html',
                  {'section': 'about'})


def services(request):
    return render(request,
                  'accounts/services.html',
                  {'section': 'services'})


def why_us(request):
    return render(request,
                  'accounts/why.html',
                  {'section': 'why_us'})


def team(request):
    return render(request,
                  'accounts/team.html',
                  {'section': 'team'})

@login_required
def show_profile(request):
    """
    Display the profile information for the currently logged-in user.

    Returns:
        HttpResponse: Rendered 'accounts/profile.html' template with profile information.
    """
    profile = get_object_or_404(Profile, id=request.user.id)
    return render(request, 'accounts/profile.html', {'section': 'show_profile',
                                                     'profile': profile})


@login_required
def edit_profile(request):
    """
    Allow the user to edit their profile information.

    Returns:
        HttpResponse: Rendered 'accounts/edit_profile.html' template with the profile edit form.
    """
    profile = get_object_or_404(Profile, id=request.user.id)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('show_profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {'section': 'show_profile',
                                                          'form': form})
