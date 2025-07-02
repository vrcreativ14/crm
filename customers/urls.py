from django.urls import path

from django.views.decorators.csrf import csrf_exempt

from customers.views import CustomerJsonListView, CustomerAddAttachmentView, CustomerDeleteAttachmentView
from customers.views import CustomerProfileMotorView
from customers.views import CustomersAddView
from customers.views import CustomersDeleteView
from customers.views import CustomersEditView
from customers.views import CustomersView, CustomerAddNoteView, CustomerDeleteNoteView
from customers.views import CustomersFieldUpdateView
from customers.views import CustomersSearchView
from customers.views import CustomerExportView
from customers.views import CustomersMergeView
from customers.views import CustomerHistoryView
from customers.views import CustomerAttachmentsView
from customers.views import CustomerCopyAttachmentView


app_name = 'customers'

urlpatterns = [
    path("", CustomersView.as_view(), name="customers"),
    path("export/", CustomerExportView.as_view(), name="export"),
    path("search/", CustomersSearchView.as_view(), name="customers-search"),
    path("new/", CustomersAddView.as_view(), name="new"),
    path("list/", CustomerJsonListView.as_view(), name="list"),
    path("profile/motor/<int:pk>/", CustomerProfileMotorView.as_view(), name="profile-motor"),
    path("<int:pk>/", CustomersEditView.as_view(), name="edit"),
    path("<int:pk>/history/", CustomerHistoryView.as_view(), name="history"),
    path("update-field/<int:pk>/<str:model>/",
         csrf_exempt(CustomersFieldUpdateView.as_view()), name="update-customer-field"),

    path('<int:pk>/note/', CustomerAddNoteView.as_view(), name='add-note'),
    path('note/<int:pk>/delete/', CustomerDeleteNoteView.as_view(), name='delete-note'),

    path('<int:pk>/list-attachments/', CustomerAttachmentsView.as_view(), name='attachments'),
    path('<int:pk>/attachment/', csrf_exempt(CustomerAddAttachmentView.as_view()), name='add-attachment'),
    path('<int:pk>/attachment/<int:attachment_id>/copy/', csrf_exempt(CustomerCopyAttachmentView.as_view()), name='copy-attachment'),
    path('attachment/<int:pk>/delete/', csrf_exempt(CustomerDeleteAttachmentView.as_view()), name='delete-attachment'),

    path('<int:pk>/delete/', CustomersDeleteView.as_view(), name='delete-customer'),
    path("<int:pk>/<str:entity>/", CustomersEditView.as_view(), name="edit-entity"),
    path('merge/<int:pk1>/<int:pk2>/', CustomersMergeView.as_view(), name='merge-customers'),
]
