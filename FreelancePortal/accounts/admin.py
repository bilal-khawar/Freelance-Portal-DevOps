from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, FreelancerProfile, EmployerProfile, AdminProfile

class AdminProfileInline(admin.StackedInline):
    """
    Inline admin for AdminProfile
    """
    model = AdminProfile
    extra = 0
    readonly_fields = ('user',)
    can_delete = False

class FreelancerProfileInline(admin.StackedInline):
    """
    Inline admin for FreelancerProfile
    """
    model = FreelancerProfile
    extra = 0
    readonly_fields = ('user',)
    can_delete = False

class EmployerProfileInline(admin.StackedInline):
    """
    Inline admin for EmployerProfile
    """
    model = EmployerProfile
    extra = 0
    readonly_fields = ('user',)
    can_delete = False

class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for CustomUser model with intelligent profile pairing
    """
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    
    # Define inlines for all possible profile types
    inlines = [
        AdminProfileInline, 
        FreelancerProfileInline, 
        EmployerProfileInline
    ]
    
    # Fieldsets for editing an existing user
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': (
                'first_name', 
                'middle_name', 
                'last_name', 
                'phone_number',
                'user_type'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_staff', 
                'is_active', 
                'is_superuser', 
                'groups', 
                'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': (
                'last_login', 
                'date_joined'
            )
        }),
    )
    
    # Fieldsets for creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'first_name', 
                'middle_name', 
                'last_name', 
                'phone_number', 
                'user_type', 
                'password1', 
                'password2'
            ),
        }),
    )
    
    # Search and ordering
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    def get_inline_instances(self, request, obj=None):
        """
        Filter inline instances based on user type
        """
        inline_instances = []
        for inline_class in self.inlines:
            inline = inline_class(self.model, self.admin_site)
            if obj:
                # Only show inline if it matches the user type
                if (obj.user_type == 'admin' and inline.model == AdminProfile) or \
                   (obj.user_type == 'freelancer' and inline.model == FreelancerProfile) or \
                   (obj.user_type == 'employer' and inline.model == EmployerProfile):
                    inline_instances.append(inline)
            else:
                # For new users, don't show any inlines
                pass
        return inline_instances

class FreelancerProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for FreelancerProfile model
    """
    list_display = (
        'user', 
        'jobs_completed', 
        'money_earned', 
        'jobs_in_queue', 
        'applications_pending', 
        'hours_logged'
    )
    
    list_filter = (
        'jobs_completed', 
        'applications_pending', 
        'jobs_in_queue'
    )
    
    search_fields = (
        'user__email', 
        'user__first_name', 
        'user__last_name', 
        'skills', 
        'bio'
    )
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Job Statistics', {
            'fields': (
                'jobs_completed', 
                'money_earned', 
                'jobs_in_queue', 
                'applications_pending', 
                'hours_logged'
            )
        }),
        ('Banking Information', {
            'fields': (
                'bank_account_number', 
                'bank_routing_number', 
                'paypal_email'
            )
        }),
        ('Profile Information', {
            'fields': (
                'skills', 
                'bio'
            )
        }),
    )
    
    readonly_fields = ('user',)

class EmployerProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for EmployerProfile model
    """
    list_display = (
        'user', 
        'company_name', 
        'jobs_posted', 
        'jobs_open', 
        'jobs_active', 
        'hired_freelancers', 
        'total_spent', 
        'total_budget'
    )
    
    list_filter = (
        'jobs_posted', 
        'jobs_open', 
        'hired_freelancers'
    )
    
    search_fields = (
        'user__email', 
        'user__first_name', 
        'user__last_name', 
        'company_name', 
        'company_website'
    )
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Company Information', {
            'fields': (
                'company_name', 
                'company_website'
            )
        }),
        ('Job Statistics', {
            'fields': (
                'jobs_posted', 
                'jobs_open', 
                'jobs_active', 
                'hired_freelancers'
            )
        }),
        ('Financial Information', {
            'fields': (
                'total_spent', 
                'spent', 
                'total_budget', 
                'pending_payments'
            )
        }),
    )
    
    readonly_fields = ('user',)

class AdminProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for AdminProfile model
    """
    list_display = (
        'user', 
        'issues_reported', 
        'issues_resolved', 
        'access_level', 
        'last_login_ip'
    )
    
    list_filter = (
        'access_level', 
        'issues_reported', 
        'issues_resolved'
    )
    
    search_fields = (
        'user__email', 
        'user__first_name', 
        'user__last_name', 
        'last_login_ip'
    )
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Issue Management', {
            'fields': (
                'issues_reported', 
                'issues_resolved'
            )
        }),
        ('Access Information', {
            'fields': (
                'access_level', 
                'last_login_ip'
            )
        }),
    )
    
    readonly_fields = ('user',)

# Register models with their respective admin classes
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(FreelancerProfile, FreelancerProfileAdmin)
admin.site.register(EmployerProfile, EmployerProfileAdmin)
admin.site.register(AdminProfile, AdminProfileAdmin)