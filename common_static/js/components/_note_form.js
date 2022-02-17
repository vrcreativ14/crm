/*** NOTE Form and List ***/
;'Use Strict';
var __NOTE;

;(function() {
    var _this = '';
    var _note_form = $('#note_form');

    __NOTE =
    {
        // Onload
        init: function()
        {
            _this = this;
            _this.initForm();
        },

        initForm: function() {
            if(_note_form.length) {

                $('[data-felix-modal="modal_add_note"]').click(function() {
                    _note_form.find('textarea').val('');
                });
                _note_form.ajaxForm({
                    beforeSubmit: Utilities.Form.beforeSubmit,
                    error: Utilities.Form.onFailure,
                    success: function(response, status, xhr, form) {
                        form.find('button[type=submit]').removeClass('loader');

                        if(response.success) {
                            Utilities.Notify.success('Note added successfully.', 'Success');

                            _note_form.find('[data-modal-close]').click();

                            var note = '<div class="label">Note created</div>';
                                if('note_pk' in response.note){
                                    note += '<div class="note note-id-'+response.note.note_pk+'">' + response.note.content + '</div>';
                                }else{
                                    note += '<div class="note">' + response.note.content + '</div>';
                                }
                                note += '<div class="text-muted">' + response.note.created_on + ' ';
                                note += 'by ' + response.note.added_by;
                                note += '</div>';
                                if('note_pk' in response.note){
                                    note += '<div><button id="delete-mortgage-note" data-deleteurl="/mortgage/deals/notes/delete/'+response.note.note_pk+'/" onclick="deleteMortgageNote(this)" class="btn btn-sm btn-danger"> Delete </button> <button data-felix-modal="modal_update_note"  data-pk="'+response.note.note_pk+'" class="btn btn-info-container btn-primary btn-sm" onclick="editMortgageNote(this)">Edit Note</button></div>'
                                }

                            _this._prependNoteInTrail(note);
                        } else {
                            Utilities.Notify.error('Please check all the required fields.', 'Error');
                            Utilities.Form.addErrors(form, response.errors);
                        }
                    }
                });
            }
        },

        _prependNoteInTrail: function(content) {
            $('.note-trail').prepend('<li>' + content + '</li>');
            $('.note-trail').removeClass('hide');
            $('.small-note.note-trail').remove();
        },
    };

    jQuery(function() {
        __NOTE.init();
    });
})();
