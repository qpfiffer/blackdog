from django.contrib import admin

from home.models import Campaign, Ride, Course, PointOfInterest, FinancialCategory, FinancialEntry, Contact

admin.site.register(Campaign)
admin.site.register(Ride)
admin.site.register(Course)
admin.site.register(PointOfInterest)
admin.site.register(FinancialCategory)
admin.site.register(FinancialEntry)
admin.site.register(Contact)
