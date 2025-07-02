/* Amplitude Analytics */

var __AMPLITUDE;
;(function() {
    var _this   = '';

    __AMPLITUDE = {
        init: function() {
            _this = this;
        },

        event: function(name) {
            events = {
                'mortgage_deal_created': 'mortgage deal created',
                'mortgage_deal_won': 'mortgage deal won',
                'mortgage_quote_created': 'mortgage quote created',
                'mortgage_quote_email_sent': 'mortgage quote email sent',
                'mortgage_product_quoted': 'mortgage product quoted',

                'motor_deal_created': 'motor deal created',
                'motor_deal_won': 'motor deal won',
                'motor_quote_created': 'motor quote created',
                'motor_quote_email_sent': 'motor quote email sent',
                'motor_product_quoted': 'motor product quoted',
                'pdf_quote_downloaded': 'pdf quote downloaded',
                'motor_order_created': 'motor order created',
                'motor_policy_saved': 'motor policy saved',
                'policy_text_extracted': 'policy text extracted',
                'motor_policy_renewed': 'motor policy renewed',

                'vehicle_valuation_checked': 'vehicle valuation checked',

                'document_previewed': 'documents previewed',
                'document_renamed': 'documents renamed'
            };

            if(name in events)
                return events[name];

            return name;
        },

        setUserData: function() {
            if(typeof amplitude != 'object')
                return;

            amplitude.getInstance().setUserId(loggedin_user_data.ID);

            var userProperties = {
                email: loggedin_user_data.EMAIL,
                company: loggedin_user_data.COMPANY
            };

            amplitude.getInstance().setUserProperties(userProperties);
        },

        logEvent: function(event_type, properties) {
            if(typeof amplitude != 'object')
                return;

            _this.setUserData();

            if(properties === undefined) properties = {};

            properties['company_id'] = current_company_info.ID;
            properties['company_name'] = current_company_info.NAME;

            amplitude.getInstance().logEvent(event_type, properties);
        }
    };

    jQuery(function() {
        __AMPLITUDE.init();
    });

})();
