from django import forms

from .models import LiveCohort, LiveCohortSession


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
