from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView

from motorinsurance.views import *
from motorinsurance.views.autoquote import TokioMarineMMTTree, AmanApiDiscountsInfoView, QICApiGetQuotesView
from motorinsurance.apis import ListPoliciesView, ListInsurersView, ListProductsView

app_name = 'motorinsurance'

urlpatterns = [
    # Public URLs
    path('get-quotes/', RedirectView.as_view(pattern_name='motorinsurance:lead-form')),
    path('get-quotes/start/<str:username>/<int:user_id>/', csrf_exempt(MotorInsuranceLeadFormView.as_view()),
         name='lead-form-for-user'),
    path('get-quotes/start/', csrf_exempt(MotorInsuranceLeadFormView.as_view()),
         name='lead-form'),
    path('get-quotes/motor-tree/', CarTreePartsView.as_view(), name="motor-tree"),
    path('get-quotes/thank-you/', LeadSubmittedThanksView.as_view(), name="lead-submitted-thanks"),
    path('terms/', QuoteTermsAndConditionsView.as_view(), name="terms-and-conditions"),

    # Motor Deals
    path("deals/", DealsView.as_view(), name="deals"),
    path("deals/new/", DealAddView.as_view(), name="deal-new"),
    path("deals/<int:pk>/", DealEditView.as_view(), name="deal-edit"),
    path("deals/<int:pk>/history/", DealHistoryView.as_view(), name="deal-history"),
    path("deals/<int:pk>/current-stage/", DealCurrentStageView.as_view(), name="deal-current-stage"),
    path("deals/<int:pk>/quote-preview/", DealQuoteView.as_view(), name="deal-quote-preview"),
    path("deals/<int:pk>/quote-extend/", csrf_exempt(DealQuoteExtendView.as_view()), name="deal-quote-extend"),
    path("deals/<int:pk>/mark-as-lost/", DealMarkasLostView.as_view(), name="deal-mark-as-lost"),
    path("deals/<int:pk>/reopen/", DealReopenView.as_view(), name="deal-reopen"),
    path("deals/<int:pk>/products/", DealGetProductsAjax.as_view(), name="deal-all-products"),
    path("deals/<int:pk>/attributes-list/", DealJsonAttributesList.as_view(), name="deal-attributes-list"),
    path("deals/<int:pk>/get-stage/", DealStagesView.as_view(), name="get-deal-stage"),
    path("deals/<int:pk>/json/", DealSingleView.as_view(), name="get-deal-json"),
    path('deals/<int:pk>/note/', DealAddNoteView.as_view(), name='deal-add-note'),
    path('deals/<int:pk>/delete/', DealDeleteView.as_view(), name='delete-deal'),
    path('deals/<int:pk>/update-order/', DealAddEditOrderView.as_view(), name='deal-update-order'),
    path('deals/<int:pk>/update-policy/', DealAddEditPolicyView.as_view(), name='deal-update-policy'),
    path('deals/<int:pk>/update-mmt/', csrf_exempt(DealUpdateMMTView.as_view()), name='deal-update-mmt'),
    path('deals/<int:pk>/quoted-products/json/',
         csrf_exempt(DealQuotedProductsView.as_view()), name='deal-quoted-products-json'),
    path('deals/<int:pk>/mark-closed/<str:type>/', DealMarkClosedView.as_view(), name='deal-mark-closed'),
    path('deals/note/<int:pk>/delete/', delete_note, name='deal-delete-note'),
    path('deals/update-field/<int:pk>/<str:model>/', csrf_exempt(DealUpdateFieldView.as_view()),
         name='update-deal-field'),
    path("deals/<int:pk>/tasks/", DealTaskListView.as_view(), name="deal-tasks"),
    path("deals/<int:pk>/remove-warning/", DealRemoveWarningView.as_view(), name="deal-remove-warning"),
    path("deals/<int:pk>/email/<str:type>/", csrf_exempt(DealHandleEmailContent.as_view()), name="deal-email-content"),
    path("deals/export/", DealsExportView.as_view(), name="deal-export"),
    path("deals/<int:pk>/policy-document-parser/", csrf_exempt(DealPolicyDocumentParserView.as_view()), name="deal-policy-document-parser"),
    path("deals/<int:pk>/can-scan-policy-document/", DealCanScanPolicyDocumentView.as_view(), name="deal-can-scan-policy-document"),
    path("deals/<int:pk>/duplicate/", DealDuplicateView.as_view(), name="deal-duplicate"),
    path('deals/<int:pk>/attachment/', DealAttachmentsView.as_view(), name='attachments'),
    path('deals/<int:pk>/attachment/add/', csrf_exempt(DealAddAttachmentView.as_view()), name='add-attachment'),
    path('deals/attachment/<int:pk>/delete/', csrf_exempt(DealDeleteAttachmentView.as_view()), name='delete-attachment'),
    path('deals/<int:pk>/attachment/<int:attachment_id>/copy/', csrf_exempt(DealCopyAttachmentView.as_view()), name='copy-attachment'),

    path('deal/car-value/', CarValuationGuideView.as_view(), name="get-car-value"),

    # Document Parser
    path("document-parser/<str:parser_id>/<str:document_id>", DealPolicyDocumentParsedValuesView.as_view(), name="document-parsed-values"),

    # Policy
    path("policies/", PolicyView.as_view(), name="policies"),
    path("policies/new/", PolicyAddView.as_view(), name="policy-new"),
    path("policies/<int:pk>/json/", PolicySingleView.as_view(), name="policy-json"),
    path('policies/attachment/<int:pk>/delete/',
         csrf_exempt(PolicyDeleteAttachmentView.as_view()), name="policy-attachment-delete"),
    path("policies/field-options/", PolicyFieldOptionsView.as_view(), name="policy-field-options"),
    path("policies/export/", PolicyExportView.as_view(), name="policy-export"),
    path("policies/import/", csrf_exempt(PolicyImportEmailView.as_view()), name="policy-import"),

    # Renewal
    path("renewals/", RenewalView.as_view(), name="renewals"),
    path("renewals/count/", RenewalCountView.as_view(), name="renewals-count"),
    path("renewals/create-deals/", CreateRenewalDealView.as_view(), name="create-renewals-deals"),
    path("renewals/export/", RenewalExportView.as_view(), name="renewals-export"),

    # Tasks
    path("tasks/", TaskView.as_view(), name="tasks"),
    path("tasks/<int:pk>/", TaskSingleView.as_view(), name="get-task-json"),
    path("tasks/mark-as-done/", csrf_exempt(TasksMarkAsDoneView.as_view()), name="tasks-mark-as-done"),
    path("tasks/addedit/", AddEditTaskView.as_view(), name="tasks-add-edit"),
    path("tasks/<int:pk>/delete/", csrf_exempt(TaskDeleteView.as_view()), name="task-delete"),
    path("tasks/<int:pk>/update-field/", csrf_exempt(TaskUpdateFieldView.as_view()), name="task-update-field"),

    # Quote
    path('quotes/<slug:reference_number>/<int:pk>/documents/upload/', csrf_exempt(QuoteDocumentsUploadView.as_view()),
         name="quote-upload-documents"),
    path('quotes/documents/upload/success/',
         QuoteDocumentsUploadSuccessView.as_view(), name="quote-upload-documents-success"),

    path('quotes/<slug:reference_number>/<int:pk>/pdf/download/', QuotePDFDownloadView.as_view(),
         name="quote-pdf-download"),
    path('quotes/<slug:reference_number>/<int:pk>/pdf/', QuotePDFView.as_view(),
         name="quote-pdf-view"),

    path('order/<slug:reference_number>/<int:pk>/pdf/', QuotePDFView.as_view(),
         name="quote-pdf-view"),

    path('quotes/<slug:reference_number>/<int:pk>/update-status/',
         csrf_exempt(QuoteProductSelectionAndDocumentUploadView.as_view()), name="update-deal-stage"),
    path('quotes/<slug:reference_number>/<int:pk>/order/', QuoteOrderSummaryView.as_view(),
         name="quote-order-summary"),
    path('quotes/<slug:reference_number>/<int:pk>/buy/', csrf_exempt(SelectProductView.as_view()),
         name="quote-select-product"),
    path('quotes/<slug:reference_number>/<int:pk>/', QuoteComparisonView.as_view(),
         name="quote-comparison"),

    # Products
    path(r'quoted-product/<int:pk>/', QuotedProductAddonListView.as_view(),
         name="quoted-product-addons"),
    path(r'product/<int:pk>/', ProductAddonListView.as_view(),
         name="product-addons"),

    # AutoQuote
    path('auto-quote/<int:pk>/<int:insurer_pk>/', csrf_exempt(AutoQuoteView.as_view()),
         name="auto-quote-insurer"),
    path('auto-quote/oic/mmt/', OICMMTTree.as_view(), name='auto-quote-oic-mmt-tree'),
    path('auto-quote/dat/mmt/', DATMMTTree.as_view(), name='auto-quote-dat-mmt-tree'),
    path('auto-quote/tokio-marine/mmt/', TokioMarineMMTTree.as_view(), name='auto-quote-tokio-marine-mmt-tree'),

    path('auto-quote/<int:pk>/aman/vehicle-info/<str:chassis_number>/', AmanApiVehicleInfoView.as_view(),
         name='auto-quote-aman-vehicle-info'),
    path('auto-quote/<int:pk>/aman/discounts/', AmanApiDiscountsInfoView.as_view(),
         name='auto-quote-aman-discounts-info'),

    path('auto-quote/qic/<int:deal_pk>/vehicle-info/', QICApiVehicleInfoView.as_view(),
         name='auto-quote-qic-vehicle-info'),
    path('auto-quote/qic/<int:deal_pk>/trims/', QICApiTrimsView.as_view(), name='auto-quote-qic-trims'),
    path('auto-quote/qic/<int:deal_pk>/trim-details/', QICApiTrimDetailsView.as_view(), name='auto-quote-qic-trim-details'),
    path('auto-quote/qic/<int:deal_pk>/get-quotes/', csrf_exempt(QICApiGetQuotesView.as_view()), name='auto-quote-qic-get-quotes'),

    # Charts
    path('dashboard/deals-created/', MotorDealsCreatedCountView.as_view(), name='dashboard-deals-created'),
    path('dashboard/orders-created/', MotorOrdersCreatedCountView.as_view(), name='dashboard-orders-created'),
    path('dashboard/orders-premium/', MotorOrdersTotalPremiumView.as_view(), name='dashboard-orders-premium'),
    path('dashboard/sales-conversion-rate/',
         MotorSalesConversionRateView.as_view(), name='dashboard-sales-conversion-rate'),

    # Order PDF
    path('order/<int:pk>/pdf/', OrderPDFView.as_view(),
         name="order-pdf-view"),

    path('api/insurers/', ListInsurersView.as_view(), name='api-list-insurers'),
    path('api/products/', ListProductsView.as_view(), name='api-list-products'),
    path('api/policies/', ListPoliciesView.as_view(), name='api-list-policies'),
    path('motor-step1/', MotorStep1.as_view(), name="motor-step1"),
    path('motor-step2/', MotorStep2.as_view(), name="motor-step2"),
    path('motor-step3/', MotorStep3.as_view(), name="motor-step3"),
    path('motor-step4/', MotorStep4.as_view(), name="motor-step4"),
    path('motor-step5/', MotorStep5.as_view(), name="motor-step5"),
    path('motor-step6/', MotorStep6.as_view(), name="motor-step6"),
    path('motor-step7/', MotorStep7.as_view(), name="motor-step7"),
    path('motor-step8/', MotorStep8.as_view(), name="motor-step8"),
    path('motor-step9/', MotorStep9.as_view(), name="motor-step9"),
    path('motor-step10/', MotorStep10.as_view(), name="motor-step10"),
    path('motor-step11/', MotorStep11.as_view(), name="motor-step11"),
    path('motor-step12/', MotorStep12.as_view(), name="motor-step12"),
    path('motor-step13/', MotorStep13.as_view(), name="motor-step13"),
    path('motor-step14/', MotorStep14.as_view(), name="motor-step14"),
    path('motor-step15/', MotorStep15.as_view(), name="motor-step15"),
    path('motor-step16/', MotorStep16.as_view(), name="motor-step16"),
    path('motor-step17/', MotorStep17.as_view(), name="motor-step17"),
    path('motor-step18/', MotorStep18.as_view(), name="motor-step18"),
]
