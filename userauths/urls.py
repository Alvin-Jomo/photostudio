from django.urls import path, reverse_lazy
from userauths import views
from django.contrib.auth import views as auth_views

app_name = "userauths"

urlpatterns = [

    # User registration and login views
    path("sign-up/", views.register_view, name="sign-up"),
    path("sign-in/", views.login_view, name="sign-in"),
    path("sign-out/", views.logout_view, name="sign-out"),

    # User profile views
    path("profile/update/", views.profile_update, name="profile-update"),

    # Password reset views
    path("password_reset/", auth_views.PasswordResetView.as_view(
        template_name="registration/password_reset_form.html",
        email_template_name="registration/password_reset_email.html",
        subject_template_name="registration/password_reset_subject.txt",
        success_url=reverse_lazy("userauths:password_reset_done")  # ✅ FIXED
    ), name="password_reset"),

    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="registration/password_reset_sent.html"
    ), name="password_reset_done"),

    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="registration/password_reset_confirm.html",
        success_url=reverse_lazy("userauths:password_reset_complete")
    ), name="password_reset_confirm"),

    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="registration/password_reset_complete.html"
    ), name="password_reset_complete"),
]
