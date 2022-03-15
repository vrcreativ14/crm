/*
    User Profile
*/
;
'Use Strict';

var __AGENTS;
;(function() {
    var SELECTORS = {
    };

    var _this = '';
    var _form = $('#agent_form');

    __AGENTS =
    {
        init: function()
        {
            _this = this;

            _form.ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: Utilities.Form.onSuccess,
                error: Utilities.Form.onFailure
            });

            $('.felix-table').on('click', '.remove-agent', function() {
                let status_url = $(this).data('status-url');
                _this._get_user_deals_count_for_delete_modal(status_url);
            });

            $('#assigned-option-0').click(function() {
                $('#modal_agent_delete_confirm select').prop('disabled', true).trigger('chosen:updated');
            });

            $('#assigned-option-1').click(function() {
                $('#modal_agent_delete_confirm select').prop('disabled', false).trigger('chosen:updated');
            });
            $('#delete-user-form .confirm-delete-user').click(function() {
                _this._confirm_delete_user();
            });

            $('.user-profile').on('click', 'button.remove-agent', function() {
                let redirect_url = $(this).data('redirect-url');
                let status_url = $(this).data('status-url');

                _this._get_user_deals_count_for_delete_modal(status_url);
            });
        },

        _get_user_deals_count_for_delete_modal: function(status_url) {
            $.get(status_url, function(res) {
                $('[data-felix-modal="modal_agent_delete_confirm"]').click();

                let elem = $('#modal_agent_delete_confirm');

                elem.find('select option').removeClass('hide');
                elem.find('select option[value=' + res.agent_id + ']').addClass('hide');
                elem.find('select').trigger('chosen:updated');

                elem.find('#delete-user-form').attr('action', res.form_action);
                elem.find('#agent_id').val(res.agent_id);

                elem.find('.agent-name').html(res.agent_name);
                elem.find('.agent-motor-deals').html(res.motor_deals_assigned_to + res.motor_deals_producer);
            });
        },

        _confirm_delete_user: function() {
            let form = $('#delete-user-form');
            form.find('.preloader').removeClass('hide');
            form.find('button').prop('disabled', true);
            $.post(form.attr('action'), form.serialize(), function(res) {
                form.find('button').prop('disabled', false);
                form.find('.preloader').addClass('hide');

                if(res.success) {
                    Utilities.Notify.success('User deleted successfully', 'Success');
                    window.location.href = '/accounts/users/';
                } else {
                    Utilities.Notify.error(res.message, 'Error');
                }
            })
        }
    };

    jQuery(function() {
        __AGENTS.init();
    });
})();

if (typeof module === "object" && typeof module.exports === "object") {
    module.exports = __AGENTS;
}

/*** Felix Dynamic Data Table + Algolia ***/
;'Use Strict';
var __ALGOLIA;
var searchIndexSelectedFilters;
var stageFacetFilter = [];
var tagsFacetFilter = [];
var usersFacetFilter = [];

;(function() {
    var _filters_open_search_field = $('.open-search-field input[type="text"]');
    var _felix_table = $('table.felix-table');
    var _felix_table_filters = $('.table-filters');

    var _this = '';

    __ALGOLIA =
    {
        // Onload
        init: function()
        {
            _this = this;
            __current_timestamp = (typeof __current_timestamp !== "undefined")?__current_timestamp:new Date().getTime();
        },

        _get_search_params_for_algolia: function() {
            var current_page = _felix_table_filters.find('#id_page').val();
            var status = _felix_table_filters.find('#id_status').val();
            var stage = _felix_table_filters.find('#id_stage').val();
            var assigned_to = _felix_table_filters.find('#id_assigned_to').val();
            var producer = _felix_table_filters.find('#id_producer').val();
            var created_on_after = _felix_table_filters.find('#id_created_on_after').val();
            var created_on_before = _felix_table_filters.find('#id_created_on_before').val();
            var facets = [];
            var facet_filters = [];
            var facet_filters_second_set = [];
            var filters = '';
            var numeric_filters = [];
            var is_deals_table = _felix_table.data('name') == 'deals';
            var is_policies_table = _felix_table.data('name') == 'policies';
            var is_renewals_table = _felix_table.data('name') == 'renewals';
            var index_name = _felix_table.data('index');
            var sort_by = _felix_table_filters.find('#id_sort_by').val();

            if(sort_by) {
                index_name = index_name + '_' + sort_by;
            }

            if(created_on_after)
                numeric_filters.push(
                    'created_on >= ' + moment(created_on_after, 'DD-MM-YYYY').unix());

            if(created_on_before)
                numeric_filters.push(
                    'created_on <= ' + moment(created_on_before, 'DD-MM-YYYY').add(1, 'days').unix());

            if(current_page > 0) current_page = current_page - 1; else current_page = 0;

            if(is_deals_table) {
                facets = ['stage', 'producer_id', 'assigned_to_id', 'tags', 'premium'];

                searchIndexSelectedFilters = [];
                stageFacetFilter = [];
                tagsFacetFilter = [];
                usersFacetFilter = [];

                if(stage) {
                    facet_filters.push('stage:' + stage);
                } else {
                    facet_filters.push(['stage:new', 'stage:quote', 'stage:order', 'stage:housekeeping']);
                }

                if(assigned_to.length) {
                    assigned_to = (assigned_to == 'unassigned')?'0':assigned_to;
                    user_set = ['assigned_to_id:' + assigned_to, 'producer_id:' + assigned_to];
                    facet_filters.push(user_set);
                    facet_filters_second_set.push(user_set);
                }

                if(_felix_table_filters.find('#id_deleted').val())
                    status = 'deleted';
            }

            if(is_policies_table || is_renewals_table) {
                var expiry = _felix_table_filters.find('#id_expiry').val();
                var product = _felix_table_filters.find('#id_products').val();

                facets = ['product_id', 'status', 'premium', 'owner_id'];

                if(expiry == 'active')
                    numeric_filters.push('policy_expiry_date > ' + __current_timestamp);

                if(expiry == 'expired')
                    numeric_filters.push('policy_expiry_date <= ' + __current_timestamp);

                if(product)
                    facet_filters.push('product_id:' + product);

                if(is_renewals_table) {
                    let policy_expiry_from_date = $('#id_from_date').val();
                    let policy_expiry_to_date = $('#id_to_date').val();
                    let hide_renewal_deals = _felix_table_filters.find('#id_hide_renewal_deal').val();

                    if(!policy_expiry_from_date && !policy_expiry_to_date) {
                        policy_expiry_from_date = moment().format('X');
                        policy_expiry_to_date = moment().add(60, 'days').format('X');
                    }
                    if(hide_renewal_deals)
                        facet_filters.push("has_renewal_deal:false");

                    if(policy_expiry_from_date)
                        numeric_filters.push('policy_expiry_date > ' + policy_expiry_from_date);
                    if(policy_expiry_to_date)
                        numeric_filters.push('policy_expiry_date <= ' + policy_expiry_to_date);
                }
            }

            facet_filters.push('status:' + (status?status:'active'));
            facet_filters_second_set.push('status:' + (status?status:'active'));

            if ($("#customer_entity_type").val() == "mortgage"){
                    filters = 'entity:"mortgage"'
                }
            if ($("#customer_entity_type").val() == "motor"){
                    filters = 'NOT  entity:"Mortgage"'
                }

            return [{
                indexName: index_name,
                query: _filters_open_search_field.val(),
                params: {
                    page: current_page,
                    hitsPerPage: 30,
                    facets: facets,
                    filters: filters,
                    numericFilters: numeric_filters,
                    facetFilters: facet_filters
                }
            }, {
                indexName: index_name,
                query: _filters_open_search_field.val(),
                params: {
                    page: current_page,
                    attributesToRetrieve: [],
                    attributesToHighlight: [],
                    attributesToSnippet: [],
                    facets: facets,
                    numericFilters: numeric_filters,
                    facetFilters: facet_filters_second_set
                }
            }];
        },

        _get_search_from_algolia: function(queries) {
            if(!_felix_table.length) return;

            if(!queries || queries === undefined) queries = _this._get_search_params_for_algolia();

            var is_deals_table = _felix_table.data('name') == 'deals';
            var is_policies_table = _felix_table.data('name') == 'policies';

            var api_key = app_config.ALGOLIA_SEARCH_API_KEY;

            if(_felix_table.data('securedapikey'))
                api_key = _felix_table.data('securedapikey');

            var client = algoliasearch(app_config.ALGOLIA_APP_ID, api_key);

            _felix_table.addClass('opacity');

            client.search(queries).then((content) => {
                _felix_table.removeClass('opacity');

                var source   = $('#row-template').html();
                var template = Handlebars.compile(source);
                var records = content.results[0];

                $('.table_counts').html(records.nbHits + ' records found');

                $('.felix-table-body').html(template({'records': records.hits}));

                Utilities.General.generatePagination((records.page + 1), records.nbPages);

                // For deals list only
                if(is_deals_table) _this._fill_motor_deals_list_content(content);
                // For policies list only
                if(is_policies_table) _this._fill_policies_list_content(content);
            });
        },

        _fill_policies_list_content: function(content) {
            var first_set = content.results[0];
            var second_set = content.results[1];

            if(first_set.nbHits) {
                $('.policies-total-amount').removeClass('hide').find('span').html(
                    '<span>' + accounting.format(first_set.facets_stats.premium.sum) + ' ('+ first_set.nbHits +' Policies)</span>'
                );
            } else {
                $('.policies-total-amount').addClass('hide');
            }
        },

        _fill_motor_deals_list_content: function(content) {
            var first_set = content.results[0];
            var second_set = content.results[1];

            if(first_set.nbHits) {
                $('.deals-total-amount').removeClass('hide').find('span').html(
                    '<span>' + accounting.format(first_set.facets_stats.premium.sum) + ' ('+ first_set.nbHits +' Deals)</span>'
                );
            } else {
                $('.deals-total-amount').addClass('hide');
            }

            _felix_table_filters.find('.stages button span').html('0');
            _felix_table_filters.find('.stages button').prop('disabled', true);

            var all_open_count = 0;

            if('facets' in second_set) {
                $.each(second_set.facets.stage, function(k, v) {
                    _felix_table_filters.find('.stages button[data-type=' + k + '] span').html(v);
                    _felix_table_filters.find('.stages button[data-type=' + k + ']').prop('disabled', !v);
                });

                $.each(second_set.facets.stage, function(k, v) {
                    if(k == 'won' || k=='lost') return;

                    all_open_count += v;
                });
            }

            _felix_table_filters.find('.stages button:first-child span').html(all_open_count);
            _felix_table_filters.find('.stages button:first-child').prop('disabled', !second_set.nbHits);

            __FELIX__._loadLibs();

        }
    };

    jQuery(function() {
        __ALGOLIA.init();
    });
})();

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

/*
    Charts JS
*/
;
'Use Strict';

let __FELIX_CHARTS;
;(function() {
    let _this = '';
    let chart_class = '.felix-chart';

    __FELIX_CHARTS =
    {
        init: function()
        {
            _this = this;

            _this.loadCharts();
        },

        loadCharts: function() {
            $.each($(chart_class), function() {
                let elem = this;
                let labels = [];
                let data = [];
                let params = elem.dataset.params;
                let endpoint = elem.dataset.endpoint;
                let options = _this.getChartOptions(elem);

                if(params)
                    endpoint = endpoint + '?' + params;

                $.get(endpoint, function(response) {
                    $.each(response, function() {
                        labels.push(this[0]);
                        data.push(this[1]);
                    });

                    let dataset = {
                        label: elem.dataset.label,
                        backgroundColor: 'rgba(0, 123, 255, 0.5)',
                        borderColor: 'rgba(4, 96, 195, 0.5)',
                        data: data,
                        lineTension: 0
                    };

                    if(elem.dataset.fill == 'false') {
                        dataset['fill'] = false;
                    }

                    let chart = new Chart(elem.getContext('2d'), {
                        type: elem.dataset.type,
                        options: options,
                        data: {
                            labels: labels,
                            datasets: [dataset]
                        }
                    });

                    $(elem).siblings('.preloader').addClass('hide');
                });
            });
        },
        getChartOptions: function(elem) {
            let options = {
                legend: {
                    display: false
                },
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero:true,
                            userCallback: function(value, index, values) {
                                return accounting.format(value.toString());
                            }
                        }
                    }]
                }
            };

            if('tooltip_prefix' in elem.dataset && elem.dataset.tooltip_prefix) {
                options['tooltips'] = {
                    callbacks: {
                        label: function(tooltipItem, data) {
                            return accounting.format(data.datasets[0].data[tooltipItem.index]) + elem.dataset.tooltip_prefix;
                        }
                    }
                };
            } else {
                options['tooltips'] = {
                    callbacks: {
                        label: function(tooltipItem, data) {
                            return accounting.format(data.datasets[0].data[tooltipItem.index]);
                        }
                    }
                };
            }

            return options;
        }
    };

    jQuery(function() {
        __FELIX_CHARTS.init();
    });
})();

/* Customers */

var __CUSTOMERS;
;(function() {
    var _this   = '';

    var __form = $("#customer_form");
    var __merge_form = $("#customer-merge-form");
    var __modal_merge_form = $("#modal_merge_customer");
    var __felix_table = $('table.felix-table');
    var __whatsapp_base_url = 'https://wa.me/';

    __CUSTOMERS = {
        init: function() {
            _this = this;

            _this.mergeCustomers();
            _this._loadHistory();

            __form.ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: Utilities.Form.onSuccess,
                error: Utilities.Form.onFailure
            });

            $('.view-all-deals').click(function() {
                $('.nav-link[href="#tab_deals"]').click();
            });
            $('.view-all-policies').click(function() {
                $('.nav-link[href="#tab_policies"]').click();
            });
        },

        _loadHistory: function() {
            if(!$('.customer-detail-container').length || !$('#tab_history').length) return;

            $.get(DjangoUrls['customers:history']($('.customer-detail-container').data('id')), function(response) {
                $('#tab_history').html(response);
            });
        },

        mergeCustomers: function() {
            // Merge Customers
            $('[data-felix-modal=modal_merge_customer]').click(function() {
                var selected_ids = $('.select-record:checked').map(function(){return this.value;}).get();
                if(selected_ids.length < 2) {
                    alert('please select 2 records in order to merge');
                    return false;
                }
                __modal_merge_form.find('.form-container').html('<div class="p-20 p-t-30">loading...</div>');
                $.get(DjangoUrls['customers:merge-customers'](selected_ids[0], selected_ids[1]), function(response) {
                    __modal_merge_form.find('.form-container').html(response);
                    __FELIX__._loadLibs();

                    $('#customer-merge-form').ajaxForm({
                        beforeSubmit: Utilities.Form.beforeSubmit,
                        success: Utilities.Form.onSuccess,
                        error: Utilities.Form.onFailure
                    });
                });
            });

            __modal_merge_form.on('click', '.merge-customer-column', function() {
                var elems = $(this).parent().siblings('.customer-info');
                $.each(elems, function() {
                    $(this).click();
                });
            });

            __modal_merge_form.on('click', '.customer-info', function() {
                _this.updateMergeField($(this));
            });
            __modal_merge_form.on('change', '#merge-customers-disclaimer', function() {
                __modal_merge_form.find('.btn-merge-customers').prop('disabled', !$(this).is(':checked'));
                __modal_merge_form.find('.disclaimer').addRemoveClass(!$(this).is(':checked'), 'error');
            });
            __modal_merge_form.on('click', '.scroll-to-disclaimer', function() {
                __modal_merge_form.find('.disclaimer').addRemoveClass(
                    __modal_merge_form.find('.btn-merge-customers').is(':disabled'), 'error');
            });
        },
        updateMergeField: function(elem) {
            if(__modal_merge_form.find(elem).length) {
                var key = __modal_merge_form.find(elem).find('.value').data('key');
                var val = __modal_merge_form.find(elem).find('.value').data('value');

                var field = __modal_merge_form.find('#' + key);

                if(field.val() == val) return;

                field.val(val);
                field.trigger('chosen:updated');

                var highlighted_elem = field.next().hasClass('chosen-container')?field.next().find('.chosen-single'):field;
                Utilities.General.AddHighlighter(highlighted_elem, 'highlight-success');
            }
        },
        _cleanNumber(number) {
            return parseInt(number.match(/\d+/)[0]);
        },
        _checkWhatsAppIcon: function(response) {
            var whatsapp_icon = $('.whatsapp-customer-icon');

            if(whatsapp_icon.length) {
                whatsapp_icon.prop('href', response.data.value?__whatsapp_base_url + this._cleanNumber(response.data.value):'');
            }
        },
        _triggerWhatsAppClick: function(elem) {
            if(!elem.href || elem.href == '#' || elem.href == window.location.href) {
                alert('Please add a phone number to start a WhatsApp chat.');
                return false;
            }

            return true;
        }
    };

    jQuery(function() {
        if($('body.customers').length)
            __CUSTOMERS.init();
    });

})();

/* DEALS */
;
'Use Strict';

