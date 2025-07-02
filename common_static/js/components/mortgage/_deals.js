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
                            debugger
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
