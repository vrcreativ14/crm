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
