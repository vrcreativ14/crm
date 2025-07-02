/* DOCUMENT VIEWER */
;
'Use Strict';
var attachments = [];
var __DOCUMENTS_VIEWER;
;(function() {

    var _this   = '';
    var _counter = 0;
    var _viewer = '.document-viewer';
    var _viewer_cta = '.preview-documents';
    var _preview_container = '.preview-container';
    var _img_container = '.preview-container img';
    var _pdf_container = '.preview-container iframe';
    var _form = '.attachment_update_form';
    var _label_field = '.attachment_update_form input[name=value]';
    var _id_field = '.attachment_update_form input[name=pk]';
    var _doc_nav_right = '.document-viewer .nav.right';
    var _doc_nav_left = '.document-viewer .nav.left';
    var _loader = '.document-viewer .loader';
    var _controls = '#modal_documents_viewer .controls';
    var _controls_rotate = '#modal_documents_viewer .controls .rotate';
    var _loaded_flag = false;

    __DOCUMENTS_VIEWER =
    {
        init: function()
        {
            _this = this;

            $(_viewer_cta).click(function() {
            	_this._loadDocuments();
                _this._right_left_key_navs();

                __AMPLITUDE.logEvent(__AMPLITUDE.event('document_previewed'));
            });

            _this._toggleNav();

            $(_doc_nav_right).click(function() {
                _this._moveRight();
            });
            $(_doc_nav_left).click(function() {
                _this._moveLeft();
            });
            $(_preview_container).click(function() {
                $(this).toggleClass('fit-to-container');
            });

            $(_controls_rotate).click(function() {
                var angle = $(this).data('angle');

                if(angle == 0) angle = 90;
                else if(angle == 90) angle = 180;
                else if(angle == 180) angle = 270;
                else if(angle == 270) angle = 0;

                $(this).data('angle', angle);
                $(_img_container).css({'transform': 'rotate(' + angle + 'deg)'});
            });

            $(_form).ajaxForm({
                success: function(response, status, xhr, form) {
                    if(response.success) {
                        Utilities.Notify.success('File name updated successfully', 'Success');
                        var id = $(_id_field).val();
                        var label = $(_label_field).val();
                        var filefield = $('#tab_documents a[data-id=' + $(_id_field).val() + '].attachment-field');
                        filefield.html(label);
                        filefield.attr('title', label);
                        filefield.attr('data-value', label);
                        filefield.editable({
                            type: 'text',
                            anim: 200,
                            mode: 'inline'});

                        _this._updateAttachmentSet(response.id, response.data['value']);
                        _this._pushEditEventAmplitude('document viewer');
                    } else {
                        Utilities.Notify.error('Please check all the required Fields.', 'Error');
                    }
                }
            });
        },

        _loadDocuments: function() {
            if (typeof attachments == "undefined") {
                console.log('No attachments variable defined'); return;
            }

            if(!attachments.length) {
            	alert('No document(s) available for preview. Please upload to preview.');
            } else {
                if(_counter < 0) _counter = 0;
                if(_counter > attachments.length-1) _counter = attachments.length-1;
                $('.preview-documents-viewer-trigger').click();
                _this._loadFile(attachments[_counter]);
            }
        },

        _updateAttachmentSet: function(id, label) {
            $.each(attachments, function(k, v){
                if(v['id'] == id)
                    attachments[k]['label'] = label;
            });
        },

        _moveLeft: function() {
            if($(_doc_nav_left).hasClass('disbaled')) return;

            _counter--;

            _this._loadDocuments();
            _this._toggleNav();
        },

        _moveRight: function() {
            if($(_doc_nav_right).hasClass('disbaled')) return;

            _counter++;

            _this._loadDocuments();  
            _this._toggleNav();
        },

        _toggleNav: function() {
            if(_counter == 0) {
                $(_doc_nav_left).addClass('disabled');
            } else {
                $(_doc_nav_left).removeClass('disabled');
            }

            if(_counter == attachments.length-1) {
                $(_doc_nav_right).addClass('disabled');
            } else {
                $(_doc_nav_right).removeClass('disabled');
            }
        },

        _loadFile: function(file) {
            if($(_preview_container).data('doc-id') == _counter && _loaded_flag) return;

            $(_loader).addClass('show');

            _loaded_flag = true;

        	if(file.extension == 'pdf') {
        		_this._loadPDF(file);
                $('.zoom-toggle').addClass('hide');
                $(_controls).addClass('hide');
            }
        	else {
        		_this._loadImage(file);
                $('.zoom-toggle').removeClass('hide');
                $(_controls).removeClass('hide');
            }

        	$(_label_field).val(file.label);
            $(_id_field).val(file.id);

            $(_form).attr('action', DjangoUrls['core:update-attachment'](file.id));

            $(_preview_container).data('doc-id', _counter);
            $(_preview_container).addClass('fit-to-container');
        },

        _loadPDF: function(file) {
        	$(_pdf_container).attr('src', file.url);

            $(_pdf_container)
                .on('load', function() {
                    $(_loader).removeClass('show');
                    $(_pdf_container).removeClass('hide');
                    $(_img_container).addClass('hide');
                })
                .attr("src", file.url);
        },

        _loadImage: function(file) {
            $(_img_container)
                .on('load', function() {
                    $(_loader).removeClass('show');
                    $(_img_container).removeClass('hide');
        	        $(_pdf_container).addClass('hide');
                    // _this._reset_rotate();
                })
                .attr("src", file.url);

        },

        // _reset_rotate: function() {
        //     $(_controls_rotate).data('angle', 0);
        //     $(_img_container).css({'transform': 'rotate(0deg)'});
        // },

        _right_left_key_navs: function() {
            $(document).on("keyup", "body", function(e) {
                if (e.target.type == 'text') return;
                if (e.keyCode == 37)_this._moveLeft();
                if (e.keyCode == 39)_this._moveRight();
                if (e.keyCode === 27) $(_viewer).find('.close').click();
            });
        },

        _updateListDocument: function(id, label) {
            _this._pushEditEventAmplitude('list');

            $.each(attachments, function() {
                if(this.id == id) {
                    this.label = label;
                }
            });
        },

        _pushEditEventAmplitude(source) {
            if(typeof source == undefined)
                return;

            __AMPLITUDE.logEvent(__AMPLITUDE.event('document_renamed'), {'source': source});
        },

        _update_attachments_obj: function(file) {
            if($('#modal_documents_viewer').length) {
                if(attachments.length) {
                    attachments.unshift({
                        "id": file.pk,
                        "label": file.label,
                        "url": file.url,
                        "can_preview": true,
                        "extension": file.extension,
                        "added_by": file.added_by,
                        "created_on": file.created_on
                    });
                }
            }
        }
    };

    jQuery(function() {
        if($('#modal_documents_viewer').length)
            __DOCUMENTS_VIEWER.init();
    });
})();