var __DEALS;
;(function() {

    var _this   = '';
    var _table  = $('#deals-table');
    var _form   = $('#deal_form');
    var _filter_form   = $('#deals-search');

    var _car_year = $('#id_car_year');
    var _car_make = $('#id_car_make');
    var _car_trim = $('#id_car_trim');

    var _customer = $('#id_customer');
    var _assign_deal_button = $('.assign-deal');
    var _clear_product_selection = $('.clear-product-selection');
    var _show_payments = $('.show-payments');
    var _felix_table_filters = $('.table-filters');
    var _felix_table_quick_filters = $('.quick-filters');

    var _selected_car_trim = _car_trim.data('value');

    var _mmt_endpoint = DjangoUrls['motorinsurance:motor-tree']();

    var _deal_id = $('.deal-container').data('id');
    var _deal_status = $('.deal-container').data('status');
    var _deal_stages_breadcrumb = $('.deal-stages-breadcrumb');
    var _deal_stage_container = $('.deal-processes');
    var _deal_open_or_lost_btn = $('.open-lost-deal');

    var _document_parser_timeout;
    var _document_parsed_data_attempts = 0;
    var _document_parsed_data_max_attempts = 10;

    var _number_of_passengers_set = false;
    var _email_address_set = false;

    __DEALS =
    {
        init: function()
        {
            _this = this;

            _this._loadMotorProducts();
            _this._initCarYearChange();
            _this._initCarMakeChange();
            _this._initCarTrimChange();
            _this._initCustomCarNameChange();
            _this._triggerAlgoDrivePricing();
            _this._dealStatusInline();
            _this._addNewDealForm();
            _this._dealStagesToggle();
            _this._dealProcessTriggers();
            _this._openLostDealTriggers();
            _this._triggerCustomEmailForm();
            _this._loadHistory();
            _this._updatePolicyTerm();

            if($(_car_year).val())
                _car_make.change();

            if(_customer.length) {
                _this._loadCustomers();

                _customer.change(function() {
                    _this._getCustomerProfile();
                });
            }

            _show_payments.click(function() {
                _this._scrollAndOpenPaymentsTab();
            });

            $("#search-clear").on("click", function () {
                window.location.href = $("#deals-search").data("reset-url");
            });

            var filter_count = Utilities.Form.addFilterCount(_filter_form);
            if(filter_count) {
                $('.filter-count').html(filter_count).removeClass('hide');
            }
            _deal_stage_container.on('click', '.policy-document-parser-dismiss', function() {
                clearTimeout(_document_parser_timeout);
                _document_parsed_data_max_attempts = 0;
                $('.policy_form .loader').addClass('hide');
            });

            $('body.motor-deals').on('click', '.duplicate-deal', function() {
                _this._duplicateDeal();
            });

            _deal_stage_container.on('change', '#id_policy_document', function() {
                $.get(DjangoUrls['motorinsurance:deal-can-scan-policy-document'](_deal_id), function(response) {
                    $('#policy_document_no_scan').addRemoveClass(response.success, 'hide');
                    $('#trigger_policy_document_parser').addRemoveClass(!response.success, 'hide');

                    $('#policy_document_no_scan span').prop('title', response.allowed_insurers);
                });
            });

            _deal_stage_container.on('click', '#trigger_policy_document_parser', function() {
                if($('#id_policy_document').val()) {
                    $('.policy_form .loader').removeClass('hide');
                    _document_parsed_data_max_attempts = 10;

                    var temp_field = $('#id_policy_document').clone();
                    temp_field.appendTo('#temp_document_parser_form');

                    $("#temp_document_parser_form").ajaxForm({
                        beforeSubmit: Utilities.Form.beforeSubmit,
                        success: function(response, status, xhr, form) {
                            if(response.success)
                                _this._fill_policy_form_with_parsed_data(response.url);
                            else
                                $('.policy_form .loader').addClass('hide');
                        },
                        error: function(response, status, xhr, form) {

                        }
                    });

                    $("#temp_document_parser_form").submit();
                } else {
                    Utilities.Notify.error('Please choose a file to upload first.');
                    $('#temp_document_parser_form input[file=type]').remove();
                }
            });

            if(_clear_product_selection.length) {
                _clear_product_selection.click(function() {
                    var url = $(this).data('url');
                    if(window.confirm('Are you sure you want to clear the selected product?')) {
                        $.get(url, function(response) {
                            if(response.success) {
                                Utilities.Notify.success('Product selection removed successfully', 'Success');
                                window.location.href = window.location.href;
                            } else {
                                Utilities.Notify.error(response.message, 'Error');
                            }
                        });
                    }
                });
            }

            // Load deal stage on load
            if(_deal_stage_container.length)
                _this._loadDealStage();

            _deal_stage_container.on('change', '.housekeeping-checkboxes', function() {
                var disabled = false;
                
                $('.housekeeping-checkboxes').each(function() {
                    if(!$(this).is(':checked')) {
                        disabled = true;
                        return false;
                    }
                });

                $('.btn-housekeeping').attr('disabled', disabled);
            });
            _deal_stage_container.on('click', '.btn-housekeeping', function() {
                $(this).addClass('show-loader');
                $.get(DjangoUrls['motorinsurance:deal-mark-closed'](_deal_id, 'won'), function(response) {
                    if(response.success) {
                        _this._loadDealStage();
                        $.get(DjangoUrls[`${__app_name}:get-deal-json`](_deal_id), function(r) {
                            __AMPLITUDE.logEvent(__AMPLITUDE.event('motor_deal_won'), {
                                'deal_id': _deal_id,
                                'deal_type': r.deal.deal_type,
                                'deal_created_date': r.deal.created_on,

                                'vehicle_model_year': r.deal.vehicle_year,
                                'vehicle make': r.deal.vehicle_make,
                                'vehicle_model': r.deal.vehicle_model,
                                'vehicle_body_type': r.deal.vehicle_body_type,
                                'vehicle_sum_insured': r.order.sum_insured,

                                'client_nationality': r.customer.nationality,
                                'client_gender': r.customer.gender,
                                'client_age': r.customer.age,
                            });
                        });

                    } else {
                        Utilities.Notify.error(response.error, 'Error');
                    }

                    $('.show-loader').removeClass('show-loader');
                });
            });

            $('.vehicle-editable .car-title').click(function(event) {
                $('.vehicle-editable-container').show();
                $(this).hide();

                $('#id_car_year').change();

                if($('.vehicle-editable #id_custom_car_name').val().length) {
                    $('#id_car_trim').prop('disabled', true);
                }

                __FELIX__.initSearchableSelect();

                if($('#id_car_trim').data('value')) {
                    setTimeout(function() {
                        _this._resetAlgoDrivenElements(false);
                    }, 1000);
                }
            });

            $('.vehicle-editable .vehicle-cancel').click(function(event) {
                $('.vehicle-editable-container').slideUp(100);
                $('.vehicle-editable a').show(100);

                __FELIX__.initSearchableSelect();
            });

            $('.vehicle-editable .vehicle-submit').click(function(event) {
                var car_year = $('#id_car_year').val();
                var car_make = $('#id_car_make').val();
                var car_trim = $('#id_car_trim').val();
                var custom_trim = $('#id_custom_car_name').val();

                $('.vehicle-editable .chosen-container').removeClass('error');

                if(!car_year) {
                    $('#id_car_year').next('.chosen-container').addClass('error');
                    return;
                }
                if(!car_make) {
                    $('#id_car_make').next('.chosen-container').addClass('error');
                    return;
                }

                if(!car_trim && !custom_trim) {
                    $('#id_car_trim').next('.chosen-container').addClass('error');
                    return;
                }

                if($('#id_car_trim').prop('disabled')) car_trim = '';

                $('.vehicle-editable .editableform-loading').removeClass('hide');
                $('.vehicle-editable .car-title').addClass('hide');
                $('.vehicle-editable-container').slideUp(100);

                $.post(DjangoUrls['motorinsurance:deal-update-mmt'](_deal_id), {
                    'pk': _deal_id,
                    'car_year': car_year,
                    'car_make': car_make,
                    'car_trim': car_trim,
                    'custom_car_name': $('#id_custom_car_name').val()
                },
                function(response) {
                    $('.vehicle-editable .car-title').show(100);

                    if(response.success) {
                        $('.vehicle-editable .car-title, .deal-title .title').html(response.car);

                        $('#id_car_make').attr('data-value', $('#id_car_make').val());
                        $('#id_car_trim').attr('data-value', $('#id_car_trim').val());

                        $('.vehicle-body-type').addClass('hide');
                        $('.vehicle-cylinders').addClass('hide');
                        $('.vehicle-seats').addClass('hide');

                        if('extra_data' in response && Object.keys(response.extra_data).length) {
                            if('body' in response.extra_data && response.extra_data['body']) {
                                $('.vehicle-body-type').removeClass('hide');
                                $('.vehicle-body-type span').html(response.extra_data['body']);
                            }

                            if('cylinders' in response.extra_data && response.extra_data['cylinders']) {
                                $('.vehicle-cylinders').removeClass('hide');
                                $('.vehicle-cylinders span').html(response.extra_data['cylinders']);
                            }

                            if('seats' in response.extra_data && response.extra_data['seats']) {
                                $('.vehicle-seats').removeClass('hide');
                                $('.vehicle-seats span').html(response.extra_data['seats']);

                                $('[data-name=number_of_passengers].number-editable').html(response['no_of_passengers']);
                            }
                        }
                    }

                    $('.vehicle-editable .editableform-loading').addClass('hide');
                    $('.vehicle-editable .car-title').removeClass('hide');
                });
            });

            $("#deal_email_field_form").ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: function(response, status, xhr, form) {
                    form.find('button[type=submit]').removeClass('loader');

                    if(response.success) {
                       $('.save-and-send:visible').click();
                       $('[data-modal-close]:visible').click();
                       $('a.text-editable[data-name=email]').editable('destroy');
                       $('a.text-editable[data-name=email]').html(response.data.value);

                       __XEDITABLE.init();
                    }
                },
                error: Utilities.Form.onFailure
            });

            $("#deal_num_passengers_field").ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: function(response, status, xhr, form) {
                    form.find('button[type=submit]').removeClass('loader');

                    if(response.success) {
                       $('.show-insurer-modal:visible').click();
                       $('[data-modal-close]:visible').click();
                       $('a.editable[data-name=number_of_passengers]').html(response.data.value);
                       $('a.editable[data-name=number_of_passengers]').attr('data-value', response.data.value);

                       __XEDITABLE.init();

                       _number_of_passengers_set = true;
                    }
                },
                error: Utilities.Form.onFailure
            });

            // Email modal Template DD change event
            $('.deal-container').on('change', '#custom_email_type', function() {
                _this._triggerCustomEmailModal($(this).val());
            });
        },

        _loadMotorProducts: function() {
            if(_deal_id) {
                $.get(DjangoUrls['motorinsurance:deal-all-products'](_deal_id), function(res) {
                    window.products_data = res
                });
            }
        },

        _resetAlgoDrivenElements: function(reset) {
            if(typeof reset == "undefined") reset = true;
            if($('.check-vehicle-value').length) {
                if(!$('.check-vehicle-value').data('allowed')) return;

                $('.check-vehicle-value').prop('disabled', reset).removeClass('hide');
                $('.valuation-guide-display').addClass('hide');
            }
        },

        _triggerAlgoDrivePricing: function() {
            $('.check-vehicle-value').click(function() {
                $(this).addClass('hide');
                $('.valuation-guide-loader').removeClass('hide');
                $('.valuation-guide-display').html();

                var event_type = _deal_id?'deal card':'new deal modal';
                var value = _deal_id?$('#id_car_trim').data('value'):$('#id_car_trim').val();

                if($('#id_car_trim').val())
                    value = $('#id_car_trim').val();

                if(value) {
                    $.get(DjangoUrls['motorinsurance:get-car-value'](), {
                        'trim': value,
                    }, function(response) {
                        $('.valuation-guide-loader').addClass('hide');

                        if(response.success) {
                            var msg = 'Dhs ' + response.low_retail + ' to Dhs ' + response.high_retail;
                            __AMPLITUDE.logEvent(
                                __AMPLITUDE.event('vehicle_valuation_checked'), {'source': event_type}
                            );
                            $('.valuation-guide-display').removeClass('hide').html(msg);
                        }
                        else {
                            var msg = response.error;
                            $('.valuation-guide-display').removeClass('hide').addClass('error').html(msg);
                        }
                    });
                } else {
                    alert('No Model/Trim selected.');
                }
            });
        },

        _loadStageWarning: function() {
            setTimeout(function() {
                $('.stage-warning').click(function() {
                    alertify
                        .okBtn("Dismiss")
                        .cancelBtn("Cancel")
                        .confirm("Some deal information has changed since you last saved your quotes. This might affect the premiums quoted. Consider reviewing  your quotes before proceeding.", function (ev) {
                            $.get(
                                DjangoUrls['motorinsurance:deal-remove-warning'](_deal_id),
                                function(response) {
                                    if(response.success)
                                       $('.stage-warning').addClass('hide'); 
                            });
                        });
                });
            }, 2000);
        },

        _loadHistory: function() {
            if(!_deal_id || !$('#tab_history').length) return;

            $.get(DjangoUrls['motorinsurance:deal-history'](_deal_id), function(response) {
                $('#tab_history').html(response);
            });
        },

        _updatePolicyTerm: function() {
            _deal_stage_container.on('change', '#policy_form #id_policy_term', function() {
                let option = $(this).val();
                let start_date_field = $('#policy_form #id_policy_start_date');
                let expiry_date_field = $('#policy_form #id_policy_expiry_date');
                let start_date = start_date_field.val();

                if(!start_date) {
                    alert('Please provide policy start date first.');
                    start_date_field.focus();

                    return false;
                }

                if (option == '0') {
                    expiry_date_field.focus();
                } else if (option == '12' || option == '13') {
                    let date = moment(start_date, 'DD-MM-YYYY').add(parseInt(option), 'M');
                    date = date.subtract(1, 'd');
                    expiry_date_field.val(date.format('DD-MM-YYYY'));
                }
            });
            function set_term_field() {
                let term_field = $('#policy_form #id_policy_term');
                let start_date = $('#policy_form #id_policy_start_date').val();
                let expiry_date = $('#policy_form #id_policy_expiry_date').val();

                if(start_date && expiry_date) {
                    let sd = start_date.split('-');
                    let ed = expiry_date.split('-');

                    let diff = moment(
                        [parseInt(ed[2]), parseInt(ed[1]), parseInt(ed[0])]).diff(moment([parseInt(sd[2]), parseInt(sd[1]), parseInt(sd[0])]),
                        'months', true);

                    if(diff == 12 || diff == 13)
                        term_field.val(diff).trigger('chosen:updated');
                    else
                        term_field.val(0).trigger('chosen:updated');
                }
            }

            _deal_stage_container.on('change', '#policy_form #id_policy_start_date, #policy_form #id_policy_expiry_date', function() {
                set_term_field();
            });
        },

        _fill_policy_form_with_parsed_data: function(url) {
            if(url) {
                $.get(url, function(response) {
                    if(response && response.success) {
                        $('.policy_form .loader').addClass('hide');
                        $('#trigger_policy_document_parser').addClass('hide');

                        var policy_number = response.policy_number;
                        var invoice_numnber = response.invoice_numnber;
                        var policy_start_date = response.policy_start_date;
                        var policy_end_date = response.policy_end_date;

                        $.get(DjangoUrls[`${__app_name}:get-deal-json`](_deal_id), function(r) {
                            __AMPLITUDE.logEvent(
                                __AMPLITUDE.event('policy_text_extracted'),
                                {
                                    'deal_id': _deal_id,
                                    'insurer': r.order.product_insurer,
                                    'policy_number': policy_number
                                }
                            );
                        });

                        if(response.policy_number) {
                            $('.policy_form #id_reference_number').val(response.policy_number);
                            Utilities.General.AddHighlighter($('.policy_form #id_reference_number'), 'highlight-success');
                        } else {
                            Utilities.Notify.error('No policy number found. Please ensure you have uploaded the correct policy document.');
                            return;
                        }

                        if(response.policy_start_date) {
                            $('.policy_form #id_policy_start_date').val(response.policy_start_date);
                            Utilities.General.AddHighlighter($('.policy_form #id_policy_start_date'), 'highlight-success');
                        }

                        if(response.policy_end_date) {
                            $('.policy_form #id_policy_expiry_date').val(response.policy_end_date);
                            Utilities.General.AddHighlighter($('.policy_form #id_policy_expiry_date'), 'highlight-success');
                        }

                        if(response.invoice_number) {
                            $('.policy_form #id_invoice_number').val(response.invoice_number);
                            Utilities.General.AddHighlighter($('.policy_form #id_invoice_number'), 'highlight-success');
                        }
                    } else {
                        if(_document_parsed_data_attempts <= _document_parsed_data_max_attempts) {
                            _document_parsed_data_attempts += 1;
                            _document_parser_timeout = setTimeout(function() {
                                _this._fill_policy_form_with_parsed_data(url);
                            }, 5000);
                        } else {
                            $('.policy_form .loader').addClass('hide');
                            Utilities.Notify.error('Unable to extract data from this policy document. Please enter data manually');
                        }
                    }
                });
            }
        },

        _resetDealForm: function() {
            Utilities.Form.removeErrors('#deal_form');
            $('#deal_form .autocomplete-container').removeClass('new');
            $('#deal_form #id_customer').val('');
            $('#deal_form input[type=text]').val('');
            $('#deal_form #id_vehicle_insured_value, #deal_form #id_number_of_passengers').val('0').trigger('change');
            $('#deal_form select').val('');
            $('#deal_form #id_car_make, #deal_form #id_car_trim').find('option').remove();
            $('#deal_form select').trigger('chosen:updated');
            $('#deal_form #id_number_of_passengers').val('');
            $('#deal_form .check-vehicle-value').removeClass('hide');
        },

        _setCustomerInDealForm: function(customer_id, customer_name) {
            $('#deal_form #id_customer').val(customer_id);
            $('#deal_form #id_customer_name').val(customer_name);
        },

        _triggerCustomEmailForm: function() {
            $('#modal_send_custom_email .send-email').click(function(event) {
                var form = $('#custom_email_form');
                var email_type = form.find('#email_type').val();

                // Validations
                form.find('.error').remove();
                if(form.find('#id_email').val() == '') {
                    form.find('#id_email').after('<span class="error">This field is required</span>');
                    return;
                }
                if(form.find('#id_subject').val() == '') {
                    form.find('#id_subject').after('<span class="error">This field is required</span>');
                    return;
                }

                form.find('button.send-email').addClass('loader');

                $.post(
                    DjangoUrls['motorinsurance:deal-email-content'](_deal_id, email_type),
                    $('#custom_email_form').serialize(),
                    function(response) {
                        form.find('button.send-email').removeClass('loader');
                        if(response.success) {
                            Utilities.Notify.success('Email sent successfully.', 'Success');
                            $('#modal_send_custom_email').hide();

                            if(response.email_type == 'new_quote' || response.email_type == 'quote_updated') {
                                __AMPLITUDE.logEvent(
                                    __AMPLITUDE.event('motor_quote_email_sent'), {
                                        'deal_id': _deal_id
                                    }
                                );
                            }

                            _this._loadHistory();

                        } else {
                            Utilities.Notify.error('Please check all the required fields and try again.', 'Error');
                            Utilities.Form.addErrors($('#custom_email_form'), response.errors);
                        }
                    }
                );
            });
        },

        _triggerCustomEmailModal: function(email_type) {
            var url = DjangoUrls['motorinsurance:deal-email-content'](_deal_id, email_type);
            $('#custom_email_form').css({'opacity': '.7'});

            $.get(url, function(response) {
                var form = $('#custom_email_form');
                $('#custom_email_form').css({'opacity': '1'});
                $('[data-felix-modal="modal_send_custom_email"]').click();

                form.find('#email_type').val(email_type);
                form.find('#id_email').val(response.to);
                form.find('#id_from_email').html(response.from);
                form.find('#id_reply_to').html(response.reply_to);
                form.find('#id_cc_emails').val(response.cc_emails);
                form.find('#id_bcc_emails').val(response.bcc_emails);
                form.find('#id_subject').val(response.subject);
                form.find('#id_content').trumbowyg($.trumbowyg.config);
                form.find('#id_content').trumbowyg('html', response.content);

                form.find('#custom_email_type option').remove();

                $.each(response.allowed_templates, function(k, v) {
                    var selected = k==response.email_type?'selected':'';
                    form.find('#custom_email_type').append(
                        `<option ${selected} value="${k}">${v}</option>`
                    );
                });
                $('#custom_email_type').trigger('chosen:updated');

                form.find('.email_type_display').html(
                    response.allowed_templates[response.email_type]
                );

                if('sms_content' in response && response.sms_content) {

                    form.find('.show-when-sms').removeClass('hide');
                    form.find('#id_sms_content').val(response.sms_content);

                    form.find('#id_send_sms').change(function() {
                        form.find('.sms_container').addRemoveClass(!$(this).is(':checked'), 'hide');
                    });

                    $('textarea[maxlength]').maxlength({
                        alwaysShow: true,
                        warningClass: "badge badge-info",
                        limitReachedClass: "badge badge-warning"
                    });
                } else {
                    form.find('.show-when-sms').addClass('hide');
                    form.find('#id_sms_content').val('');
                    form.find('#send_sms').prop('checked', false);
                }

                if('whatsapp_msg_content' in response && response.whatsapp_msg_content) {

                    form.find('.show-when-wa-msg').removeClass('hide');
                    form.find('#id_wa_msg_content').val(response.whatsapp_msg_content);

                    form.find('#id_send_sms').change(function() {
                        form.find('.sms_container').addRemoveClass(!$(this).is(':checked'), 'hide');
                    });

                    $('textarea[maxlength]').maxlength({
                        alwaysShow: true,
                        warningClass: "badge badge-info",
                        limitReachedClass: "badge badge-warning"
                    });
                } else {
                    form.find('.show-when-wa-msg').addClass('hide');
                    form.find('#id_wa_msg_content').val('');
                    form.find('#id_send_wa_msg').prop('checked', false);
                }

                if('attachments' in response && response.attachments.length) {
                    form.find('.attachments').removeClass('hide');
                    form.find('.attachments ul li').remove();
                    $.each(response.attachments, function() {
                        form.find('.attachments ul').append(
                            '<li><a href="' + this.url + '" target="_blank">' + this.name + '</a></li>'
                        );
                    });
                } else {
                    form.find('.attachments').addClass('hide');
                }
            });
        },

        _openLostDealTriggers: function() {
            _deal_open_or_lost_btn.click(function() {
                if(_deal_open_or_lost_btn.hasClass('re-open')) {
                    if(window.confirm('Are you sure you want to Re-Open this deal?')) {
                        $.get(DjangoUrls['motorinsurance:deal-reopen'](_deal_id), function(response) {
                            if(response.success) {
                                _this._loadDealStage();
                            }
                        });
                    }
                } else {
                    if(window.confirm('Are you sure you want to mark this deal as a "LOST" deal?')) {
                        $.get(DjangoUrls['motorinsurance:deal-mark-as-lost'](_deal_id), function(response) {
                            if(response.success) {
                                _this._loadDealStage();
                            }
                        });
                    }
                }
            });
        },

        _updateTags: function(tags) {
            // Updating Tags
            if(tags) {
                var tags_html = '';
                $.each(tags, function() {
                    tags_html += '<span class="m-t-15 m-r-4 badge badge-default badge-font-light badge-'+Utilities.General.slugify(this)+'">'+this+'</span>';
                });

                $('.deal-statuses').html(tags_html);
            }
        },

        _refreshStagesBar: function(stage) {
            var status = $('.deal-container').data('status');
            var stages = ['new', 'quote', 'order', 'housekeeping', 'closed'];

            $.get(DjangoUrls['motorinsurance:deal-current-stage'](_deal_id), function(response) {
                if(response)
                   status =  response.stage;

                if(stage === undefined || !stage)
                    stage = status;

                _this._updateTags(response.tags);

                _deal_stages_breadcrumb.find('li').removeClass('current completed lost won');

                // Checking for lost/won deal
                if(status == 'lost' || status == 'won' ) {
                    _deal_stages_breadcrumb.find('li').addClass(status);

                    _deal_open_or_lost_btn
                        .html('Reopen')
                        .removeClass('mark-as-lost btn-outline-danger hide')
                        .addClass('re-open btn-outline-dark');

                    return;
                } else {
                    _deal_open_or_lost_btn
                        .html('Mark as Lost')
                        .addClass('mark-as-lost btn-outline-danger')
                        .removeClass('re-open btn-outline-dark hide');
                }
                _deal_stages_breadcrumb.find('li[data-id='+ stage +']').addClass('selected');
                $.each(stages, function() {
                    if(this == status) {
                        _deal_stages_breadcrumb.find('li[data-id='+ this +']').addClass('current');
                        return false;
                    } else {
                        _deal_stages_breadcrumb.find('li[data-id='+ this +']').addClass('completed');
                    }
                });

                _this._loadHistory();
            });
        },

        _loadDealStage: function(stage) {
            if(_deal_id) {

                if(stage === undefined)
                    stage = '';

                $.get(DjangoUrls['motorinsurance:get-deal-stage'](_deal_id) + '?stage=' + stage, function(response) {
                    _deal_stage_container.html(response);

                    __FELIX__._loadLibs();
                    __DEALFORMS._initForms();
                });
                _this._refreshStagesBar(stage);
                _this._loadStageWarning();
            }
        },

        _getCustomerFromQueryParams: function() {
            var params = Utilities.General.getUrlVars();

            if('customer_id' in params && params['customer_id']) {
                return params['customer_id'];
            }

            return false;
        },

        _scrollAndOpenPaymentsTab: function() {
            var elem = $('a[href="#tab_payments"]');
            
            $([document.documentElement, document.body]).animate({
                scrollTop: elem.offset().top
            }, 100);
            elem.click();
        },

        _dealStatusInline: function() {
            $('.deal-inline-update-field').editable({
                emptytext: $(this).data('emptytext')?$(this).data('emptytext'):'-',
                mode: 'inline',
                inputclass: 'form-control-sm',
                url: $(this).data('url'),
                emptyclass: 'empty',
                source: $(this).data('options')?$.parseJSON($(this).data('options')):[],
                display: function (value, sourceData) {
                    var elem = $.grep(sourceData, function (o) {
                        return o.value == value;
                    });

                    if (elem.length) {
                        $(this).text(elem[0].text);
                    } else {
                        $(this).empty();
                    }
                },
                error: function(response) {
                    return response.responseJSON.message;
                },
                success: function(response, newValue) {
                    if(response.success) {
                        Utilities.Notify.success(response.message, 'Success');
                    } else {
                        Utilities.Notify.error(response.message, 'Error');
                        return false;
                    }
                }
            }).on('shown', function(e, editable){
                editable.input.$input.chosen();
            });
        },

        _initCarYearChange: function() {
            $(_car_year).bind('change',function(){
                //reset make and model
                var selected_year = $(this).val();

                var selected_car_make = false;

                if(!selected_year) return;

                _this._resetAlgoDrivenElements();

                if(document.getElementById('id_car_make').dataset.value)
                    selected_car_make = document.getElementById('id_car_make').dataset.value;

                Utilities.Form.updateSearchableSelectOptions(_car_make, [], 'Make');
                Utilities.Form.updateSearchableSelectOptions(_car_trim, [], 'Model');

                _this._resetAlgoDrivenElements();

                $.get(_mmt_endpoint + '?year=' + selected_year, function(response) {
                    if(response && 'makes' in response) {
                        Utilities.Form.updateSearchableSelectOptions($('#id_car_make'), response.makes, 'Make', selected_car_make);

                        if(selected_car_make) {
                            $('#id_car_make').trigger('chosen:updated');
                            $('#id_car_make').change();
                        }
                    }
                });

            });
        },

        _initCarMakeChange: function() {
            $('#id_car_make').bind('change',function(){

                var selected_year = $(_car_year).val();
                var selected_make = $(this).val();
                var selected_trim = false;

                if(document.getElementById('id_car_trim').dataset.value)
                    selected_trim = document.getElementById('id_car_trim').dataset.value;

                Utilities.Form.updateSearchableSelectOptions($('#id_car_trim'), [], 'Model');

                if(!selected_make) return;

                _this._resetAlgoDrivenElements();

                $.get(_mmt_endpoint + '?year=' + selected_year + '&make=' + selected_make, function(response) {
                    if(response && 'models' in response) {
                        Utilities.Form.updateSearchableSelectOptions($('#id_car_trim'), response.models, 'Model', selected_trim);

                        $('#id_car_trim').attr(
                            'data-placeholder',
                            response.models.length?'Select option...':'Please enter car model below'
                        ).prop('disabled', response.models.length==0);

                        $('#id_car_trim').trigger('chosen:updated');
                    }
                });
            });
        },

        _initCarTrimChange: function() {
            $('#id_car_trim').bind('change',function(){
                _this._resetAlgoDrivenElements(false);
            });
        },

        _initCustomCarNameChange: function() {
            $('#id_custom_car_name').change(function(event) {
                var len = $(this).val().length;

                _this._resetAlgoDrivenElements();

                $('#id_car_trim').prop('disabled', len);
                if(len) $('#id_car_trim').val('');

                $('#id_car_trim').trigger('chosen:updated');
            });
        },

        _getCustomerProfile: function() {
            if(!_customer.val()) return;
            $('.preloader').show();
            $.get(DjangoUrls['customers:profile-motor'](_customer.val()), function(response) {
                if(response.success) {
                    $.each(response.profile, function(k, v){
                        $('#id_' + k).val(v?v:'').change();
                    });
                } else {
                    $('.info select, .info input').each(function() { $(this).val('').change();});
                }
                $('.preloader').hide();
            });
        },

        _loadQuotePreview: function() {
            $.get(DjangoUrls['motorinsurance:deal-quote-preview'](_deal_id), function(response) {
                $('.quote-preview').html(response);
            });
        },

        _loadCustomers: function() {
            return;
            $.get(DjangoUrls['customers:list'](), function(response) {
                if(response) {
                    var selected_value = _this._getCustomerFromQueryParams();

                    if(_customer.data('selected-value') != 'None') {
                        selected_value = _customer.data('selected-value');
                    }

                    Utilities.Form.updateSearchableSelectOptions(
                        _customer, response, 'Customers', selected_value);
                    _this._getCustomerProfile();
                }
            });
        },

        _updateTableAttributes: function(data) {
            $('.deals-total-amount').html(data.total_deals_display);
            //re-init inline form defintion
            _this._dealStatusInline();
        },

        ////// DEAL Stages and Processes methods
        _addNewDealForm: function() {
            $("#deal_form").ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: function(response, status, xhr, form) {
                    if(response.success) {
                        $.get(DjangoUrls[`${__app_name}:get-deal-json`](response.deal_id), function(r) {
                            __AMPLITUDE.logEvent(__AMPLITUDE.event('motor_deal_created'), {
                                'source': 'manual',

                                'deal_id': r.deal.id,

                                'vehicle_model_year': r.deal.vehicle_year,
                                'vehicle make': r.deal.vehicle_make,
                                'vehicle_model': r.deal.vehicle_model,
                                'vehicle_body_type': r.deal.vehicle_body_type,
                                'vehicle_sum_insured': r.deal.insured_car_value,

                                'client_nationality': r.customer.nationality,
                                'client_gender': r.customer.gender,
                                'client_age': r.customer.age,

                                'deal_type': 'new'
                            });
                        });
                    }

                    Utilities.Form.onSuccess(response, status, xhr, form);
                },
                error: Utilities.Form.onFailure
            });
        },

        _dealProcessTriggers: function() {
            _deal_stage_container.on('click', '.btn-cancel-generate-new-quote', function(){
                if($('.deal-overview .deal-form .products-preview .products .row').length) {
                    $('.deal-form .products-preview').removeClass('hide');
                    $('.deal-form .form').addClass('hide');
                } else if($('.quote-overview .deal-form .products-preview .products .row').length){
                    $('.deal-form .products-preview').removeClass('hide');
                    $('.deal-form .form').addClass('hide');
                } else {
                    $('.deal-overview .new-deal').addClass('display');
                    $('.deal-overview .deal-form').removeClass('display');    
                }
            });

            $('body').on('click', '.insurer-block-container', function() {
                $('.auto-quote-insurer-field').val($(this).data('id')).change();
                $('#modal_auto_quote_form h2').html($(this).data('name'));

                $('#id_product option').addClass('hide').trigger('chosen:updated');
                $('#id_product option[data-insurer-id=' + $(this).data('id') + ']').removeClass('hide').trigger('chosen:updated');
            });

            $('body').on('click', '.show-insurer-modal', function() {
                if(_number_of_passengers_set) {
                    $('#modal_quote_insurers').show();
                    return;
                }

                $.get(DjangoUrls[`${__app_name}:get-deal-json`](_deal_id), function(response) {
                    if(response.deal.number_of_passengers) {
                        $('#modal_quote_insurers').show();
                        _number_of_passengers_set = true;
                    } else {
                        $('[data-felix-modal="modal_required_fields_quote_form"]').click();
                    }
                });
            });
        },

        _dealStagesToggle: function() {
            if(_deal_stages_breadcrumb.length) {
                _deal_stages_breadcrumb.find('li').click(function() {
                    if(!$(this).data('item') || $('.' + $(this).data('item')).is(':visible')) return;
                    _this._loadDealStage($(this).data('id'));
                    _deal_stages_breadcrumb.find('li').removeClass('selected');
                    $(this).addClass('selected');
                });
            }
        },

        _getProductAddons: function(val, element) {
            if(!val) return;
            if (window.products_data !== undefined) {
                product = window.products_data[val];
                _this._updateAddonsDD(element, product.addons);
            }
            $.get(DjangoUrls['motorinsurance:product-addons'](val), function(response) {
                $(element).find('option').remove();
                if(response.success) {
                    _this._updateAddonsDD(element, response.addons);
                }
            });
        },

        _getQuotedProductAddons: function(val, element) {
            if(!val) return;
            $.get(DjangoUrls['motorinsurance:quoted-product-addons'](val), function(response) {
                $(element).find('option').remove();
                if(response.success) {
                    _this._updateAddonsDD(element, response.addons);
                }
            });
        },

        _updateAddonsDD: function(element, addons) {
            $.each(addons, function(key, addon) {
                var selected = '';
                var addon_key = Object.keys(addon)[0];
                var addon_value = addon[addon_key].label;
                var price = addon[addon_key].price;

                var selected_addons = element.closest('.addons').data('selected-addons');

                if(typeof selected_addons !== 'undefined' && selected_addons) {
                    if(typeof selected_addons == 'string') selected_addons = selected_addons.split(',');
                    $.each(selected_addons, function(k, v){
                        if(v == addon_key) {
                            selected = 'selected';
                            return false;
                        }
                    });
                }
                $(element).append(
                    '<option data-price="'+price+'" value='+addon_key+' '+selected+'>'+addon_value+'</option>'
                );
            });
            $(element).trigger('chosen:updated');
        },

        _setDealsQuoteOutdated: function() {
            var quote_stage_container = $('.deal-stages-breadcrumb [data-id="quote"]');

            if(!quote_stage_container.length) return;

            if(quote_stage_container.hasClass('selected') || quote_stage_container.hasClass('current') || quote_stage_container.hasClass('completed')) {
                $('.stage-warning').removeClass('hide');
                __DEALS._loadStageWarning();
            }
        },

        _duplicateDeal: function() {
            if(_deal_id) {
                if(window.confirm('Are you sure you want to duplicate this deal?')) {
                    $.get(DjangoUrls['motorinsurance:deal-duplicate'](_deal_id), function(response) {
                        if(response.success) {
                            window.location = response.redirect_url;
                        } else {
                            Utilities.Notify.error('Something went wrong. Please contact support.', 'Error');
                        }
                    });
                }
            }
        }
    };

    jQuery(function() {
        if($('body').hasClass('motor-deals') || $('body').hasClass('customers'))
            __DEALS.init();
    });
})();

