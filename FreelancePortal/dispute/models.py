from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import CustomUser
from job.models import Job

class DisputeApplication(models.Model):
    """
    Represents an application or claim that can be the subject of a dispute.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )

    # Related Job
    job = models.ForeignKey(
        Job, 
        on_delete=models.CASCADE, 
        related_name='dispute_applications'
    )

    # Applicant (can be either freelancer or employer)
    applicant = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='dispute_applications'
    )

    # Application details
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Status and tracking
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )

    # Supporting documents
    supporting_documents = models.FileField(
        upload_to='dispute_application_docs/', 
        null=True, 
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dispute Application for {self.job} by {self.applicant}"


class Dispute(models.Model):
    """
    Represents a dispute raised in the platform.
    """
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    )

    # Related Dispute Application
    dispute_application = models.ForeignKey(
        DisputeApplication, 
        on_delete=models.CASCADE, 
        related_name='disputes'
    )

    # Dispute Manager - Assuming this is related to a CustomUser or AdminProfile
    dispute_manager = models.ForeignKey(
        CustomUser,  # or AdminProfile, depending on your model
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='managed_disputes'
    )

    # Dispute Details
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Status and Priority
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='open'
    )
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='medium'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Evidence and Documentation
    supporting_documents = models.FileField(
        upload_to='dispute_documents/', 
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"Dispute for {self.dispute_application} - {self.status}"

class DisputeMessage(models.Model):
    """
    Represents messages exchanged during a dispute.
    """
    MESSAGE_TYPE_CHOICES = (
        ('user', 'User Message'),
        ('admin', 'Admin Message'),
        ('system', 'System Message')
    )

    # Related Dispute
    dispute = models.ForeignKey(
        Dispute, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )

    # Sender
    sender = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='dispute_messages'
    )

    # Message Details
    message_type = models.CharField(
        max_length=20, 
        choices=MESSAGE_TYPE_CHOICES, 
        default='user'
    )
    content = models.TextField()
    
    # Attachments
    attachment = models.FileField(
        upload_to='dispute_attachments/', 
        null=True, 
        blank=True
    )

    # Timestamps
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message in {self.dispute} by {self.sender}"
