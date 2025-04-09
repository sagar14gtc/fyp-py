from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.core.files.uploadedfile import UploadedFile

from .models import Application, Document, ApplicationNote, ApplicationStatus
from .forms import ApplicationForm, DocumentForm, ApplicationNoteForm, ApplicationCreateFromSearchForm
from universities.models import Program, University # Import University
from accounts.models import CustomUser

@login_required
def application_list(request):
    """View to list all applications for current user."""
    user = request.user

    if user.role == 'student':
        applications = Application.objects.filter(student=user).order_by('-application_date')
        template = 'applications/student/application_list.html'
    elif user.role == 'consultant':
        applications = Application.objects.filter(consultant=user).order_by('-application_date')
        template = 'applications/consultant/application_list.html'
    elif user.is_staff:
        applications = Application.objects.all().order_by('-application_date')
        template = 'applications/admin/application_list.html'
    else:
        return redirect('accounts:profile')

    context = {
        'applications': applications,
        'page_title': 'My Applications'
    }
    return render(request, template, context)

@login_required
def create_application(request, program_id):
    """View to create a new application for a program."""
    program = get_object_or_404(Program, id=program_id)

    if request.user.role != 'student':
        messages.error(request, "Only students can submit applications.")
        return redirect('universities:program_detail', uni_slug=program.university.slug, prog_slug=program.slug)

    # Check if user already has an application for this program
    existing_application = Application.objects.filter(
        student=request.user,
        program=program,
        status__in=[s[0] for s in Application.STATUS_CHOICES if s[0] != Application.CANCELED]
    ).first()

    if existing_application:
        messages.warning(request, f"You already have an application for this program ({existing_application.get_status_display()}).")
        # Redirect using pk now
        return redirect('applications:application_detail', pk=existing_application.pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = request.user
            application.program = program
            application.save()

            # Create initial status history
            ApplicationStatus.objects.create(
                application=application,
                status=Application.DRAFT,
                changed_by=request.user,
                notes="Application created"
            )

            # Create required document placeholders
            for doc_type, doc_name in Document.DOCUMENT_TYPES:
                Document.objects.create(
                    application=application,
                    document_type=doc_type,
                    name=f"{doc_name} for {program.name}",
                    required=(doc_type in [Document.TRANSCRIPT, Document.CV, Document.PASSPORT])
            )

            messages.success(request, "Application created successfully. You can now upload your documents.")
            # Redirect using pk now
            return redirect('applications:application_detail', pk=application.pk)
    else:
        form = ApplicationForm(initial={'intake_date': program.start_date})

    context = {
        'form': form,
        'program': program,
        'university': program.university,
        'page_title': f'Apply for {program.name}'
    }
    return render(request, 'applications/create_application.html', context)

@login_required
def application_detail(request, pk): # Changed argument name
    """View to see details of a specific application."""
    # Lookup using pk now
    application = get_object_or_404(Application, pk=pk)

    # Check permission
    if not can_view_application(request.user, application):
        raise PermissionDenied("You don't have permission to view this application.")

    documents = application.documents.all()
    notes = application.application_notes.all()
    status_history = application.status_history.all()

    context = {
        'application': application,
        'program': application.program,
        'university': application.program.university,
        'documents': documents,
        'notes': notes,
        'status_history': status_history,
        'page_title': f'Application for {application.program.name}'
    }

    # Use a single template for all roles
    template = 'applications/application_detail.html'

    return render(request, template, context)

@login_required
def edit_application(request, pk): # Changed argument name
    """View to edit an application."""
    # Lookup using pk now
    application = get_object_or_404(Application, pk=pk)

    # Only allow editing if application is in draft state and user is the student
    if application.status != Application.DRAFT or application.student != request.user:
        messages.error(request, "You cannot edit this application.")
        # Redirect using pk now
        return redirect('applications:application_detail', pk=application.pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, "Application updated successfully.")
            # Redirect using pk now
            return redirect('applications:application_detail', pk=application.pk)
    else:
        form = ApplicationForm(instance=application)

    context = {
        'form': form,
        'application': application,
        'program': application.program,
        'university': application.program.university,
        'page_title': f'Edit Application for {application.program.name}'
    }
    return render(request, 'applications/edit_application.html', context)

@login_required
def cancel_application(request, pk): # Changed argument name
    """View to cancel an application."""
    # Lookup using pk now
    application = get_object_or_404(Application, pk=pk)

    # Check if user can cancel this application
    if application.student != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to cancel this application.")
        # Redirect using pk now
        return redirect('applications:application_detail', pk=application.pk)

    # Don't allow cancelling of already processed applications
    if application.status in [Application.ACCEPTED, Application.ENROLLMENT_CONFIRMED]:
        messages.error(request, "You cannot cancel an accepted or confirmed application.")
        # Redirect using pk now
        return redirect('applications:application_detail', pk=application.pk)

    if request.method == 'POST':
        application.status = Application.CANCELED
        application.save()

        # Create status history entry
        ApplicationStatus.objects.create(
            application=application,
            status=Application.CANCELED,
            changed_by=request.user,
            notes=request.POST.get('cancel_reason', 'Application canceled')
        )

        messages.success(request, "Application has been canceled successfully.")
        return redirect('applications:application_list')

    context = {
        'application': application,
        'page_title': 'Cancel Application'
    }
    return render(request, 'applications/cancel_application.html', context)


@login_required
def create_application_from_search(request, program_id):
    """View to create a new application from the search results page."""
    program = get_object_or_404(Program, id=program_id)

    if request.user.role != 'student':
        messages.error(request, "Only students can submit applications.")
        # Redirect back to search or program detail? Let's go back to search for now.
        return redirect('dashboard:university_search')

    # Check if user already has an application for this program
    existing_application = Application.objects.filter(
        student=request.user,
        program=program,
        status__in=[s[0] for s in Application.STATUS_CHOICES if s[0] != Application.CANCELED]
    ).first()

    if existing_application:
        messages.warning(request, f"You already have an application for this program ({existing_application.get_status_display()}).")
        # Redirect using pk now
        return redirect('applications:application_detail', pk=existing_application.pk)

    if request.method == 'POST':
        form = ApplicationCreateFromSearchForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = request.user
            application.program = program
            # Set status to Submitted directly? Or Draft? Let's assume Submitted.
            application.status = Application.SUBMITTED
            application.save()

            # Create initial status history
            ApplicationStatus.objects.create(
                application=application,
                status=Application.SUBMITTED,
                changed_by=request.user,
                notes="Application submitted from search"
            )

            # Handle document uploads
            doc_fields = {
                Document.TRANSCRIPT: form.cleaned_data.get('transcript_file'),
                Document.DIPLOMA: form.cleaned_data.get('certificate_file'),
                Document.PASSPORT: form.cleaned_data.get('passport_file'),
                Document.LANGUAGE_TEST: form.cleaned_data.get('language_test_file'),
                # Add the new document fields from the form
                Document.CV: form.cleaned_data.get('cv_file'),
                Document.RECOMMENDATION_LETTER: form.cleaned_data.get('recommendation_letter_file'),
                Document.STATEMENT_OF_PURPOSE: form.cleaned_data.get('statement_of_purpose_file'),
            }

            # Define which document types are considered required for this form submission
            # (This might differ from general program requirements)
            form_required_docs = [
                Document.TRANSCRIPT,
                Document.DIPLOMA,
                Document.PASSPORT,
                Document.CV, # Added
                Document.RECOMMENDATION_LETTER, # Added
                Document.STATEMENT_OF_PURPOSE, # Added
            ]

            for doc_type, file in doc_fields.items():
                if file and isinstance(file, UploadedFile):
                    Document.objects.create(
                        application=application,
                        document_type=doc_type,
                        file=file,
                        name=file.name,
                        status=Document.PENDING_REVIEW, # Assume pending review upon upload
                        required=(doc_type in form_required_docs) # Set required based on our list
                    )

            # Create placeholders for any required docs that *weren't* uploaded via the form
            # This ensures the student sees them in the document list later
            all_possible_required = [
                Document.TRANSCRIPT, Document.DIPLOMA, Document.CV,
                Document.RECOMMENDATION_LETTER, Document.PASSPORT,
                Document.STATEMENT_OF_PURPOSE
                # Add others if they can be universally required
            ]
            for doc_type in all_possible_required:
                 # Check if a document of this type was already created (either uploaded or placeholder)
                 if not application.documents.filter(document_type=doc_type).exists():
                     Document.objects.create(
                         application=application,
                         document_type=doc_type,
                         name=dict(Document.DOCUMENT_TYPES)[doc_type],
                         required=(doc_type in form_required_docs), # Mark as required if it was in the form list
                         status=Document.NOT_UPLOADED
                     )

            messages.success(request, "Application submitted successfully!")
            # Redirect to application detail page using pk now
            return redirect('applications:application_detail', pk=application.pk)
        else:
             messages.error(request, "Please correct the errors below.")
    else:
        # Pre-fill intake date if available from program
        initial_data = {'intake_date': program.start_date}
        form = ApplicationCreateFromSearchForm(initial=initial_data)

    context = {
        'form': form,
        'program': program,
        'university': program.university,
        'page_title': f'Apply for {program.name}'
    }
    # Need a new template for this form
    return render(request, 'applications/create_application_form.html', context)


@login_required
def manage_documents(request, pk): # Changed argument name
    """View to manage documents for an application."""
    # Lookup using pk now
    application = get_object_or_404(Application, pk=pk)

    # Check permission
    if application.student != request.user and not request.user.is_staff and application.consultant != request.user:
        messages.error(request, "You don't have permission to manage documents for this application.")
        return redirect('applications:application_list')

    documents = application.documents.all()

    context = {
        'application': application,
        'documents': documents,
        'page_title': 'Manage Documents' # Keep title specific if needed
    }
    # Render the existing application detail template which shows documents
    return render(request, 'applications/application_detail.html', context)

@login_required
def upload_document(request, pk, document_type): # Changed argument name
    """View to upload a specific document."""
    # Lookup using pk now
    application = get_object_or_404(Application, pk=pk)

    # Only student can upload documents
    if application.student != request.user:
        messages.error(request, "Only the applicant can upload documents.")
        # Redirect using pk now
        return redirect('applications:manage_documents', pk=application.pk)

    # Get or create document
    document, created = Document.objects.get_or_create(
        application=application,
        document_type=document_type,
        defaults={'name': dict(Document.DOCUMENT_TYPES)[document_type]}
    )

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.status = Document.PENDING_REVIEW
            doc.save()

            messages.success(request, "Document uploaded successfully.")

            # Check if application is in draft status and all required documents are uploaded
            if application.status == Application.DRAFT:
                required_docs = application.documents.filter(required=True)
                all_uploaded = all(doc.file for doc in required_docs)

                if all_uploaded:
                    messages.info(request, "All required documents uploaded. You can now submit your application.")

            # Redirect using pk now
            return redirect('applications:manage_documents', pk=application.pk)
    else:
        form = DocumentForm(instance=document)

    context = {
        'form': form,
        'application': application,
        'document': document,
        'document_type': dict(Document.DOCUMENT_TYPES)[document_type],
        'page_title': f'Upload {dict(Document.DOCUMENT_TYPES)[document_type]}'
    }
    return render(request, 'applications/upload_document.html', context)

@login_required
def delete_document(request, pk, document_id): # Changed argument name
    """View to delete a document."""
    # Lookup using pk now
    application = get_object_or_404(Application, pk=pk)
    document = get_object_or_404(Document, id=document_id, application=application)

    # Only student can delete documents, and only if application is not submitted yet
    if application.student != request.user:
        messages.error(request, "Only the applicant can delete documents.")
        # Redirect using pk now
        return redirect('applications:manage_documents', pk=application.pk)

    if application.status != Application.DRAFT:
        messages.error(request, "Cannot delete documents after application has been submitted.")
        # Redirect using pk now
        return redirect('applications:manage_documents', pk=application.pk)

    if request.method == 'POST':
        document.file.delete(save=False)
        document.status = Document.NOT_UPLOADED
        document.save()

        messages.success(request, "Document has been deleted.")
        # Redirect using pk now
        return redirect('applications:manage_documents', pk=application.pk)

    context = {
        'application': application,
        'document': document,
        'page_title': 'Delete Document'
    }
    return render(request, 'applications/delete_document.html', context)

@login_required
def update_status(request, pk): # Changed argument name
    """View to update application status."""
    # Lookup using pk now
    application = get_object_or_404(Application, pk=pk)

    # Only staff and consultants can update status
    if not request.user.is_staff and application.consultant != request.user:
        messages.error(request, "You don't have permission to update the status of this application.")
        # Redirect using pk now
        return redirect('applications:application_detail', pk=application.pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        if new_status in [status[0] for status in Application.STATUS_CHOICES]:
            old_status = application.status
            application.status = new_status
            application.save()

            # Create status history entry
            ApplicationStatus.objects.create(
                application=application,
                status=new_status,
                changed_by=request.user,
                notes=notes
            )

            # Create application note about status change
            ApplicationNote.objects.create(
                application=application,
                user=request.user,
                note=f"Status changed from {dict(Application.STATUS_CHOICES)[old_status]} to {dict(Application.STATUS_CHOICES)[new_status]}. {notes}"
            )

            messages.success(request, f"Application status updated to {dict(Application.STATUS_CHOICES)[new_status]}.")

            # Check if the request is AJAX using headers
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            # Redirect using pk now
            return redirect('applications:application_detail', pk=application.pk)
        else:
            messages.error(request, "Invalid status.")
            # Check if the request is AJAX using headers
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Invalid status'})

    context = {
        'application': application,
        'status_choices': Application.STATUS_CHOICES,
        'page_title': 'Update Application Status'
    }
    return render(request, 'applications/update_status.html', context)

@login_required
def add_note(request, pk): # Changed argument name
    """View to add a note to an application."""
    # Lookup using pk now
    application = get_object_or_404(Application, pk=pk)

    # Check permission
    if not can_view_application(request.user, application):
        messages.error(request, "You don't have permission to add notes to this application.")
        return redirect('applications:application_list')

    if request.method == 'POST':
        form = ApplicationNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.application = application
            note.user = request.user
            note.save()

            messages.success(request, "Note added successfully.")

            # Check if the request is AJAX using headers
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'note': note.note,
                    'user': note.user.get_full_name() or note.user.username,
                    'created_at': note.created_at.strftime('%Y-%m-%d %H:%M')
                })
            # Redirect using pk now
            return redirect('applications:application_detail', pk=application.pk)
        else:
            # Check if the request is AJAX using headers
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ApplicationNoteForm()

    context = {
        'form': form,
        'application': application,
        'page_title': 'Add Note'
    }
    return render(request, 'applications/add_note.html', context)