/*
    Company Settings
*/
;
'Use Strict';

var __DEALFORMS;
;(function() {
    var SELECTORS = {
    };

    var _this = '';

    var _deal_id = $('.deal-container').data('id');
    var _deal_stage_container = $('.deal-processes');

    var _show_loader_class = 'show-loader';

    __DEALFORMS =
    {
        init: function()
        {
            _this = this;

            _this._initForms();

            _deal_stage_container.on('click', '#order_form .product', function(event) {
                var product_id = $(this).data('id');
                var quoted_product_id = $(this).data('qpid');
                var premium = $(this).data('premium');
                var sale_price = $(this).data('sale-price');
                var product_add_ons = $(this).data('add-ons');
                var default_add_ons = $(this).data('default-add-ons');

                $(this).siblings().addClass('disable').removeClass('selected');
                $(this).addClass('selected').removeClass('disable');

                $('.base_premium').html(accounting.format(premium, 2));
                $('.sale_price').html(accounting.format(sale_price, 2));
                $('#id_selected_product').val(quoted_product_id).change();

                var html = '<span class="c-vlgray font-10 nothing-available">No default add ons</span>';
                if(default_add_ons.length) {
                    html = '';
                    $.each(default_add_ons, function() {
                        html += '<span data-key="'+this+'" class="badge badge-default badge-font-light m-t-10 m-r-10">' +this.replace(new RegExp('_' , 'g'), ' ')+ '</span>';
                    });
                }

                $('#order_form .default-add-ons').html(html);

                var html = '<span class="c-vlgray font-10 nothing-available">Nothing available</span>';
                if(product_add_ons && product_add_ons.length) {
                    html = '';
                    $.each(product_add_ons, function() {
                        if(default_add_ons.indexOf(Object.keys(this)[0]) < 0)
                            html += '<span data-key="'+Object.keys(this)[0]+'" data-price="'+this[Object.keys(this)[0]].price+'" class="badge badge-default badge-font-light m-t-10 m-r-10">' +this[Object.keys(this)[0]].label+ '</span>';
                    });
                }
                $('#order_form .addons').html(html);

                _this._updateTotal();
            });

            _deal_stage_container.on('change', '#order_form #id_discount', function() {
                _this._updateTotal();
            });
            _deal_stage_container.on('click', '#order_form .addons .badge', function() {
                $(this).toggleClass('active');
                _this._updateTotal();
            });

            _deal_stage_container.on('click', '.quote-summary .product-preview', function() {
                $('.prepare-order').click();
                $('#order_form .product[data-qpid='+$(this).data('qpid')+']').click();
            });

            _deal_stage_container.on('click', '.prepare-order', function() {
                $('.quote-summary.quote-preview').addClass('hide');
                $('.quote-summary.create-order').removeClass('hide');

                __FELIX__._loadLibs();
                _this._initForms();
            });
            _deal_stage_container.on('click', '.cancel-order', function() {
                if($('.quote-summary').length && $('.quote-summary').is(':visible')) {
                    $('.quote-summary.quote-preview').removeClass('hide');
                    $('.quote-summary.create-order').addClass('hide');
                }
                if($('.order-summary').length && $('.order-summary').is(':visible')) {
                    $('.order-summary.preview').removeClass('hide');
                    $('.order-summary.create-order').addClass('hide');
                }
            });

            _deal_stage_container.on('click', '.submit-order', function(){
                $(this).addClass('show-loader');
                $('#order_form #id_send_email').val('');
                $('#order_form').submit();
            });

            _deal_stage_container.on('click', '.submit-send-order', function(){
                $(this).addClass('show-loader');
                $('#order_form #id_send_email').val('1');

                $.get(DjangoUrls[`${__app_name}:get-deal-json`](_deal_id), function(response) {
                    if(response.customer.email == '') {
                        $('[data-felix-modal="modal_edit_customer_email"]').click();
                        $('.submit-send-order').removeClass('show-loader');
                    } else {
                        $('#order_form').submit();
                    }
                });
            });

            _deal_stage_container.on('change', '#id_selected_product', function(){
                __DEALS._getQuotedProductAddons($(this).val(), $('#id_selected_add_ons'));
            });
            _deal_stage_container.on('change', '#id_is_void', function() {
                $('button.submit-send-order').prop('disabled', $(this).is(':checked'));
            });

            _deal_stage_container.on('click', '.edit-order', function() {
                $('.order-summary.preview').addClass('hide');
                $('.order-summary.create-order').removeClass('hide');

                __FELIX__._loadLibs();
                _this._loadProductAndAddons();
                _this._initForms();
            });

            _deal_stage_container.on('click', '.edit-policy', function() {
                $('.policy-summary.preview').addClass('hide');
                $('.policy-summary.form').removeClass('hide');

                __FELIX__._loadLibs();
                _this._initForms();
            });

            _deal_stage_container.on('click', '.cancel-policy', function() {
                $('.policy-summary.preview').removeClass('hide');
                $('.policy-summary.form').addClass('hide');
            });

            _deal_stage_container.on('click', '.edit-quote', function() {
                $('.quote-summary.quote-preview').addClass('hide');
                $('.quote-summary.quote-form').removeClass('hide');

                __QUOTES._getQuotedProducts();
                __FELIX__._loadLibs();
                _this._initForms();
            });

            _deal_stage_container.on('click', '.cancel-quote', function() {
                $('.quote-summary.quote-preview').removeClass('hide');
                $('.quote-summary.quote-form').addClass('hide');
            });

            _deal_stage_container.on('click', '.order-status-display .dropdown-menu a', function() {
                var value = $(this).data('value');
                $.post(
                    DjangoUrls['motorinsurance:update-deal-field']($('.deal-container').data('id'), 'order'),
                    {'pk': $('.deal-container').data('id'), 'name': 'status', 'value': value},
                function(response) {
                    if(response.success) {
                        $('.order-status-display a.nav-link')
                            .removeClass('paid')
                            .removeClass('unpaid')
                            .addClass(value)
                            .html(value);

                        $.get(DjangoUrls['motorinsurance:deal-current-stage'](_deal_id), function(response) {
                            __DEALS._updateTags(response.tags);
                        });
                    } else {
                        Utilities.Notify.error('Some error occurred. Please try again later.', 'Error');
                    }
                });
            });
        },

        _initForms: function() {
            if($('#order_form').length) {
                $('#order_form').ajaxForm({
                    beforeSubmit: Utilities.Form.beforeSubmit,
                    success: function(response, status, xhr, form) {
                        Utilities.Form.onSuccess(response, status, xhr, form);

                        if(response.success) {
                            $('.cancel-order').click();

                            if(response.creating) {
                                $.get(DjangoUrls[`${__app_name}:get-deal-json`](_deal_id), function(r) {
                                    __AMPLITUDE.logEvent(
                                        __AMPLITUDE.event('motor_order_created'),
                                        {
                                            'source': 'manual',

                                            'deal_id': _deal_id,
                                            'deal_type': r.deal.deal_type,
                                            'deal_created_date': r.deal.created_on,
                                            'vehicle_model_year': r.deal.vehicle_year,
                                            'vehicle_model': r.deal.vehicle_model,
                                            'vehicle_body_type': r.deal.vehicle_body_type,
                                            'vehicle make': r.deal.vehicle_make,

                                            'views': r.quote.views,

                                            'product': r.order.product,
                                            'cover': r.order.product_cover,
                                            'insurer': r.order.product_insurer,
                                            'premium': r.order.payment_amount,
                                            'discounted_premium': r.order.discounted_premium,
                                            'repair_type': r.order.repair_type,
                                            'vehicle_sum_insured': r.order.sum_insured,

                                            'client_nationality': r.customer.nationality,
                                            'client_gender': r.customer.gender,
                                            'client_age': r.customer.age
                                        });
                                });
                            }

                            if($('#order_form #id_send_email').val()) {
                                __DEALS._triggerCustomEmailModal('order_confirmation');
                            }

                            __DEALS._loadDealStage();

                            if('note_content' in response) {
                                var note_content = response.note_content;
                                    note_content += '<div class="text-muted">' + response.note_created_on + '</div>';

                                __NOTE._prependNoteInTrail(note_content);
                            }
                        }
                        $('.' + _show_loader_class).removeClass(_show_loader_class);
                    },
                    error: Utilities.Form.onFailure
                });
            }
            if($('#policy_form').length) {
                $('#policy_form').ajaxForm({
                    beforeSubmit: Utilities.Form.beforeSubmit,
                    success: function(response, status, xhr, form) {
                        Utilities.Form.onSuccess(response, status, xhr, form);

                        if(response.success) {
                            $('.cancel-policy').click();

                            if(response.creating) {
                                $.get(DjangoUrls[`${__app_name}:get-deal-json`](_deal_id), function(r) {
                                    __AMPLITUDE.logEvent(
                                        __AMPLITUDE.event('motor_policy_saved'), {
                                            'deal_id': _deal_id,
                                            'deal_created_date': r.deal.created_on,

                                            'repair_type': r.order.repair_type,
                                            'insurer': r.order.product_insurer,
                                            'cover': r.order.product_cover,
                                            'product': r.order.product,
                                            'premium': r.order.payment_amount,

                                            'vehicle_model_year': r.deal.vehicle_year,
                                            'vehicle make': r.deal.vehicle_make,
                                            'vehicle_model': r.deal.vehicle_model,
                                            'vehicle_body_type': r.deal.vehicle_body_type,
                                            'vehicle_sum_insured': r.order.sum_insured,

                                            'client_nationality': r.customer.nationality,
                                            'client_gender': r.customer.gender,
                                            'client_age': r.customer.age
                                        }
                                    );
                                });
                            }

                            if($('#policy_form #id_send_email').val()) {
                                __DEALS._triggerCustomEmailModal('policy_issued');
                            }
                            __DEALS._loadDealStage();
                        }
                        $('.' + _show_loader_class).removeClass(_show_loader_class);
                    },
                    error: Utilities.Form.onFailure
                });
            }

            if($('#quote_form').length) {
                $('#quote_form').ajaxForm({
                    beforeSubmit: Utilities.Form.beforeSubmit,
                    success: Utilities.Form.onSuccess,
                    error: Utilities.Form.onFailure
                });
            }
        },

        _updateTotal: function() {
            var order_form = $('#order_form');
            var product_id = order_form.find('.product.selected').data('id');
            var product = window.products_data[product_id];
            var premium = order_form.find('.product.selected').data('sale-price');
            if(premium === undefined) premium = 0;
            var total = premium - $('#id_discount').val();
            var selected_addons = [];
            var addons_price = 0;
            order_form.find('.badge.active').each(function() {
                selected_addons.push(this.dataset.key);

                if(this.dataset.key == 'pab_passenger') {
                    addons_price += (parseFloat(this.dataset.price) * parseFloat(order_form.data('number-of-passengers')));
                } else {
                    addons_price += parseFloat(this.dataset.price);
                }
            });

            total += addons_price;

            order_form.find('.paid_addons').html(accounting.format(addons_price, 2));
            order_form.find('#id_selected_add_ons').val(selected_addons).change();

            if(total < 0) total = 0;

            $('#id_payment_amount').val(total);
            $('.order_total').html(accounting.format(total, 2));
        },

        _loadProductAndAddons: function() {
            var order_form = $('#order_form');
            if(order_form.data('selected-product')) {
                $('#id_selected_product').change();
                var id = order_form.data('selected-product');
                order_form.find('.product[data-id='+id+']').click();
            }
            setTimeout(function() {
                if(order_form.data('selected-addons')) {
                    var addons = order_form.data('selected-addons');
                    $.each(addons, function() {
                        order_form.find('.badge[data-key='+this+']').click();
                    });
                }
            }, 1000);
        }
    };

    jQuery(function() {
        __DEALFORMS.init();
    });
})();

/* DOCUMENT VIEWER */
;
'Use Strict';

var __DOCUMENTS_SECTION;
;(function() {

    var _this   = '';
    var _counter = 0;
    var _attachments_url = $('#tab_documents').data('attachments-url')
    var _delete_url = $('#tab_documents').data('delete-url')
    var _copy_url = $('#tab_documents').data('copy-url')

    __DOCUMENTS_SECTION =
    {
        init: function()
        {
            _this = this;
            _this._loadDocuments();

            $('#tab_documents').on('click', '.edit-file', function(e) {
                e.stopPropagation();
                $(this).siblings('.attachment-field').editable('toggle');
            });

            $('#tab_documents').on('click', '.delete-file', function(e) {
                e.stopPropagation();
                _this._deleteDocument($(this).data('id'));
            });

            $('#tab_documents').on('click', '.copy-file', function(e) {
                e.stopPropagation();
                _this._copyDocument($(this).data('id'));
            });
        },

        _loadDocuments: function(obj_id) {
            $.get(_attachments_url, function(response) {
                var source   = $('#documents-template').html();
                var template = Handlebars.compile(source);
                $('.documents-section').html(
                    template({'records': response}));

                attachments = $.merge(response.related_documents, response.documents);

                if($('body.customers').length)
                    __XEDITABLE.init();
            });
        },

        _deleteDocument: function(obj_id) {
            if(window.confirm('Are you sure you want to delete this file?')) {
                let url = _delete_url.replace('/0/', `/${obj_id}/`);
                $.post(url, function(resp) {
                    if(resp.redirect) {
                        _this._loadDocuments();
                    }
                });
            }
        },

        _copyDocument: function(obj_id) {
            let url = _copy_url.replace('/0/', `/${obj_id}/`);
            $.post(url, function(resp) {
                if(resp.success) {
                    _this._loadDocuments();
                }
            });
        }
    };

    jQuery(function() {
        if($('#tab_documents').length)
            __DOCUMENTS_SECTION.init();
    });
})();

