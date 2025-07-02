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
