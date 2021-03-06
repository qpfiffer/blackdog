from django import forms
from home.models import Campaign

class UploadCampaignForm(forms.Form):
    campaign = forms.ModelChoiceField(queryset=Campaign.objects.all())
    rides = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    courses = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    def __init__(self, user, *args, **kwargs):
        super(UploadCampaignForm, self).__init__(*args, **kwargs)
        self.fields['campaign'].queryset = Campaign.objects.all()
