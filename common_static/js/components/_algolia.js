/*** Felix Dynamic Data Table + Algolia ***/
;'Use Strict';
var __ALGOLIA;
var searchIndexSelectedFilters;
var stageFacetFilter = [];
var tagsFacetFilter = [];
var usersFacetFilter = [];

;(function() {
    var _filters_open_search_field = $('.open-search-field input[type="text"]');
    var _felix_table = $('table.felix-table');
    var _felix_table_filters = $('.table-filters');

    var _this = '';

    __ALGOLIA =
    {
        // Onload
        init: function()
        {
            _this = this;
            __current_timestamp = (typeof __current_timestamp !== "undefined")?__current_timestamp:new Date().getTime();
        },

        _get_search_params_for_algolia: function() {
            var current_page = _felix_table_filters.find('#id_page').val();
            var status = _felix_table_filters.find('#id_status').val();
            var stage = _felix_table_filters.find('#id_stage').val();
            var assigned_to = _felix_table_filters.find('#id_assigned_to').val();
            var producer = _felix_table_filters.find('#id_producer').val();
            var created_on_after = _felix_table_filters.find('#id_created_on_after').val();
            var created_on_before = _felix_table_filters.find('#id_created_on_before').val();
            var facets = [];
            var facet_filters = [];
            var facet_filters_second_set = [];
            var filters = '';
            var numeric_filters = [];
            var is_deals_table = _felix_table.data('name') == 'deals';
            var is_policies_table = _felix_table.data('name') == 'policies';
            var is_renewals_table = _felix_table.data('name') == 'renewals';
            var index_name = _felix_table.data('index');
            var sort_by = _felix_table_filters.find('#id_sort_by').val();

            if(sort_by) {
                index_name = index_name + '_' + sort_by;
            }

            if(created_on_after)
                numeric_filters.push(
                    'created_on >= ' + moment(created_on_after, 'DD-MM-YYYY').unix());

            if(created_on_before)
                numeric_filters.push(
                    'created_on <= ' + moment(created_on_before, 'DD-MM-YYYY').add(1, 'days').unix());

            if(current_page > 0) current_page = current_page - 1; else current_page = 0;

            if(is_deals_table) {
                facets = ['stage', 'producer_id', 'assigned_to_id', 'tags', 'premium'];

                searchIndexSelectedFilters = [];
                stageFacetFilter = [];
                tagsFacetFilter = [];
                usersFacetFilter = [];

                if(stage) {
                    facet_filters.push('stage:' + stage);
                } else {
                    facet_filters.push(['stage:new', 'stage:quote', 'stage:order', 'stage:housekeeping']);
                }

                if(assigned_to.length) {
                    assigned_to = (assigned_to == 'unassigned')?'0':assigned_to;
                    user_set = ['assigned_to_id:' + assigned_to, 'producer_id:' + assigned_to];
                    facet_filters.push(user_set);
                    facet_filters_second_set.push(user_set);
                }

                if(_felix_table_filters.find('#id_deleted').val())
                    status = 'deleted';
            }

            if(is_policies_table || is_renewals_table) {
                var expiry = _felix_table_filters.find('#id_expiry').val();
                var product = _felix_table_filters.find('#id_products').val();

                facets = ['product_id', 'status', 'premium', 'owner_id'];

                if(expiry == 'active')
                    numeric_filters.push('policy_expiry_date > ' + __current_timestamp);

                if(expiry == 'expired')
                    numeric_filters.push('policy_expiry_date <= ' + __current_timestamp);

                if(product)
                    facet_filters.push('product_id:' + product);

                if(is_renewals_table) {
                    let policy_expiry_from_date = $('#id_from_date').val();
                    let policy_expiry_to_date = $('#id_to_date').val();
                    let hide_renewal_deals = _felix_table_filters.find('#id_hide_renewal_deal').val();

                    if(!policy_expiry_from_date && !policy_expiry_to_date) {
                        policy_expiry_from_date = moment().format('X');
                        policy_expiry_to_date = moment().add(60, 'days').format('X');
                    }
                    if(hide_renewal_deals)
                        facet_filters.push("has_renewal_deal:false");

                    if(policy_expiry_from_date)
                        numeric_filters.push('policy_expiry_date > ' + policy_expiry_from_date);
                    if(policy_expiry_to_date)
                        numeric_filters.push('policy_expiry_date <= ' + policy_expiry_to_date);
                }
            }

            facet_filters.push('status:' + (status?status:'active'));
            facet_filters_second_set.push('status:' + (status?status:'active'));

            return [{
                indexName: index_name,
                query: _filters_open_search_field.val(),
                params: {
                    page: current_page,
                    hitsPerPage: 30,
                    facets: facets,
                    filters: filters,
                    numericFilters: numeric_filters,
                    facetFilters: facet_filters
                }
            }, {
                indexName: index_name,
                query: _filters_open_search_field.val(),
                params: {
                    page: current_page,
                    attributesToRetrieve: [],
                    attributesToHighlight: [],
                    attributesToSnippet: [],
                    facets: facets,
                    numericFilters: numeric_filters,
                    facetFilters: facet_filters_second_set
                }
            }];
        },

        _get_search_from_algolia: function(queries) {
            if(!_felix_table.length) return;

            if(!queries || queries === undefined) queries = _this._get_search_params_for_algolia();

            var is_deals_table = _felix_table.data('name') == 'deals';
            var is_policies_table = _felix_table.data('name') == 'policies';

            var api_key = app_config.ALGOLIA_SEARCH_API_KEY;

            if(_felix_table.data('securedapikey'))
                api_key = _felix_table.data('securedapikey');

            var client = algoliasearch(app_config.ALGOLIA_APP_ID, api_key);

            _felix_table.addClass('opacity');

            client.search(queries).then((content) => {
                _felix_table.removeClass('opacity');

                var source   = $('#row-template').html();
                var template = Handlebars.compile(source);
                var records = content.results[0];

                $('.table_counts').html(records.nbHits + ' records found');

                $('.felix-table-body').html(template({'records': records.hits}));

                Utilities.General.generatePagination((records.page + 1), records.nbPages);

                // For deals list only
                if(is_deals_table) _this._fill_motor_deals_list_content(content);
                // For policies list only
                if(is_policies_table) _this._fill_policies_list_content(content);
            });
        },

        _fill_policies_list_content: function(content) {
            var first_set = content.results[0];
            var second_set = content.results[1];

            if(first_set.nbHits) {
                $('.policies-total-amount').removeClass('hide').find('span').html(
                    '<span>' + accounting.format(first_set.facets_stats.premium.sum) + ' ('+ first_set.nbHits +' Policies)</span>'
                );
            } else {
                $('.policies-total-amount').addClass('hide');
            }
        },

        _fill_motor_deals_list_content: function(content) {
            var first_set = content.results[0];
            var second_set = content.results[1];

            if(first_set.nbHits) {
                $('.deals-total-amount').removeClass('hide').find('span').html(
                    '<span>' + accounting.format(first_set.facets_stats.premium.sum) + ' ('+ first_set.nbHits +' Deals)</span>'
                );
            } else {
                $('.deals-total-amount').addClass('hide');
            }

            _felix_table_filters.find('.stages button span').html('0');
            _felix_table_filters.find('.stages button').prop('disabled', true);

            var all_open_count = 0;

            if('facets' in second_set) {
                $.each(second_set.facets.stage, function(k, v) {
                    _felix_table_filters.find('.stages button[data-type=' + k + '] span').html(v);
                    _felix_table_filters.find('.stages button[data-type=' + k + ']').prop('disabled', !v);
                });

                $.each(second_set.facets.stage, function(k, v) {
                    if(k == 'won' || k=='lost') return;

                    all_open_count += v;
                });
            }

            _felix_table_filters.find('.stages button:first-child span').html(all_open_count);
            _felix_table_filters.find('.stages button:first-child').prop('disabled', !second_set.nbHits);

            __FELIX__._loadLibs();

        }
    };

    jQuery(function() {
        __ALGOLIA.init();
    });
})();
