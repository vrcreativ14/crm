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
