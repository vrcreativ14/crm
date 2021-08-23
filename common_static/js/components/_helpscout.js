/* Customers */

var __HELPSCOUT;
;(function() {
    var _this   = '';

    var _deal_id = $('.deal-container').data('id');
    var _modal = $('#modal_helpscout');
    var _helpscout_list_template = $('#row-helpscout-li');
    var _helpscout_conversation_template = $('#row-helpscout-conversation');

    __HELPSCOUT = {
        init: function() {
            _this = this;

            if($('#tab_helpscout').length)
                _this._loadHelpScout();
        },

        _loadHelpScout: function() {
            // Load Converstaion
            $.get(DjangoUrls['core:get-helpscout-conversations-for-deal'](_deal_id), function(response){
                var template = Handlebars.compile(_helpscout_list_template.html());
                var records = '<li class="no-record">No conversation found</li>';

                if('conversations' in response && response.conversations.length) {
                    records = template({'records': response.conversations});
                }
                $('.trail.helpscout-trail').html(records);
            });

            // Single thread
            $('.helpscout-trail').on('click', '.helpscout-converstaion-trigger', function() {
                _modal.find('h1').html($(this).data('subject'));
                _modal.find('a.helpscout_url').prop('href', $(this).data('link'));
                _modal.find('.content').html('');
                _modal.find('.loader').removeClass('hide');
                _modal.show();

                $.get(DjangoUrls['core:get-helpscout-conversation-threads-for-deal'](_deal_id, $(this).data('id')), function(response) {
                    var template = Handlebars.compile(_helpscout_conversation_template.html());
                    var records = '<div class="no-record">No conversation found</div>';

                    if(response.length)
                        records = template({'records': response});

                    _modal.find('.content').html(records);
                    _modal.find('.loader').addClass('hide');
                });
            });
        }
    };

    jQuery(function() {
        __HELPSCOUT.init();
    });

})();
