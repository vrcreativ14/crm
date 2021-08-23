/*
    User Profile
*/
;
'Use Strict';

var __AGENTS;
;(function() {
    var SELECTORS = {
    };

    var _this = '';
    var _form = $('#agent_form');

    __AGENTS =
    {
        init: function()
        {
            _this = this;

            _form.ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: Utilities.Form.onSuccess,
                error: Utilities.Form.onFailure
            });

            $('.felix-table').on('click', '.remove-agent', function() {
                let status_url = $(this).data('status-url');
                _this._get_user_deals_count_for_delete_modal(status_url);
            });

            $('#assigned-option-0').click(function() {
                $('#modal_agent_delete_confirm select').prop('disabled', true).trigger('chosen:updated');
            });

            $('#assigned-option-1').click(function() {
                $('#modal_agent_delete_confirm select').prop('disabled', false).trigger('chosen:updated');
            });
            $('#delete-user-form .confirm-delete-user').click(function() {
                _this._confirm_delete_user();
            });

            $('.user-profile').on('click', 'button.remove-agent', function() {
                let redirect_url = $(this).data('redirect-url');
                let status_url = $(this).data('status-url');

                _this._get_user_deals_count_for_delete_modal(status_url);
            });
        },

        _get_user_deals_count_for_delete_modal: function(status_url) {
            $.get(status_url, function(res) {
                $('[data-felix-modal="modal_agent_delete_confirm"]').click();

                let elem = $('#modal_agent_delete_confirm');

                elem.find('select option').removeClass('hide');
                elem.find('select option[value=' + res.agent_id + ']').addClass('hide');
                elem.find('select').trigger('chosen:updated');

                elem.find('#delete-user-form').attr('action', res.form_action);
                elem.find('#agent_id').val(res.agent_id);

                elem.find('.agent-name').html(res.agent_name);
                elem.find('.agent-motor-deals').html(res.motor_deals_assigned_to + res.motor_deals_producer);
            });
        },

        _confirm_delete_user: function() {
            let form = $('#delete-user-form');
            form.find('.preloader').removeClass('hide');
            form.find('button').prop('disabled', true);
            $.post(form.attr('action'), form.serialize(), function(res) {
                form.find('button').prop('disabled', false);
                form.find('.preloader').addClass('hide');

                if(res.success) {
                    Utilities.Notify.success('User deleted successfully', 'Success');
                    window.location.href = '/accounts/users/';
                } else {
                    Utilities.Notify.error(res.message, 'Error');
                }
            })
        }
    };

    jQuery(function() {
        __AGENTS.init();
    });
})();

if (typeof module === "object" && typeof module.exports === "object") {
    module.exports = __AGENTS;
}
