from django import forms

from .models import (
    LiveCohort,
    LiveCohortAssignment,
    LiveCohortSession,
    LiveCohortWaitList,
)


class LiveCohortForm(forms.ModelForm):
    class Meta:
        model = LiveCohort
        fields = [
            'name',
            'description',
            'features',
            'key_topics',
            'schedule',
            'requirements',
            'course_fees',
            'max_students',
            'start_date',
            'end_date',
            'price',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'features': forms.Textarea(attrs={'rows': 4}),
            'key_topics': forms.Textarea(attrs={'rows': 4}),
            'schedule': forms.Textarea(attrs={'rows': 4}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'course_fees': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def save(self, commit=True, teacher=None):
        instance = super().save(commit=False)
        if teacher:
            instance.teacher = teacher
        if commit:
            instance.save()
        return instance


class AddStudentForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()


class AddAssignmentForm(forms.ModelForm):
    class Meta:
        model = LiveCohortAssignment
        fields = [
            'name',
            'description',
            'due_date',
            'graded',
            'attachment',
            'external_url',
            'submission_optional',  # Add this field
        ]
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class LiveCohortSessionForm(forms.ModelForm):
    class Meta:
        model = LiveCohortSession
        fields = ['name', 'description', 'start_time', 'end_time', 'meeting_url']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError('End time must be after start time')

        return cleaned_data


class WaitListForm(forms.ModelForm):
    class Meta:
        model = LiveCohortWaitList
        fields = [
            'name',
            'email',
            'questions',
        ]
        widgets = {
            'name': forms.TextInput(),
            'email': forms.EmailInput(),
            'questions': forms.Textarea(attrs={'rows': 4}),
        }

    questions = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}), required=False
    )
