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
