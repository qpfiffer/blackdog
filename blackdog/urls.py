"""blackdog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static

from rest_framework import routers, viewsets

from home.views import home, campaignUpload, UserViewSet, BlogViewSet, BlogImageViewSet,\
                       RideViewSet, CourseViewSet, CampaignViewSet, instagram_redirect,\
                       add_poi, InstagramPOIViewSet, POIViewSet, EntryPOIViewSet, TextPOIViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'blog', BlogViewSet)
router.register(r'blog_images', BlogImageViewSet)
router.register(r'rides', RideViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'campaigns', CampaignViewSet)
router.register(r'instagram_pois', InstagramPOIViewSet)
router.register(r'entry_pois', EntryPOIViewSet)
router.register(r'text_pois', TextPOIViewSet)
router.register(r'pois', POIViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', home, name='home'),
    url(r'^campaignUpload$', campaignUpload, name="campaignUpload"),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^instagram_redirect/', instagram_redirect, name='instagram_redirect'),
    url(r'^add_poi/', add_poi, name='add_poi'),
    url('', include('social.apps.django_app.urls', namespace='social'))
]# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
