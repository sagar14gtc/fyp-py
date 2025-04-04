from django import forms
from accounts.models import CustomUser

class ConsultantNotificationForm(forms.Form):
    recipient = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role=CustomUser.STUDENT),
        label="Select Student",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        label="Notification Message",
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        max_length=500
    )

    # Optionally filter recipients based on the consultant sending the notification
    def __init__(self, *args, **kwargs):
        consultant = kwargs.pop('consultant', None)
        super().__init__(*args, **kwargs)
        if consultant:
            # Show only students assigned to this consultant
            assigned_student_ids = consultant.consultant_applications.values_list('student_id', flat=True).distinct()
            self.fields['recipient'].queryset = CustomUser.objects.filter(id__in=assigned_student_ids, role=CustomUser.STUDENT)
        else:
            # Fallback if consultant is not provided (e.g., maybe staff uses it too?)
             self.fields['recipient'].queryset = CustomUser.objects.filter(role=CustomUser.STUDENT)