/* DOCUMENT VIEWER */
;
'Use Strict';
var attachments = [];
var __DOCUMENTS_VIEWER;
;(function() {

    var _this   = '';
    var _counter = 0;
    var _viewer = '.document-viewer';
    var _viewer_cta = '.preview-documents';
    var _preview_container = '.preview-container';
    var _img_container = '.preview-container img';
    var _pdf_container = '.preview-container iframe';
    var _form = '.attachment_update_form';
    var _label_field = '.attachment_update_form input[name=value]';
    var _id_field = '.attachment_update_form input[name=pk]';
    var _doc_nav_right = '.document-viewer .nav.right';
    var _doc_nav_left = '.document-viewer .nav.left';
    var _loader = '.document-viewer .loader';
    var _controls = '#modal_documents_viewer .controls';
    var _controls_rotate = '#modal_documents_viewer .controls .rotate';
    var _loaded_flag = false;

    __DOCUMENTS_VIEWER =
    {
        init: function()
        {
            _this = this;

            $(_viewer_cta).click(function() {
            	_this._loadDocuments();
                _this._right_left_key_navs();

                __AMPLITUDE.logEvent(__AMPLITUDE.event('document_previewed'));
            });

            _this._toggleNav();

            $(_doc_nav_right).click(function() {
                _this._moveRight();
            });
            $(_doc_nav_left).click(function() {
                _this._moveLeft();
            });
            $(_preview_container).click(function() {
                $(this).toggleClass('fit-to-container');
            });

            $(_controls_rotate).click(function() {
                var angle = $(this).data('angle');

                if(angle == 0) angle = 90;
                else if(angle == 90) angle = 180;
                else if(angle == 180) angle = 270;
                else if(angle == 270) angle = 0;

                $(this).data('angle', angle);
                $(_img_container).css({'transform': 'rotate(' + angle + 'deg)'});
            });

            $(_form).ajaxForm({
                success: function(response, status, xhr, form) {
                    if(response.success) {
                        Utilities.Notify.success('File name updated successfully', 'Success');
                        var id = $(_id_field).val();
                        var label = $(_label_field).val();
                        var filefield = $('#tab_documents a[data-id=' + $(_id_field).val() + '].attachment-field');
                        filefield.html(label);
                        filefield.attr('title', label);
                        filefield.attr('data-value', label);
                        filefield.editable({
                            type: 'text',
                            anim: 200,
                            mode: 'inline'});

                        _this._updateAttachmentSet(response.id, response.data['value']);
                        _this._pushEditEventAmplitude('document viewer');
                    } else {
                        Utilities.Notify.error('Please check all the required Fields.', 'Error');
                    }
                }
            });
        },

        _loadDocuments: function() {
            if (typeof attachments == "undefined") {
                console.log('No attachments variable defined'); return;
            }

            if(!attachments.length) {
            	alert('No document(s) available for preview. Please upload to preview.');
            } else {
                if(_counter < 0) _counter = 0;
                if(_counter > attachments.length-1) _counter = attachments.length-1;
                $('.preview-documents-viewer-trigger').click();
                _this._loadFile(attachments[_counter]);
            }
        },

        _updateAttachmentSet: function(id, label) {
            $.each(attachments, function(k, v){
                if(v['id'] == id)
                    attachments[k]['label'] = label;
            });
        },

        _moveLeft: function() {
            if($(_doc_nav_left).hasClass('disbaled')) return;

            _counter--;

            _this._loadDocuments();
            _this._toggleNav();
        },

        _moveRight: function() {
            if($(_doc_nav_right).hasClass('disbaled')) return;

            _counter++;

            _this._loadDocuments();  
            _this._toggleNav();
        },

        _toggleNav: function() {
            if(_counter == 0) {
                $(_doc_nav_left).addClass('disabled');
            } else {
                $(_doc_nav_left).removeClass('disabled');
            }

            if(_counter == attachments.length-1) {
                $(_doc_nav_right).addClass('disabled');
            } else {
                $(_doc_nav_right).removeClass('disabled');
            }
        },

        _loadFile: function(file) {
            if($(_preview_container).data('doc-id') == _counter && _loaded_flag) return;

            $(_loader).addClass('show');

            _loaded_flag = true;

        	if(file.extension == 'pdf') {
        		_this._loadPDF(file);
                $('.zoom-toggle').addClass('hide');
                $(_controls).addClass('hide');
            }
        	else {
        		_this._loadImage(file);
                $('.zoom-toggle').removeClass('hide');
                $(_controls).removeClass('hide');
            }

        	$(_label_field).val(file.label);
            $(_id_field).val(file.id);

            $(_form).attr('action', DjangoUrls['core:update-attachment'](file.id));

            $(_preview_container).data('doc-id', _counter);
            $(_preview_container).addClass('fit-to-container');
        },

        _loadPDF: function(file) {
            debugger
            $(_pdf_container).removeClass('hide');
            $(_pdf_container).addClass('show');
        	$(_pdf_container).attr('src', file.url);

            $(_pdf_container)
                .on('load', function() {
                    $(_loader).removeClass('show');
                    $(_pdf_container).removeClass('hide');
                    $(_pdf_container).addClass('show');
                    $(_img_container).addClass('hide');
                })
                .attr("src", file.url);
        },

        _loadImage: function(file) {
            $(_img_container)
                .on('load', function() {
                    $(_loader).removeClass('show');
                    $(_img_container).removeClass('hide');
        	        $(_pdf_container).addClass('hide');
                    // _this._reset_rotate();
                })
                .attr("src", file.url);

        },

        // _reset_rotate: function() {
        //     $(_controls_rotate).data('angle', 0);
        //     $(_img_container).css({'transform': 'rotate(0deg)'});
        // },

        _right_left_key_navs: function() {
            $(document).on("keyup", "body", function(e) {
                if (e.target.type == 'text') return;
                if (e.keyCode == 37)_this._moveLeft();
                if (e.keyCode == 39)_this._moveRight();
                if (e.keyCode === 27) $(_viewer).find('.close').click();
            });
        },

        _updateListDocument: function(id, label) {
            _this._pushEditEventAmplitude('list');

            $.each(attachments, function() {
                if(this.id == id) {
                    this.label = label;
                }
            });
        },

        _pushEditEventAmplitude(source) {
            if(typeof source == undefined)
                return;

            __AMPLITUDE.logEvent(__AMPLITUDE.event('document_renamed'), {'source': source});
        },

        _update_attachments_obj: function(file) {
            if($('#modal_documents_viewer').length) {
                if(attachments.length) {
                    attachments.unshift({
                        "id": file.pk,
                        "label": file.label,
                        "url": file.url,
                        "can_preview": true,
                        "extension": file.extension,
                        "added_by": file.added_by,
                        "created_on": file.created_on
                    });
                }
            }
        }
    };

    jQuery(function() {
        if($('#modal_documents_viewer').length)
            __DOCUMENTS_VIEWER.init();
    });
})();

/*** Felix File Uploader ***/
;'Use Strict';
var __DOCUMENT_UPLOADER;

;(function() {
    var _this = '';

    __DOCUMENT_UPLOADER =
    {
        // Onload
        init: function()
        {
            _this = this;
            $('.add-documents').click(function() {
                $('[href="#tab_documents"]').click();
                $('#document_upload').click();
            });

            // enable fileuploader plugin
            if($('#document_upload').length) {
                $('#document_upload').fileuploader({
                    changeInput: '<div class="fileuploader-input">' +
                                      '<div class="fileuploader-input-inner">' +
                                          '<div class="fileuploader-main-icon"></div>' +
                                          '<h3 class="fileuploader-input-caption"><span>${captions.feedback}</span></h3>' +
                                          '<p>${captions.or}</p>' +
                                          '<div class="fileuploader-input-button"><span>${captions.button}</span></div>' +
                                      '</div>' +
                                  '</div>',
                    theme: 'dragdrop',
                    upload: {
                        url: $('#document_upload').data('url'),
                        data: null,
                        type: 'POST',
                        enctype: 'multipart/form-data',
                        start: true,
                        synchron: true,
                        beforeSend: function() {
                            $('.progress-bar').removeClass('error').removeClass('success');
                        },
                        onSuccess: function(result, item) {
                            // if success
                            if (result && result.success) {
                                // $('.files-container').prepend(
                                //     '<div class="files col col-lg-6 highlight-temp">' +
                                //         '<a href="'+ result.file.url +'" target="_blank">' +
                                //             '<div class="file-icon '+ result.file.extension +'"></div>'+
                                //         '</a>' +
                                //         '<div class="file-info">' +
                                //             '<a data-id=' + result.file.pk + ' href="'+ result.file.url +'" target="_blank" data-preview-image="'+ result.file.url +'"' + 
                                //                'class="text-editable attachment-field"' +
                                //                'data-class="form-control-sm"' +
                                //                'data-name="label"' +
                                //                'data-toggle="manual"' +
                                //                'data-value="' + result.file.label + '"' +
                                //                'data-title="' + result.file.label + '"' +
                                //                'data-pk="' + result.file.pk + '"' +
                                //                'data-url="' + DjangoUrls['core:update-attachment'](result.file.pk) + '"' +
                                //             '>' + result.file.label + '</a>' +
                                //             '<a class="edit-file" href="javascript:"><i class="ti-pencil"></i></a>' +
                                //             '<div class="dates text-muted">' + result.file.created_on + ' by ' + result.file.added_by + '</div>' +
                                //         '</div>' +
                                //     '</div>'
                                // );
                                if(typeof __DOCUMENTS_SECTION != undefined) {
                                    __DOCUMENTS_SECTION._loadDocuments();
                                }
                                if(typeof __DOCUMENTS_VIEWER != undefined) {
                                    __DOCUMENTS_VIEWER._update_attachments_obj(result.file);
                                }
                            } else {
                                $('.progress-bar').addClass('error').removeClass('success');
                                Utilities.Notify.error('Error occurred while uploading ' + item.name, 'Error');
                            }

                            setTimeout(function() {
                                $('.progress-bar').fadeOut(400);
                                __XEDITABLE.init();
                            }, 1000);

                        },
                        onError: function(item) {
                            var progressBar = $('.progress-bar');
                            if(progressBar.length) {
                                $('.progress-bar').removeClass('success').addClass('error');
                            }
                        },
                        onProgress: function(data, item) {
                            var progressBar = $('.progress-bar');
                            if(progressBar.length > 0) {
                                progressBar.removeClass('error').removeClass('success');
                                progressBar.show();
                                progressBar.width(data.percentage + "%");
                                progressBar.find('span').html(item.name);
                            }
                        },
                        onComplete: function() {
                            $('.progress-bar').removeClass('error').removeClass('success');
                            $('.progress-bar span').html('');
                            $('[name=fileuploader-list-file]').val('');
                        },
                    },
                    captions: {
                        feedback: 'Drag files here or click to upload',
                        feedback2: 'Drag files here or click to upload',
                        drop: 'Drag files here or click to upload',
                        or: ' ',
                        button: ' ',
                    },
                });
            }
        },
    };

    jQuery(function() {
        __DOCUMENT_UPLOADER.init();
    });
})();

/*** Felix Dynamic Data Table + Algolia ***/
;'Use Strict';
var __TABLE;

;(function() {

    var _filters_open_search_field = $('.open-search-field input[type="text"]');
    var _felix_table = $('table.felix-table');
    var _felix_table_filters = $('.table-filters');
    var _felix_table_quick_filters = $('.quick-filters');
    var _felix_table_action_buttons = $('.felix-table-action-buttons');

    var _this = '';

    __TABLE =
    {
        // Onload
        init: function()
        {
            _this = this;

            _this.initTable();
            _this.initFelixTableSearchForm();
            _this.initExportTrigger();
            _this.initSortTrigger();
            _this._quickFilters();
            // $('.quick-filters').on('change', 'input[type=checkbox]', function() {
            //     _this._fetch_felix_table_records();
            // });
        },

        initTable: function() {
            if(_felix_table.length) {
                // Row Click
                _felix_table.on('click', 'td', function(e) {
                    if(_felix_table.hasClass('no-row-clicks'))
                        return;

                    if($(this).hasClass('link')) {
                        if(e.target.nodeName == 'A') return;
                        // Don't trigger click if there is an editable form field in td
                        if ($('.editableform').is(e.target) || $('.editableform').has(e.target).length) {
                            return;
                        }
                        // Don't trigger click if there is checkbox
                        if ($('.felix-checkbox').is(e.target) || $('.felix-checkbox').has(e.target).length || $(e.target).find('.felix-checkbox').length) {
                            return;
                        }
                        // Don't trigger click if there is switch checkbox
                        if ($('.switch-toggle').is(e.target) || $('.switch-toggle').has(e.target).length || $(e.target).find('.switch-toggle').length) {
                            return;
                        }
                        if($(e.target).is('input[type="checkbox"]')) return;
                    }

                    var url = $(this).parent('tr').data('url');
                    var modal = $(this).parent('tr').data('trigger-modal');
                    var callback = $(this).parent('tr').data('click-callback');
                    var params = '';

                    if(window.location.href.indexOf('?') > -1) {
                        var encodedparams = encodeURIComponent(window.location.href.slice(window.location.href.indexOf('?') + 1));
                        params = '?filters=' + Utilities.General.getUrlPathname() + '?' + encodedparams;
                    }

                    if(modal) {
                        $(modal).show();
                    }

                    if(callback && typeof eval(callback) === 'function') {
                        eval(_felix_table.data('update-callback'));
                    }

                    if(url) window.location = url + params;

                    // Calling libs init functions here....
                    __FELIX__.initSearchableSelect();
                });
                // Select all Checkbox
                _felix_table.find('.select-record-all').on('change', function(){
                    $(this).parent().find('.checkmark').removeClass('partial');
                    _felix_table.find('.select-record').prop('checked', this.checked);
                    _felix_table.find('tr').addRemoveClass(this.checked, 'selected');
                    _felix_table_action_buttons.fadeInOrOut(this.checked);

                    if(typeof __RENEWALS !== 'undefined')
                        __RENEWALS.toggle_cta(this.checked);
                });
                // Single Checkbox selection
                _felix_table.on('change', '.select-record', function() {
                    var len = _felix_table.find('.select-record').length;
                    var len_selected = _felix_table.find('.select-record:checked').length;

                    $(this).closest('tr').addRemoveClass(this.checked, 'selected');
                    _felix_table_action_buttons.fadeInOrOut(len_selected);

                    if($("[data-felix-modal='modal_merge_customer']").length) {
                        $("[data-felix-modal='modal_merge_customer']").addRemoveClass(len_selected!=2, 'hide');
                    }

                    _felix_table.find('.select-record-all').prop('checked', (len_selected != len && len_selected));
                    _felix_table.find('.select-record-all').parent().find('.checkmark').addRemoveClass((len_selected != len && len_selected), 'partial');

                    if(typeof __RENEWALS !== 'undefined')
                        __RENEWALS.toggle_cta(len_selected);

                });
                // Delete Button
                _felix_table_action_buttons.find('.delete-record').on('click', function() {
                    if(window.confirm('Are you sure you want to delete selected record(s)?')) {
                        var ids = getSelectedIds();
                        $.each(ids, function(id) {
                            var row = $('#tr_' + this.substring());
                            $.get(row.data('url-delete'), function(response) {
                                if(response.success)
                                    row.remove();
                            });
                        });

                        _felix_table.find('.select-record-all').prop('checked', false);
                    }
                });

                // Delete Button
                _felix_table_action_buttons.find('.close-deal').on('click', function() {
                    var type = $(this).data('type');
                    if(window.confirm('Are you sure you want to mark selected deal(s) as lost?')) {
                        var ids = getSelectedIds();

                        $.each(ids, function(id) {
                            var row = $('#tr_' + this.substring());
                            $.get(DjangoUrls['motorinsurance:deal-mark-as-lost'](this.substring()), function(response) {
                                if(response.success)
                                    row.remove();
                            });
                        });

                        _felix_table.find('.select-record-all').prop('checked', false);
                    }
                });

                // sorting
                _felix_table.on('click', 'th', function() {
                    if($(this).hasClass('sortable')) {
                        var is_asc = $(this).hasClass('asc');
                        var is_desc = $(this).hasClass('desc');

                        _felix_table.find('th').not($(this)).removeClass('asc desc');
                        if(is_asc) {
                            $(this).addClass('desc').removeClass('asc');
                        } else {
                            $(this).addClass('asc').removeClass('desc');
                        }

                        if(_felix_table.data('mode') == 'index') {
                            var sort_type = $(this).data('name') + ((!is_asc)?'_asc':'_desc');

                            var ignore_sorting_keys = ['created_on', 'policy_start_date'];

                            if($.inArray($(this).data('name'), ignore_sorting_keys) > -1 && is_asc)
                                sort_type = '';

                            _felix_table_filters.find('#id_sort_by').val(sort_type);
                        } else {
                            _felix_table_filters.find('#id_order_by').val((is_asc?'-':'') + $(this).data('name'));
                        }
                        _this._fetch_felix_table_records();
                    }
                });

                $('.pagination').on('click', 'li a', function() {
                    if($(this).hasClass('active')) return;
                    if($(this).hasClass('ellipsis')) return;
                    $('#id_page').val($(this).data('number'));

                    _this._fetch_felix_table_records();
                });

                _this._fetch_felix_table_records();

                function getSelectedIds() {
                    return $('.select-record:checked').map(function() {
                        return this.value;
                    }).get();
                }
            }
        },

        initFelixTableSearchForm: function() {
            var st;
            if(_felix_table_filters.length) {

                var form = _felix_table_filters.find('form');
                var action = form.attr('action');

                Utilities.Form.addFilterCount(form);

                form.find('.filter-trigger').click(function() {
                    form.find('.search-popup').fadeToggle('fast');
                    form.find('.search-popup select').chosen();
                });
                form.find('.search-apply').click(function() {
                    __TABLE._fetch_felix_table_records();
                    form.find('.search-popup').fadeToggle('fast');
                });
                form.find('.search-cancel').click(function() {
                    $('.search-popup').fadeOut('fast');
                });
                form.find('.search-clear').click(function () {
                    Utilities.Form.clearForm(form);
                    __TABLE._fetch_felix_table_records();
                    form.find('.search-popup').fadeToggle('fast');
                });

                //Sorting
                form.find('#id_sort_by').change(function () {
                    __TABLE._fetch_felix_table_records();
                });

                // Search query
                $('.open-search-field').on('keyup', 'input[type="text"]', function() {
                    $('.open-search-field .cross').fadeInOrOut($(this).val());
                    let search_term = $(this).val();
                    clearTimeout(st);
                    st = setTimeout(function() {
                        if(search_term.length > 2 || search_term.length == 0) {
                            _felix_table_filters.find('#id_page').val(0);
                            __TABLE._fetch_felix_table_records();
                        }
                    }, 300);
                });
                $('.open-search-field .cross').click(function() {
                    _filters_open_search_field.val('').keyup();
                });
                $('.open-search-field .cross').fadeInOrOut(_filters_open_search_field.val());
            }
        },

        initExportTrigger: function() {
            $('.options-table .dropdown-item.export').click(function() {
                window.location = $(this).data('url') + '?' +  window.location.href.slice(window.location.href.indexOf('?') + 1);
            });
        },

        initSortTrigger: function() {
            if($('#id_sort_by').length) {
                $('.sorting-table .dropdown-item').click(function() {
                    $('.sorting-table .dropdown-item').removeClass('active');
                    $(this).addClass('active');
                    $('#id_sort_by').val($(this).data('val')).change();
                });
            }
        },

        _quickFilters: function() {
            if(!_felix_table_quick_filters.length) return;

            var form = _felix_table_filters.find('form');
            _felix_table_quick_filters.find('button').click(function() {
                if($(this).hasClass('active')) return;
                _felix_table_quick_filters.find('button').removeClass('active');
                $(this).addClass('active');

                var field = $(this).data('field');
                if($('#' + field).length) {
                    form.find('#' + field).val($(this).data('type'));
                    form.find('#id_page').val(1);
                    __TABLE._fetch_felix_table_records();
                }
            });

            if(form.find('#id_assigned_to')) {
                form.find('#id_assigned_to').change(function() {
                    __TABLE._fetch_felix_table_records();
                });
            }
        },

        _fetch_felix_table_records: function() {
            var form = _felix_table_filters.find('form');
            var action = form.attr('action');

            if(!_felix_table.length || !form || !action) return;

            if(_felix_table.data('mode') == 'index') {
                __ALGOLIA._get_search_from_algolia();
            } else {

                _felix_table.addClass('opacity');
                $.get(action, form.serialize(), function(response) {
                    var source   = $('#row-template').html();
                    var template = Handlebars.compile(source);

                    // Records
                    _felix_table.find('tbody').html(
                        response.count?template({'records': response.records}):$('#empty-row-template').html()
                    );
                    // Count
                    $('.table_counts').html(
                        response.count + ' record' + (response.count>1?'s':'') + ' found'
                    ).fadeInOrOut(response.count);
                    //Pagination
                    Utilities.General.generatePagination(response.current_page, response.pages);

                    //Checking for a callback method
                    if(_felix_table.data('update-callback') && typeof eval(_felix_table.data('update-callback')) === 'function')
                        eval(_felix_table.data('update-callback'))(response);

                }, 'json').fail(function(response) {
                    Utilities.Notify.error('Some error occurred while doing the search.', 'Error');
                }).always(function() {
                    _felix_table.removeClass('opacity');
                });

            }

            Utilities.Form.addFilterCount(form);
            //Updating browsers history
            window.history.pushState('', window.document.title, action + '?' + form.serialize());
        }
    };

    jQuery(function() {
        if(_felix_table.length)
            __TABLE.init();
    });
})();

/*** Felix File Uploader ***/
;'Use Strict';
var __FILE_UPLOADER;

;(function() {
    var _this = '';

    __FILE_UPLOADER =
    {
        // Onload
        init: function()
        {
            _this = this;
            if($('.felix-file-uploader').length) {
                $('.felix-file-uploader input.single-file-input').each(function() {
                    var elem = $(this);
                    if(!$.fileuploader.getInstance(elem)) {
                        elem.fileuploader({
                            theme: 'default',
                            enableApi: true,
                            captions: {
                                button: 'Browse'
                            },
                            thumbnails: {
                                // thumbnails for the preloaded files {String, Function}
                                item2: '<li class="fileuploader-item file-has-popup">' +
                                            '<div class="columns">' +
                                                '<div class="column-thumbnail">${image}<span class="fileuploader-action-popup"></span></div>' +
                                                '<div class="column-title">' +
                                                    '<a href="${file}" target="_blank">' +
                                                        '<div title="${name}">${data.label}</div>' +
                                                        '<span>${size2}</span>' +
                                                    '</a>' +
                                                '</div>' +
                                                '<div class="column-actions">' +
                                                    '<a href="${file}" class="fileuploader-action fileuploader-action-download" title="${captions.download}" download><i></i></a>' +
                                                    '<a class="fileuploader-action fileuploader-action-remove" data-id="${data.id}" title="${captions.remove}"><i></i></a>' +
                                                '</div>' +
                                            '</div>' +
                                        '</li>',
                            },
                            onRemove: function(item, listEl, parentEl, newInputEl, inputEl) {
                                if($(parentEl).parent().find('#trigger_policy_document_parser').length) {
                                    $(parentEl).parent().find('#trigger_policy_document_parser, #policy_document_no_scan').addClass('hide');
                                }
                            }
                        });
                    }
                });
                $('.felix-file-uploader input.multi-file-input').each(function() {
                    var elem = $(this);
                    if(!$.fileuploader.getInstance(elem)) {
                        elem.fileuploader({
                            theme: 'default',
                            enableApi: true,
                            captions: {
                                button: 'Browse'
                            },

                            thumbnails: {
                                item: '<li class="fileuploader-item file-has-popup">' +
                                           '<div class="columns">' +
                                               '<div class="column-thumbnail">${image}<span class="fileuploader-action-popup"></span></div>' +
                                               '<div class="column-title">' +
                                                   '<div title="${name}">${name}</div>' +
                                                   '<span>${size2}</span>' +
                                               '</div>' +
                                               '<div class="column-actions">' +
                                                   '<a class="fileuploader-action fileuploader-action-remove" title="${captions.remove}"><i></i></a>' +
                                               '</div>' +
                                           '</div>' +
                                           '<div class="progress-bar2">${progressBar}<span></span></div>' +
                                      '</li>',
                                      
                                // thumbnails for the preloaded files {String, Function}
                                item2: '<li class="fileuploader-item file-has-popup">' +
                                            '<div class="columns">' +
                                                '<div class="column-thumbnail">${image}<span class="fileuploader-action-popup"></span></div>' +
                                                '<div class="column-title">' +
                                                    '<a href="${file}" target="_blank">' +
                                                        '<div title="${name}">${name}</div>' +
                                                        '<span>${size2}</span>' +
                                                    '</a>' +
                                                '</div>' +
                                                '<div class="column-actions">' +
                                                    '<a href="${file}" class="fileuploader-action fileuploader-action-download" title="${captions.download}" download><i></i></a>' +
                                                    '<a class="fileuploader-action fileuploader-action-remove" data-id="${data.id}" title="${captions.remove}"><i></i></a>' +
                                                '</div>' +
                                            '</div>' +
                                        '</li>',
                            },

                            onRemove: function(item, listEl, parentEl, newInputEl, inputEl) {
                                if('data' in item && item.data.id) {
                                    $.post(DjangoUrls['motorinsurance:policy-attachment-delete'](item.data.id), function(response) {
                                        return response.success;
                                    });
                                }
                            },
                        });
                    }
                });
            }
        },
    };

    jQuery(function() {
        __FILE_UPLOADER.init();
    });
})();

