from django import forms

from apps.account.models import UserProfile
from apps.account.services.image_processor_service import ImageProcessor
from apps.account.services.image_validator_service import ImageValidator


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150, 
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        max_length=150, 
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = UserProfile
        fields = ["bio", "website", "location", "birth_date", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "birth_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"class": "form-control", "type": "date"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if not avatar or not hasattr(avatar, 'size'):
            return avatar
        try:
            ImageValidator.validate_size(avatar)
            ImageValidator.validate_extension(avatar.name)
            ImageValidator.validate_image(avatar)
            avatar.seek(0)
        except ValueError as e:
            raise forms.ValidationError(str(e))
        processed = ImageProcessor().resize(avatar)
        processed.name = avatar.name
        return processed

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        if not hasattr(profile, 'user') or not profile.user:
            profile.user = self.user
            
        user = profile.user
        if 'first_name' in self.cleaned_data:
            user.first_name = self.cleaned_data['first_name']
        if 'last_name' in self.cleaned_data:
            user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            profile.save()
            
        return profile
