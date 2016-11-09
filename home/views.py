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
from home.models import Campaign, Course, Ride, PointOfInterest, InstagramPointOfInterest,\
                        EntryPointOfInterest, TextPointOfInterest
import json, requests

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
    queryset = Entry.objects.filter(is_published=True).order_by('-published_timestamp')
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
        fields = ('id', 'uploaded', 'campaign', 'trackfile')

class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all().order_by('-id')
    serializer_class = RideSerializer

class CampaignSerializer(serializers.HyperlinkedModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Campaign
        depth = 1
        fields = ('owner', 'created_at', 'name', 'about', 'ride_set', 'course_set')

class PointOfInterestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PointOfInterest
        fields = ('lat', 'lng', 'created_at')

class InstagramPointOfInterestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InstagramPointOfInterest
        fields = ('poi', 'cached_response')
        depth = 1

class TextPointOfInterestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TextPointOfInterest
        fields = ('poi', 'text')
        depth = 1

class EntryPointOfInterestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EntryPointOfInterest
        fields = ('poi', 'entry',)
        depth = 1

class POIViewSet(viewsets.ModelViewSet):
    queryset = PointOfInterest.objects.all()
    serializer_class = PointOfInterestSerializer

class InstagramPOIViewSet(viewsets.ModelViewSet):
    queryset = InstagramPointOfInterest.objects.all()
    serializer_class = InstagramPointOfInterestSerializer

class EntryPOIViewSet(viewsets.ModelViewSet):
    queryset = EntryPointOfInterest.objects.all()
    serializer_class = EntryPointOfInterestSerializer

class TextPOIViewSet(viewsets.ModelViewSet):
    queryset = TextPointOfInterest.objects.all()
    serializer_class = TextPointOfInterestSerializer

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.filter()
    serializer_class = CampaignSerializer

def home(req):
    upload_form = UploadCampaignForm(req.user)
    all_messages = json.dumps([x.message for x in messages.get_messages(req)])
    available_backends = load_backends(['social.backends.instagram.InstagramOAuth2'])
    if req.user.is_authenticated():
        instagram_acct = UserSocialAuth.objects.filter(user=req.user, provider='instagram')
    else:
        instagram_acct = None

    return render(req, "index.html", locals())

def instagram_redirect(req):
    messages.info(req, 'Instagram now auth\'d.')
    return redirect('home')

def add_poi(req):
    shortcode_endpoint = "https://api.instagram.com/v1/media/shortcode/{SHORTCODE}?access_token={ACCESS_TOKEN}"
    instagram_acct = UserSocialAuth.objects.get(user=req.user, provider='instagram')
    if not instagram_acct:
        messages.error(req, 'Please auth with Instagram first.')
        return redirect('home')

    if req.method == 'POST':
        parsed = json.loads(req.body)
        latlng = parsed.get("latlng", None)
        poi_type = parsed.get("type", None)
        if not poi_type or not latlng:
            messages.error(req, 'Type or latlng not specified.')
            return redirect('home')

        if poi_type == "instagram":
            shortcode = parsed.get("shortcode", None)
            if shortcode and "http" in shortcode:
                shortcode = shortcode.split("/")[-2]

            formatted_url = shortcode_endpoint.format(SHORTCODE=shortcode, ACCESS_TOKEN=instagram_acct.access_token)
            resp = requests.get(formatted_url)
            # XXX: Not the first one. But fuck you.
            poi = PointOfInterest.objects.create(campaign=Campaign.objects.all()[0], lat=latlng["lat"], lng=latlng["lng"])
            InstagramPointOfInterest.objects.create(poi=poi, shortcode=shortcode, user_social_auth=instagram_acct, cached_response=resp.json())
            messages.info(req, 'Added new Instagram POI')
        elif poi_type == "entry":
            # XXX: Not the first one. But fuck you.
            poi = PointOfInterest.objects.create(campaign=Campaign.objects.all()[0], lat=latlng["lat"], lng=latlng["lng"])
            EntryPointOfInterest.objects.create(poi=poi, entry=Entry.objects.all()[0])
            messages.info(req, 'Added new Entry POI')
        elif poi_type == "text":
            # XXX: Not the first one. But fuck you.
            poi = PointOfInterest.objects.create(campaign=Campaign.objects.all()[0], lat=latlng["lat"], lng=latlng["lng"])
            TextPointOfInterest.objects.create(poi=poi, text=parsed.get("text", ""))
            messages.info(req, 'Added new text POI')

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
