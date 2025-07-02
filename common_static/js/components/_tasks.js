/* DEALS */
;
'Use Strict';

var __TASKS;
;(function() {

    var _this   = '';
    var _table  = $('#tasks-table');
    var _form   = $('#task_form');
    var _filter_form   = $('#tasks-search');

    var _tasks_trail = $('.trail.task-trail');

    var _felix_table = $('table.felix-table');
    var _felix_table_filters = $('.table-filters');
    var _felix_table_quick_filters = $('.quick-filters');

    var _deal_id = $('.deal-container').data('id');
    var _deal_title = $('.deal-container').data('title');

    var _agent_id = $('body').data('agent');

    __TASKS =
    {
        init: function()
        {
            _this = this;

            _this._initTaskForm();
            _this._loadDealTasks();

            $("#search-clear").on("click", function () {
                window.location.href = $("#tasks-search").data("reset-url");
            });

            var filter_count = Utilities.Form.addFilterCount(_filter_form);
            if(filter_count) {
                $('.filter-count').html(filter_count).removeClass('hide');
            }

            $('.mark-as-done').click(function() {
                // Delete Button
                if(window.confirm('Are you sure you want to mark the selected task(s) as done?')) {
                    var ids = $('.select-record:checked').map(function() {
                        return this.value;
                    }).get();

                    $.post(
                        DjangoUrls[__app_name + ':tasks-mark-as-done'](),
                        {'task_ids': ids},
                        function(response) {
                            __TABLE._fetch_felix_table_records();
                        }
                    );
                }
            });

            $('.deal-container').on('click', 'button.add-task', function() {
                _this._resetTaskForm();

                $('<option/>').val(_deal_id).text(_deal_title).appendTo('#task_form #id_deal');
                $('#task_form #id_deal').trigger('chosen:updated');

            });

            $('.trail.task-trail').on('click', '.task-edit', function() {
                $('[data-felix-modal="modal_task"]').click();
                _this._getTaskDetail($(this).data('id'), _deal_title);
            });

            $('.task-actions button').click(function() {
                $('#id_tasks-fitler-form #filter_type').val($(this).data('type'));
                $('.task-actions button').removeClass('active');
                $(this).addClass('active');
                _this._loadDealTasks();
            });

            $('.trail.task-trail').on('click', '.task-remove', function() {
                if(window.confirm('Are you sure you want to delete this task?')) {
                    $.get(DjangoUrls[__app_name + ':task-delete']($(this).data('id')), function(response) {
                        if(response.success) {
                            Utilities.Notify.success('Task deleted successfully', 'Success');
                            _this._loadDealTasks();
                        } else {
                            Utilities.Notify.error(response.error, 'Error');
                        }
                    });
                }
            });
        },

        _loadDealTasks: function() {
            if(!_tasks_trail.length) return;

            var url = DjangoUrls[__app_name + ':deal-tasks'](_deal_id) + '?' + $('#id_tasks-fitler-form').serialize();
            $('.task-loader').show();
            $.get(url, function(response){
                var source = $('#row-tasks-li').html();
                var template = Handlebars.compile(source);
                var records = '<li class="no-record">No task found</li>';

                if(response.length) {
                    records = template({'records': response});
                }
                _tasks_trail.html(records);

                $('.task-loader').hide();
            });
        },

        _resetTaskForm: function() {
            _form.find('select').val('');
            _form.find('textarea').val('');
            _form.find('#id_time').val('10:00');
            _form.find('select').trigger('chosen:updated');
            _form.find('#id_is_completed').prop('checked', false);
            _form.find('#id_deal option').remove();
        },

        _initTaskForm: function() {
            if(!_form.length) return;

            $('[data-felix-modal="modal_task"]').click(function() {
                if($('[href="#tab_tasks"]').length)
                    $('[href="#tab_tasks"]').click();

                _form.find('#id_title, textarea').val('').change();
                _form.find('#id_is_completed').prop('checked', false);

                if(_deal_id !== undefined) {
                    _form.find('#id_deal').val(_deal_id);
                    _form.find('#id_deal').trigger('chosen:updated');
                }

                if(_agent_id !== undefined) {
                    _form.find('#id_assigned_to').val(_agent_id);
                    _form.find('#id_assigned_to').trigger('chosen:updated');
                }

                _form.find('#id_task_id').val('');

            });

            _form.ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                error: Utilities.Form.onFailure,
                success: function(response, status, xhr, form) {
                    form.find('button[type=submit]').removeClass('loader');

                    if(response.success) {
                        _form.find('[data-modal-close]').click();
                        Utilities.Notify.success('Task ' + (response.updated?'updated':'created') + ' successfully.', 'Success');

                        if(_felix_table.length) {
                            __TABLE._fetch_felix_table_records();
                        } else {
                            if(response.task.object_id == _deal_id) {
                                _this._loadDealTasks();
                            }
                        }
                    } else {
                        Utilities.Notify.error('Please check all the required fields.', 'Error');
                        Utilities.Form.addErrors(form, response.errors);
                    }
                }
            });
        },

        _getTaskDetail: function(id, deal_title) {
            if(!id) return;

            _this._resetTaskForm();

            $.get(DjangoUrls[__app_name + ':get-task-json'](id), function(response) {
                $('<option/>').val(response.deal).text(deal_title).appendTo('#id_deal');
                _form.find('#id_deal').trigger('chosen:updated');

                _form.find('#id_task_id').val(response.pk);
                _form.find('#id_title').val(response.title);
                _form.find('#id_date').val(response.due_date);
                _form.find('#id_time').val(response.due_time);
                _form.find('#id_time').val(response.due_time).trigger('chosen:updated');
                _form.find('#id_assigned_to').val(response.assigned_to);
                _form.find('#id_assigned_to').val(response.assigned_to).trigger('chosen:updated');
                _form.find('#id_is_completed').prop('checked', response.is_completed);
                _form.find('#id_content').val(response.content);
            });
        }

    };

    jQuery(function() {
        __TASKS.init();
    });
})();
