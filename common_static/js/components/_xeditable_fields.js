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
