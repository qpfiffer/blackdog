from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from address.models import AddressField
from andablog.models import Entry

from social.apps.django_app.default.models import UserSocialAuth

# RIDE STUFF
class Campaign(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, blank=True, null=True)
    name = models.CharField(max_length=128, blank=False, null=False)
    about = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name

class Ride(models.Model):
    uploaded = models.DateTimeField(auto_now=True)
    campaign = models.ForeignKey(Campaign)
    trackfile = models.FileField(upload_to='rides')

    def __unicode__(self):
        return self.trackfile.name

class Course(models.Model):
    uploaded = models.DateTimeField(auto_now=True)
    campaign = models.ForeignKey(Campaign)
    trackfile = models.FileField(upload_to='courses')

    def __unicode__(self):
        return self.trackfile.name

class PointOfInterest(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    campaign = models.ForeignKey(Campaign, null=False, blank=False)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)

class EntryPointOfInterest(models.Model):
    poi = models.ForeignKey(PointOfInterest, null=False)
    entry = models.ForeignKey(Entry, null=False, blank=False)

class InstagramPointOfInterest(models.Model):
    poi = models.ForeignKey(PointOfInterest, null=False)
    user_social_auth = models.ForeignKey(UserSocialAuth, blank=False, null=False)
    shortcode = models.CharField(max_length=128, blank=False, null=False)

# FINANCIALS
class FinancialCategory(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=128, unique=True, null=False, blank=False)

class FinancialEntry(models.Model):
    user = models.ForeignKey(User)
    campaign = models.ForeignKey(Campaign, null=True, blank=True)
    category = models.ForeignKey(FinancialCategory)
    value = models.DecimalField(max_digits=12, decimal_places=2)

# MISC. STUFF
class Contact(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=128, null=True, blank=True)
    address = AddressField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
