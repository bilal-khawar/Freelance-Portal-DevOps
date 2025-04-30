# project_name/views.py (your main project views file)
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from job.models import Job
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, get_object_or_404
from job.models import Job, JobApplication, Milestone, Payment, Contact, Message, Submission
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count,Avg, Sum
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Avg, Q
from accounts.models import CustomUser,  FreelancerProfile, EmployerProfile
from dispute.models import DisputeApplication, Dispute,DisputeMessage
from django.db import transaction
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib import messages as django_messages

User = get_user_model()






@login_required
def submit_dispute(request, job_id):
    """
    Handles the submission of a new dispute for a job.
    """
    job = get_object_or_404(Job, id=job_id)
    user = request.user

    # Process the skills list
    skills = [skill.strip() for skill in job.skills_required.split(',')] if job.skills_required else []
    applications = job.applications.select_related('freelancer__user')
    milestones = job.milestones.all().order_by('start_date')
    payments = Payment.objects.filter(milestone__job=job).select_related('freelancer', 'milestone')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')

        # Simple validation for title and description
        if not title or not description:
            django_messages.error(request, "Title and description are required.")
            return redirect('add_dispute', job_id=job.id)

        # Create Dispute Application
        dispute_app = DisputeApplication.objects.create(
            job=job,
            applicant=user,
            title=title,
            description=description
        )

        # Create Dispute instance
        dispute = Dispute.objects.create(
            dispute_application=dispute_app,
            title=title,
            description=description,
            status='open',  # default status
            priority='medium'  # default priority
        )

        # Redirect to job detail page after dispute submission
        django_messages.success(request, "Dispute submitted successfully.")
        return redirect('job_detail', job_id=job.id)

    context = {
        'job': job,
        'skills': skills,
        'applications': applications,
        'milestones': milestones,
        'payments': payments,
    }
    return render(request, 'AddDispute.html', context)



@login_required
def dispute_detail(request, dispute_id):
    """
    Displays the details of a specific dispute.
    """
    dispute = get_object_or_404(Dispute, id=dispute_id)
    context = {
        'dispute': dispute
    }
    return render(request, 'DisputeDetail.html', context)


@login_required
def add_dispute(request, job_id):
    """
    Shows the form for submitting a new dispute for a specific job.
    """
    job = get_object_or_404(Job, id=job_id)
    skills = [skill.strip() for skill in job.skills_required.split(',')] if job.skills_required else []
    applications = job.applications.select_related('freelancer__user')
    milestones = job.milestones.all().order_by('start_date')
    payments = Payment.objects.filter(milestone__job=job).select_related('freelancer', 'milestone')

    context = {
        'job': job,
        'skills': skills,
        'applications': applications,
        'milestones': milestones,
        'payments': payments,
    }

    return render(request, 'AddDispute.html', context)


@login_required
def resolve_dispute(request, job_id):
    """
    Resolves a dispute by updating its status to 'resolved' and marking the dispute application as completed.
    """
    job = get_object_or_404(Job, id=job_id)

    # Fetch all dispute applications for the job
    dispute_applications = DisputeApplication.objects.filter(job=job)

    if request.method == 'POST':
        dispute_id = request.POST.get('dispute_id')
        dispute = get_object_or_404(Dispute, id=dispute_id)

        if dispute.status == 'resolved':
            django_messages.warning(request, "This dispute has already been resolved.")
            return redirect('job_detail', job_id=job.id)

        # Resolve the dispute
        dispute.status = 'resolved'
        dispute.save()

        # Mark the dispute application as completed
        dispute_application = dispute.dispute_application
        dispute_application.status = 'completed'
        dispute_application.save()

        django_messages.success(request, "The dispute has been resolved successfully.")
        return HttpResponseRedirect(reverse('job_detail', args=[job.id]))

    return render(request, 'ResolveDispute.html', {
        'job': job,
        'dispute_applications': dispute_applications,
    })

@require_POST
@login_required
def accept_conflict(request, job_id, dispute_id):
    dispute = get_object_or_404(Dispute, id=dispute_id)
    dispute.status = 'in_progress'
    dispute.save()
    django_messages.success(request, "Dispute marked as in progress.")

    # Redirect back to the "resolve disputes" page for this job
    return redirect('resolve_dispute', job_id=job_id)

