from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import UserPreferencesForm, UserRegistrationForm
from .models import User


class UserLoginView(LoginView):
    template_name = "account/login.html"
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("account:login")


class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "account/register.html"
    success_url = reverse_lazy("leave:month")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


@login_required
def profile(request):
    return render(request, "account/profile.html")


class UserPreferencesView(UpdateView):
    model = User
    form_class = UserPreferencesForm
    template_name = "account/preferences.html"
    success_url = reverse_lazy("account:preferences")

    def get_object(self, queryset=None):
        return self.request.user