/* Custom Config and helpers */

// Ajax Setup on Load
$.ajaxSetup({
    data: {
        ajax: true
    },
    complete: function(jqxhr, status) {
        if(jqxhr.responseJSON && 'redirect' in jqxhr.responseJSON) {
            window.location.href = jqxhr.responseJSON.url;
        }
    }
});

$.ajaxPrefilter(function( options ) {
    if(options.type == 'get' && options.data && options.data.indexOf('ajax=true') < 0) {
        options.data += '&ajax=true';
    }
});

//modify buttons style for editable select dropdown
$.fn.editableform.buttons =
    '<button type="submit" class="btn btn-success editable-submit btn-sm"><i class="ti-check"></i></button>' +
    '<button type="button" class="btn btn-danger editable-cancel btn-sm"><i class="ti-close"></i></button>';

// Custom global closures
$.fn.fadeInOrOut = function(status) {
    return status ? this.fadeIn(100) : this.fadeOut(100);
};
$.fn.addRemoveClass = function(status, class_name) {
    return status ? this.addClass(class_name) : this.removeClass(class_name);
};

$.fn.toggleProp = function(status, prop, val1, val2) {
    return status ? this.prop(prop, val1) : this.prop(prop, val2);
};

// Text editor global config
$.trumbowyg.config = {
    btns: [
        ['strong', 'em', 'del'],
        ['undo', 'redo'], // Only supported in Blink browsers
        ['link'],
        ['unorderedList', 'orderedList'],
    ],
    autogrow: true
};

//Handlebar custom helpers
Handlebars.registerHelper('times', function(n, block) {
    var accum = '';
    for(var i = 1; i <= n; ++i) accum += block.fn(i);
    return accum;
});

Handlebars.registerHelper('ifCond', function(v1, v2, options) {
    if(v1 === v2) {
        return options.fn(this);
    }
    return options.inverse(this);
});

Handlebars.registerHelper('replaceWith', function(str, find, replacewith) {
    return str.replace(new RegExp(find , 'g'), replacewith);
});

Handlebars.registerHelper('slugify', function(text) {      
  return Utilities.General.slugify(text);
});

Handlebars.registerHelper('lowercase', function(text) {      
  return text.toLowerCase();
});

Handlebars.registerHelper('felixUrl', function(str, params) {      
  return DjangoUrls[str](params);
});

Handlebars.registerHelper('money', function(number, decimals) {
  if(decimals === undefined) decimals = 0;
  if(number) return accounting.format(number, decimals);

  return number;
});

Handlebars.registerHelper('json_stringify', function(obj) {
    return (typeof(obj) == 'object') ? JSON.stringify(obj) : obj;
});

Handlebars.registerHelper('userDealUpdateDD', function(deal_id, user_id, text, app_name) {
    var user_list = "{'value': -1, 'text': '-----'},";
    var i = 0;
    var empty_class = '';
    $('#id_assigned_to option').each(function() { 
        var text = $(this).text();
        text = (text + '').replace(/[\\"']/g, '\\$&').replace(/\u0000/g, '\\0');

        if($(this).val() != 'unassigned' && $(this).val()) {
            user_list += "{'value': '" + $(this).val() + "', 'text': '" + text + "'},";
        }
    });

    if(app_name === undefined)
        app_name = 'motorinsurance';

    if(text && text.toLowerCase() == 'unassigned') {
        text = '';
        user_id = '';
    }

    return '<a href="javascript:"' +
            'class="deal-inline-update-field select-editable editable"' +
            'data-name="assigned_to_id"' +
            'data-type="select"' +
            'data-emptytext="Add"' +
            'data-pk="' + deal_id + '"' +
            'data-value="' + user_id + '"' +
            'data-source="[' + user_list + ']"' +
            'data-url="' + DjangoUrls[app_name + ':update-deal-field'](deal_id, 'deal') + '"' +
            'data-title="Select">' + text +
        '</a>';
});

Handlebars.registerHelper('producerDealUpdateDD', function(deal_id, user_id, text) {
    var user_list = "{'value': -1, 'text': '-----'},";
    var i = 0;
    var empty_class = '';
    $('#id_producer option').each(function() {
        var text = $(this).text();
        text = (text + '').replace(/[\\"']/g, '\\$&').replace(/\u0000/g, '\\0');
        if($(this).val() != 'unassigned' && $(this).val()) {
            user_list += "{'value': '" + $(this).val() + "', 'text': '" + text + "'},";
        }
    });

    if(text === undefined) {
        text = '';
        user_id = '';
    } else if(text && text.toLowerCase() == 'unassigned') {
        text = '';
        user_id = '';
    }

    return '<a href="javascript:"' +
            'class="deal-inline-update-field select-editable editable"' +
            'data-name="producer_id"' +
            'data-type="select"' +
            'data-emptytext="Add"' +
            'data-pk="' + deal_id + '"' +
            'data-value="' + user_id + '"' +
            'data-source="[' + user_list + ']"' +
            'data-url="' + DjangoUrls['motorinsurance:update-deal-field'](deal_id, 'deal') + '"' +
            'data-title="Select">' + text +
        '</a>';
});

Handlebars.registerHelper('policyStatus', function(expiry_date) {
    return (get_date_difference_from_today(expiry_date)>=0)?'active':'expired';
});

Handlebars.registerHelper('policyExpiresIn', function(expiry_date) {
    return get_date_difference_from_today(expiry_date);
});

function get_date_difference_from_today(date) {
    var t1 = new Date().getTime();
    var t2 = new Date(date * 1000).getTime(); // Converting unixtimestamp for expiry date to datetimestamp

    return parseInt((t2-t1)/(24*3600*1000));
}

/* Customers */

var __HELPSCOUT;
;(function() {
    var _this   = '';

    var _deal_id = $('.deal-container').data('id');
    var _modal = $('#modal_helpscout');
    var _helpscout_list_template = $('#row-helpscout-li');
    var _helpscout_conversation_template = $('#row-helpscout-conversation');

    __HELPSCOUT = {
        init: function() {
            _this = this;

            if($('#tab_helpscout').length)
                _this._loadHelpScout();
        },

        _loadHelpScout: function() {
            // Load Converstaion
            $.get(DjangoUrls['core:get-helpscout-conversations-for-deal'](_deal_id), function(response){
                var template = Handlebars.compile(_helpscout_list_template.html());
                var records = '<li class="no-record">No conversation found</li>';

                if('conversations' in response && response.conversations.length) {
                    records = template({'records': response.conversations});
                }
                $('.trail.helpscout-trail').html(records);
            });

            // Single thread
            $('.helpscout-trail').on('click', '.helpscout-converstaion-trigger', function() {
                _modal.find('h1').html($(this).data('subject'));
                _modal.find('a.helpscout_url').prop('href', $(this).data('link'));
                _modal.find('.content').html('');
                _modal.find('.loader').removeClass('hide');
                _modal.show();

                $.get(DjangoUrls['core:get-helpscout-conversation-threads-for-deal'](_deal_id, $(this).data('id')), function(response) {
                    var template = Handlebars.compile(_helpscout_conversation_template.html());
                    var records = '<div class="no-record">No conversation found</div>';

                    if(response.length)
                        records = template({'records': response});

                    _modal.find('.content').html(records);
                    _modal.find('.loader').addClass('hide');
                });
            });
        }
    };

    jQuery(function() {
        __HELPSCOUT.init();
    });

})();

/*
    User Profile
*/
;
'Use Strict';

var __INVITES;
;(function() {
    var SELECTORS = {
    };

    var _this = '';
    var _form = $('#agent_form');

    __INVITES =
    {
        init: function()
        {
            _this = this;

            $('.formset_row').formset({
                addText: '<span class="font-12"><i class="ti-plus"></i> Add another user</span>',
                deleteText: '<i class="ti-close"></i>',
                prefix: 'invitations_formset',
                added: function(row) {
                    $(row).find('select').chosen();
                    $(row).find('[type=email]').focus();
                    $(row).find('.errorlist').remove();
                    $('.delete-row:first').hide();
                }, removed: function(row) {
                    $(row).find('.errorlist').remove();
                }
            });
            $('.delete-row:first').hide();
            $('.cancel-invite').click(function() {
                var tr = $(this).closest('tr');
                if(window.confirm('Are you sure you want to cancel this invitation?')) {
                    $.get('/accounts/users/invite/cancel/' + $(this).data('id') + '/', function(response) {
                        tr.remove();
                    });
                }
            });
        }
    };

    jQuery(function() {
        if($('body').hasClass('invitations'))
            __INVITES.init();
    });
})();

/*** Main APP ***/
;'Use Strict';
var __FELIX__;

;(function() {

    var _general_search_field = $('#general_search_field');
    var _general_search_results_container = $('.app-search .search-results-container');
    var _felix_table = $('table.felix-table');
    var _felix_table_filters = $('.table-filters');

    var _info_container = $('.info-container');

    var _deal_id = $('.deal-container').data('id');
    var _agent_id = $('body').data('agent');

    var _this = '';

    __FELIX__ =
    {
        // Onload
        init: function()
        {
            _this = this;
            _this.initSearchableSelect();
            _this.initNavbar();
            _this.initPasswordToggler();
            _this.initLoader();
            _this.initGeneralSearch();
            _this.initMenuItem();
            _this.initComponents();
            _this.initToggleSearch();
            _this.initDatepicker();
            _this.initDeleteRecord();
            _this.initMoneyField();
            _this.initTabOnLoad();
            _this.initInfoContainer();
            _this.initAutocompleteField();
            _this.initTitleTooltip();
            _this.initImagePreview();
            _this.loadRenewalsCounter();

            // $.datepicker.setDefaults({format: 'dd-mm-yy'});

            if($('#audit-trail').length)
                $('#audit-trail').DataTable({"order": [[ 3, "desc" ]]});

            if($('table#attachments').length)
                $('table#attachments').DataTable();

            $('body').on('click', function(e) {
                var felix_table_search_popup = _felix_table_filters.find('form .search-popup');

                if (!_general_search_results_container.is(e.target) && _general_search_results_container.has(e.target).length === 0) 
                    if (!_general_search_field.is(e.target) && _general_search_field.has(e.target).length === 0) 
                        _general_search_results_container.fadeOut('fast');

                if (!felix_table_search_popup.is(e.target) && felix_table_search_popup.has(e.target).length === 0) 
                    if (!$('.filter-trigger').is(e.target) && $('.filter-trigger').has(e.target).length === 0) 
                        felix_table_search_popup.fadeOut('fast');
            });

            $(document).keydown(function(event) { 
                if (event.keyCode == 27) { 
                    if($('.felix-modal-container').is(':visible')) {
                        $('.felix-modal-container').each(function() {
                            felixModal.close($(this));
                        });
                    }
                }
            });

            $('.select-with-reset').on('click', '.reset', function() {
                $(this).siblings('select').val('').trigger('chosen:updated');
            });

            $(document).on('change', '.editable-input select', function() {
                var parent = $(this).closest('.editable-container');
                var elem = parent.parent().find('.select-editable');

                if(elem && elem.data('name') == 'producer_id' && loggedin_user_data.ROLE == 'producer' && $(this).val() != loggedin_user_data.ID) {
                    if(!window.confirm('If you assign this deal to another producer then you will no longer be able to see it. Do you want to go ahead and unassign yourself?')) {
                        parent.find('.editable-cancel').click();
                    }
                }
            });

            $('#product_line_switcher').change(function() {
                let val = $(this).val();
                window.location.href = DjangoUrls[val + ':deals']();
            });
        },

        /***** INIT Functions *****/

        _loadLibs: function() {
            _this.initSearchableSelect();
            _this.initDatepicker();
            _this.initMoneyField();
            _this.initAutocompleteField();

            __XEDITABLE.init();
            __FILE_UPLOADER.init();
        },

        initTitleTooltip: function() {
            $(function() {
                $(document).tooltip({
                    tooltipClass: 'felix-ui-tooltip',
                    show: null,
                    hide: null,
                    position: { my: "left-10 top+15", at: "left bottom", collision: "flipfit" }
                });
            });
        },

        loadRenewalsCounter: function() {
            if($('.renewals-menu-counter').length) {
                $.get(DjangoUrls['motorinsurance:renewals-count'](), function(res) {
                    if(res.count)
                        $('.renewals-menu-counter .badge-counter').html(res.count).addClass('visible');
                });
            }
        },

        initImagePreview: function() {
            $.previewImage();
        },

        initSearchableSelect: function() {
            if($('select:visible').length) {
                $('select:visible').each(function() {
                    if (!$(this).data('select2')) {
                        if($(this).hasClass('sorted')) {
                            var options = $(this).find('option').sort(function(a, b) {
                                return a.text < b.text ? -1 : a.text > b.text ? 1 : 0;
                            });
                            $(this).empty().append(options);
                        }
                        $(this).chosen({
                            placeholder_text_single: "Select option...",
                            no_results_text: "No record found"
                        });
                    }
                });
            }
        },

        initAutocompleteField: function() {

            $('.autocomplete-field').on('input', function() {
                $('#' + $(this).data('target')).val('');
                $(this).parent().removeClass('new');
            });
            $('.autocomplete-field').on('blur', function() {
                if(!$(this).val()) return;
                if($('#' + $(this).data('target')).val()) {
                    $(this).parent().removeClass('new');
                }
                else {
                    $(this).parent().addClass('new');
                }
            });
            $('.autocomplete-field').autocomplete({
                minLength: 2,
                source: function(request, response) {
                    var element = $(this.element);
                    element.parent().addClass('loader');

                    $.ajax({
                        url: element.data('url'),
                        method: 'GET',
                        data: {
                            search_term: request.term
                        },
                        success: function( data ) {
                            element.parent().removeClass('loader');
                            response(data);
                        }
                    });
                },
                focus: function(event, ui) {
                    // $(this).val(ui.item.label);
                    // return false;
                },
                select: function(event, ui) {
                    $(this).val(ui.item.label);
                    $(this).removeClass('new');
                    $('#' + $(this).data('target')).val(ui.item.id);

                    if($('body').hasClass('mortgage-deals') || ($('body').hasClass('customers') && $('body').hasClass('mortgage'))){
                        let result = ui.item.desc.trim();
                        result = result.replace(/\s/g, "");
                        result = result.split("|");
                        const email = result[0].replace("E:", "");
                        const tel = result[1].replace("T:", "");
                        $('#id_customer_email').val(email)
                        $('#id_customer_phone').val(tel)

                        $('#modal_create_mortgage_deal #id_customer_email').val(email)
                        $('#modal_create_mortgage_deal #id_customer_phone').val(tel)
                    }

                    return false;
                },
                response: function(event, ui) {
                    if(ui.content.length)
                        $(this).parent().removeClass('new');
                    else
                        $(this).parent().addClass('new');
                }
            }).autocomplete("instance")._renderItem = function(ul, item) { 
                var content = '';

                if('label' in item) content += '<span>' + item.label + '</span>';
                if('desc' in item)  content += item.desc;

                return $("<li>").append(content).appendTo(ul);
            };
        },

        initPasswordToggler: function() {
            $('.password-show-toggle').click(function() {
                var field = $(this).prev('input');

                if(field.is(':password')) {
                    $(this).html('<i class="ti-eye"></i>');
                    field.attr('type', 'text');
                } else {
                    $(this).html('<i class="ti-eye c-lgrey"></i>');
                    field.attr('type', 'password');
                }
            });
        },

        initInfoContainer: function(){
            _info_container.on('click', '.toggle-details', function() {
                $(this).toggleClass('less').closest('.info-table').find('.collapsable').slideToggle(100, function() {
                    // if ($(this).is(':visible'))
                    $(this).toggleClass('flex');
                });
            });

            _info_container.on('click', '.toggle-deal-processes', function() {
                $(this).toggleClass('show-div');
                if ($('body').hasClass('mortgage-deals')){
                    $('.mortgage-deal-processes').slideToggle(100);
                } else {
                    $('.deal-processes').slideToggle(100);
                }
            });
        },

        initTabOnLoad: function() {
            var anchor = Utilities.General.getUrlAnchor();

            if(anchor && $('a[href="#'+anchor+'"]').length) {
                $('a[href="#'+anchor+'"]').click();
            }
        },

        initGeneralSearch: function() {
            var st;
            _general_search_field.focus(function() {
                var val = $(this).val();
                if(val) _general_search_results_container.fadeIn('fast');
            });
            _general_search_field.keyup(function() {
                clearTimeout(st);
                st = setTimeout(function() {
                    _general_search_results_container.fadeIn('fast');
                }, 1000);
            });
        },

        initMoneyField: function() {
            if(!$('.auto-format-money-field').length) return;
            // Restrict to numbers comma and dot only
            $('body').on('input', '.auto-format-money-field',function() {
                var value = $(this).val()
                if($('body').hasClass('mortgage-deals')){
                    return $(this).val(accounting.formatNumber(value, 0, ',', '.'));
                }
                value = value.replace(/[^0-9.,]*/g, '');
                value = value.replace(/\.{2,}/g, '.');
                value = value.replace(/\.,/g, ',');
                value = value.replace(/\,\./g, ',');
                value = value.replace(/\,{2,}/g, ',');
                value = value.replace(/\.[0-9]+\./g, '.');

                // $(this).val(value);
            });
            // Form money field after user has done typing
            $('body').on('blur', '.auto-format-money-field', function(event) {
                $(this).val(function(index, value) {
                    if($(this).val()!=''){
                        if($('body').hasClass('mortgage-deals')){
                            return accounting.formatNumber($(this).val(), 0, ',', '.');
                        }else{
                            return accounting.formatNumber($(this).val(), 2, ',', '.');
                        }
                    }
                });
            });
            // Form money field on focus to convert it back to integer
            $('body').on('focus', '.auto-format-money-field', function(event) {
                $(this).val(function(index, value) {
                    if($(this).val()!=''){
                        return accounting.unformat($(this).val());
                    }
                });
            });
            // Format all money fields on page load
            $('.auto-format-money-field').blur();
        },

        initNavbar: function () {
            $('.navbar-toggle').on('click', function (event) {
                $(this).toggleClass('open');
                $('#navigation').slideToggle(400);
            });

            $('.navigation-menu>li').slice(-1).addClass('last-elements');

            $('.navigation-menu li.has-submenu a[href="#"]').on('click', function (e) {
                if ($(window).width() < 992) {
                    e.preventDefault();
                    $(this).parent('li').toggleClass('open').find('.submenu:first').toggleClass('open');
                }
            });
        },

        initLoader: function () {
            $(window).on('load', function () {
                $('#status').fadeOut();
                $('#preloader').delay(350).fadeOut('slow');
                $('body').delay(350).css({
                    'overflow': 'visible'
                });
            });
        },

        // === following js will activate the menu in menu bar based on url ====
        initMenuItem: function () {
            $(".navigation-menu a").each(function () {
                var current_nav = $('body').data('current-nav');

                if ($(this).data('elem') == current_nav) { 
                    // $(this).parent().addClass("active"); // add active to li of the current link
                    $(this).parent().parent().parent().addClass("active"); // add active class to an anchor
                    // $(this).parent().parent().parent().parent().parent().addClass("active"); // add active class to an anchor
                }
            });
        },

        initComponents: function () {
            if($('[data-toggle="tooltip"]').length)
                $('[data-toggle="tooltip"]').tooltip();
            if($('[data-toggle="popover"]').length)
                $('[data-toggle="popover"]').popover();
        },

        initToggleSearch: function () {
            $('.toggle-search').on('click', function () {
                var targetId = $(this).data('target');
                var $searchBar;
                if (targetId) {
                    $searchBar = $(targetId);
                    $searchBar.toggleClass('open');
                }
            });
        },

        initDatepicker: function() {
            if($('.datepicker').length)
                $('.datepicker').each(function() {
                    var options = {
                        format: 'dd-mm-yyyy',
                        autoclose: true,
                    };
                    if($(this).data('start-date-today'))
                        options['startDate'] = new Date;

                    $(this).datepicker(options);
                });

            if($('.datepicker-custom').length)
                $('.datepicker-custom').each(function() {
                    var options = {
                        format: 'dd-mm-yyyy',
                        autoclose: true,
                    };
                    if($(this).data('start-date-today'))
                        options['startDate'] = new Date;

                    $(this).datepicker(options);
                });
        },

        initDeleteRecord: function() {
            $('.btn-delete-record').click(function() {
                var redirect_url = $(this).data('redirect-to');
                if(window.confirm('Are you sure you want to delete this record?')) {
                    $.get($(this).data('url'), function(response) {
                        if(response.success) {
                            Utilities.Notify.success('Record deleted successfully.', 'Success');
                            if(redirect_url) {
                                setTimeout(function() {
                                    window.location = redirect_url;
                                }, 2000);
                            }
                        } else {
                            Utilities.Notify.error(response.error, 'Error');
                        }
                    }).fail(function(resp) {
                        if(resp.status == 403) {
                            Utilities.Notify.error('You do not have permission to delete a motor deal. Please check with your manager for details.', 'Permission Denied');
                        }
                    });
                }
            });
        },
    };

    jQuery(function() {
        __FELIX__.init();
    });
})();

/*** NOTE Form and List ***/
;'Use Strict';
var __NOTE;

;(function() {
    var _this = '';
    var _note_form = $('#note_form');

    __NOTE =
    {
        // Onload
        init: function()
        {
            _this = this;
            _this.initForm();
        },

        initForm: function() {
            if(_note_form.length) {

                $('[data-felix-modal="modal_add_note"]').click(function() {
                    _note_form.find('textarea').val('');
                });
                _note_form.ajaxForm({
                    beforeSubmit: Utilities.Form.beforeSubmit,
                    error: Utilities.Form.onFailure,
                    success: function(response, status, xhr, form) {
                        form.find('button[type=submit]').removeClass('loader');

                        if(response.success) {
                            Utilities.Notify.success('Note added successfully.', 'Success');

                            _note_form.find('[data-modal-close]').click();

                            var note = '<div class="label">Note created</div>';
                                if('note_pk' in response.note){
                                    note += '<div class="note note-id-'+response.note.note_pk+'">' + response.note.content + '</div>';
                                }else{
                                    note += '<div class="note">' + response.note.content + '</div>';
                                }
                                note += '<div class="text-muted">' + response.note.created_on + ' ';
                                note += 'by ' + response.note.added_by;
                                note += '</div>';
                                if('note_pk' in response.note){
                                    note += '<div><span title="Click to remove" id="delete-mortgage-note" data-deleteurl="/mortgage/deals/notes/delete/'+response.note.note_pk+'/" onclick="deleteMortgageNote(this)" class="remove task-remove"> <i class="ti-trash"></i> </span> <span title="Click to edit" data-felix-modal="modal_update_note"  data-pk="'+response.note.note_pk+'" class="edit task-edit" onclick="editMortgageNote(this)"><i class="ti-pencil-alt"></i></span></div>'
                                }

                            _this._prependNoteInTrail(note);
                        } else {
                            Utilities.Notify.error('Please check all the required fields.', 'Error');
                            Utilities.Form.addErrors(form, response.errors);
                        }
                    }
                });
            }
        },

        _prependNoteInTrail: function(content) {
            $('.note-trail').prepend('<li>' + content + '</li>');
            $('.note-trail').removeClass('hide');
            $('.small-note.note-trail').remove();
        },
    };

    jQuery(function() {
        __NOTE.init();
    });
})();

/* POLICIES */
;
'Use Strict';

var __POLICY;
;(function() {

    var _this   = '';
    var _table  = $('#policy-table');
    var _form   = $('#policy_form');
    var _filter_form   = $('#policy-search');

    var _customer = $('#id_customer');
    var _deal = $('#id_deal');
    var _quote = $('#id_quote');
    var _quoted_product = $('#id_quoted_product');
    var _product = $('#id_product');

    var _show_loader_class = 'show-loader';
    var _deal_id = $('.deal-container').data('id');
    var _policy_document = $('#id_policy_document');

    var _quote_container = $('.quote-container');
    var _quoted_product_container = $('.qp-container');

    var _felix_table_filters = $('.table-filters');
    var _felix_table_quick_filters = $('.quick-filters');

    var _policy_modal = $('#modal_view_policy');
    var _policy_view_template = $('#policy-view-modal-template');

    var _deal_stage_container = $('.deal-processes');

    var _import_csv_uploader = $('input[name=policy_import_file]');

    __POLICY =
    {
        init: function()
        {
            _this = this;

            _form.ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: Utilities.Form.onSuccess,
                error: Utilities.Form.onFailure
            });

            $("#search-clear").on("click", function () {
                window.location.href = $("#policy-search").data("reset-url");
            });

            if(_import_csv_uploader.length) {
                _this._policy_import_uploader();
            }

            var filter_count = Utilities.Form.addFilterCount(_filter_form);
            if(filter_count) {
                $('.filter-count').html(filter_count).removeClass('hide');
            }

            _policy_document.change(function() {
                // _this._showFilePreview();
            });

            // Save Only
            _deal_stage_container.on('click', '.create-policy', function() {
                $(this).addClass(_show_loader_class);
                $('#policy_form #id_send_email').val('');
                $('#policy_form').submit();
            });

            // Save and Send
            _deal_stage_container.on('click', '.create-send-policy', function() {
                $('.create-send-policy').addClass(_show_loader_class);
                $('#policy_form #id_send_email').val('1');

                $.get(DjangoUrls['motorinsurance:get-deal-json'](_deal_id), function(response) {
                    if(response.customer.email == '') {
                        $('[data-felix-modal="modal_edit_customer_email"]').click();
                        $('.create-send-policy').removeClass(_show_loader_class);
                    } else {
                        $('#policy_form').submit();
                    }
                });
            });
        },

        _getPolicyDetail: function(pid) {
            $('#modal_view_policy').find('.content').html('<p class="m-t-50 m-b-50">Loading...</p>');
            $.get(DjangoUrls['motorinsurance:policy-json'](pid), function(response) {
                var source   = $('#policy-view-modal-template').html();
                var template = Handlebars.compile(source);

                $('#modal_view_policy').find('.content').html(template(response));
            });
        },

        _initDT: function() {
            if(_table.length)
                _table.DataTable();
        },

        _updateTableAttributes: function(data) {
            $('.policies-total-amount').html(data.total_policies_display);
        },

        _fillFormOnLoad: function() {
            if(_customer.val()) {
                _this._fetchOptions('customer', _customer.val());
            }
        },

        _showFilePreview: function() {
            var input = document.getElementById('id_policy_document');
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.onload = function (e) {
                    var output = document.getElementById('file_preview_frame');
                    $(output).show();
                }
                reader.readAsDataURL(input.files[0]);
            }
        },

        _policy_import_uploader: function() {
            _import_csv_uploader.fileuploader({
                enableApi: true,
                changeInput: `<div class="fileuploader-input">
                                <div class="fileuploader-input-inner">
                                    <h3 class="fileuploader-input-caption">
                                        <span>Drag and drop your csv file here</span>
                                    </h3>
                                    <p>or</p>
                                    <div class="fileuploader-input-button">
                                        <span class="btn btn-primary">Click here to browse</span>
                                    </div>
                                </div>
                              </div>`,
                theme: 'dragdrop',
                upload: {
                    url: _import_csv_uploader.data('url'),
                    data: null,
                    type: 'POST',
                    enctype: 'multipart/form-data',
                    start: true,
                    synchron: true,
                    beforeSend: null,
                    onSuccess: function(result, item) {
                        if(result && result.success) {
                            $('#modal_policy_import .input-container').addClass('hide');
                            $('#modal_policy_import .success-message').removeClass('hide');
                        }
                    },
                    onError: function(item) {
                        var progressBar = item.html.find('.progress-bar2');
                        if (progressBar.length > 0) {
                            progressBar.find('span').html(0 + "%");
                            progressBar.find('.fileuploader-progressbar .bar').width(0 + "%");
                            item.html.find('.progress-bar2').fadeOut(400);
                        }
                        item.upload.status != 'cancelled' && item.html.find('.fileuploader-action-retry').length == 0 ? item.html.find('.column-actions').prepend('<a class="fileuploader-action fileuploader-action-retry" title="Retry"><i></i></a>') : null;
                    },
                    onProgress: function(data, item) {
                        var progressBar = item.html.find('.progress-bar2');
                        if (progressBar.length > 0) {
                            progressBar.show();
                            progressBar.find('span').html(data.percentage + "%");
                            progressBar.find('.fileuploader-progressbar .bar').width(data.percentage + "%");
                        }
                    },
                    onComplete: null,
                },
            });
        }

    };

    jQuery(function() {
        __POLICY.init();
    });
})();

/*
    User Profile
*/
;
'Use Strict';

var __PROFILE;
;(function() {
    var SELECTORS = {
    };

    var _this = '';
    var _profile_form = $('#profile_form');
    var _password_form = $('#profile_password_form');

    __PROFILE =
    {
        init: function()
        {
            _this = this;

            // Strength Meter
            $('#id_new_password').keyup(function() {
                var strength = Utilities.Form.passwordStrength($(this).val());

                $('.strength-meter').removeClass('very-weak weak strong very-strong');
                if(strength == 0) {
                }
                else if(strength < 2) {
                    $('.strength-meter').addClass('very-weak');
                }
                else if(strength < 3) {
                    $('.strength-meter').addClass('weak');
                }
                else if(strength < 4) {
                    $('.strength-meter').addClass('strong');
                }
                else if(strength <= 5) {
                    $('.strength-meter').addClass('very-strong');
                }
            });

            $('#id_image').change(function(e) {
                var reader = new FileReader();
                reader.onload = function() {
                    $('.profile-image-container').css({'background-image': 'url('+ reader.result +')'});
                };
                reader.readAsDataURL(e.target.files[0]);
            });

            $('.upload-new').click(function(){
                $('#id_image').click();
                $('#id_remove_avatar').val('');
            });

            $('.remove-avatar').click(function() {
                $('#id_remove_avatar').val('1');
                $('#id_image').val('');
                $('.profile-image-container').css({'background-image': 'none'});
            });

            _profile_form.ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: Utilities.Form.onSuccess,
                error: Utilities.Form.onFailure
            });

            _password_form.ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: Utilities.Form.onSuccess,
                error: Utilities.Form.onFailure
            });

        }
    };

    jQuery(function() {
        __PROFILE.init();
    });
})();

