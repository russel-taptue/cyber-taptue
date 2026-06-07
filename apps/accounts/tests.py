from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.forms import CustomUserCreationForm, CustomAuthenticationForm
from apps.accounts.models import OTP

User = get_user_model()


class CustomUserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email="test@example.com", username="testuser", password="pass12345"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("pass12345"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="admin12345"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_email_is_username_field(self):
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_email_unique(self):
        User.objects.create_user(email="dup@example.com", username="u1", password="p1")
        with self.assertRaises(Exception):
            User.objects.create_user(email="dup@example.com", username="u2", password="p2")

    def test_str_returns_email(self):
        user = User.objects.create_user(email="show@example.com", username="show", password="p1")
        self.assertEqual(str(user), "show@example.com")

    def test_required_fields(self):
        self.assertIn("username", User.REQUIRED_FIELDS)


class CustomUserCreationFormTest(TestCase):
    def test_valid_form(self):
        form = CustomUserCreationForm(data={
            "email": "new@example.com",
            "username": "newuser",
            "password1": "Str0ng!pass",
            "password2": "Str0ng!pass",
        })
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        form = CustomUserCreationForm(data={
            "email": "new@example.com",
            "username": "newuser",
            "password1": "Str0ng!pass",
            "password2": "diffpass123",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_blank_email(self):
        form = CustomUserCreationForm(data={
            "email": "",
            "username": "newuser",
            "password1": "Str0ng!pass",
            "password2": "Str0ng!pass",
        })
        self.assertFalse(form.is_valid())

    def test_duplicate_email(self):
        User.objects.create_user(email="dup@example.com", username="first", password="p1")
        form = CustomUserCreationForm(data={
            "email": "dup@example.com",
            "username": "second",
            "password1": "Str0ng!pass",
            "password2": "Str0ng!pass",
        })
        self.assertFalse(form.is_valid())


class CustomAuthenticationFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="auth@example.com", username="authuser", password="pass12345"
        )

    def test_valid_credentials(self):
        form = CustomAuthenticationForm(data={
            "username": "auth@example.com",
            "password": "pass12345",
        })
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        form = CustomAuthenticationForm(data={
            "username": "wrong@example.com",
            "password": "pass12345",
        })
        self.assertFalse(form.is_valid())

    def test_wrong_password(self):
        form = CustomAuthenticationForm(data={
            "username": "auth@example.com",
            "password": "wrongpassword",
        })
        self.assertFalse(form.is_valid())


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="login@example.com", username="loginuser", password="pass12345"
        )
        self.url = reverse("accounts:login")

    def test_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_post_valid_redirects(self):
        response = self.client.post(self.url, {
            "username": "login@example.com",
            "password": "pass12345",
        })
        self.assertEqual(response.status_code, 302)

    def test_post_invalid_stays(self):
        response = self.client.post(self.url, {
            "username": "login@example.com",
            "password": "wrong",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct email")


class RegisterViewTest(TestCase):
    def setUp(self):
        self.url = reverse("accounts:register")

    def test_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_post_valid_redirects(self):
        response = self.client.post(self.url, {
            "email": "reg@example.com",
            "username": "reguser",
            "password1": "Str0ng!pass",
            "password2": "Str0ng!pass",
        })
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertTrue(User.objects.filter(email="reg@example.com").exists())

    def test_post_invalid_stays(self):
        response = self.client.post(self.url, {
            "email": "",
            "username": "reguser",
            "password1": "Str0ng!pass",
            "password2": "Str0ng!pass",
        })
        self.assertEqual(response.status_code, 200)


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="profile@example.com", username="profileuser", password="p1"
        )

    def test_profile_auto_created(self):
        self.assertTrue(hasattr(self.user, "profile"))
        self.assertEqual(self.user.profile.user, self.user)

    def test_str(self):
        self.assertEqual(str(self.user.profile), "profileuser")

    def test_get_absolute_url(self):
        url = self.user.profile.get_absolute_url()
        self.assertIn("profileuser", url)

    def test_contribution_count_default_zero(self):
        self.assertEqual(self.user.profile.contribution_count, 0)

    def test_bio_blank_by_default(self):
        self.assertEqual(self.user.profile.bio, "")


class ProfileDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="detail@example.com", username="detailuser", password="p1"
        )
        self.url = reverse("accounts:profile_detail", kwargs={"username": "detailuser"})

    def test_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile_detail.html")

    def test_shows_username(self):
        response = self.client.get(self.url)
        self.assertContains(response, "detailuser")

    def test_404_for_nonexistent(self):
        url = reverse("accounts:profile_detail", kwargs={"username": "nobody"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ProfileUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="edit@example.com", username="edituser", password="p1"
        )
        self.url = reverse("accounts:profile_update")

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.url}")

    def test_get_200_authenticated(self):
        self.client.login(email="edit@example.com", password="p1")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile_form.html")

    def test_post_updates_bio(self):
        self.client.login(email="edit@example.com", password="p1")
        response = self.client.post(self.url, {"bio": "New bio text"})
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.bio, "New bio text")

    def test_post_updates_social_links(self):
        self.client.login(email="edit@example.com", password="p1")
        response = self.client.post(self.url, {
            "website": "https://example.com",
            "github": "https://github.com/test",
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.website, "https://example.com")
        self.assertEqual(self.user.profile.github, "https://github.com/test")

    def test_redirects_to_profile_after_save(self):
        self.client.login(email="edit@example.com", password="p1")
        response = self.client.post(self.url, {"bio": "Hi"})
        self.assertRedirects(
            response,
            reverse("accounts:profile_detail", kwargs={"username": "edituser"}),
        )


class PasswordResetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="reset@example.com",
            username="resetuser",
            password="oldpass12345",
        )

    def test_password_reset_page_200(self):
        url = reverse("accounts:password_reset")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset.html")

    def test_password_reset_post_valid_email_redirects(self):
        url = reverse("accounts:password_reset")
        response = self.client.post(url, {"email": "reset@example.com"})
        self.assertRedirects(response, reverse("accounts:password_reset_done"))

    def test_password_reset_post_invalid_email_stays(self):
        url = reverse("accounts:password_reset")
        response = self.client.post(url, {"email": "wrong@example.com"})
        self.assertRedirects(response, reverse("accounts:password_reset_done"))

    def test_password_reset_done_page_200(self):
        url = reverse("accounts:password_reset_done")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset_done.html")

    def test_password_reset_complete_page_200(self):
        url = reverse("accounts:password_reset_complete")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset_complete.html")

    def test_password_reset_confirm_invalid_token_shows_form(self):
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse("accounts:password_reset_confirm", kwargs={
            "uidb64": uidb64, "token": "bad-token",
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset_confirm.html")

    def test_password_reset_confirm_valid_token_redirects_to_set_password(self):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse("accounts:password_reset_confirm", kwargs={
            "uidb64": uidb64, "token": token,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/reset/", response.url)
        self.assertIn("/set-password/", response.url)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset_confirm.html")

    def test_password_reset_confirm_post_valid_resets_password(self):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse("accounts:password_reset_confirm", kwargs={
            "uidb64": uidb64, "token": token,
        })
        # Validate token (redirects to set-password URL)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        set_password_url = response.url
        # POST to set-password URL
        response = self.client.post(set_password_url, {
            "new_password1": "newpassword567!",
            "new_password2": "newpassword567!",
        })
        self.assertRedirects(response, reverse("accounts:password_reset_complete"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword567!"))

    def test_password_reset_confirm_post_mismatched_passwords_stays(self):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse("accounts:password_reset_confirm", kwargs={
            "uidb64": uidb64, "token": token,
        })
        # Validate token (redirects to set-password URL)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        set_password_url = response.url
        # POST mismatched passwords
        response = self.client.post(set_password_url, {
            "new_password1": "newpassword567!",
            "new_password2": "differentpass!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset_confirm.html")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("oldpass12345"))

    def test_forgot_password_link_on_login_page(self):
        url = reverse("accounts:login")
        response = self.client.get(url)
        self.assertContains(response, "Forgot your password?")
        self.assertContains(response, reverse("accounts:password_reset"))


class Email2FATest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="2fa@example.com",
            username="2fauser",
            password="testpass12345",
        )
        self.login_url = reverse("accounts:login")
        self.verify_url = reverse("accounts:verify_otp")
        self.resend_url = reverse("accounts:resend_otp")

    @override_settings(EMAIL_HOST_USER="test@test.com")
    def test_login_sends_otp_email(self):
        self.client.post(self.login_url, {"username": "2fa@example.com", "password": "testpass12345"})
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("verification code", mail.outbox[0].subject.lower())

    def test_login_redirects_to_verify_otp(self):
        response = self.client.post(self.login_url, {"username": "2fa@example.com", "password": "testpass12345"})
        self.assertRedirects(response, self.verify_url)

    def test_otp_stored_in_session(self):
        self.client.post(self.login_url, {"username": "2fa@example.com", "password": "testpass12345"})
        self.assertIn("_otp_user_id", self.client.session)
        self.assertEqual(self.client.session["_otp_user_id"], self.user.pk)

    def test_verify_otp_requires_session(self):
        response = self.client.get(self.verify_url)
        self.assertRedirects(response, self.login_url)

    def test_verify_otp_page_200_when_authenticated(self):
        self.client.post(self.login_url, {"username": "2fa@example.com", "password": "testpass12345"})
        response = self.client.get(self.verify_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/verify_otp.html")

    @override_settings(EMAIL_HOST_USER="test@test.com")
    def test_valid_otp_logs_user_in(self):
        self.client.post(self.login_url, {"username": "2fa@example.com", "password": "testpass12345"})
        otp = OTP.objects.get(user=self.user, is_used=False)
        response = self.client.post(self.verify_url, {"code": otp.code}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_invalid_otp_shows_error(self):
        self.client.post(self.login_url, {"username": "2fa@example.com", "password": "testpass12345"})
        response = self.client.post(self.verify_url, {"code": "000000"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Incorrect")

    def test_expired_otp_redirects_to_resend(self):
        self.client.post(self.login_url, {"username": "2fa@example.com", "password": "testpass12345"})
        otp = OTP.objects.get(user=self.user, is_used=False)
        otp.created_at = otp.created_at - timezone.timedelta(minutes=settings.OTP_EXPIRY_MINUTES + 1)
        otp.save(update_fields=["created_at"])
        response = self.client.post(self.verify_url, {"code": otp.code})
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.resend_url, response.url)

    def test_max_attempts_redirects_to_login(self):
        self.client.post(self.login_url, {"username": "2fa@example.com", "password": "testpass12345"})
        for _ in range(settings.OTP_MAX_ATTEMPTS):
            response = self.client.post(self.verify_url, {"code": "000000"})
        self.assertRedirects(response, self.login_url)

    def test_resend_otp_creates_new_code(self):
        self.client.post(self.login_url, {"username": "2fa@example.com", "password": "testpass12345"})
        otp1 = OTP.objects.get(user=self.user, is_used=False)
        self.client.get(self.resend_url)
        otp2 = OTP.objects.get(user=self.user, is_used=False)
        self.assertNotEqual(otp1.code, otp2.code)
        self.assertTrue(OTP.objects.get(pk=otp1.pk).is_used)

    @override_settings(EMAIL_HOST_USER="test@test.com")
    def test_resend_sends_email(self):
        self.client.post(self.login_url, {"username": "2fa@example.com", "password": "testpass12345"})
        mail.outbox.clear()
        self.client.get(self.resend_url)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("verification", mail.outbox[0].subject.lower())

    def test_register_sends_welcome_email(self):
        mail.outbox.clear()
        with self.settings(EMAIL_HOST_USER="test@test.com"):
            self.client.post(reverse("accounts:register"), {
                "email": "newuser@example.com",
                "username": "newuser",
                "password1": "Str0ng!Password",
                "password2": "Str0ng!Password",
            })
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("welcome", mail.outbox[0].subject.lower())

    def test_otp_info_on_login_page(self):
        response = self.client.get(self.login_url)
        self.assertContains(response, "verification code")


@override_settings(
    AXES_ENABLED=True,
    AXES_COOLOFF_TIME=timedelta(hours=1),
    AXES_RESET_ON_SUCCESS=True,
    AXES_FAILURE_LIMIT=5,
)
class LoginRateLimitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="ratelimit@example.com", username="ratelimituser", password="pass12345"
        )
        self.login_url = reverse("accounts:login")

    def test_five_failures_then_lockout(self):
        for _ in range(4):
            resp = self.client.post(self.login_url, {
                "username": "ratelimit@example.com",
                "password": "wrongpass",
            })
            self.assertEqual(resp.status_code, 200)
        resp = self.client.post(self.login_url, {
            "username": "ratelimit@example.com",
            "password": "wrongpass",
        })
        self.assertEqual(resp.status_code, 429)

    def test_lockout_message_shown(self):
        for _ in range(4):
            self.client.post(self.login_url, {
                "username": "ratelimit@example.com",
                "password": "wrongpass",
            })
        resp = self.client.post(self.login_url, {
            "username": "ratelimit@example.com",
            "password": "wrongpass",
        })
        self.assertContains(resp, "locked", status_code=429)

    def test_different_ip_unaffected(self):
        for _ in range(5):
            self.client.post(self.login_url, {
                "username": "ratelimit@example.com",
                "password": "wrongpass",
            })
        resp = self.client.post(
            self.login_url,
            {"username": "ratelimit@example.com", "password": "wrongpass"},
            REMOTE_ADDR="10.0.0.1",
        )
        self.assertEqual(resp.status_code, 200)

    def test_correct_password_below_limit_redirects_to_otp(self):
        for _ in range(3):
            self.client.post(self.login_url, {
                "username": "ratelimit@example.com",
                "password": "wrongpass",
            })
        resp = self.client.post(self.login_url, {
            "username": "ratelimit@example.com",
            "password": "pass12345",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn("verify-otp", resp.url)
