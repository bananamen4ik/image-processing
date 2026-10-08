from django.urls import path

from user_profile.views import ProfileView

app_name = 'user_profile'
urlpatterns = [
    path('', ProfileView.as_view(), name='index'),
]