if (typeof module === "object" && typeof module.exports === "object") {
    module.exports = __PROFILE;
}

/*
    Company Settings
*/
;
'Use Strict';
var _quoted_products_data;
var __QUOTES;
;(function() {
    var SELECTORS = {
    };

    var _this = '';
    var _form = $('#quote_form');
    var _filter_form = $('#quotes-search');
    var _payment_form = $('#payment_form');
    var _products = $('.products-container');
    var _temp_products = $('.temp-product-row');
    var _product_field = $('.product-field');
    var _deal = $('#id_deal');
    var _add_product = $('.add-product');
    var _add_another_product = $('.add-another-product');
    var _remove_product = $('.remove-product');
    var _update_and_send = $('.update-and-send-email');

    var _show_loader_class = 'show-loader';

    var _quote_payment_selected_product = $('#id_selected_product');
    var _quote_payment_selected_addons = $('#id_selected_add_ons');

    var _deal_id = $('.deal-container').data('id');
    var _deal_stages_breadcrumb = $('.deal-stages-breadcrumb');
    var _deal_stage_container = $('.deal-processes');

    var _auto_quoter_xhr_form_request = false;

    _quoted_products_data = {'products': [], 'quote': {'status': true, 'email': false, 'delete': false}};


    __QUOTES =
    {
        init: function()
        {
            _this = this;
            // _this._initForms();
            _this._addProduct();
            _this._editProduct();
            _this._removeProduct();
            _this._fillAddonsOnload();
            _this._checkDeal();
            _this._productStatusChange();
            _this._triggerAutoQuoteForm();
            _this._extendQuoteExpiry();

            _deal_stage_container.on('change', '.product-field', function() {
                if(__app_name != 'motorinsurance') return;
                    _this._getAddons(
                        $(this).val(),
                        $(this).closest('.product-row').find('.product-addons')
                    );

                var product = window.products_data[$(this).val()];

                $('.quote-form .form #id_agency_repair').prop('disabled', !product.allows_agency_repair);
                $('.quote-form .form #id_agency_repair').closest('label').addRemoveClass(!product.allows_agency_repair, 'disabled');
            });

            if(_deal.length) {
                _this._getDeal();
                _deal.change(function() {
                    _this._getDeal();
                });
            }

            if(_quote_payment_selected_product.length) {
                _quote_payment_selected_product.change(function(event) {
                    _this._getQuotedProductAddons(
                        $(this).val(),
                        _quote_payment_selected_addons
                    );
                });

                _quote_payment_selected_product.trigger('chosen:updated');

                if($('#selected-add-ons').data('addons')) {
                    var addons = $('#selected-add-ons').data('addons').split(',');
                    setTimeout(function(){
                        _quote_payment_selected_addons.val(addons).change();
                    }, 2000);
                }

            }

            $("#search-clear").on("click", function () {
                window.location.href = $("#quotes-search").data("reset-url");
            });

            var filter_count = Utilities.Form.addFilterCount(_filter_form);
            if(filter_count) {
                $('.filter-count').html(filter_count).removeClass('hide');
            }

            _update_and_send.click(function() {
                $('#notify_customer').prop('checked', true);
                _form.submit();
            });

            _payment_form.ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: Utilities.Form.onSuccess,
                error: Utilities.Form.onFailure
            });

            // Save Only
            _deal_stage_container.on('click', '.quote-submit', function() {
                if($(this).hasClass(_show_loader_class)) return;

                var current_product_length = $('.products-preview .products .row.product').length;

                if(!current_product_length) {
                    if(window.confirm('Are you sure you want to delete this quote? \nYou cannot undo this.')){
                        _quoted_products_data['quote']['email'] = false;
                        _quoted_products_data['quote']['delete'] = true;
                        $(this).addClass(_show_loader_class);
                        _this._submitQuoteForm(false);

                        _deal_stages_breadcrumb.find('[data-item=quote-overview] .duration').remove();
                        _deal_stages_breadcrumb.find('[data-item=quote-overview] .quote-views').remove();
                    }
                } else {
                    _quoted_products_data['quote']['email'] = false;
                    $(this).addClass(_show_loader_class);
                    _this._submitQuoteForm(false);
                }
            });

            // Save and Send
            _deal_stage_container.on('click', '.quote-submit-send', function() {
                if($(this).hasClass(_show_loader_class)) return;

                _quoted_products_data['quote']['email'] = true;
                $(this).addClass(_show_loader_class);

                $.get(DjangoUrls[`${__app_name}:get-deal-json`](_deal_id), function(response) {
                    if(response.customer.email == '') {
                        $('[data-felix-modal="modal_edit_customer_email"]').click();
                        $('.quote-submit-send').removeClass(_show_loader_class);
                    } else {
                        _this._submitQuoteForm(true, 'quote' in response && response.quote.id);
                    }
                });
            });

            _deal_stage_container.on('change', '#id_quote_status', function() {
                _quoted_products_data['quote']['status'] = $(this).is(':checked');
                $('.quote-submit-send').attr('disabled', !$(this).is(':checked'));
            });

            _deal_stage_container.on('blur', '#id_premium', function() {
                if(parseInt($('#id_sale_price').val()) == 0) {
                    $('#id_sale_price').val($('#id_premium').val()).blur();
                }
            });
        },

        _initForms: function() {
            _form.ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: Utilities.Form.onSuccess,
                error: Utilities.Form.onFailure
            });
        },

        _extendQuoteExpiry: function() {
            _deal_stage_container.on('click', '.extend-quote-expiry a', function() {
                if(window.confirm('Are you sure you want to extend the expiry of this quote?')) {
                    $.post(DjangoUrls['motorinsurance:deal-quote-extend'](_deal_id), function(response) {
                        if(response.success) {
                            Utilities.Notify.success('Quote updated successfully', 'Success');
                            $('.extend-quote-expiry').hide();
                        } else {
                            Utilities.Notify.error('Something went wrong. Please try again later.', 'Error');
                        }
                    });
                }
            });
        },

        _productStatusChange: function() {
            _deal_stage_container.on('change', '.product-status-checkbox', function() {
                var index = $(this).data('id');
                var checked = $(this).is(':checked');

                $.each(_quoted_products_data['products'], function(k, v) {
                    if(k == index) {
                        v['published'] = checked;
                    }
                });
            });
        },

        _submitQuoteForm: function(send_email, updated) {
            $.ajax({
                type: "POST",
                url: DjangoUrls[`${__app_name}:deal-quoted-products-json`](_deal_id),
                data: JSON.stringify(_quoted_products_data),
                success: function(response) {
                    if(response.success) {
                        Utilities.Notify.success('Quote updated successfully', 'Success');

                        if(response.creating && !response.deleted && __app_name == 'motorinsurance') {
                            $.get(DjangoUrls[`${__app_name}:get-deal-json`](_deal_id), function(r) {
                                __AMPLITUDE.logEvent(
                                    __AMPLITUDE.event('motor_quote_created'),
                                    {
                                        'deal_id': _deal_id,
                                        'deal_created_date': r.deal.created_on,
                                        'vehicle make': r.deal.vehicle_make,
                                        'vehicle_model_year': r.deal.vehicle_year,
                                        'vehicle_model': r.deal.vehicle_model,
                                        'vehicle_body_type': r.deal.vehicle_body_type,
                                        'vehicle_sum_insured': r.deal.insured_car_value,

                                        'client_nationality': r.customer.nationality,
                                        'client_gender': r.customer.gender,
                                        'client_age': r.customer.age
                                    }
                                );
                            });
                        }

                        if(response.deleted) {
                            _quoted_products_data['products'] = [];
                        }

                        var deals_cls = __DEALS;

                        if(send_email) {
                            var email_type = updated?'quote_updated':'new_quote';
                            deals_cls._triggerCustomEmailModal(email_type);
                        }

                        var selected_stage = 'quote';
                        if(!$('.products-preview .products .row.product').length)
                            selected_stage = 'new';

                        deals_cls._loadDealStage(selected_stage);

                        $('.stage-warning').addClass('hide');
                    }

                    $('.' + _show_loader_class).removeClass(_show_loader_class);
                },
                'processData': false,
                'contentType': 'application/json'
            });
        },

        _checkDeal: function() {
            var params = Utilities.General.getUrlVars();

            if('deal_id' in params && params['deal_id'] && !_deal.val()) {
                _deal.val(params['deal_id']).change();
            }
        },

        _getQuotedProducts: function() {
            $.get(DjangoUrls[`${__app_name}:deal-quoted-products-json`](_deal_id), function(response) {
                if(response) {
                    _quoted_products_data['products'] = response;
                    _quoted_products_data['quote']['status'] = $('#id_quote_status').is(':checked');

                    _this._renderQuotedProductsPreview();
                }
            });
        },

        _renderQuotedProductsPreview: function(highlight_index) {
            if(highlight_index === undefined) highlight_index = -1;

            $('.deal-form .products-preview .products').html('');
            $.each(_quoted_products_data['products'], function(k, v) {
                if(v === undefined || ('deleted' in v && v.deleted)) return;
                var source   = $('#deal-quote-add-product-template').html();
                var template = Handlebars.compile(source);
                v['index'] = k;
                $('.deal-form .products-preview .products').append(template(v));
            });
            _this._toggleProductFormActionButtons();

            if(highlight_index > -1) {
                $('.products .product[data-id=' + highlight_index + ']').addClass('highlight-success');

                setTimeout(function(){
                    $('.highlight-success').removeClass('highlight-success');
                }, 2000);
            }
        },

        _resetProductForm: function() {
            $('.deal-form .form #id_product').val('');
            $('.deal-form .form #id_product').trigger('chosen:updated');
            $('.deal-form .form #id_default_add_ons').val('');
            $('.deal-form .form #id_default_add_ons').trigger('chosen:updated');
            $('.deal-form .form #id_premium').val('').change();
            $('.deal-form .form #id_sale_price').val('').change();
            $('.deal-form .form #id_insurer_quote_reference').val('');
            $('.deal-form .form #id_deductible').val('').change();
            $('.deal-form .form #id_deductible_extras').val('');
            $('.deal-form .form #id_agency_repair').prop('checked', false);
            $('.deal-form .form #id_agency_repair').prop('disabled', false);
            $('.deal-form .form #id_agency_repair').closest('label').removeClass('disabled');
            $('.deal-form .form #id_ncd_required').prop('checked', false);
        },

        _scrollToProductForm: function() {
            $([document.documentElement, document.body]).animate({
                scrollTop: 100
            }, 200);
        },

        _addProduct: function() {
            $('body').on('click', '.add-another-product', function() {

                $('.deal-overview .new-deal').removeClass('display');
                $('.deal-overview .deal-form').addClass('display');

                $('.deal-form .products-preview').addClass('hide');
                $('.deal-form .form').removeClass('hide');

                $('#edited_id').val('');

                $('.deal-form .form .add-label').removeClass('hide');
                $('.deal-form .form .edit-label').addClass('hide');

                _this._scrollToProductForm();
                _this._resetProductForm();

                __FELIX__.initSearchableSelect();
                __FELIX__._loadLibs();

                $('#id_product').val('').trigger('chosen:updated');
            });

            _deal_stage_container.on('click', '.add-product', function() {

                // Validation
                var error = false;
                $('.error').remove();
                $.each(['#id_product', '#id_premium'], function() {
                    var field = $(this + '');
                    if(!field.val() || parseInt(field.val()) <= 0) {
                        error = true;
                        field.closest('.form-group').append('<div class="error">This field is required</div>');
                    }
                });

                if(error) return;

                var product = window.products_data[$('#id_product').val()];
                var premium = $('#id_premium').val();
                var sale_price = $('#id_sale_price').val();
                var deductible = $('#id_deductible').val();
                if(!accounting.unformat(sale_price))
                    sale_price = premium;
                if(deductible === ""){
                    document.querySelector('#id_deductible').value = parseFloat("0").toFixed(2)
                    deductible = parseFloat("0").toFixed(2)
                }
                var data = {
                    'product_id': $('#id_product').val(),
                    'product_name': product.name,
                    'product_logo': product.logo,
                    'currency': 'Dhs',
                    'default_add_ons': $('#id_default_add_ons').val() || [],
                    'agency_repair': $('#id_agency_repair').is(':enabled:checked'),
                    'ncd_required': $('#id_ncd_required').is(':enabled:checked'),
                    'deductible': deductible,
                    'deductible_extras': $('#id_deductible_extras').val(),
                    'insurer_quote_reference': $('#id_insurer_quote_reference').val(),
                    'premium': premium,
                    'sale_price': sale_price,
                    'insured_car_value': $('#id_insured_car_value').val(),
                    'published': true,
                    'auto_quoted': false,
                    'is_tpl_product': product.is_tpl_product,
                    'allows_agency_repair': product.allows_agency_repair
                };

                let highlight_index = '';

                if($('#edited_id').val().length) {
                    if($('#edited_qp_id').val().length)
                        data['id'] = parseInt($('#edited_qp_id').val());
                    $.each(_quoted_products_data['products'], function(k, v) {
                        if(k == parseInt($('#edited_id').val())) {
                            _quoted_products_data['products'][k] = data;
                        }
                    });
                    highlight_index = parseInt($('#edited_id').val());
                } else {
                    _quoted_products_data['products'].push(data);
                    highlight_index = _quoted_products_data['products'].length - 1;
                }

                _this._renderQuotedProductsPreview(highlight_index);

                $('.deal-form .products-preview').removeClass('hide');
                $('.deal-form .form').addClass('hide');
            });
        },

        _removeProduct: function() {
            _deal_stage_container.on('click', '.product-remove', function() {
                $(this).closest('.row').remove();

                var index = $(this).data('id');

                $.each(_quoted_products_data['products'], function(k, v) {
                    if(k == index) {
                        if('id' in v)
                            v['deleted'] = true;
                        else
                            delete _quoted_products_data['products'][k];
                    }
                });

                _this._toggleProductFormActionButtons();
            });
        },

        _editProduct: function() {
            _deal_stage_container.on('click', '.product-edit', function() {
                var index = $(this).data('id');
                var qpid = $(this).data('qp-id');
                var product = _quoted_products_data['products'][index];

                $('#edited_qp_id').val(qpid);
                $('#edited_id').val(index);

                $('.deal-form .form .add-label').addClass('hide');
                $('.deal-form .form .edit-label').removeClass('hide');

                _this._resetProductForm();
                _this._scrollToProductForm();

                $('.deal-form .products-preview').addClass('hide');
                $('.deal-form .form').removeClass('hide');

                _this.__set_motor_deal_edit_form(product);
            });
        },

        __set_motor_deal_edit_form: function(product) {
            $('.deal-form .form #id_insured_car_value').val(product['insured_car_value']).change();
            $('.deal-form .form #id_premium').val(product['premium']).change();
            $('.deal-form .form #id_sale_price').val(product['sale_price']).change();
            $('.deal-form .form #id_deductible').val(product['deductible']).change();
            $('.deal-form .form #id_deductible_extras').val(product['deductible_extras']);
            $('.deal-form .form #id_insurer_quote_reference').val(product['insurer_quote_reference']);
            $('.deal-form .form #id_agency_repair').prop('checked', product['agency_repair']);
            $('.deal-form .form #id_ncd_required').prop('checked', product['ncd_required']);

            $('.deal-form .form #id_agency_repair').prop('disabled', !product['allows_agency_repair']);
            $('.deal-form .form #id_agency_repair').closest('label').addRemoveClass(!product['allows_agency_repair'], 'disabled');

            $('#id_product option').addClass('hide').trigger('chosen:updated');
            $('#id_product option[data-insurer-id=' + window.products_data[product.product_id].insurer_id + ']').removeClass('hide').trigger('chosen:updated');

            __FELIX__._loadLibs();

            $('.deal-form .form #id_product').val(product['product_id']);
            $('.deal-form .form #id_product').trigger('chosen:updated');

            let all_products_addons = window.products_data[product.product_id].addons;

            if(all_products_addons.length) {
                $('.deal-form .form #id_default_add_ons option').remove();
                $.each(all_products_addons, function(k, v) {
                    let key = Object.keys(this)[0];
                    let val = v[key].label
                    $('.deal-form .form #id_default_add_ons').append(
                        '<option ' + ($.inArray(key, product['default_add_ons'])>-1?'selected':'') + ' value="' + key + '">' + val + '</option>'
                    );
                });
                $('.deal-form .form #id_default_add_ons').trigger('chosen:updated');
            }
        },

        _toggleProductFormActionButtons: function() {
            var quote_id = $('.deal-form').data('quote-id');
            var quoted_product_length = $('.deal-form .products-preview .products .product').length;
            $('.quote-submit-send').prop('disabled',  quoted_product_length <= 0);

            if(!quoted_product_length && !$('.deal-form').data('quote-id')) {
                // _this._resetProductForm();

                // $('.deal-overview .new-deal').addClass('display');
                // $('.deal-overview .deal-form').removeClass('display');

                // $('.deal-form .form').removeClass('hide');
                // $('.deal-form .products-preview').addClass('hide');
            }
        },

        _getAddons: function(val, element) {
            if(!val) return;
            if (window.products_data !== undefined) {
                product = window.products_data[val];
                _this._updateAddonsDD(element, product.addons);
            }
            $.get(DjangoUrls['motorinsurance:product-addons'](val), function(response) {
                $(element).find('option').remove();
                if(response.success) {
                    _this._updateAddonsDD(element, response.addons);
                }
            });
        },

        _getQuotedProductAddons: function(val, element) {
            if(!val) return;
            $.get(DjangoUrls['motorinsurance:quoted-product-addons'](val), function(response) {
                $(element).find('option').remove();
                if(response.success) {
                    _this._updateAddonsDD(element, response.addons);
                }
            });
        },

        _triggerAutoQuoteForm: function() {
            var auto_quote_modal = $('#modal_auto_quote_form');

            $('.deal-container').on('change', '.auto-quote-insurer-field', function() {
                var insurer_code = $(this).val();
                auto_quote_modal.find('.get-auto-quotes').addClass('hide');

                clearAutoQuoteForm();

                if(_auto_quoter_xhr_form_request)
                    _auto_quoter_xhr_form_request.abort();

                if(insurer_code) {
                    auto_quote_modal.find('.content').addClass('loader');
                    _auto_quoter_xhr_form_request = $.get(DjangoUrls['motorinsurance:auto-quote-insurer'](_deal_id, insurer_code))
                        .done(function(response) {
                            auto_quote_modal.find('.auto-quote-form-container').html(response);
                            auto_quote_modal.find('.get-auto-quotes').removeClass('hide');
                            __FELIX__._loadLibs();
                        }).fail(function(jqXHR, textStatus, errorThrown) {
                            Utilities.Notify.error('Please contact support for more details.', 'Error');
                            var error_response = `We’ve encountered an unexpected error and this report will be sent to Felix automatically. In the mean time we suggest you <a data-modal-close class="underline add-another-product" href="javascript:">add a product manually</a> or go back and <a class="show-insurer-modal underline" href="javascript:" data-modal-close>choose another insurer</a>.`;
                            auto_quote_modal.find('.auto-quote-form-container').html(error_response);
                        }).always(function(jqXHR, textStatus) {
                            auto_quote_modal.find('.content').removeClass('loader');
                        });
                }

            });

            $('.deal-container').on('change', '.add-autoquoted-product-checkbox', function() {
                if($('.add-autoquoted-product-checkbox:checked').length)
                    auto_quote_modal.find('.add-selected-quoted-products').removeClass('hide');
                else
                    auto_quote_modal.find('.add-selected-quoted-products').addClass('hide');
            });

            $('.deal-container').on('click', '.add-selected-quoted-products', function() {
                if($('.add-autoquoted-product-checkbox:checked').length) {
                    $.each($('.add-autoquoted-product-checkbox:checked'), function() {
                        _this._addNewAutoQuotedProduct($(this).data('quote'));
                    });

                    $('.add-autoquoted-product-checkbox:checked').prop('checked', false);
                }
                else
                    alert('Please select atleast one product.');
            });

            $('.deal-container').on('click', '[data-felix-modal="modal_auto_quote_form"]', function() {
                clearAutoQuoteForm();

                $('#modal_auto_quote_form #id_auto_quote_insurer').val('').trigger('chosen:updated');
                $('#modal_auto_quote_form .auto-quote-form-container').html('');
            });

            $('.deal-container').on('click', '.get-auto-quotes', function() {
                var insurer = auto_quote_modal.find('.auto-quote-insurer-field').val();
                auto_quote_modal.find('.content').animate({scrollTop: 0}, 'fast');
                clearAutoQuoteForm();

                if(insurer.length) {
                    auto_quote_modal.find('.content').addClass('loader');

                    $.post(DjangoUrls['motorinsurance:auto-quote-insurer'](_deal_id, insurer), $('#auto_quote_form').serialize())
                        .done(function(response) {
                            if(response.success) {
                                if('quotes' in response && response['quotes'].length) {
                                    var source   = $('#autoquoted-product-list-template').html();
                                    var template = Handlebars.compile(source);
                                    auto_quote_modal.find('.response').html(
                                        template({'records': response.quotes})
                                    );
                                } else {
                                    auto_quote_modal.find('.response').html('<span class="error">No quote found for the given details.</span>');
                                }
                            } else {
                                if('errors' in response) {
                                    $('#modal_auto_quote_form ul.error').show();
                                    $.each(response.errors, function() {
                                        $('#modal_auto_quote_form ul.error').append('<li>'+this+'</li>');
                                    });
                                }
                                if('form_errors' in response) {
                                    $.each(response.form_errors, function(k, v) {
                                        if(auto_quote_modal.find('#id_' + k).next('.chosen-container').length)
                                            auto_quote_modal.find('#id_' + k).next('.chosen-container').after('<div class="error">'+v+'</div>');
                                        else
                                            auto_quote_modal.find('#id_' + k).after('<div class="error">'+v+'</div>');
                                    });
                                }
                                auto_quote_modal.find('.content').animate({
                                    scrollTop:  auto_quote_modal.find('div.error:first').offset().top
                                });
                            }
                        }).fail(function(jqXHR, textStatus, errorThrown) {
                            Utilities.Notify.error('Please contact support for more details.', 'Error');
                        }).always(function(jqXHR, textStatus) {
                            auto_quote_modal.find('.content').removeClass('loader');
                        });
                } else {
                    alert('Please select a product.');
                }
            });

            function clearAutoQuoteForm() {
                $('#modal_auto_quote_form .content').removeClass('loader');
                $('#modal_auto_quote_form ul.error').hide();
                $('#modal_auto_quote_form ul.error li').remove();
                $('#modal_auto_quote_form div.error').remove();
                $('#modal_auto_quote_form .response').html('');
                $('#modal_auto_quote_form .add-selected-quoted-products').addClass('hide');
            }
        },

        _addNewAutoQuotedProduct: function(quote) {
            var data = {
                'product_id': quote.pk,
                'product_name': quote.name,
                'product_logo': quote.logo,
                'currency': 'Dhs',
                'default_add_ons': [],
                'agency_repair': quote.agencyRepair,
                'ncd_required': quote.ncd,
                'deductible': accounting.format(quote.deductible, 2),
                'deductible_extras': '',
                'insurer_quote_reference': quote.quoteReference || '',
                'premium': accounting.format(quote.premium, 2),
                'sale_price': accounting.format(quote.premium, 2),
                'insured_car_value': accounting.format(quote.insuredCarValue, 2),
                'published': true,
                'auto_quoted': true
            };

            _quoted_products_data['products'].push(data);
            _this._renderQuotedProductsPreview(_quoted_products_data['products'].length - 1);

            $('.deal-overview .new-deal').removeClass('display');
            $('.deal-overview .deal-form').addClass('display');
            $('.deal-form .form').addClass('hide');
            $('.deal-form .products-preview').removeClass('hide');

            let message = quote.name + '(' + (quote.agencyRepair?'Agency':'Non-Agency') + ')';

            Utilities.Notify.success(message + ' added successfully', 'Success');
        },

        _updateAddonsDD: function(element, addons) {
            $.each(addons, function(key, addon) {
                var selected = '';
                var addon_key = Object.keys(addon)[0];
                var addon_value = addon[addon_key].label;
                var price = addon[addon_key].price;

                var selected_addons = element.closest('.addons').data('selected-addons');

                if(typeof selected_addons !== 'undefined' && selected_addons) {
                    if(typeof selected_addons == 'string') selected_addons = selected_addons.split(',');
                    $.each(selected_addons, function(k, v){
                        if(v == addon_key) {
                            selected = 'selected';
                            return false;
                        }
                    });
                }
                $(element).append(
                    '<option data-price="'+price+'" value='+addon_key+' '+selected+'>'+addon_value+'</option>'
                );
            });
            $(element).trigger('chosen:updated');
        },

        _getDeal: function() {
            if(!_deal.val()) return;
            $('.preloader').show();
            let url = DjangoUrls[`${__app_name}:get-deal-json`](_deal.val());

            $.get(url, function(response) {
                if(response.success) {
                    $.each(response.deal, function(k, v){
                        if($('.field-' + k).length) {
                            $('.field-' + k).html(v?v:'-');
                        }
                    });
                } else {
                    $('.info-value').val('-');
                }

                if(__app_name == 'motorinsurance') {
                    if(!parseInt($('#id_form-0-insured_car_value').val()) && !$('#id_insured_car_value').val()) {
                        $('#id_insured_car_value').val(response.deal.insured_car_value);
                        $('#id_form-0-insured_car_value').val(response.deal.insured_car_value);
                    }
                }

                $('.preloader').hide();
            });
        },

        _reorderFields: function() {
            _products.find('.product-row').each(function(key) {
                var elements = $(this).find('label, select, input').not('input.select2-search__field');
                elements.each(function() {
                    if (this.tagName == 'LABEL') {
                        // $(this).attr('for', $(this).attr('for').replace(/-[0-9]-/g, '-' + key + '-'));
                    } else {
                        $(this).attr('id', $(this).attr('id').replace(/-[0-9]-/g, '-' + key + '-'));
                        $(this).attr('name', $(this).attr('name').replace(/-[0-9]-/g, '-' + key + '-'));
                    }

                    // if(this.tagName == 'SELECT')
                    //     $(this).change();
                });
            });
        },

        _fillAddonsOnload: function() {
            _products.find('.product-row').each(function(key, val) {
                var product = $(this).find(_product_field).val();
                var dropdown_element = $(this).find('select.product-addons');
                var addons = _this._getAddons(product, dropdown_element);
                var selected_addons = '';
            });
        }
    };

    jQuery(function() {
        __QUOTES.init();
    });
})();

