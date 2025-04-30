from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from job.models import Job, JobApplication, Milestone, Payment, Submission
from dispute.models import DisputeApplication, Dispute
from accounts.models import EmployerProfile, FreelancerProfile
from django.utils import timezone
from datetime import timedelta
from colorama import Fore, Back, Style, init

# Initialize Colorama
init(autoreset=True)

User = get_user_model()

class ViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        self.employer_user = User.objects.create_user(
            email='employer@test.com', password='testpassword', user_type='employer')
        self.freelancer_user = User.objects.create_user(
            email='freelancer@test.com', password='testpassword', user_type='freelancer')

        self.employer_profile = EmployerProfile.objects.get(user=self.employer_user)
        self.freelancer_profile = FreelancerProfile.objects.get(user=self.freelancer_user)

        self.job = Job.objects.create(
            employer=self.employer_profile,
            title='Test Job',
            description='Testing job description',
            skills_required='Python, Django',
            total_budget=1000,
            deadline=timezone.now() + timedelta(days=10),
            status='open'
        )

        self.job.freelancer = self.freelancer_profile
        self.job.save()

        self.milestone = Milestone.objects.create(
            job=self.job,
            title='Milestone 1',
            description='Milestone description',
            budget=500,
            expected_end_date=timezone.now() + timedelta(days=5)
        )

        self.client.login(email='employer@test.com', password='testpassword')

    def print_test_result(self, test_name, message, status):
        """ Helper function to print test result nicely with colors """
        if status == 'PASS':
            print(f"{Fore.GREEN}{Back.BLACK}{Style.BRIGHT}Test: {test_name}{Style.RESET_ALL} - {message}")
        elif status == 'FAIL':
            print(f"{Fore.RED}{Back.BLACK}{Style.BRIGHT}Test: {test_name}{Style.RESET_ALL} - {message}")
        else:
            print(f"{Fore.YELLOW}{Back.BLACK}{Style.BRIGHT}Test: {test_name}{Style.RESET_ALL} - {message}")


    def test_submit_dispute(self):
        self.print_test_result('Submit Dispute', "Running...", "RUNNING")
        url = reverse('submit_dispute', kwargs={'job_id': self.job.id})
        response = self.client.post(url, {
            'title': 'Dispute Test Title',
            'description': 'Dispute Test Description',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(DisputeApplication.objects.filter(title='Dispute Test Title').exists())
        self.assertTrue(Dispute.objects.filter(title='Dispute Test Title').exists())
        self.print_test_result('Submit Dispute', "Dispute submitted successfully.", "PASS")



    def test_resolve_dispute(self):
        self.print_test_result('Resolve Dispute', "Running...", "RUNNING")
        dispute_app = DisputeApplication.objects.create(
            job=self.job,
            applicant=self.employer_user,
            title='Dispute App Test',
            description='Desc'
        )
        dispute = Dispute.objects.create(
            dispute_application=dispute_app,
            title='Dispute App Test',
            description='Desc',
            status='open'
        )
        url = reverse('resolve_dispute', kwargs={'job_id': self.job.id})
        response = self.client.post(url, {'dispute_id': dispute.id})
        self.assertEqual(response.status_code, 302)
        dispute.refresh_from_db()
        self.assertEqual(dispute.status, 'resolved')
        self.print_test_result('Resolve Dispute', "Dispute resolved successfully.", "PASS")


    def test_job_detail_view(self):
        self.print_test_result('Job Detail View', "Running...", "RUNNING")
        url = reverse('job_detail', kwargs={'job_id': self.job.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')
        self.assertTemplateUsed(response, 'ProjectPage.html')
        self.print_test_result('Job Detail View', "Job details displayed successfully.", "PASS")




    def test_submit_job_application(self):
        self.print_test_result('Submit Job Application', "Running...", "RUNNING")
        self.client.logout()
        self.client.login(email='freelancer@test.com', password='testpassword')
        url = reverse('submit_job_application', kwargs={'job_id': self.job.id})
        response = self.client.post(url, {
            'cover_letter': 'I am interested.',
            'bid_amount': 500,
            'time_estimate': 5
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(JobApplication.objects.filter(freelancer=self.freelancer_profile, job=self.job).exists())
        self.print_test_result('Submit Job Application', "Application submitted successfully.", "PASS")



    def test_accept_milestone(self):
        self.print_test_result('Accept Milestone', "Running...", "RUNNING")
        url = reverse('accept_milestone', kwargs={'milestone_id': self.milestone.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.milestone.refresh_from_db()
        self.assertEqual(self.milestone.status, 'completed')
        self.print_test_result('Accept Milestone', "Milestone accepted and completed.", "PASS")



    def test_milestone_submission(self):
        self.print_test_result('Milestone Submission', "Running...", "RUNNING")
        self.client.logout()
        self.client.login(email='freelancer@test.com', password='testpassword')
        url = reverse('milestone_submission', kwargs={'milestone_id': self.milestone.id})
        response = self.client.post(url, {'paragraph': 'This is my submission.'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Submission.objects.filter(milestone=self.milestone).exists())
        self.print_test_result('Milestone Submission', "Milestone submitted successfully.", "PASS")



    def test_add_dispute_view(self):
        self.print_test_result('Add Dispute View', "Running...", "RUNNING")
        url = reverse('add_dispute', kwargs={'job_id': self.job.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'AddDispute.html')
        self.assertEqual(response.context['job'], self.job)
        self.print_test_result('Add Dispute View', "Add dispute form loaded successfully.", "PASS")



    def test_accept_conflict(self):
        self.print_test_result('Accept Conflict', "Running...", "RUNNING")
        dispute_app = DisputeApplication.objects.create(
            job=self.job,
            applicant=self.employer_user,
            title='Conflict App',
            description='Conflict'
        )
        dispute = Dispute.objects.create(
            dispute_application=dispute_app,
            title='Conflict',
            description='Conflict description',
            status='open'
        )
        url = reverse('accept_conflict', kwargs={'job_id': self.job.id, 'dispute_id': dispute.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        dispute.refresh_from_db()
        self.assertEqual(dispute.status, 'in_progress')
        self.print_test_result('Accept Conflict', "Dispute moved to in_progress.", "PASS")



    def test_hire_freelancer_view(self):
        self.print_test_result('Hire Freelancer View', "Running...", "RUNNING")
        url = reverse('hire_freelancer')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'HireFreelancer.html')
        self.print_test_result('Hire Freelancer View', "Hire freelancer page loaded.", "PASS")




    def test_employer_dashboard(self):
        self.print_test_result('Employer Dashboard View', "Running...", "RUNNING")
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Employer_Dashboard.html')
        self.assertContains(response, 'Employer')
        self.print_test_result('Employer Dashboard View', "Employer dashboard displayed.", "PASS")



    def test_accept_application(self):
        self.print_test_result('Accept Application', "Running...", "RUNNING")
        application = JobApplication.objects.create(
            job=self.job,
            freelancer=self.freelancer_profile,
            proposed_rate=400,
            cover_letter="Cover letter",
            time_estimate=7,
            status='pending'
        )
        url = reverse('accept_application', kwargs={'application_id': application.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        application.refresh_from_db()
        self.assertEqual(application.status, 'accepted')
        self.print_test_result('Accept Application', "Application accepted successfully.", "PASS")



    def test_freelancer_dashboard(self):
        self.print_test_result('Freelancer Dashboard View', "Running...", "RUNNING")
        self.client.logout()
        self.client.login(email='freelancer@test.com', password='testpassword')
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Freelancer_Dashboard.html')
        self.assertContains(response, 'Freelancer')
        self.print_test_result('Freelancer Dashboard View', "Freelancer dashboard displayed.", "PASS")




    def test_admin_dashboard(self):
        self.print_test_result('Admin Dashboard View', "Running...", "RUNNING")
        admin_user = User.objects.create_user(
            email='admin@test.com', password='testpassword', user_type='admin', is_staff=True
        )
        self.client.logout()
        self.client.login(email='admin@test.com', password='testpassword')
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Admin_Dashboard.html')
        self.print_test_result('Admin Dashboard View', "Admin dashboard displayed.", "PASS")



    def test_add_job_view_get(self):
        self.print_test_result('Add Job View (GET)', "Running...", "RUNNING")
        url = reverse('add_job')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'AddProject.html')
        self.print_test_result('Add Job View (GET)', "Add Job page loaded successfully.", "PASS")



    def test_milestone_submission_get(self):
        self.print_test_result('Milestone Submission (GET)', "Running...", "RUNNING")
        self.client.logout()
        self.client.login(email='freelancer@test.com', password='testpassword')

        url = reverse('milestone_submission', kwargs={'milestone_id': self.milestone.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Submission.html')
        self.assertContains(response, self.milestone.title)
        self.print_test_result('Milestone Submission (GET)', "Milestone submission form opened successfully.", "PASS")



    def test_accept_milestone_forbidden_for_wrong_user(self):
        self.print_test_result('Accept Milestone Forbidden (Wrong User)', "Running...", "RUNNING")
        self.client.logout()
        self.client.login(email='freelancer@test.com', password='testpassword')

        url = reverse('accept_milestone', kwargs={'milestone_id': self.milestone.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)  # Redirect since not allowed
        self.milestone.refresh_from_db()
        self.assertNotEqual(self.milestone.status, 'completed')  # Still not completed
        self.print_test_result('Accept Milestone Forbidden (Wrong User)', "Freelancer correctly blocked from accepting milestone.", "PASS")


    def test_hire_freelancer_forbidden_for_non_employer(self):
        self.print_test_result('Hire Freelancer Forbidden', "Running...", "RUNNING")
        self.client.logout()
        self.client.login(email='freelancer@test.com', password='testpassword')
        url = reverse('hire_freelancer')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.print_test_result('Hire Freelancer Forbidden', "Freelancer access to hire freelancer page correctly forbidden.", "PASS")
