from .car import CarTreePartsView
from .car import CarValuationGuideView

from .deal import DealAddView
from .deal import DealDeleteView
from .deal import DealEditView
from .deal import DealSingleView
from .deal import DealUpdateFieldView
from .deal import DealsView
from .deal import DealCurrentStageView
from .deal import DealQuoteView
from .deal import DealQuoteExtendView
from .deal import DealMarkasLostView
from .deal import DealMarkClosedView
from .deal import DealReopenView
from .deal import DealStagesView
from .deal import DealAddNoteView
from .deal import DealDeleteNoteView
from .deal import DealAddEditOrderView
from .deal import DealUpdateMMTView
from .deal import DealQuotedProductsView
from .deal import DealAssignToMeView
from .deal import DealTaskListView
from .deal import DealsExportView
from .deal import DealRemoveWarningView
from .deal import DealHistoryView
from .deal import DealDuplicateView
from .deal import DealAttachmentsView
from .deal import DealAddAttachmentView
from .deal import DealDeleteAttachmentView
from .deal import DealCopyAttachmentView
from .deal import DealGetProductsAjax
from .deal import DealJsonAttributesList

from .deal.email import DealHandleEmailContent

from .deal.policy import DealAddEditPolicyView
from .deal.policy import DealPolicyDocumentParserView
from .deal.policy import DealPolicyDocumentParsedValuesView
from .deal.policy import DealCanScanPolicyDocumentView

from .lead import LeadSubmittedThanksView
from .lead import MotorInsuranceLeadFormView

from .policy import PolicyView
from .policy import PolicyAddView
from .policy import PolicySingleView
from .policy import PolicyDeleteAttachmentView
from .policy import PolicyFieldOptionsView
from .policy import PolicyExportView
from .policy import PolicyImportEmailView

from .renewal import RenewalView
from .renewal import CreateRenewalDealView
from .renewal import RenewalCountView
from .renewal import RenewalExportView

from .product import QuotedProductAddonListView
from .product import ProductAddonListView

from .quote_public import SelectProductView
from .quote_public import QuoteComparisonView
from .quote_public import QuoteOrderSummaryView
from .quote_public import QuoteProductSelectionAndDocumentUploadView
from .quote_public import QuoteDocumentsUploadView
from .quote_public import QuoteDocumentsUploadSuccessView
from .quote_public import QuoteTermsAndConditionsView
from .quote_public import QuotePDFView
from .quote_public import QuotePDFDownloadView

from .task import TaskView
from .task import TaskSingleView
from .task import AddEditTaskView
from .task import TasksMarkAsDoneView
from .task import TaskDeleteView
from .task import TaskUpdateFieldView

from .autoquote import AutoQuoteView
from .autoquote import OICMMTTree
from .autoquote import DATMMTTree
from .autoquote import AmanApiVehicleInfoView
from .autoquote import QICApiVehicleInfoView
from .autoquote import QICApiTrimsView
from .autoquote import QICApiTrimDetailsView

from .order import OrderPDFView

from .dashboard import MotorDealsCreatedCountView
from .dashboard import MotorOrdersCreatedCountView
from .dashboard import MotorOrdersTotalPremiumView
from .dashboard import MotorSalesConversionRateView
