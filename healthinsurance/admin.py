from django.contrib import admin

# Register your models here.
from healthinsurance.models.deal import *
from healthinsurance.models.quote import *
from healthinsurance.models.policy import *

admin.site.register(Deal)
admin.site.register(PrimaryMember)
admin.site.register(AdditionalMember)
admin.site.register(Quote)
admin.site.register(QuotedPlan)
admin.site.register(Order)
admin.site.register(SubStage)
admin.site.register(DealFiles)
admin.site.register(MemberDocuments)
admin.site.register(HealthPolicy)
admin.site.register(PolicyFiles)
admin.site.register(PaymentDetails)
admin.site.register(AdditionalBenefit)
admin.site.register(ProcessEmail)
