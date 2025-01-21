import io
import sys

from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image

from .models.profiles import Profile, ProfileCategory, ProfileLink


class ProfileForm(forms.ModelForm):
    DEFAULT_PROFILE_IMAGES = {
        'default_male': 'static/img/profile/default_male_avatar.jpg',
        'default_female': 'static/img/profile/default_female_avatar.jpg',
        'default_dog': 'static/img/profile/default_dog_avatar.jpg',
    }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].required = False

    class Meta:
        model = Profile
        fields = [
            'name',
            'bio',
            'threads_url',
            'instagram_url',
            'email_url',
            'facebook_url',
            'youtube_url',
            'twitter_url',
            'website_url',
        ]


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image']

    def clean_profile_image(self):
        _image = self.cleaned_data.get('profile_image')
        if not _image:
            raise forms.ValidationError('No image uploaded')

        if _image.content_type not in ['image/jpeg', 'image/png']:
            raise forms.ValidationError('Image must be in .jpg or .png format')

        return _image


class ProfileLinkForm(forms.ModelForm):
    class Meta:
        model = ProfileLink
        fields = ['title', 'url']


class ProfileCategoryForm(forms.ModelForm):
    class Meta:
        model = ProfileCategory
        fields = ['title']

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title) > 64:
            raise forms.ValidationError('Title must be less than 64 characters')
        return title
