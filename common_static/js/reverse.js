this.DjangoUrls = (function () {
    "use strict";
    var data = {"urls":
          [
              ["company-forms-submit", [["forms/submit/%(submission_id)s/", ["submission_id"]]]],
              ["company-forms-web", [["forms/%(pk)s/", ["pk"]]]],
              ["company-forms-web-thankyou", [["forms/thankyou/", []]]],
              ["core:company-forms-redirect-view", [["core/cf/r/pqsfA20nld0kj/", []]]],
              ["core:company-forms-webhook", [["core/cf/w/pqsfA20nld0kj/", []]]],
              ["core:companyform-generate-pdf", [["core/cf/generate/%(submission_id)s/", ["submission_id"]]]],
              ["core:countries-list", [["core/countries/", []]]],
              ["core:get-helpscout-conversation-threads-for-deal", [["core/help-scout/conversations/%(deal_id)s/threads/%(conversation_id)s/", ["deal_id", "conversation_id"]]]],
              ["core:get-helpscout-conversations-for-deal", [["core/help-scout/conversations/%(deal_id)s/", ["deal_id"]]]],
              ["core:hellosign-webhook", [["core/hellosign/webhook/jasdK89nsd2kjka/", []]]],
              ["core:redirect-to-allowed-module", [["core/premission-check/", []]]],
              ["core:update-attachment", [["core/attachment/%(pk)s/", ["pk"]]]],
              ["customers:add-attachment", [["people/%(pk)s/attachment/", ["pk"]]]],
              ["customers:add-note", [["people/%(pk)s/note/", ["pk"]]]],
              ["customers:attachments", [["people/%(pk)s/list-attachments/", ["pk"]]]],
              ["customers:copy-attachment", [["people/%(pk)s/attachment/%(attachment_id)s/copy/", ["pk", "attachment_id"]]]],
              ["customers:customers", [["people/", []]]],
              ["customers:customers-search", [["people/search/", []]]],
              ["customers:delete-attachment", [["people/attachment/%(pk)s/delete/", ["pk"]]]],
              ["customers:delete-customer", [["people/%(pk)s/delete/", ["pk"]]]],
              ["customers:delete-note", [["people/note/%(pk)s/delete/", ["pk"]]]],
              ["customers:edit", [["people/%(pk)s/", ["pk"]]]],
              ["customers:export", [["people/export/", []]]],
              ["customers:history", [["people/%(pk)s/history/", ["pk"]]]],
              ["customers:list", [["people/list/", []]]],
              ["customers:merge-customers", [["people/merge/%(pk1)s/%(pk2)s/", ["pk1", "pk2"]]]],
              ["customers:new", [["people/new/", []]]],
              ["customers:profile-motor", [["people/profile/motor/%(pk)s/", ["pk"]]]],
              ["customers:update-customer-field", [["people/update-field/%(pk)s/%(model)s/", ["pk", "model"]]]],
              ["motorinsurance:add-attachment", [["motor-insurance/deals/%(pk)s/attachment/add/", ["pk"]]]],
              ["motorinsurance:api-list-insurers", [["motor-insurance/api/insurers/", []]]],
              ["motorinsurance:api-list-policies", [["motor-insurance/api/policies/", []]]],
              ["motorinsurance:api-list-products", [["motor-insurance/api/products/", []]]],
              ["motorinsurance:attachments", [["motor-insurance/deals/%(pk)s/attachment/", ["pk"]]]],
              ["motorinsurance:auto-quote-aman-discounts-info", [["motor-insurance/auto-quote/%(pk)s/aman/discounts/", ["pk"]]]],
              ["motorinsurance:auto-quote-aman-vehicle-info",
                  [["motor-insurance/auto-quote/%(pk)s/aman/vehicle-info/%(chassis_number)s/", ["pk", "chassis_number"]]]],
              ["motorinsurance:auto-quote-dat-mmt-tree", [["motor-insurance/auto-quote/dat/mmt/", []]]],
              ["motorinsurance:auto-quote-insurer",
                  [["motor-insurance/auto-quote/%(pk)s/%(insurer_pk)s/", ["pk", "insurer_pk"]]]],
              ["motorinsurance:auto-quote-oic-mmt-tree", [["motor-insurance/auto-quote/oic/mmt/", []]]],
              ["motorinsurance:auto-quote-qic-get-quotes",
                  [["motor-insurance/auto-quote/qic/%(deal_pk)s/get-quotes/", ["deal_pk"]]]],
              ["motorinsurance:auto-quote-qic-trim-details",
                  [["motor-insurance/auto-quote/qic/%(deal_pk)s/trim-details/", ["deal_pk"]]]],
              ["motorinsurance:auto-quote-qic-trims", [["motor-insurance/auto-quote/qic/%(deal_pk)s/trims/", ["deal_pk"]]]],
              ["motorinsurance:auto-quote-qic-vehicle-info",
                  [["motor-insurance/auto-quote/qic/%(deal_pk)s/vehicle-info/", ["deal_pk"]]]],
              ["motorinsurance:auto-quote-tokio-marine-mmt-tree", [["motor-insurance/auto-quote/tokio-marine/mmt/", []]]],
              ["motorinsurance:copy-attachment",
                  [["motor-insurance/deals/%(pk)s/attachment/%(attachment_id)s/copy/", ["pk", "attachment_id"]]]],
              ["motorinsurance:create-renewals-deals", [["motor-insurance/renewals/create-deals/", []]]],
              ["motorinsurance:dashboard-deals-created", [["motor-insurance/dashboard/deals-created/", []]]],
              ["motorinsurance:dashboard-orders-created", [["motor-insurance/dashboard/orders-created/", []]]],
              ["motorinsurance:dashboard-orders-premium", [["motor-insurance/dashboard/orders-premium/", []]]],
              ["motorinsurance:dashboard-sales-conversion-rate", [["motor-insurance/dashboard/sales-conversion-rate/", []]]],
              ["motorinsurance:deal-add-note", [["motor-insurance/deals/%(pk)s/note/", ["pk"]]]],
              ["motorinsurance:deal-all-products", [["motor-insurance/deals/%(pk)s/products/", ["pk"]]]],
              ["motorinsurance:deal-attributes-list", [["motor-insurance/deals/%(pk)s/attributes-list/", ["pk"]]]],
              ["motorinsurance:deal-can-scan-policy-document",
                  [["motor-insurance/deals/%(pk)s/can-scan-policy-document/", ["pk"]]]],
              ["motorinsurance:deal-current-stage", [["motor-insurance/deals/%(pk)s/current-stage/", ["pk"]]]],
              ["motorinsurance:deal-delete-note", [["motor-insurance/deals/note/%(pk)s/delete/", ["pk"]]]],
              ["motorinsurance:deal-duplicate", [["motor-insurance/deals/%(pk)s/duplicate/", ["pk"]]]],
              ["motorinsurance:deal-edit", [["motor-insurance/deals/%(pk)s/", ["pk"]]]],
              ["motorinsurance:deal-email-content", [["motor-insurance/deals/%(pk)s/email/%(type)s/", ["pk", "type"]]]],
              ["motorinsurance:deal-export", [["motor-insurance/deals/export/", []]]],
              ["motorinsurance:deal-history", [["motor-insurance/deals/%(pk)s/history/", ["pk"]]]],
              ["motorinsurance:deal-mark-as-lost", [["motor-insurance/deals/%(pk)s/mark-as-lost/", ["pk"]]]],
              ["motorinsurance:deal-mark-closed", [["motor-insurance/deals/%(pk)s/mark-closed/%(type)s/", ["pk", "type"]]]],
              ["motorinsurance:deal-new", [["motor-insurance/deals/new/", []]]],
              ["motorinsurance:deal-policy-document-parser",
                  [["motor-insurance/deals/%(pk)s/policy-document-parser/", ["pk"]]]],
              ["motorinsurance:deal-quote-extend", [["motor-insurance/deals/%(pk)s/quote-extend/", ["pk"]]]],
              ["motorinsurance:deal-quote-preview", [["motor-insurance/deals/%(pk)s/quote-preview/", ["pk"]]]],
              ["motorinsurance:deal-quoted-products-json", [["motor-insurance/deals/%(pk)s/quoted-products/json/", ["pk"]]]],
              ["motorinsurance:deal-remove-warning", [["motor-insurance/deals/%(pk)s/remove-warning/", ["pk"]]]],
              ["motorinsurance:deal-reopen", [["motor-insurance/deals/%(pk)s/reopen/", ["pk"]]]],
              ["motorinsurance:deal-tasks", [["motor-insurance/deals/%(pk)s/tasks/", ["pk"]]]],
              ["motorinsurance:deal-update-mmt", [["motor-insurance/deals/%(pk)s/update-mmt/", ["pk"]]]],
              ["motorinsurance:deal-update-order", [["motor-insurance/deals/%(pk)s/update-order/", ["pk"]]]],
              ["motorinsurance:deal-update-policy", [["motor-insurance/deals/%(pk)s/update-policy/", ["pk"]]]],
              ["motorinsurance:deals", [["motor-insurance/deals/", []]]],
              ["motorinsurance:delete-attachment", [["motor-insurance/deals/attachment/%(pk)s/delete/", ["pk"]]]],
              ["motorinsurance:delete-deal", [["motor-insurance/deals/%(pk)s/delete/", ["pk"]]]],
              ["motorinsurance:document-parsed-values",
                  [["motor-insurance/document-parser/%(parser_id)s/%(document_id)s", ["parser_id", "document_id"]]]],
              ["motorinsurance:get-car-value", [["motor-insurance/deal/car-value/", []]]],
              ["motorinsurance:get-deal-json", [["motor-insurance/deals/%(pk)s/json/", ["pk"]]]],
              ["motorinsurance:get-deal-stage", [["motor-insurance/deals/%(pk)s/get-stage/", ["pk"]]]],
              ["motorinsurance:get-task-json", [["motor-insurance/tasks/%(pk)s/", ["pk"]]]],
              ["motorinsurance:lead-form", [["motor-insurance/get-quotes/start/", []]]],
              ["motorinsurance:lead-form-for-user",
                  [["motor-insurance/get-quotes/start/%(username)s/%(user_id)s/", ["username", "user_id"]]]],
              ["motorinsurance:lead-submitted-thanks", [["motor-insurance/get-quotes/thank-you/", []]]],
              ["motorinsurance:motor-tree", [["motor-insurance/get-quotes/motor-tree/", []]]],
              ["motorinsurance:order-pdf-view", [["motor-insurance/order/%(pk)s/pdf/", ["pk"]]]],
              ["motorinsurance:policies", [["motor-insurance/policies/", []]]],
              ["motorinsurance:policy-attachment-delete", [["motor-insurance/policies/attachment/%(pk)s/delete/", ["pk"]]]],
              ["motorinsurance:policy-export", [["motor-insurance/policies/export/", []]]],
              ["motorinsurance:policy-field-options", [["motor-insurance/policies/field-options/", []]]],
              ["motorinsurance:policy-import", [["motor-insurance/policies/import/", []]]],
              ["motorinsurance:policy-json", [["motor-insurance/policies/%(pk)s/json/", ["pk"]]]],
              ["motorinsurance:policy-new", [["motor-insurance/policies/new/", []]]],
              ["motorinsurance:product-addons", [["motor-insurance/product/%(pk)s/", ["pk"]]]],
              ["motorinsurance:quote-comparison",
                  [["motor-insurance/quotes/%(reference_number)s/%(pk)s/", ["reference_number", "pk"]]]],
              ["motorinsurance:quote-order-summary",
                  [["motor-insurance/quotes/%(reference_number)s/%(pk)s/order/", ["reference_number", "pk"]]]],
              ["motorinsurance:quote-pdf-download",
                  [["motor-insurance/quotes/%(reference_number)s/%(pk)s/pdf/download/", ["reference_number", "pk"]]]],
              ["motorinsurance:quote-pdf-view",
                  [["motor-insurance/order/%(reference_number)s/%(pk)s/pdf/", ["reference_number", "pk"]],
                  ["motor-insurance/quotes/%(reference_number)s/%(pk)s/pdf/", ["reference_number", "pk"]]]],
              ["motorinsurance:quote-select-product",
                  [["motor-insurance/quotes/%(reference_number)s/%(pk)s/buy/", ["reference_number", "pk"]]]],
              ["motorinsurance:quote-upload-documents",
                  [["motor-insurance/quotes/%(reference_number)s/%(pk)s/documents/upload/", ["reference_number", "pk"]]]],
              ["motorinsurance:quote-upload-documents-success", [["motor-insurance/quotes/documents/upload/success/", []]]],
              ["motorinsurance:quoted-product-addons", [["motor-insurance/quoted-product/%(pk)s/", ["pk"]]]],
              ["motorinsurance:renewals", [["motor-insurance/renewals/", []]]],
              ["motorinsurance:renewals-count", [["motor-insurance/renewals/count/", []]]],
              ["motorinsurance:renewals-export", [["motor-insurance/renewals/export/", []]]],
              ["motorinsurance:task-delete", [["motor-insurance/tasks/%(pk)s/delete/", ["pk"]]]],
              ["motorinsurance:task-update-field", [["motor-insurance/tasks/%(pk)s/update-field/", ["pk"]]]],
              ["motorinsurance:tasks", [["motor-insurance/tasks/", []]]],
              ["motorinsurance:tasks-add-edit", [["motor-insurance/tasks/addedit/", []]]],
              ["motorinsurance:tasks-mark-as-done", [["motor-insurance/tasks/mark-as-done/", []]]],
              ["motorinsurance:terms-and-conditions", [["motor-insurance/terms/", []]]],
              ["motorinsurance:update-deal-field", [["motor-insurance/deals/update-field/%(pk)s/%(model)s/", ["pk", "model"]]]],
              ["motorinsurance:update-deal-stage",
                  [["motor-insurance/quotes/%(reference_number)s/%(pk)s/update-status/", ["reference_number", "pk"]]]],

              ["mortgage:add-attachment", [["mortgage/deals/%(pk)s/attachment/add/", ["pk"]]]],
              ["mortgage:api-list-banks", [["mortgage/api/banks/", []]]],
              ["mortgage:api-list-policies", [["mortgage/api/policies/", []]]],
              ["mortgage:api-list-products", [["mortgage/api/products/", []]]],
              ["mortgage:attachments", [["mortgage/deals/%(pk)s/attachment/", ["pk"]]]],
              ["mortgage:auto-quote-aman-discounts-info", [["mortgage/auto-quote/%(pk)s/aman/discounts/", ["pk"]]]],
              ["mortgage:auto-quote-aman-vehicle-info",
                  [["mortgage/auto-quote/%(pk)s/aman/vehicle-info/%(chassis_number)s/", ["pk", "chassis_number"]]]],
              ["mortgage:auto-quote-dat-mmt-tree", [["mortgage/auto-quote/dat/mmt/", []]]],
              // ["mortgage:auto-quote-insurer",
              //     [["mortgage/auto-quote/%(pk)s/%(insurer_pk)s/", ["pk", "insurer_pk"]]]],
              // ["mortgage:auto-quote-oic-mmt-tree", [["mortgage/auto-quote/oic/mmt/", []]]],
              // ["mortgage:auto-quote-qic-get-quotes",
              //     [["mortgage/auto-quote/qic/%(deal_pk)s/get-quotes/", ["deal_pk"]]]],
              // ["mortgage:auto-quote-qic-trim-details",
              //     [["mortgage/auto-quote/qic/%(deal_pk)s/trim-details/", ["deal_pk"]]]],
              // ["mortgage:auto-quote-qic-trims", [["mortgage/auto-quote/qic/%(deal_pk)s/trims/", ["deal_pk"]]]],
              // ["mortgage:auto-quote-qic-vehicle-info",
              //     [["mortgage/auto-quote/qic/%(deal_pk)s/vehicle-info/", ["deal_pk"]]]],
              // ["mortgage:auto-quote-tokio-marine-mmt-tree", [["mortgage/auto-quote/tokio-marine/mmt/", []]]],
              ["mortgage:copy-attachment",
                  [["mortgage/deals/%(pk)s/attachment/%(attachment_id)s/copy/", ["pk", "attachment_id"]]]],
              ["mortgage:create-renewals-deals", [["mortgage/renewals/create-deals/", []]]],
              ["mortgage:dashboard-deals-created", [["mortgage/dashboard/deals-created/", []]]],
              ["mortgage:dashboard-orders-created", [["mortgage/dashboard/orders-created/", []]]],
              ["mortgage:dashboard-orders-premium", [["mortgage/dashboard/orders-premium/", []]]],
              ["mortgage:dashboard-sales-conversion-rate", [["mortgage/dashboard/sales-conversion-rate/", []]]],
              ["mortgage:deal-add-note", [["mortgage/deals/%(pk)s/note/", ["pk"]]]],
              ["mortgage:deal-all-products", [["mortgage/deals/%(pk)s/products/", ["pk"]]]],
              ["mortgage:deal-attributes-list", [["mortgage/deals/%(pk)s/attributes-list/", ["pk"]]]],
              ["mortgage:deal-can-scan-policy-document",
                  [["mortgage/deals/%(pk)s/can-scan-policy-document/", ["pk"]]]],
              ["mortgage:deal-current-stage", [["mortgage/deals/%(pk)s/current-stage/", ["pk"]]]],
              ["mortgage:deal-delete-note", [["mortgage/deals/notes/delete/%(pk)s/", ["pk"]]]],
              ["mortgage:deal-duplicate", [["mortgage/deals/%(pk)s/duplicate/", ["pk"]]]],
              ["mortgage:deal-edit", [["mortgage/deals/%(pk)s/", ["pk"]]]],
              ["mortgage:deal-email-content", [["mortgage/deals/%(pk)s/email/%(type)s/", ["pk", "type"]]]],
              ["mortgage:deal-export", [["mortgage/deals/export/", []]]],
              ["mortgage:deal-history", [["mortgage/deals/%(pk)s/history/", ["pk"]]]],
              ["mortgage:deal-mark-as-lost", [["mortgage/deals/%(pk)s/mark-as-lost/", ["pk"]]]],
              ["mortgage:deal-mark-closed", [["mortgage/deals/%(pk)s/mark-closed/%(type)s/", ["pk", "type"]]]],
              ["mortgage:deal-new", [["mortgage/deals/new/", []]]],
              ["mortgage:deal-policy-document-parser",
                  [["mortgage/deals/%(pk)s/policy-document-parser/", ["pk"]]]],
              ["mortgage:deal-quote-extend", [["mortgage/deals/%(pk)s/quote-extend/", ["pk"]]]],
              ["mortgage:deal-quote-preview", [["mortgage/deals/%(pk)s/quote-preview/", ["pk"]]]],
              ["mortgage:deal-quoted-products-json", [["mortgage/deals/%(pk)s/quoted-products/json/", ["pk"]]]],
              ["mortgage:deal-remove-warning", [["mortgage/deals/%(pk)s/remove-warning/", ["pk"]]]],
              ["mortgage:deal-reopen", [["mortgage/deals/%(pk)s/reopen/", ["pk"]]]],
              ["mortgage:deal-tasks", [["mortgage/deals/%(pk)s/tasks/", ["pk"]]]],
              ["mortgage:deal-update-mmt", [["mortgage/deals/%(pk)s/update-mmt/", ["pk"]]]],
              ["mortgage:deal-update-order", [["mortgage/deals/%(pk)s/update-order/", ["pk"]]]],
              ["mortgage:deal-update-policy", [["mortgage/deals/%(pk)s/update-policy/", ["pk"]]]],
              ["mortgage:deals", [["mortgage/deals/", []]]],
              ["mortgage:delete-attachment", [["mortgage/deals/attachment/%(pk)s/delete/", ["pk"]]]],
              ["mortgage:delete-deal", [["mortgage/deals/%(pk)s/delete/", ["pk"]]]],
              ["mortgage:document-parsed-values",
                  [["mortgage/document-parser/%(parser_id)s/%(document_id)s", ["parser_id", "document_id"]]]],
              // ["mortgage:get-car-value", [["mortgage/deal/car-value/", []]]],
              ["mortgage:get-deal-json", [["mortgage/deals/%(pk)s/json/", ["pk"]]]],
              ["mortgage:get-deal-stage", [["mortgage/deals/%(pk)s/get-stage/", ["pk"]]]],
              ["mortgage:get-task-json", [["mortgage/tasks/%(pk)s/", ["pk"]]]],
              ["mortgage:lead-form", [["mortgage/get-quotes/start/", []]]],
              ["mortgage:lead-form-for-user",
                  [["mortgage/get-quotes/start/%(username)s/%(user_id)s/", ["username", "user_id"]]]],
              ["mortgage:lead-submitted-thanks", [["mortgage/get-quotes/thank-you/", []]]],
              // ["mortgage:motor-tree", [["mortgage/get-quotes/motor-tree/", []]]],
              ["mortgage:order-pdf-view", [["mortgage/order/%(pk)s/pdf/", ["pk"]]]],
              ["mortgage:policies", [["mortgage/policies/", []]]],
              ["mortgage:policy-attachment-delete", [["mortgage/policies/attachment/%(pk)s/delete/", ["pk"]]]],
              ["mortgage:policy-export", [["mortgage/policies/export/", []]]],
              ["mortgage:policy-field-options", [["mortgage/policies/field-options/", []]]],
              ["mortgage:policy-import", [["mortgage/policies/import/", []]]],
              ["mortgage:policy-json", [["mortgage/policies/%(pk)s/json/", ["pk"]]]],
              ["mortgage:policy-new", [["mortgage/policies/new/", []]]],
              ["mortgage:product-addons", [["mortgage/product/%(pk)s/", ["pk"]]]],
              ["mortgage:quote-comparison",
                  [["mortgage/quotes/%(reference_number)s/%(pk)s/", ["reference_number", "pk"]]]],
              ["mortgage:quote-order-summary",
                  [["mortgage/quotes/%(reference_number)s/%(pk)s/order/", ["reference_number", "pk"]]]],
              ["mortgage:quote-pdf-download",
                  [["mortgage/quotes/%(reference_number)s/%(pk)s/pdf/download/", ["reference_number", "pk"]]]],
              ["mortgage:quote-pdf-view",
                  [["mortgage/order/%(reference_number)s/%(pk)s/pdf/", ["reference_number", "pk"]],
                  ["mortgage/quotes/%(reference_number)s/%(pk)s/pdf/", ["reference_number", "pk"]]]],
              ["mortgage:quote-select-product",
                  [["mortgage/quotes/%(reference_number)s/%(pk)s/buy/", ["reference_number", "pk"]]]],
              ["mortgage:quote-upload-documents",
                  [["mortgage/quotes/%(reference_number)s/%(pk)s/documents/upload/", ["reference_number", "pk"]]]],
              ["mortgage:quote-upload-documents-success", [["mortgage/quotes/documents/upload/success/", []]]],
              ["mortgage:quoted-product-addons", [["mortgage/quoted-product/%(pk)s/", ["pk"]]]],
              ["mortgage:renewals", [["mortgage/renewals/", []]]],
              ["mortgage:renewals-count", [["mortgage/renewals/count/", []]]],
              ["mortgage:renewals-export", [["mortgage/renewals/export/", []]]],
              ["mortgage:task-delete", [["mortgage/tasks/%(pk)s/delete/", ["pk"]]]],
              ["mortgage:task-update-field", [["mortgage/tasks/%(pk)s/update-field/", ["pk"]]]],
              ["mortgage:tasks", [["mortgage/tasks/", []]]],
              ["mortgage:tasks-add-edit", [["mortgage/tasks/addedit/", []]]],
              ["mortgage:tasks-mark-as-done", [["mortgage/tasks/mark-as-done/", []]]],
              ["mortgage:terms-and-conditions", [["mortgage/terms/", []]]],
              ["mortgage:update-deal-field", [["mortgage/deals/update-field/%(pk)s/", ["pk"]]]],
              ["mortgage:update-deal-stage",
                  [["mortgage/quotes/%(reference_number)s/%(pk)s/update-status/", ["reference_number", "pk"]]]],

                  ["health-insurance:deal-details", [["health-insurance/deals/%(pk)s", ["pk"]]]],
                  ["health-insurance:deal-tasks", [["health-insurance/deals/%(pk)s/tasks/", ["pk"]]]],
                ["health-insurance:tasks", [["health-insurance/tasks/", []]]],
                ["health-insurance:tasks-add-edit", [["health-insurance/tasks/addedit/", []]]],
                ["health-insurance:tasks-mark-as-done", [["health-insurance/tasks/mark-as-done/", []]]],
                ["health-insurance:task-delete", [["health-insurance/tasks/%(pk)s/delete/", ["pk"]]]],
              ["health-insurance:task-update-field", [["health-insurance/tasks/%(pk)s/update-field/", ["pk"]]]],
              ["health-insurance:get-task-json", [["health-insurance/tasks/%(pk)s/", ["pk"]]]],
              ["health-insurance:get-deal-stage", [["health-insurance/deals/%(pk)s/get-stage/", ["pk"]]]],
              ["health-insurance:deal-quoted-products-json", [["health-insurance/deals/%(pk)s/quoted-products/json/", ["pk"]]]],
              ["health-insurance:health-plans", [["health-insurance/insurers/%(pk)s/plans", ["pk"]]]],
              ["health-insurance:deal-email-content", [["health-insurance/deals/%(pk)s/email/%(type)s/", ["pk", "type"]]]],
              ["health-insurance:plan-details", [["health-insurance/plan/detail/%(pk)s/", ["pk"]]]],
              ["health-insurance:lose-deal", [["health-insurance/deals/%(pk)s/lost/", ["pk"]]]],
              ["health-insurance:deal-history", [["health-insurance/deals/%(pk)s/history/", ["pk"]]]],
              ["health-insurance:deal-mark-as-lost", [["health-insurance/deals/%(pk)s/mark-as-lost/", ["pk"]]]],
              ["health-insurance:deal-reopen", [["health-insurance/deals/%(pk)s/reopen/", ["pk"]]]],
              ["health-insurance:policy-json", [["health-insurance/policies/%(pk)s/json/", ["pk"]]]],
              ["health-insurance:create-renewals-deals", [["health-insurance/renewals/create-deal/", []]]],
              ["health-insurance:renewals-count", [["health-insurance/renewals/count/", []]]],
              ["health-insurance:renewals-filter", [["health-insurance/renewals/filter/", []]]],
              ["health-insurance:quote-reactivate", [["health-insurance/quote/reactivate/%(pk)s/", ["pk"]]]],
              ["health-insurance:download-zipfile", [["health-insurance/files/%(pk)s/%(type)s/", ["pk", "type"]]]],
              ["health-insurance:processed_emails", [["health-insurance/processed-email/%(pk)s/", ["pk"]]]],
              ["health-insurance:deal-void", [["health-insurance/deals/void/%(pk)s/", ["pk"]]]],
              ["health-insurance:renewals-list", [["health-insurance/policy/json/", []]]],

              ["short-url", [["r/%(short_id)s/", ["short_id"]]]],
              ["tinymce-compressor", [["tinymce/compressor/", []]]],
              ["tinymce-filebrowser", [["tinymce/filebrowser/", []]]],
              ["tinymce-linklist", [["tinymce/flatpages_link_list/", []]]],
              ["tinymce-spellcheck", [["tinymce/spellchecker/", []]]]
          ],
        "prefix": "/"};
    function factory(d) {
        var url_patterns = d.urls;
        var url_prefix = d.prefix;
        var Urls = {};
        var self_url_patterns = {};

        var _get_url = function (url_pattern) {
        return function () {
            var _arguments, index, url, url_arg, url_args, _i, _len, _ref,
            _ref_list, match_ref, provided_keys, build_kwargs;

            _arguments = arguments;
            _ref_list = self_url_patterns[url_pattern];

            if (arguments.length == 1 && typeof (arguments[0]) == "object") {
            // kwargs mode
            var provided_keys_list = Object.keys (arguments[0]);
            provided_keys = {};
            for (_i = 0; _i < provided_keys_list.length; _i++)
                provided_keys[provided_keys_list[_i]] = 1;

            match_ref = function (ref)
            {
                var _i;

                // Verify that they have the same number of arguments
                if (ref[1].length != provided_keys_list.length)
                return false;

                for (_i = 0;
                 _i < ref[1].length && ref[1][_i] in provided_keys;
                 _i++);

                // If for loop completed, we have all keys
                return _i == ref[1].length;
            }

            build_kwargs = function (keys) {return _arguments[0];}

            } else {
            // args mode
            match_ref = function (ref)
            {
                return ref[1].length == _arguments.length;
            }

            build_kwargs = function (keys) {
                var kwargs = {};

                for (var i = 0; i < keys.length; i++) {
                kwargs[keys[i]] = _arguments[i];
                }

                return kwargs;
            }
            }

            for (_i = 0;
             _i < _ref_list.length && !match_ref(_ref_list[_i]);
             _i++);

            // can't find a match
            if (_i == _ref_list.length)
            return null;

            _ref = _ref_list[_i];
            url = _ref[0], url_args = build_kwargs(_ref[1]);
            for (url_arg in url_args) {
            var url_arg_value = url_args[url_arg];
            if (url_arg_value === undefined || url_arg_value === null) {
                url_arg_value = '';
            } else {
                url_arg_value = url_arg_value.toString();
            }
            url = url.replace("%(" + url_arg + ")s", url_arg_value);
            }
            return url_prefix + url;
        };
        };

        var name, pattern, url, _i, _len, _ref;
        for (_i = 0, _len = url_patterns.length; _i < _len; _i++) {
        _ref = url_patterns[_i], name = _ref[0], pattern = _ref[1];
        self_url_patterns[name] = pattern;
        url = _get_url(name);
        Urls[name.replace(/[-_]+(.)/g, function (_m, p1) { return p1.toUpperCase(); })] = url;
        Urls[name.replace(/-/g, '_')] = url;
        Urls[name] = url;
        }

        return Urls;
    }
    return data ? factory(data) : factory;
})();
