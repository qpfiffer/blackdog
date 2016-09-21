from django import forms
from home.models import Campaign

class UploadCampaignForm(forms.Form):
    campaign = forms.ModelChoiceField(queryset=Campaign.objects.all())
    rides = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    courses = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    def __init__(self, user, *args, **kwargs):
        super(UploadCampaignForm, self).__init__(*args, **kwargs)
        if user.is_authenticated:
            self.fields['campaign'].queryset = Campaign.objects.filter(owner=user)
        else:
            self.fields['campaign'].queryset = Campaign.objects.none()
