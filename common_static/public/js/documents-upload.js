var DocumentUpload;
;(function() {
    'Use Strict';
    var SELECTORS = {
        "form": "#motor_document_form",

        "upload_document": ".upload-document-button",
        "upload_element": ".file-input",
        "remove_element": ".file-remove",

        "submit_button": ".submit-document",
        "later_button": ".save-later",
    };

    var _this = '';

    var concurrentUploads = 0;

    DocumentUpload =
    {
        init: function()
        {
            _this = this;

            $('.add-file').click(function(){
                $('.fileuploader-container .fileuploader-input').click();
            });

            $(SELECTORS.submit_button).click(function(){
                var qrn = $(this).data('quote-reference');
                var qid = $(this).data('quote-id');

                if($('.upload-successful .document-info').length){
                    (new PNotify({
                        title: 'Have you attached all required documents?',
                        text: 'Please make sure all documents are attached before submission, so we can process your policy faster.',
                        hide: false,
                        styling: 'bootstrap3',
                        confirm: {
                            confirm: true,
                            buttons: [{
                                text: 'Yes',
                                addClass: 'btn-primary',
                                click: function(notice) {
                                    $.post(DjangoUrls['motorinsurance:update-deal-stage'](qrn, qid) + '?st=dc', function(response) {
                                        if(response.status) {
                                            window.location = DjangoUrls['motorinsurance:quote-upload-documents-success']();
                                        } else {
                                            Utilities.Notify.error(response.error_message, 'Error Occurred!');
                                        }
                                    });
                                }
                            },
                            {
                                text: 'No',
                                addClass: 'btn-primary',
                                click: function(notice) {
                                    PNotify.removeAll();
                                }
                            }]
                        },
                        buttons: {
                            closer: false,
                            sticker: false
                        },
                        history: {
                            history: false
                        },
                    }));
                } else {
                    Utilities.Notify.error('There are no documents to submit. Please upload all the required documents.', 'Error');
                }
            });

            $(SELECTORS.later_button).click(function(){
                Utilities.Notify.success('Files saved successfully', 'Success');
            });

            _this.uploader();

        },

        uploader: function() {
            var _this = this;

            $('.fileuploader-container input[name="files"]').fileuploader({
                theme: 'onebutton',
                maxSize: 30,
                fileMaxSize: 10,
                extensions: ['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx'],
                thumbnails: {
                    item: '<li class="fileuploader-item">' +
                           '<div class="columns">' +
                            '<div class="column-thumbnail">${image}</div>' +
                            '<div class="column-title">' +
                                 '<div title="${name}">${name}</div>' +
                                 '<span>${size2}</span>' +
                            '</div>' +
                            '<div class="column-actions">' +
                                 '<span class="document-info" data-type="${type}" data-size="${size}" data-url="" data-name="${name}"><input type="hidden" name="file_url" value="${data.url}" /></span>' +
                                 '<a target="_blank" href="javascript:" class="fileuploader-action fileuploader-action-view" title="View File"><i class="fa fa-search" aria-hidden="true"></i><span>View File</span></a>' +
                                 '<a href="javascript:" class="fileuploader-action fileuploader-action-remove" title="Remove"><i class="fa fa-trash-o" aria-hidden="true"></i><span>Delete</span></a>' +
                            '</div>' +
                            '</div>' +
                            '<div class="progress-bar2">${progressBar}<span></span></div>' +
                        '</li>',
                    item2: '<li class="fileuploader-item upload-successful">' +
                           '<div class="columns">' +
                            '<div class="column-thumbnail">${image}</div>' +
                            '<div class="column-title">' +
                                 '<div title="${name}">${name}</div>' +
                                 '<span>${size2}</span>' +
                            '</div>' +
                            '<div class="column-actions">' +
                                 '<span class="document-info" data-type="${type}" data-size="${size}" data-url="${data.url}" data-name="${name}"><input type="hidden" name="file_url" value="${data.url}" /></span>' +
                                 '<a target="_blank" href="${data.url}" class="fileuploader-action fileuploader-action-view" title="View File"><i class="fa fa-search" aria-hidden="true"></i><span>View File</span></a>' +
                                 '<a href="javascript:" class="fileuploader-action fileuploader-action-remove" title="Remove"><i class="fa fa-trash-o" aria-hidden="true"></i><span>Delete</span></a>' +
                            '</div>' +
                            '</div>' +
                            '<div class="progress-bar2">${progressBar}<span></span></div>' +
                        '</li>',
                    removeConfirmation: false,
                },
                upload: {
                    url: DjangoUrls['motorinsurance:quote-upload-documents'](),
                    data: null,
                    type: 'POST',
                    enctype: 'multipart/form-data',
                    start: true,
                    synchron: true,
                    beforeSend: null,
                    onSuccess: function(result, item) {
                        if(result.url) {
                            item.html.find('.fileuploader-action-view').attr('href', result.url);
                            item.html.find('input[name=file_url]').val(result.url);
                            item.html.find('.document-info').data('name', item.name);
                            item.html.find('.document-info').data('type', item.type);
                            item.html.find('.document-info').data('size', item.size);
                            item.html.find('.document-info').data('file', result.url);
                            item.html.find('.document-info').data('url', result.url);

                        } else {
                            item.html.removeClass('upload-successful').addClass('upload-failed');
                            return this.onError ? this.onError(item) : null;
                        }

                        setTimeout(function() {
                            item.html.find('.progress-bar2').fadeOut(400);
                        }, 400);
                    },
                    onError: function(item, listEl, parentEl, newInputEl, inputEl, jqXHR, textStatus, errorThrown) {
                        var progressBar = item.html.find('.progress-bar2');

                        if(progressBar.length > 0) {
                            progressBar.find('span').html(0 + "%");
                            progressBar.find('.fileuploader-progressbar .bar').width(0 + "%");
                            item.html.find('.progress-bar2').fadeOut(400);
                        }

                        item.upload.status != 'cancelled' && item.html.find('.fileuploader-action-retry').length == 0 ? item.html.find('.column-actions').prepend(
                            '<a class="fileuploader-action fileuploader-action-retry" title="Retry"><i></i></a>'
                        ) : null;
                    },
                    onProgress: function(data, item) {
                        $('.add-file, .submit-document, .save-later').attr({'disabled':true});
                        var progressBar = item.html.find('.progress-bar2');

                        if(progressBar.length > 0) {
                            progressBar.show();
                            progressBar.find('span').html(data.percentage + "%");
                            progressBar.find('.fileuploader-progressbar .bar').width(data.percentage + "%");
                        }
                    },
                    onComplete: function(listEl, parentEl, newInputEl, inputEl, jqXHR, textStatus) {
                        $('.add-file, .submit-document, .save-later').attr({'disabled':false});
                        $(SELECTORS.later_button).addClass('show');

                        _this.save();
                    },
                },
                afterRender: function(items) {
                    if(items.find('li').length) {
                        $(SELECTORS.later_button).addClass('show');
                    }
                },
                // onRemove: function(item, listEl, parentEl, newInputEl, inputEl) {
                //     _this.removeUploadedFile(item);
                //     return false;
                // },
            });
        },

        removeUploadedFile: function(item) {
            (new PNotify({
                title: 'Are you sure?',
                text: 'you want to remove this file',
                hide: false,
                styling: 'bootstrap3',
                confirm: {
                    confirm: true
                },
                buttons: {
                    closer: false,
                    sticker: false
                },
                history: {
                    history: false
                },
            })).get().on('pnotify.confirm', function(){
                $(item.html).slideUp('fast');
                setTimeout(function() {
                    item.html.remove();
                    if(!$('div.fileuploader .fileuploader-items-list li').length) {
                        $(SELECTORS.later_button).removeClass('show');
                    }
                    _this.save();
                }, 1000);
            });
        },

        save: function(submit) {
            var elem = $('.upload-successful .document-info');
            var urls = [];

            elem.each(function() {
                var file_url = $(this).find('input[name=file_url]').val();
                urls.push({
                    "name": $(this).data('name'),
                    "type": $(this).data('type'),
                    "size": $(this).data('size'),
                    "file": file_url,
                    "data": { "url": file_url }
                });
            });

            var params = {"documents": JSON.stringify(urls)};

            if(submit) {
                params['submit_type'] = true;
            }
            $.ajax({
                method: "POST",
                url: $(SELECTORS.submit_button).data('submit-url'),
                data: params
            }).done(function( response ) {
                if(submit) {
                    window.location.hash = "#submitted"
                    location.reload();
                }
            });
        },

    };

    $(function() {
        DocumentUpload.init();
    });
})();
