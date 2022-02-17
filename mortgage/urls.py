"""felix URL Configuration"""
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView
 
from mortgage.views import *
from mortgage.views.issued import issuedDeaitl
app_name = "mortgage"

urlpatterns = [
    path("", RedirectView.as_view(url="/accounts?entity=mortgage"), name="index"),

    path("deals/", MortgageDeals.as_view(), name="deals"),
    path("new-deals/",  MortgageDealsAddView.as_view(), name="new-deals"),
    path("create-deals/", csrf_exempt(MortgageBrokerDealAdd.as_view()), name="create-deals"),

    path("deals/<int:pk>/", csrf_exempt(MortgageDealsItem.as_view()), name="deal-edit"),
    path("deals/<int:pk>/history/", MortgageDealHistoryView.as_view(), name="history-deal"),
    path("deals/<int:pk>/get-stage/", MortgageDealStagesView.as_view(), name="get-deal-stage"),
    path("deals/<int:pk>/current-stage/", MortgageDealCurrentStageView.as_view(), name="deal-current-stage"),
    path("deals/<int:pk>/products/", MortgageDealGetProductsView.as_view(), name="deal-all-products"),
    path("deals/<int:pk>/json/", MortgageDealSingleView.as_view(), name="get-deal-json"),
    path("deals/<int:pk>/mark-as-lost/", MortgageDealMarkasLostView.as_view(), name="deal-mark-as-lost"),
    path("deals/<int:pk>/reopen/", MortgageDealReopenView.as_view(), name="deal-reopen"),
    path("deals/update-field/<int:pk>/", csrf_exempt(MortgageDealUpdateFieldView.as_view()), name="update-deal-field"),
    path("deals/delete-deal/<int:pk>/", MortgageDealDeleteView.as_view(), name="delete-deal"),
    path("deals/delete-deals/", DeleteDeals.as_view(), name="delete-deals"),

    path("deals/notes/<int:pk>/", MortgageDealsNotes.as_view(), name="notes"),
    path("deals/notes/delete/<int:pk>/", delete_note, name="notes-delete"),
    path("deals/notes/edit/", EditNote.as_view(), name="note-edit"),

    path("deals/tasks/<int:pk>/", MortgageDealsTaskAdd.as_view(), name="tasks"),
    path("deals/<int:pk>/tasks/", DealTaskListView.as_view(), name="deal-tasks"),
    path("deals/<int:pk>/email/<str:type>/", csrf_exempt(MortgageHandleEmailContent.as_view()), name="deal-email-content"),
    path("deals/<int:pk>/attachment/add/<str:type>/", csrf_exempt(MortgageDealAddAttachment.as_view()),
         name="add-attachment"),
    path("deals/<int:pk>/attachment/", csrf_exempt(MortgageDealAttachment.as_view()), name="attachments"),
    path("deals/attachment/<int:pk>/delete/", csrf_exempt(MortgageDealDeleteAttachment.as_view()), name="delete-attachment"),
    path("processed-email/<int:pk>/", csrf_exempt(ProcessedEmailView.as_view()), name="processed_emails"),
    path("deals/<int:pk>/attachment/delete/<str:type>/", csrf_exempt(MortgageDeleteAttachedFile.as_view()), name="delete-file"),
    path("policies/", MortgagePolicy.as_view(), name="policies"),
    path("peoples/", PeopleView.as_view(), name="peoples"),
    path("eibor/", EiborView.as_view(), name="eibor"),
    path("eibor_post/", EiborPostView.as_view(), name="eibor_post"),
    path("govt-fee/", GovernmentFeeView.as_view(), name="govt-fee"),

    path("deals-created/", MortgageDealsCreatedCountView.as_view(), name="dashboard-deals-created",),
    path("deals-bank/", BankActiveDealsView.as_view(), name="dashboard-deals-bank",),
    path("deals-lost/", BankLostDealsView.as_view(), name="dashboard-deals-lost"),
    path("deals-total/", TotalDealsView.as_view(), name="dashboard-deals-total"),
    path("deals-total-won/", TotalWonView.as_view(), name="dashboard-deals-total-won"),
    path("deals-won/", DealsWonView.as_view(), name="dashboard-deals-won"),


    path("banks/", MortgageBank.as_view(), name="banks"),
    path("banks/edit/<int:pk>/", MortgageBank.as_view(), name="bank-edit"),

    path("get-quotes/start/", MortgageLead.as_view(), name="lead-form-for-user"),
    path("quote/", csrf_exempt(MortgageQuote.as_view()), name="quotes"),
    path("quote-api/<int:pk>/", csrf_exempt(QuoteAPI.as_view()), name="quote-api"),
    path("segmented-customer/<int:pk>/", csrf_exempt(SegmentedCustomer.as_view()), name="segmented-customer",),

    path("renewals/", RedirectView.as_view(url="/accounts?entity=mortgage"), name="renewals"),

    path("stage/", csrf_exempt(StagePropagateView.as_view()), name="stage"),
    path("update-status/", csrf_exempt(StatusToggleView.as_view()), name="update-status"),

    path("tasks/<int:pk>/", TaskSingleView.as_view(), name="tasks"),
    path("tasks/", TaskView.as_view(), name="tasks"),
    path("deals/tasks/<int:pk>/", MortgageDealsTaskAdd.as_view(), name="tasks"),
    path("deals/<int:pk>/tasks/", DealTaskListView.as_view(), name="deal-tasks"),
    path("tasks/mark-as-done/", csrf_exempt(TasksMarkAsDoneView.as_view()), name="tasks-mark-as-done"),
    path("tasks/addedit/", AddEditTaskView.as_view(), name="tasks-add-edit"),
    path("tasks/<int:pk>/delete/", csrf_exempt(TaskDeleteView.as_view()), name="task-delete"),
    path("tasks/<int:pk>/update-field/", csrf_exempt(TaskUpdateFieldView.as_view()), name="task-update-field"),
    
    path("issued/", IssuedView.as_view(), name="issued"),
    path("issued/filter/", FilterIssuedDeals.as_view(), name="filter-issued"),    
    path("issued/<int:pk>/", csrf_exempt(issuedDeaitl.as_view()), name="issued_details"),
    path("substage/", SubStageToggle.as_view(), name="substage"),
    path("bank-ref-number/<int:pk>/", csrf_exempt(BankRefNumber.as_view()), name="bank-ref-number"),
    path("issued/export/", IssuedDealsExportView.as_view(), name="export-issued-deals")


]

