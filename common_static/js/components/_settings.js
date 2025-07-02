/*
    Company Settings
*/
;
'Use Strict';

var __SETTINGS;
;(function() {
    var SELECTORS = {
    };

    var _this = '';
    var _form = $('#company_settings_form');

    __SETTINGS =
    {
        init: function()
        {
            _this = this;

            if(_form.length) {
                _this._initForms();
                _this._config();
            }

            if($('#id_auto-close-chk').length) {
                $('#id_auto-close-chk').change(function() {
                    $('#id_auto_close_quoted_deals_in_days').attr('disabled', !$(this).is(':checked'));
                });
            }
        },

        _config: function() {
            $('textarea').not('.ignore-length').maxlength({
                alwaysShow: true,
                warningClass: "badge badge-info",
                limitReachedClass: "badge badge-warning"
            });

            $('.upload-new').click(function(){
                $('#id_logo').click();
                $('#id_remove_avatar').val('');
            });

            $('#id_logo').change(function(e) {
                var reader = new FileReader();
                reader.onload = function() {
                    $('.profile-image-container').css({'background-image': 'url('+ reader.result +')'});
                };
                reader.readAsDataURL(e.target.files[0]);
            });

            $('.remove-avatar').click(function() {
                $('#id_remove_avatar').val('1');
                $('#id_image').val('');
                $('.profile-image-container').css({'background-image': 'none'});
            });
        },

        _initForms: function() {
            _form.ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: Utilities.Form.onSuccess,
                error: Utilities.Form.onFailure
            });
        }
    };

    jQuery(function() {
        __SETTINGS.init();
    });
})();

if (typeof module === "object" && typeof module.exports === "object") {
    module.exports = __SETTINGS;
}
