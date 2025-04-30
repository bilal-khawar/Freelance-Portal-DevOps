from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from . import views  # Import the views module with your test_page view


# Update this section in your FreelancePortal/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('test/', views.test_page, name='test_page'),  # Keep test page on its own URL
    
    # Uncomment the home URL to match redirects in your account views
    path('', views.home, name='home'),  # Make this the root URL for your site
    
    # Uncomment dashboard URL for authenticated users
    path('dashboard/', views.dashboard, name='dashboard'),
    path('projects/', views.projects, name='projects'),
    path('messages/', views.messages, name='messages'),
    path('profile/', views.profile, name='profile'),
    path('addProject/', views.add_project, name='addProject'),
    path('addUser/', views.add_user, name='addUser'),
    path('viewUsers/', views.view_users, name='viewUsers'),
    path('users/<int:user_id>/', views.user_detail_view, name='user_detail'),
    path('users/block/<int:user_id>/', views.user_block_view, name='user_block'),
    path('users/delete/<int:user_id>/', views.user_delete_view, name='user_delete'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('addDispute/<int:job_id>/', views.add_dispute, name='add_dispute'),
    path('resolveDispute/<int:job_id>/', views.resolve_dispute, name='resolve_dispute'),
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),
    path('milestone/<int:milestone_id>/', views.milestone_detail, name='milestone_detail'),
    path('payment/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('api/send-message/', views.send_personal_message, name='send_message'),
    path('api/get-messages/', views.get_messages, name='get_messages'),
    path('api/profile/update/', views.ajax_profile_update, name='ajax_profile_update'),
    path('payments/', views.makePayment, name='payments'),
    path('hire-freelancer', views.hire_freelancer, name='hire_freelancer'),
    path('contracts', views.contracts, name='contracts'),
    path('invoice', views.invoices, name='invoices'),
    path('reports', views.reports, name='reports'),
    path('add-job/', views.add_job, name='add_job'),
    path('error/', views.some_error_page, name='some_error_page'),
    path('job/<int:job_id>/apply/', views.submit_job_application, name='submit_job_application'),
    path('accept-application/<int:application_id>/', views.accept_application, name='accept_application'),
    path('reject-application/<int:application_id>/', views.reject_application, name='reject_application'),
    path('milestone/<int:milestone_id>/submission/', views.milestone_submission, name='milestone_submission'),
    path('milestone/<int:milestone_id>/', views.milestone_detail, name='milestone_detail'),
    path('milestone/<int:milestone_id>/submit_submission/', views.submit_submission, name='submit_submission'),
    path('milestone/<int:milestone_id>/accept_milestone/', views.accept_milestone, name='accept_milestone'),

    # Add the dispute URLs
    path('job/<int:job_id>/dispute/submit/', views.submit_dispute, name='submit_dispute'),
    path('disputes/<int:job_id>/accept/<int:dispute_id>/', views.accept_conflict, name='accept_conflict'),
    path('disputes/<int:dispute_id>/', views.dispute_detail, name='dispute_detail'),  # Dispute detail view
    path('job/<int:job_id>/dispute/add/', views.add_dispute, name='add_dispute'),  # Add dispute page
    path('job/<int:job_id>/dispute/resolve/', views.resolve_dispute, name='resolve_dispute'),  # Resolve dispute page
    path('disputes/<int:dispute_id>/message/', views.send_message, name='send_message'),  # Send message in dispute
    path('disputes/<int:dispute_id>/client/message/', views.send_message_client, name='send_message_client'),  # Send message in dispute
    path('disputes/<int:job_id>/accept/<int:dispute_id>/', views.accept_conflict, name='dispute_detail'),
    path('jobs/<int:job_id>/accepted-disputes/',views.accepted_disputes_view,name='accepted_disputes'),


]

# Serve static and media files during development and production
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