@login_required
def send_message(request, dispute_id):
    """
    Allows users to send messages related to a specific dispute.
    """
    if request.method == 'POST':
        content = request.POST.get('content')
        dispute = get_object_or_404(Dispute, id=dispute_id)

        # Check if the message is being sent by an admin or user
        message_type = 'admin' if request.user.is_staff else 'user'

        # Create the message
        DisputeMessage.objects.create(
            dispute=dispute,
            sender=request.user,
            content=content,
            message_type=message_type
        )

        django_messages.success(request, "Message sent successfully.")
        return redirect('resolve_dispute', job_id=dispute.dispute_application.job.id)

    return HttpResponseRedirect(reverse('resolve_dispute', args=[dispute.dispute_application.job.id]))



@login_required
def send_message_client(request, dispute_id):
    """
    Allows users to send messages related to a specific dispute.
    """
    if request.method == 'POST':
        content = request.POST.get('content')
        dispute = get_object_or_404(Dispute, id=dispute_id)

        # Check if the message is being sent by an admin or user
        message_type = 'admin' if request.user.is_staff else 'user'

        # Create the message
        DisputeMessage.objects.create(
            dispute=dispute,
            sender=request.user,
            content=content,
            message_type=message_type
        )

        django_messages.success(request, "Message sent successfully.")
        return redirect('accepted_disputes', job_id=dispute.dispute_application.job.id)

    return HttpResponseRedirect(reverse('accepted_disputes', args=[dispute.dispute_application.job.id]))








def test_page(request):
    """Your existing test page view."""
    return render(request, 'Test.html')

def home(request):
    """Home page view that can serve as your main landing page."""
    return render(request, 'Home.html')


@login_required
def accepted_disputes_view(request, job_id):
    # Load the job or 404
    job = get_object_or_404(Job, id=job_id)

    # Fetch only "in_progress" disputes for that job
    disputes = (
        Dispute.objects
        .filter(status='in_progress', dispute_application__job=job)
        .select_related(
            'dispute_application__job',
            'dispute_application__applicant'
        )
        .prefetch_related('messages__sender')
    )

    return render(request, 'ClientSideDisputePage.html', {
        'job': job,
        'accepted_disputes': disputes,
    })


@login_required
def projects(request):
    user = request.user
    user_type = user.user_type

    # Base queryset
    alljobs=Job.objects.all()
    if user_type == 'freelancer':
        profile = user.freelancer_profile
        jobs = Job.objects.filter(freelancer=profile)
    elif user_type == 'employer':
        profile = user.employer_profile
        jobs = Job.objects.filter(employer=profile)
    else:  # admin
        jobs = Job.objects.all()

    # Skill list population
    for job in jobs:
        job.skill_list = [s.strip() for s in (job.skills_required or '').split(',')]
        job.update_progress_based_on_status()
       

    # Categorize
    ongoing = jobs.filter(status__in=['open', 'in_progress'])
    completed = jobs.filter(status='completed')

    context = {
        'jobs': alljobs if user_type != 'employer' else None,
        'ongoing_jobs': ongoing,
        'completed_jobs': completed,
        'alljobs':alljobs
    }

    return render(request, 'Projects.html', context)


