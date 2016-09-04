from django.shortcuts import render
from django.http import JsonResponse

def home(req):
    return render(req, "index.html", locals())

def campaigns(req):
    return JsonResponse({})

def blog(req):
    return JsonResponse({})
