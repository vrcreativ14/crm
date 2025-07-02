/* POLICIES */
;
'Use Strict';

var __RENEWALS;
;(function() {

    var _this   = '';

    __RENEWALS =
    {
        init: function()
        {
            _this = this;

            let default_start_date = moment();
            let default_end_date = moment().add(60, 'days');

            let url_params = Utilities.General.getUrlParamKeyValue();

            if('from_date' in url_params && url_params.from_date)
                default_start_date = moment.unix(url_params.from_date);

            if('to_date' in url_params && url_params.to_date)
                default_end_date = moment.unix(url_params.to_date);

            $('#renewal_date_filter').daterangepicker({
                startDate: default_start_date,
                endDate: default_end_date,
                ranges: {
                   'Today': [moment(), moment()],
                   'Tomorrow': [moment().add(1, 'days'), moment().add(1, 'days')],
                   'Next 7 Days': [moment(), moment().add(6, 'days')],
                   'Next 30 Days': [moment(), moment().add(29, 'days')],
                   'Next 60 Days': [moment(), moment().add(60, 'days')],
                   'This Month': [moment().startOf('month'), moment().endOf('month')],
                   'Next Month': [moment().add(1, 'month').startOf('month'), moment().add(1, 'month').endOf('month')],
                   'Next 12 Months': [moment(), moment().add(365, 'days')],
                },
                locale: {
                  format: 'MMMM D, YYYY',
                  cancelLabel: 'Clear'
                }
            }, _this.change_date);

            $('#id_from_date').val(default_start_date.unix());
            $('#id_to_date').val(default_end_date.unix());

            $('#renewal_date_filter').html('Next 60 Days');

            $('[name=hide-renewaldeals]').change(function() {
                $('#id_hide_renewal_deal').val($(this).is(':checked')?'true':'');
                __TABLE._fetch_felix_table_records();
            });

            $('.renewal-deal').on('click', function() {
                var ids = $('.select-record:checked').map(function() {
                    return this.value;
                }).get();

                if(!ids.length) { Utilities.Notify.notice('Please select at least one record to create a renewal deal.'); return; }

                if(window.confirm('Are you sure you want to create a renewal deal from all selected policy record(s)?')) {
                    var ids = $('.select-record:checked').map(function() {
                        return this.value;
                    }).get();
                    $.get(
                        DjangoUrls['motorinsurance:create-renewals-deals'](),
                        {'pids': ids.join(',')},
                        function(response) {
                            if(response.success) {
                                if(response.new_deals_data.length) {
                                    Utilities.Notify.success('Deal(s) created successfully', 'Success');
                                }
                                if(response.errors.length) {
                                    var errors = `<ul class="m-t-10 m-l--20 font-12">`;
                                    response.errors.map(function(e) {
                                        errors += `<li>${e}</li>`;
                                    });
                                    errors += `</ul>`;

                                    Utilities.Notify.error('Following errors occurred:' + errors, 'Error');
                                }

                                setTimeout(function() {
                                    __TABLE._fetch_felix_table_records();
                                }, 2000);
                            }
                        }
                    );
                }
            });
        },

        change_date: function(start, end, label) {
            if(typeof start === 'undefined') start = moment(); 
            if(typeof end === 'undefined') end = moment().add(29, 'days');

            $('#id_from_date').val(start.unix());
            $('#id_to_date').val(end.unix());

            $('#renewal_date_filter').html(label);

            $('.clear-calendar').removeClass('hide');

            $('.quick-filters [data-type="all"]').click();

            __TABLE._fetch_felix_table_records();
        },

        toggle_cta: function(count) {
            $('button.renewal-deal').attr(
                'title',
                count?'':'Select at least one record to create a renewal deal'
            );
            $('button.renewal-deal').addRemoveClass(!count, 'disabled');
        }
    };

    jQuery(function() {
        if($('body[data-current-nav=renewals]').length)
            __RENEWALS.init();
    });
})();
