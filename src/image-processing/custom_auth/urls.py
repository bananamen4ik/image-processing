from django.urls import path

from custom_auth.views import (
    SignupView,
    LoginView,
)

app_name = "custom_auth"
urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
]
