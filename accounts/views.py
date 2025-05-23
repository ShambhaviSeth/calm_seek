from django.contrib.auth.decorators import login_required

from appointments.models import Appointment
from .forms import (
    ClientEditForm,
    ProfileEditForm,
    ProviderEditForm,
    PasswordResetRequestForm,
)
from accounts.models import Profile
from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from .models import Provider, Client


@login_required
def profile(request):
    user = request.user
    context = {
        "user": user,
        "is_provider": hasattr(user, "provider"),
        "is_client": hasattr(user, "client"),
        "MEDIA_URL": settings.MEDIA_URL,
    }
    return render(request, "accounts/profile.html", context)


@login_required
def edit_profile(request):
    user = request.user

    # Determine if the user is a provider
    is_provider = user.role == "Provider"

    if request.method == "POST":
        profile_form = ProfileEditForm(request.POST, instance=user)
        provider_form = (
            ProviderEditForm(request.POST, request.FILES, instance=user.provider)
            if is_provider
            else None
        )
        client_form = (
            ClientEditForm(request.POST, instance=user.client)
            if not is_provider
            else None
        )

        # Save forms based on validity
        if is_provider and profile_form.is_valid() and provider_form.is_valid():
            profile_form.save()
            provider_form.save()
            return redirect("accounts:profile")
        elif not is_provider and profile_form.is_valid() and client_form.is_valid():
            profile_form.save()
            client_form.save()
            return redirect("accounts:profile")
    else:
        profile_form = ProfileEditForm(instance=user)
        provider_form = (
            ProviderEditForm(instance=user.provider) if is_provider else None
        )
        client_form = ClientEditForm(instance=user.client) if not is_provider else None

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "profile_form": profile_form,
            "provider_form": provider_form,
            "is_provider": is_provider,
            "client_form": client_form,
            "MEDIA_URL": settings.MEDIA_URL,
        },
    )


def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            try:
                profile = Profile.objects.get(username=username, email=email)
            except Profile.DoesNotExist:
                form.add_error(
                    None, "User with the provided username and email does not exist."
                )
            else:
                token = default_token_generator.make_token(profile)
                uid = urlsafe_base64_encode(force_bytes(profile.pk))
                reset_url = request.build_absolute_uri(
                    reverse(
                        "accounts:password_reset_confirm",
                        kwargs={"uidb64": uid, "token": token},
                    )
                )
                send_mail(
                    subject="Password Reset Request",
                    message=f"Click the link to reset your password: {reset_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                )
                return redirect("accounts:password_reset_sent")
    else:
        form = PasswordResetRequestForm()
    return render(request, "accounts/password_reset_request.html", {"form": form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        profile = Profile.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Profile.DoesNotExist):
        profile = None

    if profile is not None and default_token_generator.check_token(profile, token):
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            profile.set_password(new_password)
            profile.save()
            return redirect("accounts:password_reset_complete")
        return render(
            request, "accounts/password_reset_confirm.html", {"validlink": True}
        )
    else:
        return render(
            request, "accounts/password_reset_confirm.html", {"validlink": False}
        )


def password_reset_sent(request):
    return render(request, "accounts/password_reset_sent.html")


def password_reset_complete(request):
    return render(request, "accounts/password_reset_complete.html")


@login_required
def client_dashboard(request):
    # Check if the user is a client
    if request.user.role != "User":
        return redirect("error")  # Redirect to error page if not a client

    today = timezone.now().date().isoformat()
    # Fetch client-specific data
    client_data = get_object_or_404(Client, user=request.user)
    appointments = Appointment.objects.filter(
        user=request.user, time_slot__start_time__gte=today
    ).select_related("time_slot")

    context = {
        "client_data": client_data,
        "appointments": appointments,
        # Add any additional client-specific data here
    }
    return render(request, "accounts/client_dashboard.html", context)


@login_required
def provider_dashboard(request):
    # Check if the user is a provider
    if request.user.role != "Provider":
        return redirect("error")  # Redirect to error page if not a provider

    # Filter the slots after today's date
    today = timezone.now().date().isoformat()

    # Fetch provider-specific data
    provider_data = get_object_or_404(Provider, user=request.user)
    appointments = Appointment.objects.filter(
        time_slot__provider=request.user, time_slot__start_time__gte=today
    ).select_related("time_slot")
    context = {
        "provider_data": provider_data,
        "appointments": appointments,
        # Add any additional provider-specific data here
    }
    return render(request, "accounts/provider_dashboard.html", context)
