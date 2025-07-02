/*
    User Profile
*/
;
'Use Strict';

var __PROFILE;
;(function() {
    var SELECTORS = {
    };

    var _this = '';
    var _profile_form = $('#profile_form');
    var _password_form = $('#profile_password_form');

    __PROFILE =
    {
        init: function()
        {
            _this = this;

            // Strength Meter
            $('#id_new_password').keyup(function() {
                var strength = Utilities.Form.passwordStrength($(this).val());

                $('.strength-meter').removeClass('very-weak weak strong very-strong');
                if(strength == 0) {
                }
                else if(strength < 2) {
                    $('.strength-meter').addClass('very-weak');
                }
                else if(strength < 3) {
                    $('.strength-meter').addClass('weak');
                }
                else if(strength < 4) {
                    $('.strength-meter').addClass('strong');
                }
                else if(strength <= 5) {
                    $('.strength-meter').addClass('very-strong');
                }
            });

            $('#id_image').change(function(e) {
                var reader = new FileReader();
                reader.onload = function() {
                    $('.profile-image-container').css({'background-image': 'url('+ reader.result +')'});
                };
                reader.readAsDataURL(e.target.files[0]);
            });

            $('.upload-new').click(function(){
                $('#id_image').click();
                $('#id_remove_avatar').val('');
            });

            $('.remove-avatar').click(function() {
                $('#id_remove_avatar').val('1');
                $('#id_image').val('');
                $('.profile-image-container').css({'background-image': 'none'});
            });

            _profile_form.ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: Utilities.Form.onSuccess,
                error: Utilities.Form.onFailure
            });

            _password_form.ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: Utilities.Form.onSuccess,
                error: Utilities.Form.onFailure
            });

        }
    };

    jQuery(function() {
        __PROFILE.init();
    });
})();

if (typeof module === "object" && typeof module.exports === "object") {
    module.exports = __PROFILE;
}
