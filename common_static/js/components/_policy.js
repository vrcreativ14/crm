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