@login_required
def application_detail(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    return render(request, 'ApplicationDetail.html', {'application': application})

@login_required
def milestone_detail(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    return render(request, 'MilestoneDetail.html', {'milestone': milestone})

@login_required
def payment_detail(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'PaymentDetail.html', {'payment': payment})



@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    skills = [skill.strip() for skill in job.skills_required.split(',')] if job.skills_required else []

    applications = job.applications.select_related('freelancer__user')
    milestones = job.milestones.all().order_by('start_date')
    payments = Payment.objects.filter(milestone__job=job).select_related('freelancer', 'milestone')
    user = request.user

    my_application = None
    if user.user_type == 'freelancer' and hasattr(user, 'freelancer_profile'):
        my_application = applications.filter(freelancer=user.freelancer_profile).first()

    context = {
        'job': job,
        'skills': skills,
        'applications': applications,
        'milestones': milestones,
        'payments': payments,
        'profile': user,
        'my_application': my_application,
    }
    return render(request, 'ProjectPage.html', context)





@login_required
def profile(request):
    """Profile view for authenticated users."""
    user = request.user
    context = {
        'profile': user,
    }
    return render(request, 'Profile.html', context)


@login_required
def add_project(request):
    user = request.user
    context = {
        'profile': user,
    }
    return render(request, 'AddProject.html', context)


@login_required
def add_user(request):
    user = request.user
    context = {
        'profile': user,
    }
    return render(request, 'AddUser.html', context)

@login_required
def view_users(request):
    CustomUser = get_user_model()
    users = CustomUser.objects.all()
    return render(request, 'ViewAllUsers.html', {'users': users})


from datetime import datetime
from django.utils import timezone
@login_required
def user_block_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def user_delete_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def user_detail_view(request, user_id):
    CustomUser = get_user_model()
    user_obj = get_object_or_404(CustomUser, id=user_id)

    context = {
        'user': user_obj,
    }
 

    return render(request, 'ViewUserDetail.html', context)



@login_required
def messages(request):
    user = request.user

    # 0) Dedupe existing Contacts (keep smallest id per pair)
    with transaction.atomic():
        first = {}
        for cid, emp_id, fl_id in Contact.objects.order_by('id')\
                                                .values_list('id', 'employer_id', 'freelancer_id'):
            key = (emp_id, fl_id)
            if key not in first:
                first[key] = cid
            elif cid != first[key]:
                Contact.objects.filter(id=cid).delete()

    # 1) Bootstrap contacts for everyone
    with transaction.atomic():
        if user.user_type == 'freelancer':
            prof = user.freelancer_profile
            seen = set()
            for job in Job.objects.filter(freelancer=prof).select_related('employer'):
                emp = job.employer
                if emp.id in seen:
                    continue
                seen.add(emp.id)
                Contact.objects.get_or_create(
                    employer=emp,
                    freelancer=prof,
                    defaults={'job': job}
                )

        elif user.user_type == 'employer':
            prof = user.employer_profile
            seen = set()
            for job in Job.objects.filter(employer=prof).select_related('freelancer'):
                fl = job.freelancer
                if not fl or fl.id in seen:
                    continue
                seen.add(fl.id)
                Contact.objects.get_or_create(
                    employer=prof,
                    freelancer=fl,
                    defaults={'job': job}
                )

        else:  # admin
            seen_pairs = set()
            for job in Job.objects.exclude(
                    freelancer__isnull=True
                ).exclude(
                    employer__isnull=True
                ).select_related('freelancer', 'employer'):
                pair = (job.employer.id, job.freelancer.id)
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                Contact.objects.get_or_create(
                    employer=job.employer,
                    freelancer=job.freelancer,
                    defaults={'job': job}
                )

    # 2) POST → send a message into an existing thread
    if request.method == 'POST':
        cid     = request.POST.get('contact_id')
        content = request.POST.get('content', '').strip()
        if cid and content:
            contact = get_object_or_404(Contact, id=cid)
            Message.objects.create(
                contact=contact,
                sender=user,
                content=content
            )
        return redirect(f"{request.path}?contact_id={cid}")

    # 3) GET → load contacts + optional selected thread
    if user.user_type == 'freelancer':
        contacts = Contact.objects.filter(
            freelancer=user.freelancer_profile
        ).select_related('employer__user', 'job')
    elif user.user_type == 'employer':
        contacts = Contact.objects.filter(
            employer=user.employer_profile
        ).select_related('freelancer__user', 'job')
    else:  # admin
        contacts = Contact.objects.all().select_related(
            'employer__user', 'freelancer__user', 'job'
        )

    contact_id       = request.GET.get('contact_id')
    selected_contact = None
    messages_list    = []
    if contact_id:
        selected_contact = get_object_or_404(Contact, id=contact_id)
        messages_list     = selected_contact.messages.select_related('sender').order_by('timestamp')

    return render(request, 'Messages.html', {
        'contacts': contacts,
        'selected_contact': selected_contact,
        'messages_list': messages_list,
        'current_user': user,
    })


from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from django.shortcuts import render
from job.models import Job, JobApplication
from accounts.models import CustomUser, FreelancerProfile

@login_required
def dashboard(request):
    user = request.user

    if user.user_type == 'freelancer':
        freelancer_profile = user.freelancer_profile
        allprojects=Job.objects.all()
        alldisputes=Dispute.objects.all()
        allusers=CustomUser.objects.all()
        allapplications=JobApplication.objects.all()
        myapplications=allapplications.filter(freelancer=freelancer_profile)

        freelancer_profile.update(alljobs=allprojects,alldispute=alldisputes,allusers=allusers,allapplications=allapplications)

        my_projects = Job.objects.filter(freelancer=freelancer_profile)

        available_projects = Job.objects.filter(freelancer=None, status='open')  
        top_employees = EmployerProfile.objects.order_by('-average_rating')[:3]

        early_milestones = Milestone.objects.filter(job__freelancer=freelancer_profile).order_by('expected_end_date')[:2]
        
        for proj in my_projects:
            proj.update_progress_based_on_status()

        pending_count = allapplications.filter(freelancer=freelancer_profile, status='pending').count()
        freelancer_profile.applications_pending = pending_count
        freelancer_profile.save()
        context = {
            'profile': freelancer_profile,
            'my_projects': my_projects,
            'available_projects': available_projects,
            'top_employees': top_employees,
            'early_milestones': early_milestones,
            'myapplications':myapplications,
            'range_5': range(1, 6),
        }

        return render(request, 'Freelancer_Dashboard.html', context)
    elif user.user_type == 'employer':
        profile = user.employer_profile

        allprojects=Job.objects.all()
        alldisputes=Dispute.objects.all()
        allusers=CustomUser.objects.all()
        allapplications=JobApplication.objects.all()
        profile.update(alljobs=allprojects,alldispute=alldisputes,allusers=allusers,allapplications=allapplications)
        

        remaining = profile.total_budget - profile.spent - profile.pending_payments

        avg_rating = Job.objects.filter(employer=profile).aggregate(Avg('employer_rating'))['employer_rating__avg']
        if avg_rating:
            profile.average_rating = round(avg_rating, 2)
            profile.save()  


        my_projects = Job.objects.filter(employer=profile)
        received_applications = JobApplication.objects.filter(job__in=my_projects)


        top_freelancers = FreelancerProfile.objects.order_by('-average_rating')[:3]

        for proj in Job.objects.all():
            proj.update_progress_based_on_status()

        early_milestones = Milestone.objects.filter(job__employer=profile).order_by('expected_end_date')[:2]
        profile.save()
        context = {
            'profile': user,
            'remaining': remaining,
            'my_projects': my_projects,
            'received_applications': received_applications,
            'top_freelancers': top_freelancers,
            "early_milestones":early_milestones,
            'range_5': range(1, 6),
        }

        return render(request, 'Employer_Dashboard.html', context)

    elif user.user_type == 'admin':
        all_users = CustomUser.objects.all()
        totalusercount = all_users.count()
        totaljobcount = Job.objects.count()

        completed_projects = Job.objects.filter(status='completed')
    

        employee_count = all_users.filter(user_type='employer').count()
        freelancer_count = all_users.filter(user_type='freelancer').count()
        total_budget=0
        for project in completed_projects:
            total_budget += 0.1 * project.total_budget
            

        totalworker = employee_count + freelancer_count
        employee_ratio = (employee_count / totalworker if totalusercount else 0) * 100
        freelancerratio = (freelancer_count / totalworker if totalusercount else 0) * 100
        count_active_users = all_users.filter(is_active=True).count()

        avg_project_budget = completed_projects.aggregate(avg=Avg('total_budget'))['avg'] or 0

        context = {
            'profile': user.admin_profile,
            'user': user,
            'all_users': all_users,
            'totalusercount': totalusercount,
            'totaljobcount': totaljobcount,
            'totalbudget': total_budget,
            'employee_ratio': employee_ratio,
            'employee_count': employee_count,
            'freelancerratio': freelancerratio,
            'freelancer_count': freelancer_count,
            'allprojects': Job.objects.all(),
            'totalworker': totalworker,
            'count_active_users': count_active_users,
            'avg_project_budget': avg_project_budget,
        }
        return render(request, 'Admin_Dashboard.html', context)


    
@csrf_exempt
@login_required
def send_personal_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        contact_id = data.get('contact_id')
        message_text = data.get('message')

        if not contact_id or not message_text:
            return JsonResponse({'error': 'Missing fields'}, status=400)
        if len(message_text) > 500:
            return JsonResponse({'error': 'Message exceeds 500 characters'}, status=400)

        try:
            contact = Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return JsonResponse({'error': 'Invalid contact'}, status=404)

        msg = Message.objects.create(
            contact=contact,
            sender=request.user,
            content=message_text
        )

        return JsonResponse({
            'success': True,
            'message': {
                'id': msg.id,
                'sender': msg.sender.email,
                'content': msg.content,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M'),
                'type': 'outgoing',
                'is_read': msg.is_read
            }
        })
    return JsonResponse({'error': 'Invalid request'}, status=405)

@login_required
def get_messages(request):
    contact_id = request.GET.get('contact_id')
    if not contact_id:
        return JsonResponse({'error': 'Missing contact_id'}, status=400)

    try:
        contact = Contact.objects.get(id=contact_id)
    except Contact.DoesNotExist:
        return JsonResponse({'error': 'Invalid contact'}, status=404)

    current_user = request.user
    messages = contact.messages.select_related('sender').order_by('timestamp')

    message_data = [
        {
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M'),
            'type': 'outgoing' if msg.sender == current_user else 'incoming',
            'is_read': msg.is_read
        }
        for msg in messages
    ]

    receiver_name = (
        contact.freelancer.user.get_full_name()
        if current_user == contact.employer.user
        else contact.employer.user.get_full_name()
    )

    return JsonResponse({'messages': message_data, 'receiver_name': receiver_name})











@csrf_exempt
@login_required
def ajax_profile_update(request):
    if request.method == 'POST':
        user = request.user
        data = request.POST

        # Update base user fields
        user.first_name = data.get('first_name', user.first_name)
        user.middle_name = data.get('middle_name', user.middle_name)
        user.last_name = data.get('last_name', user.last_name)
        user.phone_number = data.get('phone_number', user.phone_number)
        user.save()

        # Employer-specific
        if hasattr(user, 'employer_profile'):
            profile = user.employer_profile
            profile.company_name = data.get('company_name', profile.company_name)
            profile.company_website = data.get('company_website', profile.company_website)
            profile.total_budget = data.get('total_budget', profile.total_budget)
            profile.save()

        # Freelancer-specific
        elif hasattr(user, 'freelancer_profile'):
            profile = user.freelancer_profile
            profile.bank_account_number = data.get('bank_account_number', profile.bank_account_number)
            profile.bank_routing_number = data.get('bank_routing_number', profile.bank_routing_number)
            profile.paypal_email = data.get('paypal_email', profile.paypal_email)
            profile.skills = data.get('skills', profile.skills)
            profile.bio = data.get('bio', profile.bio)
            profile.save()

        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)



@login_required
def makePayment(request):
    user = request.user
    context = {}

    # If user is a freelancer
    if hasattr(user, 'freelancer_profile'):
        freelancer = user.freelancer_profile
        my_projects = Job.objects.filter(freelancer=freelancer)
        my_milestones = Milestone.objects.filter(job__in=my_projects)

        context.update({
            'role': 'freelancer',
            'jobs': my_projects,
            'milestones': my_milestones,
        })

    # If user is an employer
    elif hasattr(user, 'employer_profile'):
        employer = user.employer_profile
        jobs = Job.objects.filter(employer=employer)
        all_milestones = Milestone.objects.filter(job__in=jobs)

        context.update({
            'role': 'employer',
            'jobs': jobs,
            'milestones': all_milestones,
        })

    return render(request, 'Payments.html', context)

@login_required
def hire_freelancer(request):
    # Ensure the user is an employer
    if request.user.user_type != 'employer':
        return redirect('some_error_page')  # Redirect if the user is not an employer

    # Get the employer profile associated with the current user
    employer_profile = EmployerProfile.objects.get(user=request.user)

    # Get all the jobs posted by this employer
    jobs_posted = Job.objects.filter(employer=employer_profile)

    # Create a list to hold the jobs with their respective applications
    jobs_with_applications = []

    for job in jobs_posted:
        # Get all applications for each job
        job_applications = JobApplication.objects.filter(job=job)
        jobs_with_applications.append({
            'job': job,
            'applications': job_applications
        })

    # Pass the jobs with applications to the template
    return render(request, 'HireFreelancer.html', {'jobs_with_applications': jobs_with_applications})


@login_required
def contracts(request):
    return render(request, 'Contracts.html')
@login_required
def invoices(request):
    return render(request, 'Invoice.html')
@login_required
def reports(requests):
    return render(requests, 'Reports.html')



def update_profiles(application):
    """
    Helper function to update profiles of freelancer, employer, and admin-related data.
    """
    freelancer_profile = application.freelancer
    employer_profile = application.job.employer

    # Update Freelancer Profile
    if application.status == 'accepted':
        freelancer_profile.jobs_completed += 1
    elif application.status == 'rejected':
        freelancer_profile.jobs_in_queue -= 1

    freelancer_profile.save()

    # Update Employer Profile
    if application.status == 'accepted':
        employer_profile.jobs_posted += 1
        employer_profile.jobs_active += 1
    elif application.status == 'rejected':
        employer_profile.jobs_active -= 1

    employer_profile.save()

    # Optionally, update job milestones or other related models
    for milestone in application.job.milestones.all():
        if milestone.status == 'pending' and application.status == 'accepted':
            milestone.status = 'in_progress'
            milestone.save()

    # Add logic to notify admins if needed
    # E.g., update admin profiles, etc.

def accept_application(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)

    with transaction.atomic():
        # Accept the job application
        application.accept()
        
        # Update profiles and related data
        update_profiles(application)

    return redirect('hire_freelancer')

def reject_application(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)

    with transaction.atomic():
        # Reject the job application
        application.reject()
        
        # Update profiles and related data
        update_profiles(application)

    return redirect('hire_freelancer')

from django.utils import timezone
from datetime import datetime

from decimal import Decimal

@login_required
def add_job(request):
    if request.method == "POST":
        # Fetch the employer profile for the current user
        employer_profile = EmployerProfile.objects.get(user=request.user)

        # Extract job details from the form
        title = request.POST.get('title')
        description = request.POST.get('description')
        skills = request.POST.get('skills')
        budget = request.POST.get('budget')
        deadline_raw = request.POST.get('deadline')
        deadline = timezone.make_aware(datetime.fromisoformat(deadline_raw)) if deadline_raw else None

        # Create the job
        job = Job.objects.create(
            employer=employer_profile,
            title=title,
            description=description,
            skills_required=skills,
            total_budget=budget,
            deadline=deadline,
            status='open'
        )

        # Update EmployerProfile after job creation
        employer_profile.jobs_posted += 1  # Increase the job posted count
        employer_profile.jobs_open += 1  # Increase the open job count
        employer_profile.total_budget += Decimal(budget)  # Convert budget to Decimal and add to total_budget
        employer_profile.save()

        # Process milestones
        index = 1
        while f'milestone_title_{index}' in request.POST:
            end_raw = request.POST.get(f'milestone_end_{index}')
            expected_end_date = timezone.make_aware(datetime.fromisoformat(end_raw)) if end_raw else timezone.now()

            # Create each milestone associated with the job
            Milestone.objects.create(
                job=job,
                title=request.POST.get(f'milestone_title_{index}'),
                description=request.POST.get(f'milestone_desc_{index}'),
                budget=request.POST.get(f'milestone_budget_{index}'),
                expected_end_date=expected_end_date
            )
            index += 1

        # After creating job and updating profile, redirect to the job detail page
        return redirect('job_detail', job_id=job.id)

    # Render the form for creating a new job if the method is GET
    return render(request, 'AddProject.html')



@login_required
def submit_job_application(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    user = request.user


    freelancer_profile = user.freelancer_profile

    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter')
        bid_amount = request.POST.get('bid_amount')
        time_estimate = request.POST.get('time_estimate')

        # Check if bid amount is provided
        if not bid_amount:
            # You can also pass an error message to the template
            return render(request, 'apply_job.html', {'job': job, 'error': 'Please enter a bid amount.'})

        # Create the job application
        JobApplication.objects.create(
            job=job,
            freelancer=freelancer_profile,
            proposed_rate=bid_amount,
            cover_letter=cover_letter,
            time_estimate=time_estimate
        )

        # Redirect to job detail page after successful submission
        return redirect('job_detail', job_id=job.id)

    return render(request, 'apply_job.html', {'job': job})




def some_error_page(request):
    return render(request, 'error_page_template.html')


def milestone_submission(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    user = request.user

    if request.method == 'POST':
        paragraph = request.POST.get('paragraph')
        Submission.objects.create(milestone=milestone, paragraph=paragraph)
        return redirect('milestone_detail', milestone_id=milestone.id)

    submissions = Submission.objects.filter(milestone=milestone)
    return render(request, 'Submission.html', {
        'user':user,
        'milestone': milestone,
        'submissions': submissions
    })

def submit_submission(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    
    if request.method == 'POST':
        paragraph = request.POST.get('paragraph')
        Submission.objects.create(milestone=milestone, paragraph=paragraph)
        return redirect('milestone_detail', milestone_id=milestone.id)

    return render(request, 'Submission.html', {'milestone': milestone})


@login_required
def accept_milestone(request, milestone_id):
    print(f"Entering accept_milestone with milestone_id: {milestone_id}")
    
    milestone = get_object_or_404(Milestone, id=milestone_id)
    print(f"Milestone found: {milestone.title} - {milestone.status}")
    
    job = milestone.job
    print(f"Job found: {job.title} - {job.status}")

    # Ensure only employer can accept the milestone
    if request.user.id != job.employer.user.id:
        print(f"User is not the employer. Redirecting...")
        return redirect('milestone_detail', milestone_id=milestone.id)

    if request.method == 'POST':
        print(f"POST request received. Checking milestone status before proceeding...")

        # Check if the milestone is already completed or rejected
        if milestone.status in ['completed', 'rejected']:
            print(f"Milestone status before check: {milestone.status}")
            print(f"Milestone is already {milestone.status}. Skipping milestone update but proceeding with profile updates.")
        else:
            # Accept the milestone (Mark as completed)
            milestone.status = 'completed'
            milestone.completed_date = timezone.now()
            milestone.save()
            print(f"Milestone status updated to 'completed'.")

        # Update EmployerProfile
        employer_profile, created = EmployerProfile.objects.get_or_create(user=job.employer.user)
        if created:
            print(f"EmployerProfile created for employer: {job.employer.user.username}")
        else:
            print(f"EmployerProfile found for employer: {job.employer.user.username}")
        
        print(f"Updating EmployerProfile: total_spent={employer_profile.total_spent}, spent={employer_profile.spent}, pending_payments={employer_profile.pending_payments}")
        employer_profile.total_spent += milestone.budget
        employer_profile.spent += milestone.budget
        employer_profile.pending_payments = max(0, employer_profile.pending_payments - milestone.budget)
        employer_profile.save()
        print(f"EmployerProfile updated.")

        # Update FreelancerProfile
        freelancer_profile, created = FreelancerProfile.objects.get_or_create(user=job.freelancer.user)
        if created:
            print(f"FreelancerProfile created for freelancer: {job.freelancer.user.username}")
        else:
            print(f"FreelancerProfile found for freelancer: {job.freelancer.user.username}")
        
        print(f"Updating FreelancerProfile: money_earned={freelancer_profile.money_earned}, jobs_completed={freelancer_profile.jobs_completed}, jobs_in_queue={freelancer_profile.jobs_in_queue}")
        freelancer_profile.money_earned += milestone.budget
        freelancer_profile.jobs_completed += 1
        freelancer_profile.jobs_in_queue = max(0, freelancer_profile.jobs_in_queue - 1)
        freelancer_profile.save()
        print(f"FreelancerProfile updated.")
        Payment.objects.create(
            job=job,
            milestone=milestone,
            freelancer=job.freelancer,
            amount=milestone.budget,
            status='completed',
            transaction_id=f"TXN-{timezone.now().strftime('%Y%m%d%H%M%S')}-{milestone.id}",
            payment_method='manual',  # or 'wallet', 'card', etc.
            paid_at=timezone.now()
        )
        print("Payment record created for the milestone.")
        # Optionally, update job status if all milestones are completed
        if all(m.status == 'completed' for m in job.milestones.all()):
            job.status = 'completed'
            job.save()
            print(f"All milestones completed. Job status updated to 'completed'.")

        return redirect('milestone_detail', milestone_id=milestone.id)

    return render(request, 'milestone_detail.html', {'milestone': milestone})
