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
