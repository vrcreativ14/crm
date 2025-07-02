/*** Felix File Uploader ***/
;'Use Strict';
var __FILE_UPLOADER;

;(function() {
    var _this = '';

    __FILE_UPLOADER =
    {
        // Onload
        init: function()
        {
            _this = this;
            if($('.felix-file-uploader').length) {
                $('.felix-file-uploader input.single-file-input').each(function() {
                    var elem = $(this);
                    if(!$.fileuploader.getInstance(elem)) {
                        elem.fileuploader({
                            theme: 'default',
                            enableApi: true,
                            captions: {
                                button: 'Browse'
                            },
                            thumbnails: {
                                // thumbnails for the preloaded files {String, Function}
                                item2: '<li class="fileuploader-item file-has-popup">' +
                                            '<div class="columns">' +
                                                '<div class="column-thumbnail">${image}<span class="fileuploader-action-popup"></span></div>' +
                                                '<div class="column-title">' +
                                                    '<a href="${file}" target="_blank">' +
                                                        '<div title="${name}">${data.label}</div>' +
                                                        '<span>${size2}</span>' +
                                                    '</a>' +
                                                '</div>' +
                                                '<div class="column-actions">' +
                                                    '<a href="${file}" class="fileuploader-action fileuploader-action-download" title="${captions.download}" download><i></i></a>' +
                                                    '<a class="fileuploader-action fileuploader-action-remove" data-id="${data.id}" title="${captions.remove}"><i></i></a>' +
                                                '</div>' +
                                            '</div>' +
                                        '</li>',
                            },
                            onRemove: function(item, listEl, parentEl, newInputEl, inputEl) {
                                if($(parentEl).parent().find('#trigger_policy_document_parser').length) {
                                    $(parentEl).parent().find('#trigger_policy_document_parser, #policy_document_no_scan').addClass('hide');
                                }
                            }
                        });
                    }
                });
                $('.felix-file-uploader input.multi-file-input').each(function() {
                    var elem = $(this);
                    if(!$.fileuploader.getInstance(elem)) {
                        elem.fileuploader({
                            theme: 'default',
                            enableApi: true,
                            captions: {
                                button: 'Browse'
                            },

                            thumbnails: {
                                item: '<li class="fileuploader-item file-has-popup">' +
                                           '<div class="columns">' +
                                               '<div class="column-thumbnail">${image}<span class="fileuploader-action-popup"></span></div>' +
                                               '<div class="column-title">' +
                                                   '<div title="${name}">${name}</div>' +
                                                   '<span>${size2}</span>' +
                                               '</div>' +
                                               '<div class="column-actions">' +
                                                   '<a class="fileuploader-action fileuploader-action-remove" title="${captions.remove}"><i></i></a>' +
                                               '</div>' +
                                           '</div>' +
                                           '<div class="progress-bar2">${progressBar}<span></span></div>' +
                                      '</li>',
                                      
                                // thumbnails for the preloaded files {String, Function}
                                item2: '<li class="fileuploader-item file-has-popup">' +
                                            '<div class="columns">' +
                                                '<div class="column-thumbnail">${image}<span class="fileuploader-action-popup"></span></div>' +
                                                '<div class="column-title">' +
                                                    '<a href="${file}" target="_blank">' +
                                                        '<div title="${name}">${name}</div>' +
                                                        '<span>${size2}</span>' +
                                                    '</a>' +
                                                '</div>' +
                                                '<div class="column-actions">' +
                                                    '<a href="${file}" class="fileuploader-action fileuploader-action-download" title="${captions.download}" download><i></i></a>' +
                                                    '<a class="fileuploader-action fileuploader-action-remove" data-id="${data.id}" title="${captions.remove}"><i></i></a>' +
                                                '</div>' +
                                            '</div>' +
                                        '</li>',
                            },

                            onRemove: function(item, listEl, parentEl, newInputEl, inputEl) {
                                if('data' in item && item.data.id) {
                                    $.post(DjangoUrls['motorinsurance:policy-attachment-delete'](item.data.id), function(response) {
                                        return response.success;
                                    });
                                }
                            },
                        });
                    }
                });
            }
        },
    };

    jQuery(function() {
        __FILE_UPLOADER.init();
    });
})();
