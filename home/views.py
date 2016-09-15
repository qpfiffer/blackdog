from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User

from rest_framework import serializers, viewsets
from andablog.models import Entry, EntryImage

# Why is everything in here? Whatever.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# BLOG STUFF
class BlogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Entry
        fields = ('title', 'slug', 'content', 'published_timestamp', 'author', 'entryimage_set')
        depth = 1

class BlogImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EntryImage
        fields = ('entry', 'image', 'image_url')

class BlogViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.filter(is_published=True)
    serializer_class = BlogSerializer

class BlogImageViewSet(viewsets.ModelViewSet):
    queryset = EntryImage.objects.filter(entry__is_published=True)
    serializer_class = BlogImageSerializer


def home(req):
    return render(req, "index.html", locals())
