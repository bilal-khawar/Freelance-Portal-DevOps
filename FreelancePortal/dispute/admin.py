from django.contrib import admin
from .models import Dispute, DisputeApplication, DisputeMessage

class DisputeMessageInline(admin.TabularInline):
    """
    Inline admin for DisputeMessage model
    """
    model = DisputeMessage
    extra = 0
    readonly_fields = ('sender', 'sent_at')
    can_delete = False

class DisputeAdmin(admin.ModelAdmin):
    """
    Admin configuration for Dispute model
    """
    list_display = (
        'dispute_application', 
        'get_dispute_manager',  # Use a method to get the dispute_manager info
        'title', 
        'status', 
        'priority', 
        'created_at'
    )
    
    list_filter = (
        'status', 
        'priority', 
        'created_at'
    )
    
    search_fields = (
        'dispute_application__job__title', 
        'dispute_manager__email',  # Assuming CustomUser model has an email field
        'title', 
        'description'
    )
    
    inlines = [
        DisputeMessageInline
    ]
    
    fieldsets = (
        ('Dispute Details', {
            'fields': (
                'dispute_application', 
                'dispute_manager',  # Ensure this is added here as well
                'title', 
                'description'
            )
        }),
        ('Status', {
            'fields': (
                'status', 
                'priority'
            )
        }),
        ('Documentation', {
            'fields': (
                'supporting_documents',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 
                'updated_at', 
                'resolved_at'
            )
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

    def get_dispute_manager(self, obj):
        return obj.dispute_manager.email if obj.dispute_manager else None  # Accessing email of the manager
    get_dispute_manager.admin_order_field = 'dispute_manager'  # Optional for sorting by the manager field
    get_dispute_manager.short_description = 'Dispute Manager'  # Custom column header

class DisputeApplicationAdmin(admin.ModelAdmin):
    """
    Admin configuration for DisputeApplication model
    """
    list_display = (
        'job', 
        'applicant', 
        'title', 
        'status', 
        'created_at'
    )
    
    list_filter = (
        'status', 
        'created_at'
    )
    
    search_fields = (
        'job__title', 
        'applicant__email', 
        'title', 
        'description'
    )
    
    fieldsets = (
        ('Job Information', {
            'fields': (
                'job', 
                'applicant'
            )
        }),
        ('Application Details', {
            'fields': (
                'title', 
                'description', 
                'status'
            )
        }),
        ('Documentation', {
            'fields': (
                'supporting_documents',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 
                'updated_at'
            )
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

class DisputeMessageAdmin(admin.ModelAdmin):
    """
    Admin configuration for DisputeMessage model
    """
    list_display = (
        'dispute', 
        'sender', 
        'message_type', 
        'sent_at'
    )
    
    list_filter = (
        'message_type', 
        'sent_at'
    )
    
    search_fields = (
        'dispute__title', 
        'sender__email', 
        'content'
    )
    
    fieldsets = (
        ('Message Details', {
            'fields': (
                'dispute', 
                'sender', 
                'message_type', 
                'content'
            )
        }),
        ('Attachment', {
            'fields': (
                'attachment',
            )
        }),
        ('Timestamp', {
            'fields': (
                'sent_at',
            )
        }),
    )
    
    readonly_fields = ('sent_at',)

# Register models with their respective admin classes
admin.site.register(Dispute, DisputeAdmin)
admin.site.register(DisputeApplication, DisputeApplicationAdmin)
admin.site.register(DisputeMessage, DisputeMessageAdmin)
