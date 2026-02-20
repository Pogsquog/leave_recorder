from django.urls import path

from .views import UserLoginView, UserLogoutView, UserPreferencesView, UserRegistrationView, profile

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("profile/", profile, name="profile"),
    path("preferences/", UserPreferencesView.as_view(), name="preferences"),
]
