'use strict';

import React from 'react';


module.exports = {
	'app_path': DjangoUrls['motorinsurance:quote-comparison'](user_data.ref_number, user_data.quote_pk) + '#/',
	'buy_product_path': DjangoUrls['motorinsurance:quote-select-product'](user_data.ref_number, user_data.quote_pk),
	'order_summary': DjangoUrls['motorinsurance:quote-order-summary'](user_data.ref_number, user_data.quote_pk),
	'currency': company_currency
};
