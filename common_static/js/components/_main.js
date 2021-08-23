/*** Main APP ***/
;'Use Strict';
var __FELIX__;

;(function() {

    var _general_search_field = $('#general_search_field');
    var _general_search_results_container = $('.app-search .search-results-container');
    var _felix_table = $('table.felix-table');
    var _felix_table_filters = $('.table-filters');

    var _info_container = $('.info-container');

    var _deal_id = $('.deal-container').data('id');
    var _agent_id = $('body').data('agent');

    var _this = '';

    __FELIX__ =
    {
        // Onload
        init: function()
        {
            _this = this;
            _this.initSearchableSelect();
            _this.initNavbar();
            _this.initPasswordToggler();
            _this.initLoader();
            _this.initGeneralSearch();
            _this.initMenuItem();
            _this.initComponents();
            _this.initToggleSearch();
            _this.initDatepicker();
            _this.initDeleteRecord();
            _this.initMoneyField();
            _this.initTabOnLoad();
            _this.initInfoContainer();
            _this.initAutocompleteField();
            _this.initTitleTooltip();
            _this.initImagePreview();
            _this.loadRenewalsCounter();

            // $.datepicker.setDefaults({format: 'dd-mm-yy'});

            if($('#audit-trail').length)
                $('#audit-trail').DataTable({"order": [[ 3, "desc" ]]});

            if($('table#attachments').length)
                $('table#attachments').DataTable();

            $('body').on('click', function(e) {
                var felix_table_search_popup = _felix_table_filters.find('form .search-popup');

                if (!_general_search_results_container.is(e.target) && _general_search_results_container.has(e.target).length === 0) 
                    if (!_general_search_field.is(e.target) && _general_search_field.has(e.target).length === 0) 
                        _general_search_results_container.fadeOut('fast');

                if (!felix_table_search_popup.is(e.target) && felix_table_search_popup.has(e.target).length === 0) 
                    if (!$('.filter-trigger').is(e.target) && $('.filter-trigger').has(e.target).length === 0) 
                        felix_table_search_popup.fadeOut('fast');
            });

            $(document).keydown(function(event) { 
                if (event.keyCode == 27) { 
                    if($('.felix-modal-container').is(':visible')) {
                        $('.felix-modal-container').each(function() {
                            felixModal.close($(this));
                        });
                    }
                }
            });

            $('.select-with-reset').on('click', '.reset', function() {
                $(this).siblings('select').val('').trigger('chosen:updated');
            });

            $(document).on('change', '.editable-input select', function() {
                var parent = $(this).closest('.editable-container');
                var elem = parent.parent().find('.select-editable');

                if(elem && elem.data('name') == 'producer_id' && loggedin_user_data.ROLE == 'producer' && $(this).val() != loggedin_user_data.ID) {
                    if(!window.confirm('If you assign this deal to another producer then you will no longer be able to see it. Do you want to go ahead and unassign yourself?')) {
                        parent.find('.editable-cancel').click();
                    }
                }
            });

            $('#product_line_switcher').change(function() {
                let val = $(this).val();
                window.location.href = DjangoUrls[val + ':deals']();
            });
        },

        /***** INIT Functions *****/

        _loadLibs: function() {
            _this.initSearchableSelect();
            _this.initDatepicker();
            _this.initMoneyField();
            _this.initAutocompleteField();

            __XEDITABLE.init();
            __FILE_UPLOADER.init();
        },

        initTitleTooltip: function() {
            $(function() {
                $(document).tooltip({
                    tooltipClass: 'felix-ui-tooltip',
                    show: null,
                    hide: null,
                    position: { my: "left-10 top+15", at: "left bottom", collision: "flipfit" }
                });
            });
        },

        loadRenewalsCounter: function() {
            if($('.renewals-menu-counter').length) {
                $.get(DjangoUrls['motorinsurance:renewals-count'](), function(res) {
                    if(res.count)
                        $('.renewals-menu-counter .badge-counter').html(res.count).addClass('visible');
                });
            }
        },

        initImagePreview: function() {
            $.previewImage();
        },

        initSearchableSelect: function() {
            if($('select:visible').length) {
                $('select:visible').each(function() {
                    if (!$(this).data('select2')) {
                        if($(this).hasClass('sorted')) {
                            var options = $(this).find('option').sort(function(a, b) {
                                return a.text < b.text ? -1 : a.text > b.text ? 1 : 0;
                            });
                            $(this).empty().append(options);
                        }
                        $(this).chosen({
                            placeholder_text_single: "Select option...",
                            no_results_text: "No record found"
                        });
                    }
                });
            }
        },

        initAutocompleteField: function() {

            $('.autocomplete-field').on('input', function() {
                $('#' + $(this).data('target')).val('');
                $(this).parent().removeClass('new');
            });
            $('.autocomplete-field').on('blur', function() {
                if(!$(this).val()) return;
                if($('#' + $(this).data('target')).val()) {
                    $(this).parent().removeClass('new');
                }
                else {
                    $(this).parent().addClass('new');
                }
            });
            $('.autocomplete-field').autocomplete({
                minLength: 2,
                source: function(request, response) {
                    var element = $(this.element);
                    element.parent().addClass('loader');

                    $.ajax({
                        url: element.data('url'),
                        method: 'GET',
                        data: {
                            search_term: request.term
                        },
                        success: function( data ) {
                            element.parent().removeClass('loader');
                            response(data);
                        }
                    });
                },
                focus: function(event, ui) {
                    // $(this).val(ui.item.label);
                    // return false;
                },
                select: function(event, ui) {
                    $(this).val(ui.item.label);
                    $(this).removeClass('new');
                    $('#' + $(this).data('target')).val(ui.item.id);

                    return false;
                },
                response: function(event, ui) {
                    if(ui.content.length)
                        $(this).parent().removeClass('new');
                    else
                        $(this).parent().addClass('new');
                }
            }).autocomplete("instance")._renderItem = function(ul, item) { 
                var content = '';

                if('label' in item) content += '<span>' + item.label + '</span>';
                if('desc' in item)  content += item.desc;

                return $("<li>").append(content).appendTo(ul);
            };
        },

        initPasswordToggler: function() {
            $('.password-show-toggle').click(function() {
                var field = $(this).prev('input');

                if(field.is(':password')) {
                    $(this).html('<i class="ti-eye"></i>');
                    field.attr('type', 'text');
                } else {
                    $(this).html('<i class="ti-eye c-lgrey"></i>');
                    field.attr('type', 'password');
                }
            });
        },

        initInfoContainer: function(){
            _info_container.on('click', '.toggle-details', function() {
                $(this).toggleClass('less').closest('.info-table').find('.collapsable').slideToggle(100, function() {
                    // if ($(this).is(':visible'))
                    $(this).toggleClass('flex');
                });
            });

            _info_container.on('click', '.toggle-deal-processes', function() {
                $(this).toggleClass('show-div');
                $('.deal-processes').slideToggle(100);
            });
        },

        initTabOnLoad: function() {
            var anchor = Utilities.General.getUrlAnchor();

            if(anchor && $('a[href="#'+anchor+'"]').length) {
                $('a[href="#'+anchor+'"]').click();
            }
        },

        initGeneralSearch: function() {
            var st;
            _general_search_field.focus(function() {
                var val = $(this).val();
                if(val) _general_search_results_container.fadeIn('fast');
            });
            _general_search_field.keyup(function() {
                clearTimeout(st);
                st = setTimeout(function() {
                    _general_search_results_container.fadeIn('fast');
                }, 1000);
            });
        },

        initMoneyField: function() {
            if(!$('.auto-format-money-field').length) return;
            // Restrict to numbers comma and dot only
            $('body').on('input', '.auto-format-money-field',function() {
                var value = $(this).val().replace(/[^0-9.,]*/g, '');
                value = value.replace(/\.{2,}/g, '.');
                value = value.replace(/\.,/g, ',');
                value = value.replace(/\,\./g, ',');
                value = value.replace(/\,{2,}/g, ',');
                value = value.replace(/\.[0-9]+\./g, '.');

                // $(this).val(value);
            });
            // Form money field after user has done typing
            $('body').on('blur', '.auto-format-money-field', function(event) {
                $(this).val(function(index, value) {
                    return accounting.formatNumber($(this).val(), 2, ',', '.');
                });
            });
            // Form money field on focus to convert it back to integer
            $('body').on('focus', '.auto-format-money-field', function(event) {
                $(this).val(function(index, value) {
                    return accounting.unformat($(this).val());
                });
            });
            // Format all money fields on page load
            $('.auto-format-money-field').blur();
        },

        initNavbar: function () {
            $('.navbar-toggle').on('click', function (event) {
                $(this).toggleClass('open');
                $('#navigation').slideToggle(400);
            });

            $('.navigation-menu>li').slice(-1).addClass('last-elements');

            $('.navigation-menu li.has-submenu a[href="#"]').on('click', function (e) {
                if ($(window).width() < 992) {
                    e.preventDefault();
                    $(this).parent('li').toggleClass('open').find('.submenu:first').toggleClass('open');
                }
            });
        },

        initLoader: function () {
            $(window).on('load', function () {
                $('#status').fadeOut();
                $('#preloader').delay(350).fadeOut('slow');
                $('body').delay(350).css({
                    'overflow': 'visible'
                });
            });
        },

        // === following js will activate the menu in menu bar based on url ====
        initMenuItem: function () {
            $(".navigation-menu a").each(function () {
                var current_nav = $('body').data('current-nav');

                if ($(this).data('elem') == current_nav) { 
                    // $(this).parent().addClass("active"); // add active to li of the current link
                    $(this).parent().parent().parent().addClass("active"); // add active class to an anchor
                    // $(this).parent().parent().parent().parent().parent().addClass("active"); // add active class to an anchor
                }
            });
        },

        initComponents: function () {
            if($('[data-toggle="tooltip"]').length)
                $('[data-toggle="tooltip"]').tooltip();
            if($('[data-toggle="popover"]').length)
                $('[data-toggle="popover"]').popover();
        },

        initToggleSearch: function () {
            $('.toggle-search').on('click', function () {
                var targetId = $(this).data('target');
                var $searchBar;
                if (targetId) {
                    $searchBar = $(targetId);
                    $searchBar.toggleClass('open');
                }
            });
        },

        initDatepicker: function() {
            if($('.datepicker').length)
                $('.datepicker').each(function() {
                    var options = {
                        format: 'dd-mm-yyyy',
                        autoclose: true,
                    };
                    if($(this).data('start-date-today'))
                        options['startDate'] = new Date;

                    $(this).datepicker(options);
                });

            if($('.datepicker-custom').length)
                $('.datepicker-custom').each(function() {
                    var options = {
                        format: 'dd-mm-yyyy',
                        autoclose: true,
                    };
                    if($(this).data('start-date-today'))
                        options['startDate'] = new Date;

                    $(this).datepicker(options);
                });
        },

        initDeleteRecord: function() {
            $('.btn-delete-record').click(function() {
                var redirect_url = $(this).data('redirect-to');
                if(window.confirm('Are you sure you want to delete this record?')) {
                    $.get($(this).data('url'), function(response) {
                        if(response.success) {
                            Utilities.Notify.success('Record deleted successfully.', 'Success');
                            if(redirect_url) {
                                setTimeout(function() {
                                    window.location = redirect_url;
                                }, 2000);
                            }
                        } else {
                            Utilities.Notify.error(response.error, 'Error');
                        }
                    }).fail(function(resp) {
                        if(resp.status == 403) {
                            Utilities.Notify.error('You do not have permission to delete a motor deal. Please check with your manager for details.', 'Permission Denied');
                        }
                    });
                }
            });
        },
    };

    jQuery(function() {
        __FELIX__.init();
    });
})();
