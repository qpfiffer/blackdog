from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages

from rest_framework import serializers, viewsets
from andablog.models import Entry, EntryImage
from social.backends.utils import load_backends
from social.apps.django_app.default.models import UserSocialAuth

from home.forms import UploadCampaignForm
from home.models import Campaign, Course, Ride
import json

# Why is everything in here? Whatever.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# BLOG STUFF
class BlogImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EntryImage
        fields = ('entry', 'image', 'image_url')

class BlogSerializer(serializers.HyperlinkedModelSerializer):
    entryimage_set = BlogImageSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Entry
        fields = ('title', 'slug', 'content', 'published_timestamp', 'author', 'entryimage_set')

class BlogViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.filter(is_published=True)
    serializer_class = BlogSerializer

class BlogImageViewSet(viewsets.ModelViewSet):
    queryset = EntryImage.objects.filter(entry__is_published=True)
    serializer_class = BlogImageSerializer

# CAMPAIGNS
class CourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Course
        fields = ('uploaded', 'campaign', 'trackfile')

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter()
    serializer_class = CourseSerializer

class RideSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ride
        fields = ('uploaded', 'campaign', 'trackfile')

class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.filter()
    serializer_class = RideSerializer

class CampaignSerializer(serializers.HyperlinkedModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Campaign
        depth = 1
        fields = ('owner', 'created_at', 'name', 'about', 'ride_set', 'course_set')

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.filter()
    serializer_class = CampaignSerializer

def home(req):
    upload_form = UploadCampaignForm(req.user)
    all_messages = json.dumps([x.message for x in messages.get_messages(req)])
    available_backends = load_backends(['social.backends.instagram.InstagramOAuth2'])
    instagram_acct = UserSocialAuth.objects.filter(user=req.user, provider='instagram')

    return render(req, "index.html", locals())

def instagram_redirect(req):
    messages.info(req, 'Instagram now auth\'d.')
    return redirect('home')

def add_instagram_poi(req):
    shortcode_endpoint = "https://api.instagram.com/v1/media/{SHORTCODE}/D?access_token={ACCESS_TOKEN}"
    if req.method == 'POST':
        import json
        parsed = json.loads(req.POST)
        print "PARSED: " + parsed
        #formatted_url = shortcode_endpoint.format(SHORTCODE=
    return redirect('home')

def campaignUpload(req):
    if not req.user.is_authenticated:
        return redirect('home')

    if req.method == 'POST':
        form = UploadCampaignForm(req.user, req.POST, req.FILES)
        if form.is_valid():
            for ride in req.FILES.getlist('rides'):
                if not ride.name.lower().endswith(".gpx"):
                    messages.info(req, 'Could not upload {}: Does not end in GPX.'.format(ride.name))
                    continue
                new_ride = Ride.objects.create(campaign = form.cleaned_data['campaign'],
                                               trackfile = ride)
            for course in req.FILES.getlist('courses'):
                new_course = Course.objects.create(campaign = form.cleaned_data['campaign'],
                                                   trackfile = course)
                if not course.name.lower().endswith(".gpx"):
                    messages.info(req, 'Could not upload {}: Does not end in GPX.'.format(course.name))
                    continue
            messages.info(req, 'Success!')
        else:
            [messages.info(req, 'Failure: {}: {}'.format(x, form.errors[x].as_text())) for x in form.errors]
    return redirect('home')
