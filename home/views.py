from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages

from rest_framework import serializers, viewsets
from andablog.models import Entry, EntryImage
from home.forms import UploadCampaignForm
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


def home(req):
    upload_form = UploadCampaignForm(req.user)
    all_messages = json.dumps([x.message for x in messages.get_messages(req)])
    return render(req, "index.html", locals())

def campaignUpload(req):
    if not req.user.is_authenticated:
        return redirect('home')

    if req.method == 'POST':
        import ipdb; ipdb.set_trace()
        "asdf"
        form = UploadCampaignForm(req.user, req.POST, req.FILES)
        if form.is_valid():
            for ride in req.FILES.getlist('rides'):
                # DO RIDES
            for course in req.FILES.getlist('courses'):
                # DO COURSES
            messages.info(req, 'Success!')
        else:
            [messages.info(req, 'Failure: {}: {}'.format(x, form.errors[x].as_text())) for x in form.errors]
    return redirect('home')
