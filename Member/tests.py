"""Regression tests encoding the security/robustness fixes applied to the
4time backend. Every test here maps to a previously-present vulnerability or
crash that must not reappear.

Runs on SQLite only (see conftest.py); nothing here imports torch/transformers
or any ML/translation code.
"""
import pytest
from rest_framework.test import APIClient

from Member.models import Member, MemberP

# Public endpoint paths (part of the frontend contract — keep in sync).
REGISTER_URL = "/Center/register/"
LOGIN_URL = "/Center/login/"
REQUEST_RESET_URL = "/Center/request_password_reset/"
RESET_URL = "/Center/reset_password/"
MEMBER_INFO_URL = "/Member/info/"
TEST_CHECK_URL = "/Test/check/"

STRONG_PASSWORD = "Xq7vplmZ29t"


@pytest.fixture
def client():
    return APIClient()


def build_register_payload(account="alice01", email="alice@example.com",
                           password=STRONG_PASSWORD):
    """A full, valid registration body covering all four sub-serializers."""
    return {
        "Private": {"account": account, "password": password},
        "Member": {
            "name": "Alice",
            "birth": "2000-01-01",
            "email": email,
            "gender": "female",
            "job": "engineer",
        },
        "Health": {
            "height": 165,
            "weight": 55,
            "mental": ["ok"],
            "allergen": ["none"],
            "exercise_intensity": 2,
            "excercise_frequency": 3,
            "excercise_time": 2,
            "disease": ["none"],
        },
        "Prefer": {
            "target": ["fitness"],
            "restrict": ["none"],
            "prefer": ["veg"],
            "Nut_need": ["protein"],
        },
    }


def make_user(account, password, email, uid):
    """Create a MemberP (auth) + linked Member profile directly."""
    mp = MemberP.objects.create_user(account=account, password=password, uid=uid)
    Member.objects.create(uid=mp, name=account, email=email,
                          gender="male", job="none")
    return mp


# ---------------------------------------------------------------------------
# Authorization / IDOR: Member CRUD routes must no longer exist.
# ---------------------------------------------------------------------------

class TestMemberAuthorization:
    def test_authenticated_user_cannot_list_all_members(self, client):
        me = make_user("victim", STRONG_PASSWORD, "victim@example.com", "U000001")
        make_user("other", STRONG_PASSWORD, "other@example.com", "U000002")
        client.force_authenticate(user=me)

        resp = client.get("/Member/")
        # No list route is registered -> route does not exist.
        assert resp.status_code in (403, 404, 405)

    @pytest.mark.parametrize("method", ["get", "put", "delete"])
    def test_authenticated_user_cannot_touch_other_member_by_pk(self, client, method):
        me = make_user("victim", STRONG_PASSWORD, "victim@example.com", "U000001")
        make_user("other", STRONG_PASSWORD, "other@example.com", "U000002")
        client.force_authenticate(user=me)

        resp = getattr(client, method)("/Member/U000002/")
        # The /Member/{pk}/ detail routes were removed (IDOR fix).
        assert resp.status_code in (403, 404, 405)

    def test_member_info_requires_authentication(self, client):
        resp = client.get(MEMBER_INFO_URL)
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Registration: hashed passwords + password-strength enforcement.
# ---------------------------------------------------------------------------

class TestRegistration:
    def test_register_happy_path_hashes_password(self, client):
        payload = build_register_payload()
        resp = client.post(REGISTER_URL, payload, format="json")

        assert resp.status_code == 200
        mp = MemberP.objects.get(account="alice01")
        # Password must be stored hashed, never as plaintext.
        assert mp.password != STRONG_PASSWORD
        assert mp.password.startswith(("pbkdf2_", "argon2", "bcrypt"))
        assert mp.check_password(STRONG_PASSWORD)
        # Profile row was created and linked.
        assert Member.objects.filter(uid=mp).exists()

    def test_register_rejects_weak_password(self, client):
        payload = build_register_payload(account="weakuser",
                                         email="weak@example.com",
                                         password="123")
        resp = client.post(REGISTER_URL, payload, format="json")

        assert resp.status_code == 400
        # Nothing should have been persisted for a rejected registration.
        assert not MemberP.objects.filter(account="weakuser").exists()


# ---------------------------------------------------------------------------
# Login: token on valid creds, 400 on invalid.
# ---------------------------------------------------------------------------

class TestLogin:
    def test_login_valid_credentials_returns_token(self, client):
        make_user("bob", STRONG_PASSWORD, "bob@example.com", "U000005")
        resp = client.post(LOGIN_URL,
                           {"account": "bob", "password": STRONG_PASSWORD},
                           format="json")
        assert resp.status_code == 200
        assert resp.data.get("token")

    def test_login_invalid_credentials_returns_400(self, client):
        make_user("bob", STRONG_PASSWORD, "bob@example.com", "U000005")
        resp = client.post(LOGIN_URL,
                           {"account": "bob", "password": "wrong-password"},
                           format="json")
        assert resp.status_code == 400
        assert "token" not in resp.data


# ---------------------------------------------------------------------------
# Password reset: no account enumeration, token-validated reset.
# ---------------------------------------------------------------------------

class TestPasswordReset:
    def test_request_reset_does_not_reveal_email_existence(self, client):
        make_user("carol", STRONG_PASSWORD, "carol@example.com", "U000006")

        existing = client.post(REQUEST_RESET_URL,
                              {"email": "carol@example.com"}, format="json")
        missing = client.post(REQUEST_RESET_URL,
                             {"email": "nobody@example.com"}, format="json")

        # Both branches return the same generic 200 status.
        assert existing.status_code == 200
        assert missing.status_code == 200
        assert "message" in existing.data
        assert "message" in missing.data
        # A non-existent account must not leak a reset token.
        assert "token" not in missing.data

    def test_reset_with_bad_token_fails(self, client):
        make_user("dave", STRONG_PASSWORD, "dave@example.com", "U000007")
        req = client.post(REQUEST_RESET_URL,
                         {"email": "dave@example.com"}, format="json")
        uidb64 = req.data["uid"]

        resp = client.post(RESET_URL,
                          {"uid": uidb64, "token": "not-a-valid-token",
                           "password": "N3w!Str0ngPwd"},
                          format="json")
        assert resp.status_code == 400

    def test_reset_with_valid_token_succeeds(self, client):
        mp = make_user("erin", STRONG_PASSWORD, "erin@example.com", "U000008")
        req = client.post(REQUEST_RESET_URL,
                         {"email": "erin@example.com"}, format="json")
        # DEBUG-only fields used to drive the reset in tests.
        uidb64 = req.data["uid"]
        token = req.data["token"]

        new_password = "N3w!Str0ngPwd"
        resp = client.post(RESET_URL,
                          {"uid": uidb64, "token": token, "password": new_password},
                          format="json")
        assert resp.status_code == 200

        mp.refresh_from_db()
        assert mp.check_password(new_password)


# ---------------------------------------------------------------------------
# Input guard: quiz check() returns 400 (not 500) on empty body.
# ---------------------------------------------------------------------------

class TestRecordCheckInputGuard:
    def test_check_empty_body_returns_400(self, client):
        resp = client.post(TEST_CHECK_URL, [], format="json")
        assert resp.status_code == 400
