from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from address.models import AddressField
from andablog.models import Entry

# RIDE STUFF
class Campaign(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=128, blank=False, null=False)

class Ride(models.Model):
    uploaded = models.DateTimeField(auto_now=True)
    campaign = models.ForeignKey(Campaign)
    trackfile = models.FileField(upload_to='rides')

class Course(models.Model):
    uploaded = models.DateTimeField(auto_now=True)
    campaign = models.ForeignKey(Campaign)
    trackfile = models.FileField(upload_to='courses')

class PointOfInterest(models.Model):
    entry = models.ForeignKey(Entry, null=False, blank=False)
    campaign = models.ForeignKey(Campaign, null=False, blank=False)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)

# MISC. STUFF
class Contact(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=128, null=True, blank=True)
    address = AddressField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
