from django.contrib import admin
from mortgage.models import (
    Bank,
    Deal,
    Order,
    Stage,
    Quote,
    PreApproval,
    PostApproval,
    BankInterestRate,
    CustomerProfile,
    SegmentedRate,
    Eibor,
    GovernmentFee,
    SubStage,
    EiborPost,
)

class SingleInstanceAdminMixin(object):
    """Hides the "Add" button when there is already an instance."""
    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
            return False
        return super(SingleInstanceAdminMixin, self).has_add_permission(request)


class EiborAdmin(SingleInstanceAdminMixin, admin.ModelAdmin):
    model = Eibor


class GovernmentFeeAdmin(SingleInstanceAdminMixin, admin.ModelAdmin):
    model = GovernmentFee


class DealAdmin(admin.ModelAdmin):
    ...


class BankInterestRateAdmin(admin.StackedInline):
    model = BankInterestRate
    show_change_link = True

    def get_extra(self, request, obj=None, **kwargs):
        extra = 1
        if obj:
            return 0
        return extra


class BankAdmin(admin.ModelAdmin):
    model = Bank
    inlines = [
        BankInterestRateAdmin,
    ]

admin.site.register(SegmentedRate)
admin.site.register(Order)
admin.site.register(Stage)
admin.site.register(Quote)
admin.site.register(PreApproval)
admin.site.register(PostApproval)
admin.site.register(CustomerProfile)
admin.site.register(BankInterestRate)
admin.site.register(SubStage)
admin.site.register(EiborPost)
admin.site.register(Deal, DealAdmin)
admin.site.register(Bank, BankAdmin)
admin.site.register(Eibor, EiborAdmin)
admin.site.register(GovernmentFee, GovernmentFeeAdmin)
