/*
    User Profile
*/
;
'Use Strict';

var __INVITES;
;(function() {
    var SELECTORS = {
    };

    var _this = '';
    var _form = $('#agent_form');

    __INVITES =
    {
        init: function()
        {
            _this = this;

            $('.formset_row').formset({
                addText: '<span class="font-12"><i class="ti-plus"></i> Add another user</span>',
                deleteText: '<i class="ti-close"></i>',
                prefix: 'invitations_formset',
                added: function(row) {
                    $(row).find('select').chosen();
                    $(row).find('[type=email]').focus();
                    $(row).find('.errorlist').remove();
                    $('.delete-row:first').hide();
                }, removed: function(row) {
                    $(row).find('.errorlist').remove();
                }
            });
            $('.delete-row:first').hide();
            $('.cancel-invite').click(function() {
                var tr = $(this).closest('tr');
                if(window.confirm('Are you sure you want to cancel this invitation?')) {
                    $.get('/accounts/users/invite/cancel/' + $(this).data('id') + '/', function(response) {
                        tr.remove();
                    });
                }
            });
        }
    };

    jQuery(function() {
        if($('body').hasClass('invitations'))
            __INVITES.init();
    });
})();
