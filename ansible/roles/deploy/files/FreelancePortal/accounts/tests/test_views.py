from django.test import TestCase
from django.urls import reverse
from accounts.models import CustomUser
from accounts.forms import CustomUserChangeForm
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

class UserAuthAndChangeFormTests(TestCase):

    def setUp(self):

        self.user = CustomUser.objects.create_user(
            email='bilal123@gmail.com',
            password='test123strong',
            user_type='Employer',
            first_name='Bilal',
            last_name='Khan',
        )

    def print_test_result(self, test_name, message, status):
        """ Helper function to print test result with color """
        if status == 'PASS':
            print(f"{Fore.GREEN}{Back.BLACK}{Style.BRIGHT}Test: {test_name}{Style.RESET_ALL} - {message}")
        elif status == 'FAIL':
            print(f"{Fore.RED}{Back.BLACK}{Style.BRIGHT}Test: {test_name}{Style.RESET_ALL} - {message}")
        else:
            print(f"{Fore.YELLOW}{Back.BLACK}{Style.BRIGHT}Test: {test_name}{Style.RESET_ALL} - {message}")

    def test_valid_employer_registration(self):
        self.print_test_result('Valid Employer Registration', "Running...", "RUNNING")
        response = self.client.post(reverse('register'), {
            'email': 'bilal@gmail.com',
            'password1': 'test123strong',
            'password2': 'test123strong',
            'user_type': 'Employer',
            'first_name': 'Bilal',
            'last_name': 'Khan',
        })

        self.assertEqual(response.status_code, 200)  
        self.print_test_result('Valid Employer Registration', "Registration test passed with status code: " + str(response.status_code), 'PASS')

    def test_valid_login_redirect(self):
        self.print_test_result('Valid Login Redirect', "Running...", "RUNNING")
        # Create user first
        CustomUser.objects.create_user(
            email='bilal@gmail.com',
            password='test123strong',
            user_type='Employer',
            first_name='Bilal',
            last_name='Khan'
        )

        response = self.client.post(reverse('login'), {
            'username': 'bilal@gmail.com',
            'password': 'test123strong'
        })

        self.assertEqual(response.status_code, 302) 
        self.print_test_result('Valid Login Redirect', "User successfully redirected to home page.", 'PASS')



    def test_password_minimum_length(self):
        self.print_test_result('Password Minimum Length', "Running...", "RUNNING")
        response = self.client.post(reverse('register'), {
            'email': 'test123@gmail.com',
            'password1': 'test',
            'password2': 'test',
            'user_type': 'Employer',
            'first_name': 'Bilal',
            'last_name': 'Khan',
        })

        self.assertEqual(response.status_code, 200)
        user = CustomUser.objects.filter(email='test123@gmail.com').exists()
        self.assertFalse(user, "User with minimum password length should not be created.")
        self.print_test_result('Password Minimum Length', "Password validation for minimum length passed.", 'PASS')

    def test_user_change_form_valid_data(self):
        self.print_test_result('User Change Form (Valid Data)', "Running...", "RUNNING")
        form_data = {
            'email': 'new_email@gmail.com',
            'first_name': 'Bilal',
            'last_name': 'Khan',
            'middle_name': 'Ali',
            'phone_number': '1234567890',
        }

        form = CustomUserChangeForm(instance=self.user, data=form_data)

        self.assertTrue(form.is_valid()) 
        updated_user = form.save()  

        self.assertEqual(updated_user.email, 'new_email@gmail.com')
        self.assertEqual(updated_user.first_name, 'Bilal')
        self.assertEqual(updated_user.middle_name, 'Ali')
        self.assertEqual(updated_user.phone_number, '1234567890')
        self.print_test_result('User Change Form (Valid Data)', "Valid data test passed with updated user details.", 'PASS')

    def test_user_change_form_invalid_email(self):
        self.print_test_result('User Change Form (Invalid Email)', "Running...", "RUNNING")
        form_data = {
            'email': 'invalid_email', 
            'first_name': 'Bilal',
            'last_name': 'Khan',
            'middle_name': 'Ali',
            'phone_number': '1234567890',
        }

        form = CustomUserChangeForm(instance=self.user, data=form_data)

        self.assertFalse(form.is_valid())  
        self.assertIn('email', form.errors) 
        self.print_test_result('User Change Form (Invalid Email)', "Invalid email test passed with form errors.", 'PASS')

    def test_user_change_form_missing_phone_number(self):
        self.print_test_result('User Change Form (Missing Phone Number)', "Running...", "RUNNING")
        form_data = {
            'email': 'new_email@gmail.com',
            'first_name': 'Bilal',
            'last_name': 'Khan',
            'middle_name': 'Ali',
            'phone_number': '',  
        }

        form = CustomUserChangeForm(instance=self.user, data=form_data)

        self.assertFalse(form.is_valid()) 
        self.assertIn('phone_number', form.errors)  
        self.print_test_result('User Change Form (Missing Phone Number)', "Missing phone number test passed with form errors.", 'PASS')

    def test_user_change_form_update_without_password(self):
        self.print_test_result('User Change Form (Without Password)', "Running...", "RUNNING")
        form = CustomUserChangeForm(instance=self.user)

        self.assertNotIn('password', form.fields) 
        self.print_test_result('User Change Form (Without Password)', "Password field excluded test passed.", 'PASS')