@login_required
def create_application_for_university(request, uni_id):
    """View to initiate application creation for a specific university."""
    university = get_object_or_404(University, id=uni_id)
    programs = university.programs.filter(is_active=True).order_by('name') # Get active programs for this uni

    if not programs.exists():
        messages.error(request, f"There are currently no active programs listed for {university.name} to apply to.")
        return redirect('dashboard:university_search') # Redirect back to search

    if request.user.role != 'student':
        messages.error(request, "Only students can submit applications.")
        return redirect('dashboard:university_search')

    if request.method == 'POST':
        # We expect 'program' to be selected in the form now
        program_id = request.POST.get('program')
        if not program_id:
            messages.error(request, "Please select a program to apply for.")
            # Re-render the form with error
            form = ApplicationCreateFromSearchForm(request.POST, request.FILES) # Keep submitted data
            context = {
                'form': form,
                'university': university,
                'programs': programs, # Pass programs for the dropdown
                'page_title': f'Apply to {university.name}'
            }
            return render(request, 'applications/create_application_form.html', context)

        program = get_object_or_404(Program, id=program_id, university=university)

        # Check if user already has an application for this program
        existing_application = Application.objects.filter(
            student=request.user,
            program=program,
            status__in=[s[0] for s in Application.STATUS_CHOICES if s[0] != Application.CANCELED]
        ).first()

        if existing_application:
            messages.warning(request, f"You already have an application for this program ({existing_application.get_status_display()}).")
            # Redirect using pk now
            return redirect('applications:application_detail', pk=existing_application.pk)

        form = ApplicationCreateFromSearchForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = request.user
            application.program = program # Assign the selected program
            application.status = Application.SUBMITTED
            application.save()

            # Create initial status history
            ApplicationStatus.objects.create(
                application=application,
                status=Application.SUBMITTED,
                changed_by=request.user,
                notes="Application submitted after selecting university"
            )

            # Handle document uploads (copied from create_application_from_search)
            doc_fields = {
                Document.TRANSCRIPT: form.cleaned_data.get('transcript_file'),
                Document.DIPLOMA: form.cleaned_data.get('certificate_file'),
                Document.PASSPORT: form.cleaned_data.get('passport_file'),
                Document.LANGUAGE_TEST: form.cleaned_data.get('language_test_file'),
            }

            for doc_type, file in doc_fields.items():
                if file and isinstance(file, UploadedFile):
                    Document.objects.create(
                        application=application,
                        document_type=doc_type,
                        file=file,
                        name=file.name,
                        status=Document.PENDING_REVIEW,
                        required=(doc_type in [Document.TRANSCRIPT, Document.DIPLOMA, Document.PASSPORT])
                    )

            required_types = [Document.CV, Document.RECOMMENDATION_LETTER, Document.STATEMENT_OF_PURPOSE]
            for doc_type in required_types:
                 if not application.documents.filter(document_type=doc_type).exists():
                     Document.objects.create(
                         application=application,
                         document_type=doc_type,
                         name=dict(Document.DOCUMENT_TYPES)[doc_type],
                         required=True,
                         status=Document.NOT_UPLOADED
                     )

            messages.success(request, "Application submitted successfully!")
            # Redirect using pk now
            return redirect('applications:application_detail', pk=application.pk)
        else:
             messages.error(request, "Please correct the errors below.")
             # Re-render form with errors, ensuring programs are passed back
             context = {
                 'form': form,
                 'university': university,
                 'programs': programs, # Pass programs for the dropdown
                 'page_title': f'Apply to {university.name}'
             }
             return render(request, 'applications/create_application_form.html', context)

    else:
        # GET request: Prepare the form
        form = ApplicationCreateFromSearchForm() # No initial data needed here unless desired

    context = {
        'form': form,
        'university': university,
        'programs': programs, # Pass programs for the dropdown
        'page_title': f'Apply to {university.name}'
    }
    return render(request, 'applications/create_application_form.html', context)


# Helper functions
def can_view_application(user, application):
    """Check if user can view the application."""
    return (
        user == application.student or
        user == application.consultant or
        user.is_staff
    )