/* POLICIES */
;
'Use Strict';

var __RENEWALS;
;(function() {

    var _this   = '';

    __RENEWALS =
    {
        init: function()
        {
            _this = this;

            let default_start_date = moment();
            let default_end_date = moment().add(60, 'days');

            let url_params = Utilities.General.getUrlParamKeyValue();

            if('from_date' in url_params && url_params.from_date)
                default_start_date = moment.unix(url_params.from_date);

            if('to_date' in url_params && url_params.to_date)
                default_end_date = moment.unix(url_params.to_date);

            $('#renewal_date_filter').daterangepicker({
                startDate: default_start_date,
                endDate: default_end_date,
                ranges: {
                   'Today': [moment(), moment()],
                   'Tomorrow': [moment().add(1, 'days'), moment().add(1, 'days')],
                   'Next 7 Days': [moment(), moment().add(6, 'days')],
                   'Next 30 Days': [moment(), moment().add(29, 'days')],
                   'Next 60 Days': [moment(), moment().add(60, 'days')],
                   'This Month': [moment().startOf('month'), moment().endOf('month')],
                   'Next Month': [moment().add(1, 'month').startOf('month'), moment().add(1, 'month').endOf('month')],
                   'Next 12 Months': [moment(), moment().add(365, 'days')],
                },
                locale: {
                  format: 'MMMM D, YYYY',
                  cancelLabel: 'Clear'
                }
            }, _this.change_date);

            $('#id_from_date').val(default_start_date.unix());
            $('#id_to_date').val(default_end_date.unix());

            $('#renewal_date_filter').html('Next 60 Days');

            $('[name=hide-renewaldeals]').change(function() {
                $('#id_hide_renewal_deal').val($(this).is(':checked')?'true':'');
                __TABLE._fetch_felix_table_records();
            });

            $('.renewal-deal').on('click', function() {
                var ids = $('.select-record:checked').map(function() {
                    return this.value;
                }).get();

                if(!ids.length) { Utilities.Notify.notice('Please select at least one record to create a renewal deal.'); return; }

                if(window.confirm('Are you sure you want to create a renewal deal from all selected policy record(s)?')) {
                    var ids = $('.select-record:checked').map(function() {
                        return this.value;
                    }).get();
                    $.get(
                        DjangoUrls['motorinsurance:create-renewals-deals'](),
                        {'pids': ids.join(',')},
                        function(response) {
                            if(response.success) {
                                if(response.new_deals_data.length) {
                                    Utilities.Notify.success('Deal(s) created successfully', 'Success');
                                }
                                if(response.errors.length) {
                                    var errors = `<ul class="m-t-10 m-l--20 font-12">`;
                                    response.errors.map(function(e) {
                                        errors += `<li>${e}</li>`;
                                    });
                                    errors += `</ul>`;

                                    Utilities.Notify.error('Following errors occurred:' + errors, 'Error');
                                }

                                setTimeout(function() {
                                    __TABLE._fetch_felix_table_records();
                                }, 2000);
                            }
                        }
                    );
                }
            });
        },

        change_date: function(start, end, label) {
            if(typeof start === 'undefined') start = moment(); 
            if(typeof end === 'undefined') end = moment().add(29, 'days');

            $('#id_from_date').val(start.unix());
            $('#id_to_date').val(end.unix());

            $('#renewal_date_filter').html(label);

            $('.clear-calendar').removeClass('hide');

            $('.quick-filters [data-type="all"]').click();

            __TABLE._fetch_felix_table_records();
        },

        toggle_cta: function(count) {
            $('button.renewal-deal').attr(
                'title',
                count?'':'Select at least one record to create a renewal deal'
            );
            $('button.renewal-deal').addRemoveClass(!count, 'disabled');
        }
    };

    jQuery(function() {
        if($('body[data-current-nav=renewals]').length)
            __RENEWALS.init();
    });
})();

/*
    Company Settings
*/
;
'Use Strict';

var __SETTINGS;
;(function() {
    var SELECTORS = {
    };

    var _this = '';
    var _form = $('#company_settings_form');

    __SETTINGS =
    {
        init: function()
        {
            _this = this;

            if(_form.length) {
                _this._initForms();
                _this._config();
            }

            if($('#id_auto-close-chk').length) {
                $('#id_auto-close-chk').change(function() {
                    $('#id_auto_close_quoted_deals_in_days').attr('disabled', !$(this).is(':checked'));
                });
            }
        },

        _config: function() {
            $('textarea').not('.ignore-length').maxlength({
                alwaysShow: true,
                warningClass: "badge badge-info",
                limitReachedClass: "badge badge-warning"
            });

            $('.upload-new').click(function(){
                $('#id_logo').click();
                $('#id_remove_avatar').val('');
            });

            $('#id_logo').change(function(e) {
                var reader = new FileReader();
                reader.onload = function() {
                    $('.profile-image-container').css({'background-image': 'url('+ reader.result +')'});
                };
                reader.readAsDataURL(e.target.files[0]);
            });

            $('.remove-avatar').click(function() {
                $('#id_remove_avatar').val('1');
                $('#id_image').val('');
                $('.profile-image-container').css({'background-image': 'none'});
            });
        },

        _initForms: function() {
            _form.ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: Utilities.Form.onSuccess,
                error: Utilities.Form.onFailure
            });
        }
    };

    jQuery(function() {
        __SETTINGS.init();
    });
})();

if (typeof module === "object" && typeof module.exports === "object") {
    module.exports = __SETTINGS;
}

/* DEALS */
;
'Use Strict';

var __TASKS;
;(function() {

    var _this   = '';
    var _table  = $('#tasks-table');
    var _form   = $('#task_form');
    var _filter_form   = $('#tasks-search');

    var _tasks_trail = $('.trail.task-trail');

    var _felix_table = $('table.felix-table');
    var _felix_table_filters = $('.table-filters');
    var _felix_table_quick_filters = $('.quick-filters');

    var _deal_id = $('.deal-container').data('id');
    var _deal_title = $('.deal-container').data('title');

    var _agent_id = $('body').data('agent');

    __TASKS =
    {
        init: function()
        {
            _this = this;

            _this._initTaskForm();
            _this._loadDealTasks();

            $("#search-clear").on("click", function () {
                window.location.href = $("#tasks-search").data("reset-url");
            });

            var filter_count = Utilities.Form.addFilterCount(_filter_form);
            if(filter_count) {
                $('.filter-count').html(filter_count).removeClass('hide');
            }

            $('.mark-as-done').click(function() {
                // Delete Button
                if(window.confirm('Are you sure you want to mark the selected task(s) as done?')) {
                    var ids = $('.select-record:checked').map(function() {
                        return this.value;
                    }).get();

                    $.post(
                        DjangoUrls[__app_name + ':tasks-mark-as-done'](),
                        {'task_ids': ids},
                        function(response) {
                            __TABLE._fetch_felix_table_records();
                        }
                    );
                }
            });

            $('.deal-container').on('click', 'button.add-task', function() {
                _this._resetTaskForm();

                $('<option/>').val(_deal_id).text(_deal_title).appendTo('#task_form #id_deal');
                $('#task_form #id_deal').trigger('chosen:updated');

            });

            $('.trail.task-trail').on('click', '.task-edit', function() {
                $('[data-felix-modal="modal_task"]').click();
                _this._getTaskDetail($(this).data('id'), _deal_title);
            });

            $('.task-actions button').click(function() {
                $('#id_tasks-fitler-form #filter_type').val($(this).data('type'));
                $('.task-actions button').removeClass('active');
                $(this).addClass('active');
                _this._loadDealTasks();
            });

            $('.trail.task-trail').on('click', '.task-remove', function() {
                if(window.confirm('Are you sure you want to delete this task?')) {
                    $.get(DjangoUrls[__app_name + ':task-delete']($(this).data('id')), function(response) {
                        if(response.success) {
                            Utilities.Notify.success('Task deleted successfully', 'Success');
                            _this._loadDealTasks();
                        } else {
                            Utilities.Notify.error(response.error, 'Error');
                        }
                    });
                }
            });
        },

        _loadDealTasks: function() {
            if(!_tasks_trail.length) return;

            var url = DjangoUrls[__app_name + ':deal-tasks'](_deal_id) + '?' + $('#id_tasks-fitler-form').serialize();
            $('.task-loader').show();
            $.get(url, function(response){
                var source = $('#row-tasks-li').html();
                var template = Handlebars.compile(source);
                var records = '<li class="no-record">No task found</li>';

                if(response.length) {
                    records = template({'records': response});
                }
                _tasks_trail.html(records);

                $('.task-loader').hide();
            });
        },

        _resetTaskForm: function() {
            _form.find('select').val('');
            _form.find('textarea').val('');
            _form.find('#id_time').val('10:00');
            _form.find('select').trigger('chosen:updated');
            _form.find('#id_is_completed').prop('checked', false);
            _form.find('#id_deal option').remove();
        },

        _initTaskForm: function() {
            if(!_form.length) return;

            $('[data-felix-modal="modal_task"]').click(function() {
                if($('[href="#tab_tasks"]').length)
                    $('[href="#tab_tasks"]').click();

                _form.find('#id_title, textarea').val('').change();
                _form.find('#id_is_completed').prop('checked', false);

                if(_deal_id !== undefined) {
                    _form.find('#id_deal').val(_deal_id);
                    _form.find('#id_deal').trigger('chosen:updated');
                }

                if(_agent_id !== undefined) {
                    _form.find('#id_assigned_to').val(_agent_id);
                    _form.find('#id_assigned_to').trigger('chosen:updated');
                }

                _form.find('#id_task_id').val('');

            });

            _form.ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                error: Utilities.Form.onFailure,
                success: function(response, status, xhr, form) {
                    form.find('button[type=submit]').removeClass('loader');

                    if(response.success) {
                        _form.find('[data-modal-close]').click();
                        Utilities.Notify.success('Task ' + (response.updated?'updated':'created') + ' successfully.', 'Success');

                        if(_felix_table.length) {
                            __TABLE._fetch_felix_table_records();
                        } else {
                            if(response.task.object_id == _deal_id) {
                                _this._loadDealTasks();
                            }
                        }
                    } else {
                        Utilities.Notify.error('Please check all the required fields.', 'Error');
                        Utilities.Form.addErrors(form, response.errors);
                    }
                }
            });
        },

        _getTaskDetail: function(id, deal_title) {
            if(!id) return;

            _this._resetTaskForm();

            $.get(DjangoUrls[__app_name + ':get-task-json'](id), function(response) {
                $('<option/>').val(response.deal).text(deal_title).appendTo('#id_deal');
                _form.find('#id_deal').trigger('chosen:updated');

                _form.find('#id_task_id').val(response.pk);
                _form.find('#id_title').val(response.title);
                _form.find('#id_date').val(response.due_date);
                _form.find('#id_time').val(response.due_time);
                _form.find('#id_time').val(response.due_time).trigger('chosen:updated');
                _form.find('#id_assigned_to').val(response.assigned_to);
                _form.find('#id_assigned_to').val(response.assigned_to).trigger('chosen:updated');
                _form.find('#id_is_completed').prop('checked', response.is_completed);
                _form.find('#id_content').val(response.content);
            });
        }

    };

    jQuery(function() {
        __TASKS.init();
    });
})();

