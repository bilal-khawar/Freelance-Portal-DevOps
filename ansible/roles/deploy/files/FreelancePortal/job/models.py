from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import CustomUser, FreelancerProfile, EmployerProfile
from django.db import transaction
from decimal import Decimal

class Job(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )

    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='posted_jobs')
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.SET_NULL, related_name='assigned_jobs', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    skills_required = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_budget = models.DecimalField(max_digits=10, decimal_places=2)
    Progress = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)


    
    freelancer_rating= models.DecimalField(max_digits=3, decimal_places=2, default=0)
    employer_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.title} - {self.status}"
    
    def update_progress_based_on_status(self):
        self.update_status_based_on_milestones()
        status_progress_map = {
            'draft': 0,
            'open': 5,
            'in_progress': 50,
            'completed': 100,
            'cancelled': 0
        }
        self.Progress = status_progress_map.get(self.status, 0)
        self.save()
        

    def update_status_based_on_milestones(self):
        milestones = self.milestones.all()
        total = milestones.count()
        completed = milestones.filter(status='completed').count()

        if total == 0:
            return  # No update if there are no milestones

        if completed == total:
            self.status = 'completed'
            self.freelancer.hours_logged += int(Decimal('0.00001') * self.total_budget)
            self.Progress=100
            self.freelancer.save()
        elif completed > 0:
            self.status = 'in_progress'

        else:
            self.status = 'open'

        


class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='job_applications')
    proposed_rate = models.DecimalField(max_digits=10, decimal_places=2)
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    time_estimate = models.PositiveIntegerField(null=True, blank=True) 

    def __str__(self):
        return f"Application by {self.freelancer.user.email} for {self.job.title}"

    def accept(self):
        # Accept this job application and reject others for the same job
        with transaction.atomic():
            # Reject all other applications for the same job
            JobApplication.objects.filter(job=self.job).exclude(id=self.id).update(status='rejected')
            
            # Set the current application as accepted
            self.status = 'accepted'
            self.save()

            # Set the job status to 'in_progress' if it was open
            if self.job.status == 'open':
                self.job.status = 'in_progress'
                self.job.freelancer = self.freelancer  # Assign freelancer to the job
                self.job.save()

    def reject(self):
        # Reject the current job application
        self.status = 'rejected'
        self.save()

    


class Milestone(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected')
    )
    

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField(null=True, blank=True)
    expected_end_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.status}"

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment for job: {self.job.title if self.job else 'N/A'}, milestone: {self.milestone.title if self.milestone else 'N/A'}"


class Contact(models.Model):
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='contacts')
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='contacts')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='contacts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employer', 'freelancer', 'job')

    def __str__(self):
        return f"Contact: {self.employer.user.email} & {self.freelancer.user.email} for {self.job.title}"

class Message(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.email} at {self.timestamp.strftime('%d-%m-%Y %H:%M')}"


class Submission(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='submissions')
    timestamp = models.DateTimeField(auto_now_add=True)
    paragraph = models.TextField()

    def __str__(self):
        return f"Submission for {self.milestone.title} at {self.timestamp.strftime('%d-%m-%Y %H:%M')}"
