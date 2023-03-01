from django.urls import path
from healthinsurance.views import *
from healthinsurance.views.deal import *
from healthinsurance.views.email import *
from healthinsurance.views.tasks import *
from healthinsurance.views.policy import *
from healthinsurance.views.dashboard import *
from healthinsurance.views.renewal import *
from healthinsurance.views.order import *
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView


app_name = "health-insurance"
urlpatterns = [
    path("", RedirectView.as_view(url="/accounts?entity=health"), name="index"),
    path("deals/", DealsList.as_view(), name="deals"),
    path("policies/", PolicyListView.as_view(), name="policies"),
    path("deals/add", csrf_exempt(NewHealthDeal.as_view()), name="new-deal"),
    path("deals/edit/<int:pk>", csrf_exempt(EditDeal.as_view()), name="edit-deal"),
    path("deals/edit/members/<int:pk>", csrf_exempt(EditAdditionalMembers.as_view()), name="edit-members"),
    path("deals/delete-deal/<int:pk>/", DeleteDealView.as_view(), name="delete-deal"),
    path("deals/delete-deals/", DeleteDeals.as_view(), name="delete-deals"),
    path("deals/<int:pk>/lost/", DealMarkasLostView.as_view(), name="lose-deal"),
    path('deals/<int:pk>', DealDetails.as_view(), name="deal-details"),
    path("deals/<int:pk>/details", DealMoreDetails.as_view(), name="deal-more-details"),
    path("deals/export/", DealExportView.as_view(), name="deal-export"),
    path("tasks/add/", AddEditTaskView.as_view(), name="tasks-add-edit"),
    path("tasks/<int:pk>/", TaskSingleView.as_view(), name="get-task-json"),
    path("deals/notes/<int:pk>/", DealsNotes.as_view(), name="deals-notes"),
    path("deals/notes/delete/<int:pk>/", delete_note, name="notes-delete"),
    path("deals/tasks/<int:pk>/", DealsTaskAdd.as_view(), name="tasks"),
    path("deals/<int:pk>/tasks/", DealTaskListView.as_view(), name="deal-tasks"),
    path("deals/<int:pk>/get-stage/", HealthDealStagesView.as_view(), name="get-deal-stage"),
    path('deals/<int:pk>/quoted-products/json/', csrf_exempt(DealQuotedProductsView.as_view()), name='deal-quoted-products-json'),
    path("deals/<int:pk>/products/", DealGetProductsAjax.as_view(), name="deal-all-products"),
    path("plan/detail/<int:pk>/",GetPlanDetails.as_view(),name="plan-details" ),
    path("deals/<int:pk>/attachment/add/<str:type>/", csrf_exempt(DealAddAttachment.as_view())),
    path("deals/<int:pk>/attachment/delete/<str:type>/", csrf_exempt(DeleteAttachedFile.as_view()), name="delete-file"),
    path("deals/<int:pk>/substage", csrf_exempt(SubStageView.as_view()), name="substage-processor"),
    path("deals/<int:pk>/email/<str:type>/", csrf_exempt(HandleEmailContent.as_view()), name="deal-email-content"),
    path("deals/<int:pk>/policy/", csrf_exempt(PolicyView.as_view()), name="health-policy"),    
    path("policies/<int:pk>/json/", PolicySingleView.as_view(), name="policy-json"),
    path("policies/export/", PolicyExportView.as_view(), name="policy-export"),
    path("insurers/<int:pk>/plans", csrf_exempt(HealthPlans.as_view()), name="health-plans"),
    path("insurers/<int:pk>/basic-plans", csrf_exempt(BasicHealthPlans.as_view()), name="health-plans"),
    path("deals-created/", HealthDealsCreatedCountView.as_view(), name="health-dashboard-deals-created",),
    path("deals-won/", DealsWonView.as_view(), name="dashboard-deals-won"),
    path('sales-conversion-rate/',HealthSalesConversionRateView.as_view(), name='health-dashboard-sales-conversion-rate'),
    path("deals-lost/", HealthLostDealsView.as_view(), name="dashboard-deals-lost"),
    path('order/<int:pk>/pdf/', OrderPDFView.as_view(), name="order-pdf-view"),
    path('orders-premium/', HealthOrdersTotalPremiumView.as_view(), name='health-dashboard-orders-premium'),
    path('deal-insurer/', HealthDealByInsurer.as_view(), name='health-dashboard-deal-by-insurer'),
    path("deals/<int:pk>/attributes-list/", DealJsonAttributesList.as_view(), name="deal-attributes-list"),
    path("deals/update-field/<int:pk>/", csrf_exempt(DealUpdateFieldView.as_view()), name="update-deal-field"),
    path("deals/<int:pk>/mark-as-lost/", DealMarkasLostView.as_view(), name="deal-mark-as-lost"),
    path("deals/<int:pk>/reopen/", DealReopenView.as_view(), name="deal-reopen"),
    path("deals/<int:pk>/history/", HealthDealHistoryView.as_view(), name="deal-history"),
    path("files/<int:pk>/<str:type>/", DocumentsZipFile.as_view(), name="download-zipfile"),
    path("quote-api/<int:pk>", csrf_exempt(QuoteAPIView.as_view()), name="quote-api"),
    path("quote-api/", csrf_exempt(StageProcessView.as_view()), name="quote-api"),
    path("policy/add", csrf_exempt(PolicyAddView.as_view()), name="new-policy"),
    path("quote/reactivate/<int:pk>/", csrf_exempt(ReactivateQuoteLink.as_view()), name="quote-reactivate"),
    path("tasks/", TaskView.as_view(), name='tasks'),
    path("tasks/<int:pk>/update-field/", csrf_exempt(TaskUpdateFieldView.as_view()), name="task-update-field"),
    path("processed-email/<int:pk>/", csrf_exempt(ProcessedEmailView.as_view()), name="processed_emails"),
    path("renewals/", RenewalView.as_view(), name="renewals"),
    path("renewals/create-deal/", CreateRenewalDealView.as_view(), name="create-renewals-deals"),
    path("renewals/count/", RenewalCountView.as_view(), name="renewals-count"),
    path("renewals/filter/", RenewalListFilter.as_view(), name="renewals-filter"),
    path("policy/json/", PolicyJsonView, name="policies-list"),
    path("renewals/json/", RenewalPolicyJsonView, name="renewals-list"),
    path("deals/json/", DealJsonView, name="deals-list"),
    path("deals/void/<int:pk>/", csrf_exempt(DealVoid.as_view()), name="deal-void"),
]