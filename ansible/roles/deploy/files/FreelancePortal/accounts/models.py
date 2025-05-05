from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models import F, Sum, DecimalField, ExpressionWrapper


class CustomUserManager(BaseUserManager):
    """
    Custom user manager for the CustomUser model with email as the unique identifier
    instead of username.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    """
    Base User model with email as the unique identifier
    """
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('employer', 'Employer'),
        ('freelancer', 'Freelancer'),
    )

    # Make email the unique identifier
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    
    # Name fields
    first_name = models.CharField(_('first name'), max_length=30)
    middle_name = models.CharField(_('middle name'), max_length=30, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=150)
    
    # Additional custom fields
    phone_number = models.CharField(max_length=15, default="Not provided")
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, blank=True, null=True)
    
    # Set email as the USERNAME_FIELD
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email

class NonAdminUser(CustomUser):
    """
    Base class for non-admin users (employers and freelancers)
    """
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            # Ensure user_type is not admin when creating
            self.user_type = self.user_type or 'employer'
        super().save(*args, **kwargs)

class EmployerUser(NonAdminUser):
    """
    Employer-specific user model
    """
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.user_type = 'employer'
        super().save(*args, **kwargs)

class FreelancerUser(NonAdminUser):
    """
    Freelancer-specific user model
    """
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.user_type = 'freelancer'
        super().save(*args, **kwargs)

class AdminUser(CustomUser):
    """
    Admin-specific user model
    """
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.user_type = 'admin'
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)

class FreelancerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='freelancer_profile')
    jobs_completed = models.IntegerField(default=0)
    money_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    jobs_in_queue = models.IntegerField(default=0)
    applications_pending = models.IntegerField(default=0)
    hours_logged = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_routing_number = models.CharField(max_length=50, blank=True, null=True)
    paypal_email = models.EmailField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    def __str__(self):
        return f"Freelancer Profile: {self.user.email}"

    def update(self, alljobs, alldispute, allusers, allapplications):
        user_jobs = alljobs.filter(freelancer=self)
        completed_jobs = user_jobs.filter(status='completed')
        self.jobs_completed = completed_jobs.count()
        self.jobs_in_queue = user_jobs.exclude(status='completed').count()
        self.applications_pending = alljobs.filter(applications__freelancer__user=self.user, status='open').distinct().count()
        self.hours_logged=0.0
        # Earnings from completed payments
        milestone_earnings = self.payments.filter(
            milestone__status='completed',
            status='completed'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0


        # Add 80% of each completed job's total budget
        job_bonuses = completed_jobs.aggregate(
            bonus=Sum(
                ExpressionWrapper(F('total_budget') * 0.8, output_field=DecimalField())
            )
        )['bonus'] or 0

        self.money_earned = milestone_earnings + job_bonuses

        # Rating calculation
        ratings = completed_jobs.exclude(freelancer_rating__isnull=True).values_list('freelancer_rating', flat=True)
        ratings = list(ratings)
        self.average_rating = sum(ratings) / len(ratings) if ratings else 0

        self.save()





class EmployerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employer_profile')
    jobs_posted = models.IntegerField(default=0)
    jobs_open = models.IntegerField(default=0)
    jobs_active = models.IntegerField(default=0)
    hired_freelancers = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pending_payments = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    def __str__(self):
        return f"Employer Profile: {self.user.email}"

    def update(self, alljobs, alldispute, allusers, allapplications):
        user_jobs = alljobs.filter(employer=self)
        completed_jobs = user_jobs.filter(status='completed')

        self.jobs_posted = user_jobs.count()
        self.jobs_open = user_jobs.filter(status='open').count()
        self.jobs_active = user_jobs.exclude(status__in=['completed', 'cancelled']).count()
        self.hired_freelancers = allapplications.filter(job__in=user_jobs, status='accepted').values('freelancer').distinct().count()

        # Total spent: sum of completed payments on completed jobs
        self.total_spent = completed_jobs.aggregate(
            total=models.Sum('payments__amount', filter=models.Q(payments__status='completed'))
        )['total'] or 0

        # Pending payments: sum of pending payments across all employer jobs
        self.pending_payments = user_jobs.aggregate(
            total=models.Sum('payments__amount', filter=models.Q(payments__status='pending'))
        )['total'] or 0

        # Total budget of all jobs posted
        self.total_budget = user_jobs.aggregate(
            total=models.Sum('total_budget')
        )['total'] or 0

        # Average freelancer rating given by employer
        ratings = user_jobs.exclude(freelancer_rating__isnull=True).values_list('freelancer_rating', flat=True)
        ratings = list(ratings)
        self.average_rating = sum(ratings) / len(ratings) if ratings else 0

        self.save()



class AdminProfile(models.Model):
    """
    Profile model for admins with admin-specific attributes.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='admin_profile')
    issues_reported = models.IntegerField(default=0)
    issues_resolved = models.IntegerField(default=0)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    access_level = models.CharField(max_length=20, default="standard")
    
    def __str__(self):
        return f"Admin Profile: {self.user.email}"

# Signal handlers to create appropriate profile when a user is created
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create the appropriate profile when a user is created.
    """
    if created:
        if instance.user_type == 'freelancer':
            FreelancerProfile.objects.create(user=instance)
        elif instance.user_type == 'employer':
            EmployerProfile.objects.create(user=instance)
        elif instance.user_type == 'admin':
            AdminProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler to save the appropriate profile when a user is saved.
    """
    if instance.user_type == 'freelancer' and hasattr(instance, 'freelancer_profile'):
        instance.freelancer_profile.save()
    elif instance.user_type == 'employer' and hasattr(instance, 'employer_profile'):
        instance.employer_profile.save()
    elif instance.user_type == 'admin' and hasattr(instance, 'admin_profile'):
        instance.admin_profile.save()