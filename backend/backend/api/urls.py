from django.urls import path
from .views import upload_resume,home,login,signup

urlpatterns = [
    path("upload-resume/", upload_resume, name="upload_resume"),
    path("", home, name="home"),
    path("login/", login, name="login"),
    path("signup/", signup, name="signup")
]

