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

                if(!accounting.unformat(sale_price))
                    sale_price = premium;

                var data = {
                    'product_id': $('#id_product').val(),
                    'product_name': product.name,
                    'product_logo': product.logo,
                    'currency': 'Dhs',
                    'default_add_ons': $('#id_default_add_ons').val() || [],
                    'agency_repair': $('#id_agency_repair').is(':enabled:checked'),
                    'ncd_required': $('#id_ncd_required').is(':enabled:checked'),
                    'deductible': $('#id_deductible').val(),
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
