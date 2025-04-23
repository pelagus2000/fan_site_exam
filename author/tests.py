from django.test import TestCase
from django.contrib.auth.models import User
from author.models import Author
from django.utils.timezone import now, timedelta
from django.urls import reverse
from django.core import mail


class AuthorVerificationTests(TestCase):
    def setUp(self):
        """Set up a user and author for testing."""
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com",
                                             password="securepassword")
        self.author = Author.objects.create(author_name=self.user)

    def test_verification_code_generation(self):
        """Test that a verification code is generated and saved correctly."""
        self.author.set_verification_code("12345")
        self.assertEqual(self.author.verification_code, "12345")
        self.assertTrue(self.author.code_expires_at > now())
        self.assertTrue(self.author.code_expires_at < now() + timedelta(minutes=10))

    def test_verification_code_validation(self):
        """Test that the verification code validation works correctly."""
        self.author.set_verification_code("12345")
        # Validation should pass for the correct code
        self.assertTrue(self.author.is_verification_code_valid("12345"))
        # Validation should fail for an incorrect code
        self.assertFalse(self.author.is_verification_code_valid("54321"))
        # Validation should fail if the code has expired
        self.author.code_expires_at = now() - timedelta(minutes=1)  # Simulate expiration
        self.author.save()
        self.assertFalse(self.author.is_verification_code_valid("12345"))

    def test_clearing_verification_code(self):
        """Test that the verification code and expiration time are cleared."""
        self.author.set_verification_code("12345")
        self.author.clear_verification_code()
        self.assertIsNone(self.author.verification_code)
        self.assertIsNone(self.author.code_expires_at)

    def test_register_view(self):
        """Test that the registration view handles verification code generation and email sending."""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newsecurepassword'
        })
        # Assert that the response redirects to the confirmation page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('code_confirm'))

        # Check that the user and author have been created
        new_user = User.objects.get(username='newuser')
        new_author = Author.objects.get(author_name=new_user)
        self.assertIsNotNone(new_author.verification_code)

        # Check that a verification email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('newuser@example.com', mail.outbox[0].to)
        self.assertIn(new_author.verification_code, mail.outbox[0].body)

    def test_confirm_code_view_success(self):
        """Test that the confirmation view validates the code and clears it on success."""
        self.author.set_verification_code("12345")
        response = self.client.post(reverse('code_confirm'), {
            'email': 'testuser@example.com',
            'code': '12345'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email verified successfully!')
        self.author.refresh_from_db()
        self.assertIsNone(self.author.verification_code)

    def test_confirm_code_view_failure_invalid_code(self):
        """Test that the confirmation view rejects invalid codes."""
        self.author.set_verification_code("12345")
        response = self.client.post(reverse('code_confirm'), {
            'email': 'testuser@example.com',
            'code': '54321'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid code!')
        self.author.refresh_from_db()
        self.assertIsNotNone(self.author.verification_code)

    def test_confirm_code_view_failure_expired_code(self):
        """Test that the confirmation view rejects expired codes."""
        self.author.set_verification_code("12345")
        self.author.code_expires_at = now() - timedelta(minutes=1)  # Simulate expiration
        self.author.save()
        response = self.client.post(reverse('code_confirm'), {
            'email': 'testuser@example.com',
            'code': '12345'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid code!')
        self.author.refresh_from_db()
        self.assertIsNotNone(self.author.verification_code)


# Create your tests here.
