from django import forms

from .models import LiveCohort, LiveCohortAssignment, LiveCohortSession


class LiveCohortForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(required=False, widget=forms.Textarea)
    price = forms.DecimalField(max_digits=6, decimal_places=2, min_value=0)
    max_students = forms.IntegerField(min_value=1, max_value=99)

    # First session fields
    session_name = forms.CharField(max_length=255)
    session_description = forms.CharField(required=False, widget=forms.Textarea)
    start_time = forms.DateTimeField()
    end_time = forms.DateTimeField()

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError('End time must be after start time')

        return cleaned_data

    def save(self, teacher):
        cohort = LiveCohort.objects.create(
            name=self.cleaned_data['name'],
            description=self.cleaned_data['description'],
            price=self.cleaned_data['price'],
            max_students=self.cleaned_data['max_students'],
            teacher=teacher,
        )

        LiveCohortSession.objects.create(
            cohort=cohort,
            name=self.cleaned_data['session_name'],
            description=self.cleaned_data['session_description'],
            start_time=self.cleaned_data['start_time'],
            end_time=self.cleaned_data['end_time'],
        )

        return cohort


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
