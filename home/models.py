from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from address.models import AddressField

# RIDE STUFF
class Campaign(models.Model):
    name = models.CharField(max_length=128, blank=False, null=False)

class Ride(models.Model):
    campaign = models.ForeignKey(Campaign)

class Course(models.Model):
    campaign = models.ForeignKey(Campaign)

# MISC. STUFF
class Contact(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=128, null=True, blank=True)
    address = AddressField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
