from django.contrib import admin
from .models import Job, JobApplication, Milestone, Payment, Contact, Message

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """
    Admin configuration for Job model
    """
    list_display = (
        'title', 'employer', 'freelancer', 'status', 
        'total_budget', 'created_at', 'deadline','Progress'
    )
    list_filter = (
        'status', 'created_at', 'deadline'
    )
    search_fields = (
        'title', 'description', 
        'employer__user__email', 
        'freelancer__user__email'
    )
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Job Details', {
            'fields': (
                'title', 'description', 'skills_required',
                'employer', 'freelancer'
            )
        }),
        ('Job Status', {
            'fields': (
                'status', 'total_budget', 
                'deadline'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            )
        })
    )

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """
    Admin configuration for JobApplication model
    """
    list_display = (
        'job', 'freelancer', 'proposed_rate', 
        'status', 'applied_at'
    )
    list_filter = (
        'status', 'applied_at'
    )
    search_fields = (
        'job__title', 
        'freelancer__user__email', 
        'cover_letter'
    )
    list_editable = ('status',)
    readonly_fields = ('applied_at', 'updated_at')
    
    fieldsets = (
        ('Application Details', {
            'fields': (
                'job', 'freelancer', 
                'proposed_rate', 'cover_letter'
            )
        }),
        ('Application Status', {
            'fields': (
                'status',
            )
        }),
        ('Timestamps', {
            'fields': (
                'applied_at', 'updated_at'
            )
        })
    )

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    """
    Admin configuration for Milestone model
    """
    list_display = (
        'title', 'job', 'status', 'budget', 
        'start_date', 'expected_end_date', 'completed_date'
    )
    list_filter = (
        'status', 'start_date', 
        'expected_end_date', 'completed_date'
    )
    search_fields = (
        'title', 'description', 
        'job__title'
    )
    list_editable = ('status',)
    readonly_fields = ('start_date', 'completed_date')
    
    fieldsets = (
        ('Milestone Details', {
            'fields': (
                'job', 'title', 'description', 
                'budget'
            )
        }),
        ('Milestone Status', {
            'fields': (
                'status', 
                'expected_end_date'
            )
        }),
        ('Dates', {
            'fields': (
                'start_date', 'completed_date'
            )
        })
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Payment model
    """
    list_display = (
        'milestone', 'freelancer', 'amount', 
        'status', 'payment_method', 
        'transaction_id', 'created_at', 'paid_at'
    )
    list_filter = (
        'status', 'created_at', 
        'paid_at', 'payment_method'
    )
    search_fields = (
        'milestone__title', 
        'freelancer__user__email', 
        'transaction_id'
    )
    list_editable = ('status',)
    readonly_fields = (
        'created_at', 'updated_at', 
        'paid_at'
    )
    
    fieldsets = (
        ('Payment Details', {
            'fields': (
                'milestone', 'freelancer', 
                'amount', 'payment_method', 
                'transaction_id'
            )
        }),
        ('Payment Status', {
            'fields': (
                'status',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at', 
                'paid_at'
            )
        })
    )





@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('employer', 'freelancer', 'job', 'created_at')
    search_fields = (
        'employer__user__email',
        'freelancer__user__email',
        'job__title'
    )
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'contact', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = (
        'sender__email',
        'contact__employer__user__email',
        'contact__freelancer__user__email',
        'content'
    )
    readonly_fields = ('timestamp',)