/*** Felix Inline Editable fields ***/
;'Use Strict';
var __XEDITABLE;

;(function() {
    var _this = '';

    __XEDITABLE =
    {
        // Onload
        init: function()
        {
            _this = this;

            // For Text Fields
            if($('.text-editable').length) {
                $('.text-editable').each(function() {
                    $(this).editable({
                        type: 'text',
                        anim: 200,
                        mode: 'inline',
                        emptytext: $(this).data('emptytext')?$(this).data('emptytext'):'Add',
                        emptyclass: 'empty',
                        display: function(value, response) {
                            if(response) $(this).text(response.data.value);
                        },
                        error: function(response) {
                            return response.responseJSON.message;
                        },
                        success: function(response) {
                            if('quote_outdated' in response && response.quote_outdated)
                                __DEALS._setDealsQuoteOutdated();

                            if('previewImage' in this.dataset)
                                __DOCUMENTS_VIEWER._updateListDocument(this.dataset['id'], response.data.value);

                            __DEALS._loadHistory();
                            __CUSTOMERS._loadHistory();

                            if(this.dataset.name == 'phone')
                                __CUSTOMERS._checkWhatsAppIcon(response);
                        }
                    }).on('shown', function(e, editable) {
                        if($(e.target).data('class').indexOf('datepicker') >= 0) {
                            editable.input.$input.datepicker({
                                format: 'dd-mm-yyyy',
                                autoShow: true,
                                autoclose: true,
                            });
                        }
                    });
                });
            }

            // For Select options
            if($('.select-editable').length) {
                $('.select-editable').each(function() {
                    if(!$(this).data('value')) {
                        $(this).addClass('empty');
                        $(this).html('Add');
                    }

                    $(this).editable({
                        type: 'select',
                        anim: 200,
                        mode: 'inline',
                        emptytext: $(this).data('emptytext')?$(this).data('emptytext'):'Add',
                        emptyclass: 'empty',
                        error: function(response) {
                            return response.responseJSON.message;
                        },
                        success: function(response) {
                            if('quote_outdated' in response && response.quote_outdated) {
                                __DEALS._setDealsQuoteOutdated();
                            }
                            __DEALS._loadHistory();
                            __CUSTOMERS._loadHistory();
                        }
                    }).on('shown', function(e, editable) {
                        editable.input.$input.chosen({
                            placeholder: editable.input.$input.attr('placeholder')
                        });
                    });
                });
            }

            // For Number (Money) Fields
            if($('.number-editable').length) {
                $('.number-editable').each(function() {
                    $(this).editable({
                        type: 'number',
                        anim: 200,
                        mode: 'inline',
                        emptytext: $(this).data('emptytext')?$(this).data('emptytext'):'Add',
                        emptyclass: 'empty',
                        display: function (value, sourceData, response) {
                            if(sourceData) {
                                if(value > 999)
                                    value = accounting.format(value, 2);

                                $(this).html(value);
                            }
                        },
                        error: function(response) {
                            return response.responseJSON.message;
                        },
                        success: function(response) {
                            if('quote_outdated' in response && response.quote_outdated) {
                                __DEALS._setDealsQuoteOutdated();
                            }
                            __DEALS._loadHistory();
                            __CUSTOMERS._loadHistory();
                        }
                    });
                });
            }
        },
    };

    jQuery(function() {
        __XEDITABLE.init();
    });
})();


/* BANKS */
'Use Strict';

var __BANKS;
;(function() {
    __BANKS = {
        _deleteBank: function(element)
        {
            var element = element
            $.ajax({
                url: element.dataset.deleteUrl+"?bank="+ element.dataset.bank,
                method: 'DELETE',
                headers: {
                    "X-CSRFToken":element.previousElementSibling.value
               },
                success: function( data ) {
                    element.closest('tr').remove()
                    // alert(data.message)
                },
                error: function(data){
                    

                }
            });
        }
    }
}
)();
/* DEALS */
;
'Use Strict';

var __MORTGAGE_DEALS;
;(function() {

    var _this   = '';
    var _table  = $('#deals-table');
    var _form   = $('#deal_form');
    var _filter_form   = $('#deals-search');
    var _clear_product_selection = $('.clear-product-selection');
    var _show_payments = $('.show-payments');
    var _deal_id = $('.deal-container').data('id');
    var _deal_status = $('.deal-container').data('status');
    var _deal_stages_breadcrumb = $('.deal-stages-breadcrumb');
    var _deal_stage_container = $('.mortgage-deal-processes');
    var _deal_open_or_lost_btn = $('.open-lost-deal');

    __MORTGAGE_DEALS =
    {
        init: function()
        {
            _this = this;

            _this._loadMortgageProducts();
            _this._dealStatusInline();
            _this._addNewDealForm();
            _this._dealStagesToggle();
            _this._dealProcessTriggers();
            _this._openLostDealTriggers();
            _this._triggerCustomEmailForm();
            _this._loadHistory();

            _show_payments.click(function() {
                _this._scrollAndOpenPaymentsTab();
            });

            $("#search-clear").on("click", function () {
                window.location.href = $("#deals-search").data("reset-url");
            });

            var filter_count = Utilities.Form.addFilterCount(_filter_form);
            if(filter_count) {
                $('.filter-count').html(filter_count).removeClass('hide');
            }

            $('body.mortgage-deals').on('click', '.duplicate-deal', function() {
                _this._duplicateDeal();
            });

            if(_clear_product_selection.length) {
                _clear_product_selection.click(function() {
                    var url = $(this).data('url');
                    if(window.confirm('Are you sure you want to clear the selected product?')) {
                        $.get(url, function(response) {
                            if(response.success) {
                                Utilities.Notify.success('Product selection removed successfully', 'Success');
                                window.location.href = window.location.href;
                            } else {
                                Utilities.Notify.error(response.message, 'Error');
                            }
                        });
                    }
                });
            }

            // Load deal stage on load
            if(_deal_stage_container.length)
                _this._loadMortgageDealStage();

            $("#deal_email_field_form").ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: function(response, status, xhr, form) {
                    form.find('button[type=submit]').removeClass('loader');

                    if(response.success) {
                       $('.save-and-send:visible').click();
                       $('[data-modal-close]:visible').click();
                       $('a.text-editable[data-name=email]').editable('destroy');
                       $('a.text-editable[data-name=email]').html(response.data.value);

                       __XEDITABLE.init();
                    }
                },
                error: Utilities.Form.onFailure
            });

            // Email modal Template DD change event
            $('.deal-container').on('change', '#custom_email_type', function() {
                if($('body').hasClass('mortgage-deals')) {
                    _this._triggerCustomEmailMortgageModal($(this).val());
                }
            });
        },

        _loadMortgageProducts: function() {
            if(_deal_id) {
                $.get(DjangoUrls['mortgage:deal-all-products'](_deal_id), function(res) {
                    window.products_data = res
                });
            }
        },

        _loadStageWarning: function() {
            setTimeout(function() {
                $('.stage-warning').click(function() {
                    alertify
                        .okBtn("Dismiss")
                        .cancelBtn("Cancel")
                        .confirm("Some deal information has changed since you last saved your quotes. This might affect the premiums quoted. Consider reviewing  your quotes before proceeding.", function (ev) {
                            $.get(
                                DjangoUrls['mortgage:deal-remove-warning'](_deal_id),
                                function(response) {
                                    if(response.success)
                                       $('.stage-warning').addClass('hide'); 
                            });
                        });
                });
            }, 2000);
        },

        _loadHistory: function() {
            if(!_deal_id || !$('#mortgage_tab_history').length) return;

            $.get(DjangoUrls['mortgage:deal-history'](_deal_id), function(response) {
                console.log(response)
                $('#mortgage_tab_history').html(response);
            });
        },

        _resetMortgageDealForm: function(event) {
            Utilities.Form.removeErrors('#deal_form');
            $('#deal_form .autocomplete-container').removeClass('new');
            $('#deal_form #id_customer').val('');
            $('#deal_form input[type=text]').val('');
            $('#deal_form select').val('');
            $('#deal_form select').trigger('chosen:updated');
            $('#deal_form #id_number_of_passengers').val('');
        },

        _setCustomerInDealForm: function(customer_id, customer_name) {
            $('#deal_form #id_customer').val(customer_id);
            $('#deal_form #id_customer_name').val(customer_name);
        },

        _triggerCustomEmailForm: function() {
            $('#modal_send_custom_email .send-email').click(function(event) {
                var form = $('#custom_email_form');
                var email_type = form.find('#email_type').val();

                // Validations
                form.find('.error').remove();
                if(form.find('#id_email').val() == '') {
                    form.find('#id_email').after('<span class="error">This field is required</span>');
                    return;
                }
                if(form.find('#id_subject').val() == '') {
                    form.find('#id_subject').after('<span class="error">This field is required</span>');
                    return;
                }

                form.find('button.send-email').addClass('loader');

                $.post(
                    DjangoUrls['mortgage:deal-email-content'](_deal_id, email_type),
                    $('#custom_email_form').serialize(),
                    function(response) {
                        form.find('button.send-email').removeClass('loader');
                        if(response.success) {
                            Utilities.Notify.success('Email sent successfully.', 'Success');
                            $('#modal_send_custom_email').hide();

                            if(response.email_type == 'new_quote' || response.email_type == 'quote_updated') {
                                __AMPLITUDE.logEvent(
                                    __AMPLITUDE.event('mortgage_quote_email_sent'), {
                                        'deal_id': _deal_id
                                    }
                                );
                            }

                            _this._loadHistory();

                        } else {
                            Utilities.Notify.error('Please check all the required fields and try again.', 'Error');
                            Utilities.Form.addErrors($('#custom_email_form'), response.errors);
                        }
                    }
                );
            });
        },

        _triggerCustomEmailMortgageModal: function(email_type) {
            var url = DjangoUrls['mortgage:deal-email-content'](_deal_id, email_type);
            $('#custom_email_form').css({'opacity': '.7'});

            $.get(url, function(response) {
                var form = $('#custom_email_form');
                $('#custom_email_form').css({'opacity': '1'});
                $('[data-felix-modal="modal_send_custom_email"]').click();

                form.find('#email_type').val(email_type);
                form.find('#id_email').val(response.to);
                form.find('#id_from_email').html(response.from);
                form.find('#id_reply_to').html(response.reply_to);
                // form.find('#id_cc_emails').val(response.cc_emails);
                // form.find('#id_bcc_emails').val(response.bcc_emails);
                form.find('#id_subject').val(response.subject);
                form.find('#id_content').trumbowyg($.trumbowyg.config);
                form.find('#id_content').trumbowyg('html', response.content);

                form.find('#custom_email_type option').remove();

                $.each(response.allowed_templates, function(k, v) {
                    var selected = k==response.email_type?'selected':'';
                    form.find('#custom_email_type').append(
                        `<option ${selected} value="${k}">${v}</option>`
                    );
                });
                $('#custom_email_type').trigger('chosen:updated');

                form.find('.email_type_display').html(
                    response.allowed_templates[response.email_type]
                );

                if('sms_content' in response && response.sms_content) {

                    form.find('.show-when-sms').removeClass('hide');
                    form.find('#id_sms_content').val(response.sms_content);

                    form.find('#id_send_sms').change(function() {
                        form.find('.sms_container').addRemoveClass(!$(this).is(':checked'), 'hide');
                    });

                    $('textarea[maxlength]').maxlength({
                        alwaysShow: true,
                        warningClass: "badge badge-info",
                        limitReachedClass: "badge badge-warning"
                    });
                } else {
                    form.find('.show-when-sms').addClass('hide');
                    form.find('#id_sms_content').val('');
                    form.find('#send_sms').prop('checked', false);
                }

                if('whatsapp_msg_content' in response && response.whatsapp_msg_content) {

                    form.find('.show-when-wa-msg').removeClass('hide');
                    form.find('#id_wa_msg_content').val(response.whatsapp_msg_content);

                    form.find('#id_send_sms').change(function() {
                        form.find('.sms_container').addRemoveClass(!$(this).is(':checked'), 'hide');
                    });

                    $('textarea[maxlength]').maxlength({
                        alwaysShow: true,
                        warningClass: "badge badge-info",
                        limitReachedClass: "badge badge-warning"
                    });
                } else {
                    form.find('.show-when-wa-msg').addClass('hide');
                    form.find('#id_wa_msg_content').val('');
                    form.find('#id_send_wa_msg').prop('checked', false);
                }

                // if('attachments' in response && response.attachments.length) {
                //     form.find('.attachments').removeClass('hide');
                //     form.find('.attachments ul li').remove();
                //     $.each(response.attachments, function() {
                //         form.find('.attachments ul').append(
                //             '<li><a href="' + this.url + '" target="_blank">' + this.name + '</a></li>'
                //         );
                //     });
                // } else {
                //     form.find('.attachments').addClass('hide');
                // }
            });
        },

        _openLostDealTriggers: function() {
            _deal_open_or_lost_btn.click(function() {
                if(_deal_open_or_lost_btn.hasClass('re-open')) {
                    if(window.confirm('Are you sure you want to Re-Open this deal?')) {
                        $.get(DjangoUrls['mortgage:deal-reopen'](_deal_id), function(response) {
                            if(response.success) {
                                _this._loadMortgageDealStage();
                            }
                        });
                    }
                } else {
                    if(window.confirm('Are you sure you want to mark this deal as a "LOST" deal?')) {
                        $.get(DjangoUrls['mortgage:deal-mark-as-lost'](_deal_id), function(response) {
                            if(response.success) {
                                _this._loadMortgageDealStage();
                            }
                        });
                    }
                }
            });
        },

        _updateTags: function(tags) {
            // Updating Tags
            if(tags) {
                var tags_html = '';
                $.each(tags, function() {
                    tags_html += '<span class="m-t-15 m-r-4 badge badge-default badge-font-light badge-'+Utilities.General.slugify(this)+'">'+this+'</span>';
                });

                $('.deal-statuses').html(tags_html);
            }
        },

        _refreshStagesBar: function(stage) {
            var status = $('.deal-container').data('status');
            var stages = ['new', 'quote', 'preApproval', 'valuation', 'offer', 'settlement', 'loanDisbursal', 'propertyTransfer', 'closed'];

            $.get(DjangoUrls['mortgage:deal-current-stage'](_deal_id), function(response) {
                if(response)
                   status =  response.stage;

                if(stage === undefined || !stage)
                    stage = status;

                _this._updateTags(response.tags);

                _deal_stages_breadcrumb.find('li').removeClass('current completed lost won');

                // Checking for lost/won deal
                if(status == 'lost' || status == 'won' ) {
                    _deal_stages_breadcrumb.find('li').addClass(status);

                    _deal_open_or_lost_btn
                        .html('Reopen')
                        .removeClass('mark-as-lost btn-outline-danger hide')
                        .addClass('re-open btn-outline-dark');

                    return;
                } else {
                    _deal_open_or_lost_btn
                        .html('Mark as Lost')
                        .addClass('mark-as-lost btn-outline-danger')
                        .removeClass('re-open btn-outline-dark hide');
                }
                _deal_stages_breadcrumb.find('li[data-id='+ stage +']').addClass('selected');
                $.each(stages, function() {
                    if(this == status) {
                        _deal_stages_breadcrumb.find('li[data-id='+ this +']').addClass('current');
                        return false;
                    } else {
                        _deal_stages_breadcrumb.find('li[data-id='+ this +']').addClass('completed');
                    }
                });

                _this._loadHistory();
            });
        },

        _loadMortgageDealStage: function(stage) {
            if(_deal_id) {

                if(stage === undefined)
                    stage = '';

                if($('body').hasClass('mortgage-deals')) {
                    $.get(DjangoUrls['mortgage:get-deal-stage'](_deal_id) + '?stage=' + stage, function(response) {
                        _deal_stage_container.html(response);

                        __FELIX__._loadLibs();
                        __DEALFORMS._initForms();
                    });
                    _this._refreshStagesBar(stage);
                    _this._loadStageWarning();
                }
            }
        },

        _getCustomerFromQueryParams: function() {
            var params = Utilities.General.getUrlVars();

            if('customer_id' in params && params['customer_id']) {
                return params['customer_id'];
            }

            return false;
        },

        _scrollAndOpenPaymentsTab: function() {
            var elem = $('a[href="#tab_payments"]');
            
            $([document.documentElement, document.body]).animate({
                scrollTop: elem.offset().top
            }, 100);
            elem.click();
        },

        _dealStatusInline: function() {
            $('.deal-inline-update-field').editable({
                emptytext: $(this).data('emptytext')?$(this).data('emptytext'):'-',
                mode: 'inline',
                inputclass: 'form-control-sm',
                url: $(this).data('url'),
                emptyclass: 'empty',
                source: $(this).data('options')?$.parseJSON($(this).data('options')):[],
                display: function (value, sourceData) {
                    var elem = $.grep(sourceData, function (o) {
                        return o.value == value;
                    });

                    if (elem.length) {
                        $(this).text(elem[0].text);
                    } else {
                        $(this).empty();
                    }
                },
                error: function(response) {
                    return response.responseJSON.message;
                },
                success: function(response, newValue) {
                    if(response.success) {
                        Utilities.Notify.success(response.message, 'Success');
                    } else {
                        Utilities.Notify.error(response.message, 'Error');
                        return false;
                    }
                }
            }).on('shown', function(e, editable){
                editable.input.$input.chosen();
            });
        },

        _loadQuotePreview: function() {
            $.get(DjangoUrls['mortgage:deal-quote-preview'](_deal_id), function(response) {
                $('.quote-preview').html(response);
            });
        },

        _updateTableAttributes: function(data) {
            $('.deals-total-amount').html(data.total_deals_display);
            //re-init inline form defintion
            _this._dealStatusInline();
        },

        ////// DEAL Stages and Processes methods
        _addNewDealForm: function() {
            $("#deal_form").ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: function(response, status, xhr, form) {
                    if(response.success) {
                        $.get(DjangoUrls[`${__app_name}:get-deal-json`](response.deal_id), function(r) {
                            __AMPLITUDE.logEvent(__AMPLITUDE.event('mortgage_deal_created'), {
                                'source': 'manual',

                                'deal_id': r.deal.id,

                                'client_nationality': r.customer.nationality,
                                'client_gender': r.customer.gender,
                                'client_age': r.customer.age,

                                'deal_type': 'new'
                            });
                        });
                    }

                    Utilities.Form.onSuccess(response, status, xhr, form);
                },
                error: Utilities.Form.onFailure
            });
        },

        _dealProcessTriggers: function() {
            _deal_stage_container.on('click', '.btn-cancel-generate-new-quote', function(){
                if($('.deal-overview .deal-form .products-preview .products .row').length) {
                    $('.deal-form .products-preview').removeClass('hide');
                    $('.deal-form .form').addClass('hide');
                } else if($('.quote-overview .deal-form .products-preview .products .row').length){
                    $('.deal-form .products-preview').removeClass('hide');
                    $('.deal-form .form').addClass('hide');
                } else {
                    $('.deal-overview .new-deal').addClass('display');
                    $('.deal-overview .deal-form').removeClass('display');    
                }
            });

            $('body').on('click', '.insurer-block-container', function() {
                $('.auto-quote-insurer-field').val($(this).data('id')).change();
                $('#modal_auto_quote_form h2').html($(this).data('name'));

                $('#id_product option').addClass('hide').trigger('chosen:updated');
                $('#id_product option[data-insurer-id=' + $(this).data('id') + ']').removeClass('hide').trigger('chosen:updated');
            });

            $("#mortgage_deal_form").submit(function (e) {
            e.preventDefault();
            var form = $("#mortgage_deal_form");
            var url = form.attr('action');
            $('.mortgage-deal-form-error').html('')
            $.ajax({
                    beforeSubmit: Utilities.Form.beforeSubmit,
                    type: "POST",
                    url: url,
                    data: form.serialize(),
                    success: function(data)
                    {
                        if (data.success){
                            location = data.redirect_url
                        }
                        else{
                            $('.mortgage-deal-form-error').html('')
                            var form_el = $("#mortgage_deal_form")[0].getElementsByTagName('input');
                            var form_el_select = $("#mortgage_deal_form")[0].getElementsByTagName('select');
                            for (var key in data.errors)
                            {
                                for (let i = 0; i < form_el.length; i++) {
                                if (form_el[i].name == key){
                                    form_el[i].parentElement.getElementsByTagName('span')[0].innerText = data.errors[key][0]
                                }
                              }
                              for (let i = 0; i < form_el_select.length; i++) {
                                if (form_el_select[i].name == key){
                                    form_el_select[i].parentElement.getElementsByTagName('span')[0].innerText = data.errors[key][0]

                                }
                              }
                            }
                            
                            if (data.errors.__all__){
                                form_el.property_price.parentElement.getElementsByTagName('span')[0].innerText = data.errors.__all__[0]
                            }
                        }
                    }
                });
                return false;
            });
        },

        _dealStagesToggle: function() {
            if(_deal_stages_breadcrumb.length) {
                _deal_stages_breadcrumb.find('li').click(function() {
                    if(!$(this).data('item') || $('.' + $(this).data('item')).is(':visible')) return;
                    _this._loadMortgageDealStage($(this).data('id'));
                    _deal_stages_breadcrumb.find('li').removeClass('selected');
                    $(this).addClass('selected');
                });
            }
        },

        _setDealsQuoteOutdated: function() {
            var quote_stage_container = $('.deal-stages-breadcrumb [data-id="quote"]');

            if(!quote_stage_container.length) return;

            if(quote_stage_container.hasClass('selected') || quote_stage_container.hasClass('current') || quote_stage_container.hasClass('completed')) {
                $('.stage-warning').removeClass('hide');
                __MORTGAGE_DEALS._loadStageWarning();
            }
        },

        _duplicateDeal: function() {
            if(_deal_id) {
                if(window.confirm('Are you sure you want to duplicate this deal?')) {
                    $.get(DjangoUrls['mortgage:deal-duplicate'](_deal_id), function(response) {
                        if(response.success) {
                            window.location = response.redirect_url;
                        } else {
                            Utilities.Notify.error('Something went wrong. Please contact support.', 'Error');
                        }
                    });
                }
            }
        }
    };

    jQuery(function() {
        if($('body').hasClass('mortgage-deals'))
            __MORTGAGE_DEALS.init();
    });
})();
