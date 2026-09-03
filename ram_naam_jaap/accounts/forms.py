from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

MAX_PROFILE_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('city', 'profile_image')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['city'].required = False
        self.fields['profile_image'].required = False
        self.fields['city'].widget.attrs['class'] = 'form-control'

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image and hasattr(image, 'size') and image.size > MAX_PROFILE_IMAGE_SIZE:
            raise forms.ValidationError('Image too large. Max size is 5 MB.')
        return image 