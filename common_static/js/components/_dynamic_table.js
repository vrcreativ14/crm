/*** Felix Dynamic Data Table + Algolia ***/
;'Use Strict';
var __TABLE;

;(function() {

    var _filters_open_search_field = $('.open-search-field input[type="text"]');
    var _felix_table = $('table.felix-table');
    var _felix_table_filters = $('.table-filters');
    var _felix_table_quick_filters = $('.quick-filters');
    var _felix_table_action_buttons = $('.felix-table-action-buttons');

    var _this = '';

    __TABLE =
    {
        // Onload
        init: function()
        {
            _this = this;

            _this.initTable();
            _this.initFelixTableSearchForm();
            _this.initExportTrigger();
            _this.initSortTrigger();
            _this._quickFilters();
            // $('.quick-filters').on('change', 'input[type=checkbox]', function() {
            //     _this._fetch_felix_table_records();
            // });
        },

        initTable: function() {
            if(_felix_table.length) {
                // Row Click
                _felix_table.on('click', 'td', function(e) {
                    if(_felix_table.hasClass('no-row-clicks'))
                        return;

                    if($(this).hasClass('link')) {
                        if(e.target.nodeName == 'A') return;
                        // Don't trigger click if there is an editable form field in td
                        if ($('.editableform').is(e.target) || $('.editableform').has(e.target).length) {
                            return;
                        }
                        // Don't trigger click if there is checkbox
                        if ($('.felix-checkbox').is(e.target) || $('.felix-checkbox').has(e.target).length || $(e.target).find('.felix-checkbox').length) {
                            return;
                        }
                        // Don't trigger click if there is switch checkbox
                        if ($('.switch-toggle').is(e.target) || $('.switch-toggle').has(e.target).length || $(e.target).find('.switch-toggle').length) {
                            return;
                        }
                        if($(e.target).is('input[type="checkbox"]')) return;
                    }

                    var url = $(this).parent('tr').data('url');
                    var modal = $(this).parent('tr').data('trigger-modal');
                    var callback = $(this).parent('tr').data('click-callback');
                    var params = '';

                    if(window.location.href.indexOf('?') > -1) {
                        var encodedparams = encodeURIComponent(window.location.href.slice(window.location.href.indexOf('?') + 1));
                        params = '?filters=' + Utilities.General.getUrlPathname() + '?' + encodedparams;
                    }

                    if(modal) {
                        $(modal).show();
                    }

                    if(callback && typeof eval(callback) === 'function') {
                        eval(_felix_table.data('update-callback'));
                    }

                    if(url) window.location = url + params;

                    // Calling libs init functions here....
                    __FELIX__.initSearchableSelect();
                });
                // Select all Checkbox
                _felix_table.find('.select-record-all').on('change', function(){
                    $(this).parent().find('.checkmark').removeClass('partial');
                    _felix_table.find('.select-record').prop('checked', this.checked);
                    _felix_table.find('tr').addRemoveClass(this.checked, 'selected');
                    _felix_table_action_buttons.fadeInOrOut(this.checked);

                    if(typeof __RENEWALS !== 'undefined')
                        __RENEWALS.toggle_cta(this.checked);
                });
                // Single Checkbox selection
                _felix_table.on('change', '.select-record', function() {
                    var len = _felix_table.find('.select-record').length;
                    var len_selected = _felix_table.find('.select-record:checked').length;

                    $(this).closest('tr').addRemoveClass(this.checked, 'selected');
                    _felix_table_action_buttons.fadeInOrOut(len_selected);

                    if($("[data-felix-modal='modal_merge_customer']").length) {
                        $("[data-felix-modal='modal_merge_customer']").addRemoveClass(len_selected!=2, 'hide');
                    }

                    _felix_table.find('.select-record-all').prop('checked', (len_selected != len && len_selected));
                    _felix_table.find('.select-record-all').parent().find('.checkmark').addRemoveClass((len_selected != len && len_selected), 'partial');

                    if(typeof __RENEWALS !== 'undefined')
                        __RENEWALS.toggle_cta(len_selected);

                });
                // Delete Button
                _felix_table_action_buttons.find('.delete-record').on('click', function() {
                    if(window.confirm('Are you sure you want to delete selected record(s)?')) {
                        var ids = getSelectedIds();
                        $.each(ids, function(id) {
                            var row = $('#tr_' + this.substring());
                            $.get(row.data('url-delete'), function(response) {
                                if(response.success)
                                    row.remove();
                            });
                        });

                        _felix_table.find('.select-record-all').prop('checked', false);
                    }
                });

                // Delete Button
                _felix_table_action_buttons.find('.close-deal').on('click', function() {
                    var type = $(this).data('type');
                    if(window.confirm('Are you sure you want to mark selected deal(s) as lost?')) {
                        var ids = getSelectedIds();

                        $.each(ids, function(id) {
                            var row = $('#tr_' + this.substring());
                            $.get(DjangoUrls['motorinsurance:deal-mark-as-lost'](this.substring()), function(response) {
                                if(response.success)
                                    row.remove();
                            });
                        });

                        _felix_table.find('.select-record-all').prop('checked', false);
                    }
                });

                // sorting
                _felix_table.on('click', 'th', function() {
                    if($(this).hasClass('sortable')) {
                        var is_asc = $(this).hasClass('asc');
                        var is_desc = $(this).hasClass('desc');

                        _felix_table.find('th').not($(this)).removeClass('asc desc');
                        if(is_asc) {
                            $(this).addClass('desc').removeClass('asc');
                        } else {
                            $(this).addClass('asc').removeClass('desc');
                        }

                        if(_felix_table.data('mode') == 'index') {
                            var sort_type = $(this).data('name') + ((!is_asc)?'_asc':'_desc');

                            var ignore_sorting_keys = ['created_on', 'policy_start_date'];

                            if($.inArray($(this).data('name'), ignore_sorting_keys) > -1 && is_asc)
                                sort_type = '';

                            _felix_table_filters.find('#id_sort_by').val(sort_type);
                        } else {
                            _felix_table_filters.find('#id_order_by').val((is_asc?'-':'') + $(this).data('name'));
                        }
                        _this._fetch_felix_table_records();
                    }
                });

                $('.pagination').on('click', 'li a', function() {
                    if($(this).hasClass('active')) return;
                    if($(this).hasClass('ellipsis')) return;
                    $('#id_page').val($(this).data('number'));

                    _this._fetch_felix_table_records();
                });

                _this._fetch_felix_table_records();

                function getSelectedIds() {
                    return $('.select-record:checked').map(function() {
                        return this.value;
                    }).get();
                }
            }
        },

        initFelixTableSearchForm: function() {
            var st;
            if(_felix_table_filters.length) {

                var form = _felix_table_filters.find('form');
                var action = form.attr('action');

                Utilities.Form.addFilterCount(form);

                form.find('.filter-trigger').click(function() {
                    form.find('.search-popup').fadeToggle('fast');
                    form.find('.search-popup select').chosen();
                });
                form.find('.search-apply').click(function() {
                    __TABLE._fetch_felix_table_records();
                    form.find('.search-popup').fadeToggle('fast');
                });
                form.find('.search-cancel').click(function() {
                    $('.search-popup').fadeOut('fast');
                });
                form.find('.search-clear').click(function () {
                    Utilities.Form.clearForm(form);
                    __TABLE._fetch_felix_table_records();
                    form.find('.search-popup').fadeToggle('fast');
                });

                //Sorting
                form.find('#id_sort_by').change(function () {
                    __TABLE._fetch_felix_table_records();
                });

                // Search query
                $('.open-search-field').on('keyup', 'input[type="text"]', function() {
                    $('.open-search-field .cross').fadeInOrOut($(this).val());
                    let search_term = $(this).val();
                    clearTimeout(st);
                    st = setTimeout(function() {
                        if(search_term.length > 2 || search_term.length == 0) {
                            _felix_table_filters.find('#id_page').val(0);
                            __TABLE._fetch_felix_table_records();
                        }
                    }, 300);
                });
                $('.open-search-field .cross').click(function() {
                    _filters_open_search_field.val('').keyup();
                });
                $('.open-search-field .cross').fadeInOrOut(_filters_open_search_field.val());
            }
        },

        initExportTrigger: function() {
            $('.options-table .dropdown-item.export').click(function() {
                window.location = $(this).data('url') + '?' +  window.location.href.slice(window.location.href.indexOf('?') + 1);
            });
        },

        initSortTrigger: function() {
            if($('#id_sort_by').length) {
                $('.sorting-table .dropdown-item').click(function() {
                    $('.sorting-table .dropdown-item').removeClass('active');
                    $(this).addClass('active');
                    $('#id_sort_by').val($(this).data('val')).change();
                });
            }
        },

        _quickFilters: function() {
            if(!_felix_table_quick_filters.length) return;

            var form = _felix_table_filters.find('form');
            _felix_table_quick_filters.find('button').click(function() {
                if($(this).hasClass('active')) return;
                _felix_table_quick_filters.find('button').removeClass('active');
                $(this).addClass('active');

                var field = $(this).data('field');
                if($('#' + field).length) {
                    form.find('#' + field).val($(this).data('type'));
                    form.find('#id_page').val(1);
                    __TABLE._fetch_felix_table_records();
                }
            });

            if(form.find('#id_assigned_to')) {
                form.find('#id_assigned_to').change(function() {
                    __TABLE._fetch_felix_table_records();
                });
            }
        },

        _fetch_felix_table_records: function() {
            var form = _felix_table_filters.find('form');
            var action = form.attr('action');

            if(!_felix_table.length || !form || !action) return;

            if(_felix_table.data('mode') == 'index') {
                __ALGOLIA._get_search_from_algolia();
            } else {

                _felix_table.addClass('opacity');
                $.get(action, form.serialize(), function(response) {
                    var source   = $('#row-template').html();
                    var template = Handlebars.compile(source);

                    // Records
                    _felix_table.find('tbody').html(
                        response.count?template({'records': response.records}):$('#empty-row-template').html()
                    );
                    // Count
                    $('.table_counts').html(
                        response.count + ' record' + (response.count>1?'s':'') + ' found'
                    ).fadeInOrOut(response.count);
                    //Pagination
                    Utilities.General.generatePagination(response.current_page, response.pages);

                    //Checking for a callback method
                    if(_felix_table.data('update-callback') && typeof eval(_felix_table.data('update-callback')) === 'function')
                        eval(_felix_table.data('update-callback'))(response);

                }, 'json').fail(function(response) {
                    Utilities.Notify.error('Some error occurred while doing the search.', 'Error');
                }).always(function() {
                    _felix_table.removeClass('opacity');
                });

            }

            Utilities.Form.addFilterCount(form);
            //Updating browsers history
            window.history.pushState('', window.document.title, action + '?' + form.serialize());
        }
    };

    jQuery(function() {
        if(_felix_table.length)
            __TABLE.init();
    });
})();
