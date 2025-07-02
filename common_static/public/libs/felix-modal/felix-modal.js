'Use Strict';

var felixModal;
;(function() {
    var SELECTORS = {
        "parentElement": "body",
        "modalContainer": ".felix-modal-container",
        "modal": ".felix-modal-container .felix-modal",
        "triggerElement": "[data-felix-modal]",
        "closeButton": ".felix-modal-container .close"
    };

    var closeElement = '<div class="close-bar"><a href="javascript:" class="close"></a></div>';

    var _this = '';

    felixModal =
    {
        init: function()
        {
            _this = this;
            var parent = SELECTORS.parentElement;

            $(parent).on('click', SELECTORS.closeButton, function() {
                _this.close($(this));
            });

            $(parent).on('click', SELECTORS.modalContainer, function(e) {
                if(e.target.className == (SELECTORS.modalContainer.replace('.',''))){
                    _this.close($(this));
                }
            });

            $(parent).on('click', SELECTORS.triggerElement, function() {
                _this.open($(this).data('felix-modal'));
            });
        },

        open: function(element_id) {
            if($('#' + element_id).length) {
                $('#' + element_id).show();
                felixModal.injectCloseTrigger(element_id);
            }
        },

        close: function(element) {
            if(element.closest(SELECTORS.modalContainer).hasClass('dont-close')) return;

            element.closest(SELECTORS.modalContainer).hide();
        },

        injectCloseTrigger: function(element_id) {
            if(!$('#' + element_id + ' .close-bar').length) {
                $('#' + element_id).find('.felix-modal').prepend(closeElement);
            }
        }
    };

    $(function() {
        felixModal.init();
    });
})();

if (typeof module === "object" && typeof module.exports === "object") {
    module.exports = felixModal;
}
