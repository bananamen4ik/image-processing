from django.urls import path

from custom_auth.views import SignupView

app_name = "custom_auth"
urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
]
