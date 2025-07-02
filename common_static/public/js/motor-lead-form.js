'Use Strict';

var __MotorLeadForm__;
var lead_form_wizard = '';
;(function() {
    var SELECTORS = {
        "tooltip": ".tooltip-help-layout",
        "tooltipClose": ".tooltip-help-close-container",
        "select": "select",
        "select_numeric": "select.numeric-field",
        "select_no_width": ".select-no-width",
        "select_medium_width": ".select-medium-width",
        "datepicker": "#id_dob, #id_date_of_first_registration, #id_uae_license_issue_date",
        "newCar": "#id_new_car",

        "form": "#motor_lead_form",
        "calendarIcon": ".fa-calendar",

        "oldCars": ".for-old-cars-only",

        "preloader": ".preloader",
        "submitButton": ".submit-button",
        "helpButton": ".help-trigger",

        "carYear": "#id_car_year",
        "carMake": "#id_car_make",
        "carModel": "#id_car_model",

        "pagination": "[aria-label='Pagination']",

        "day": ".dd_days",
        "month": ".dd_months",
        "year": ".dd_years",

        "first_license": "#id_first_license_country",

        "error_popup": ".popup-error-container",

    };

    var requiredFieldsArray = ['id_lead_type', 'id_current_insurer', 'id_car_year', 'id_vehicle_insured_value', 'new_date_of_first_registration', 'id_name', 'id_email', 'id_contact_number'];

    var MESSAGES = {
        'error_title': 'Oops, something\'s missing',
        'error_text': 'Please complete all the required fields on this page to move forward.',
    };

    var modelEndpointUrl = DjangoUrls['motorinsurance:motor-tree']();
    var thankYouUrl = DjangoUrls['motorinsurance:lead-submitted-thanks']();

    var validationTemplate = '<span class="validation-error custom-validation-error"><span class="field-validation-error">{msg}</span></span>';

    var NCC_CANT_REMEMBER   = 'unknown';
    var NCC_NEVER           = 'never';
    var NCC_12_MONTHS       = 'this year';

    var LEAD_TYPE_NEW       = 'new';
    var LEAD_TYPE_RENEW     = 'own';
    var LEAD_TYPE_USED      = 'used';

    var _this = '';

    __MotorLeadForm__ =
    {
        init: function()
        {
            _this = this;

            _this._initForm();
            _this._initTooltipActions();
            _this._initModelMakeActions();
            _this._initOldCarOnlyTriggers();

            $('body').on('focus', 'select, input', function(){
                $('.form-group.active').removeClass('active');
                $(this).closest('.form-group').addClass('active');
            });

            $(".form-group").hover(
                function () {
                    $('.form-group.active').removeClass('active');
                    $(this).addClass("active");
                }
            );

            $('.auto-format-money-field').keyup(function(event) {
                if(event.which >= 37 && event.which <= 40) return;
                $(this).val(function(index, value) {
                    return value.replace(/\D/g, "").replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                });
            });

            $('.popup-error-container .error-message').on('click', function() {
                _this._showErrorPopup();
                
            });
            
            $('select, input').on('change', function(){
                $(this).closest('.heading-error').removeClass('heading-error');
            });

            $('#id_cant_find_car, #id_custom_car_name').addClass('ignore');

            $('#id_cant_find_car').on('change', function(){
                var custom_car_field = $('.custom_car_name_field');
                var car_model_field = $('#id_car_model');

                if($(this).is(":checked")) {
                    custom_car_field.slideDown('fast');
                    $('#id_custom_car_name').focus();
                    car_model_field.attr('disabled', true).trigger('chosen:updated');

                    $('#id_cant_find_car, #id_custom_car_name').removeClass('ignore');
                } else {
                    custom_car_field.slideUp('fast');
                    car_model_field.attr('disabled', false).trigger('chosen:updated');

                    $('#id_cant_find_car, #id_custom_car_name').addClass('ignore');
                }
            });

            $('.field-select-buttons button').on('click', function(){
                $(this).siblings('button').removeClass('active');
                $(this).addClass('active');
                $(this).closest('.field-select-buttons').find('input[type="hidden"]').val(
                    $(this).data('value')
                );
                //remove error if any
                $(this).closest('.field-select-buttons').find('em').remove();
                $(this).closest('label').removeClass('heading-error');
            });

            $date_of_first_registration = $("#new_date_of_first_registration");
            var event_type = "keypress";

            if(Utilities.Check.isMobile() && !Utilities.Browser.isFirefox()) {
                event_type = "textInput";
            }

            $date_of_first_registration.on(event_type, function(e) {
                _this.restrictNumeric(e);
                _this.formatDateField(e);
                _this.formatForwardSlashAndSpace(e);
            });

            $('#id_car_model').on('change', function() {
                _this.checkIfCanQuote();
            });

            $('#id_vehicle_insured_value').on('focusout', function() {
                _this.checkIfCanQuote();
            });

            $('#modal_cant_insure_your_car a.trim').on('click', function() {
                $('#modal_cant_insure_your_car').hide();
                $('#id_car_model').val('').trigger('chosen:updated');
                setTimeout(function(){
                    $('body').css('overflow','auto');
                    $('#id_car_model').trigger('chosen:open');
                }, 500);
            });

            $('#id_age_year, #id_age_month, #id_age_day').change(function() {
                let year = $('#id_age_year').val();
                let month = $('#id_age_month').val();
                let day = $('#id_age_day').val();

                if(day && parseInt(day) < 10) {
                    day = `0${parseInt(day)}`;
                }

                if(year && month && day)
                    $('#id_age').val(day + '/' + month + '/' + year);
            });
        },

        checkIfCanQuote: function() {
            var vehicle_insured_value = Number($('#id_vehicle_insured_value').val().replace(/[^0-9\.]+/g,""));
            var vehicle_trim = $('#id_car_model').val();
        },

        restrictNumeric: function(e) {
            var input;
            var charCode = e.which;
            if(typeof e.originalEvent.data !== 'undefined') {
                charCode = e.originalEvent.data.charCodeAt(0);
            }

            if (e.metaKey || e.ctrlKey) {
                return true;
            }
            if (charCode === 32) {
                return false;
            }
            if (charCode === 0) {
                return true;
            }
            if (charCode < 33) {
                return true;
            }
            input = String.fromCharCode(charCode);
            return !!/[\d\s]/.test(input);
        },

        formatDateField: function(e) {
            var $target, digit, val;
            var charCode = e.which;
            if(typeof e.originalEvent.data !== 'undefined') {
                charCode = e.originalEvent.data.charCodeAt(0);
            }
            digit = String.fromCharCode(charCode);
            if (!/^\d+$/.test(digit)) {
                return;
            }
            $target = $(e.currentTarget);
            val = $target.val() + digit;
            if (/^\d$/.test(val) && (val !== "0" && val !== "1")) {
                e.preventDefault();
                return setTimeout(function() {
                    return $target.val("0" + val + " / ");
                });
            } else if (/^\d\d$/.test(val)) {
                e.preventDefault();
                return setTimeout(function() {
                    var m1, m2;
                    m1 = parseInt(val[0], 10);
                    m2 = parseInt(val[1], 10);
                    if (m2 > 2 && m1 !== 0) {
                        return $target.val("0" + m1 + " / " + m2);
                    } else {
                        return $target.val("" + val + " / ");
                    }
                });
            }
        },

        formatForwardSlashAndSpace: function(e) {
            var $target, val, which;
            var charCode = e.which;
            if(typeof e.originalEvent.data !== 'undefined') {
                charCode = e.originalEvent.data.charCodeAt(0);
            }
            which = String.fromCharCode(charCode);
            if (!(which === "/" || which === " ")) {
                return;
            }
            $target = $(e.currentTarget);
            val = $target.val();
            if (/^\d$/.test(val) && val !== "0") {
                return $target.val("0" + val + " / ");
            }
        },

        _showErrorPopup: function() {
            Utilities.Notify.error(MESSAGES.error_text, MESSAGES.error_title);
        },

        _initForm: function() {
            //Hash callbacks
            $(window).hashchange({
                hash: "#!/contact-details/",
                onSet: function() {
                },
                onRemove: function() {
                    if(window.location.hash == '') {
                        $(SELECTORS.form).steps('previous');
                    }
                },
            });

            //Steps
            var form = $(SELECTORS.form).show();

            $.validator.addMethod("regex", function(value, element, regexpr) {
                return regexpr.test(value);
            });

            lead_form_wizard = form.steps({
                headerTag: "h3",
                bodyTag: "fieldset",
                transitionEffect: "slideLeft",
                enableAllSteps: true,

                /* Templates */
                titleTemplate: '#title#',
                loadingTemplate: '<div class="preloader"><img src="static/images/loader-trans.gif">Please wait....</div>',

                labels: {
                    finish: 'Get Quotes'
                },

                transitionEffect: 'slideLeft',

                onStepChanging: function (event, currentIndex, newIndex)
                {
                    // Allways allow previous action even if the current form is not valid!
                    if (currentIndex > newIndex)
                    {
                        $('.step-2').hide();
                        $('.step-1').show();
                        $('.step-2 .animated-car').removeClass('animated-car-go');

                        return true;
                    }

                    // Needed in some cases if the user went back (clean up)
                    if (currentIndex < newIndex)
                    {
                        // To remove error styles
                        form.find(".body:eq(" + newIndex + ") label.error").remove();
                        form.find(".body:eq(" + newIndex + ") .error").removeClass("error");
                    }

                    var ignore_settings = ".ignore,:disabled,:hidden:not('.select-to-button-field')";

                    form.validate().settings.ignore = ignore_settings;
                    var is_valid = form.valid();

                    if(is_valid) {
                        $(SELECTORS.error_popup).fadeOut();

                        if(newIndex == 1) {
                            window.location.hash = '!/contact-details/';

                            $('.step-1').hide();
                            $('.step-2').show();

                            $('html, body').animate({
                                scrollTop: 0
                            }, 500, 'swing', function(){
                                $('#id_name').focus();
                            });

                            setTimeout(function(){
                                $('.step-2 .animated-car').addClass('animated-car-go');
                            }, 1000);
                        } else {
                            window.location.hash = '';
                        }
                    }

                    return is_valid;
                },
                onFinishing: function (event, currentIndex)
                {
                    $('em.error').remove();

                    var ignore_settings = ".ignore,:disabled";

                    form.validate().settings.ignore = ignore_settings;

                    return form.valid();
                },
                onFinished: function (event, currentIndex)
                {
                    $(SELECTORS.preloader).show();

                    if(typeof drift !== 'undefined') {
                        drift.identify($('#id_email').val(), {
                            email: $('#id_email').val(),
                            phoneNumber: $('#id_contact_number').val(),
                            name: $('#id_name').val()
                        });
                    }
                    var params = '';
                    var post_url = DjangoUrls['motorinsurance:lead-form']();

                    var url_params = Utilities.General.getUrlParamKeyValue();

                    if('utm_source' in url_params)
                        params += '&utm_source=' + url_params['utm_source'];
                    if('utm_medium' in url_params)
                        params += '&utm_medium=' + url_params['utm_medium'];
                    if('utm_campaign' in url_params)
                        params += '&utm_campaign=' + url_params['utm_campaign'];

                    if(params) {
                        post_url += '?' + params;
                    }

                    $('.actions li a[href="#finish"], .actions li a[href="#previous"]').hide();

                    $.post(post_url, _this._prepareData())
                        .done(function(response) {
                            var redirectUrl = thankYouUrl;

                            if (typeof response.lead_id !== 'undefined')
                                redirectUrl += '?lead_id=' + response.lead_id;

                            if(typeof amplitude !== "undefined") {
                                if('client_email_hash' in response && response.client_email_hash) {
                                    amplitude.getInstance().setUserId(response.client_email_hash);
                                    amplitude.getInstance().setUserProperties({
                                        email: response.client_email
                                    });
                                }

                                amplitude.getInstance().logEvent(
                                    'motor deal created', {
                                        'source': 'e-commerce',
                                        'company_id': current_company_info.ID,
                                        'company_name': current_company_info.NAME,

                                        'deal_id': response.deal_id,
                                        'email': response.client_email,

                                        'vehicle_model_year': response.vehicle_model_year,
                                        'vehicle make': response.vehicle_make,
                                        'vehicle_model': response.vehicle_model,
                                        'vehicle_body_type': response.vehicle_body_type,
                                        'vehicle_sum_insured': response.vehicle_sum_insured,

                                        'client_nationality': response.client_nationality,
                                        'client_gender': response.client_gender,
                                        'client_age': response.client_age
                                    });
                            }
                            setTimeout(function() {
                                window.location.href = redirectUrl;
                            }, 2000);
                        })
                        .fail(function(xhr, status, error) {
                            _this._showErrors(xhr.responseJSON);
                            $(SELECTORS.preloader).hide();
                            $('.actions li a[href="#finish"], .actions li a[href="#previous"]').show();
                        }).always(function() {
                        });
                }
            }).validate({
                rules: {
                    current_insurer: {
                        required: function() {
                            return $('#id_lead_type').val() == LEAD_TYPE_RENEW
                        }
                    },
                    current_insurance_type: {
                        required: function() {
                            return $('#id_lead_type').val() == LEAD_TYPE_RENEW
                        }
                    },
                    new_date_of_first_registration: {
                        required: function() {
                            return $('#id_lead_type').val() != LEAD_TYPE_NEW
                        },
                        regex: /^\d{1,2}\s?\/\s?\d{4}$/
                    }
                },
                messages: {
                    vehicle_insured_value: ' If you\'d like us to suggest a number then just enter 0',
                    terms: "You must agree with the terms.",
                    new_date_of_first_registration: {
                        required: "This field is required.",
                        regex: "Invalid Date. A correct format would be: 02/2012",
                    }
                },
                onfocusout: function(element) {
                    if ($.inArray($(element).attr('id'), requiredFieldsArray) >= 0) {
                        this.element(element);
                    }
                },
                errorElement: "em",
                errorPlacement: function ( error, element ) {
                    if ( element.prop( "type" ) === "checkbox" ) {
                        element.append(error);
                    } else {
                        error.insertAfter( element );
                    }
                },
                highlight: function ( element, errorClass, validClass ) {
                    $( element ).closest('label').addClass('heading-error');
                },
                unhighlight: function (element, errorClass, validClass) {
                    $( element ).closest('label').removeClass('heading-error');
                },
                focusInvalid: false,
                invalidHandler: function(form, validator) {
                    
                    if (!validator.errorList.length)
                        return;

                    if($(validator.errorList[0].element).closest('fieldset').hasClass('about-car-panel')) {
                        $('#motor_lead_form-t-0').click();
                    }
                    $('html, body').animate({
                        scrollTop: $(validator.errorList[0].element).parent().offset().top - 100
                    }, 300);

                    _this._showErrorPopup();
                }
            });

            // Should trigger after steps init. So all the libraries will be loaded (select2 etc) within steps
            _this._initGeneralTriggers();
        },

        _prepareData: function() {
            var data = $(SELECTORS.form).serialize();

            if($('#id_lead_type').val() != LEAD_TYPE_NEW) {
                var dofr_month = $.trim($('#new_date_of_first_registration').val().split('/')[0]);
                var dofr_year = $.trim($('#new_date_of_first_registration').val().split('/')[1]);
                data += '&date_of_first_registration=' + dofr_year + '-' + dofr_month;
            }
            if($('#first_license_issue_date_year').val() && $('#first_license_issue_date_month').val()){
                data += '&first_license_issue_date=' + $('#first_license_issue_date_year').val() + '-' + $('#first_license_issue_date_month').val();
            }
            if($('#uae_license_issue_date_year').val() && $('#uae_license_issue_date_month').val()) {
                data += '&uae_license_issue_date=' + $('#uae_license_issue_date_year').val() + '-' + $('#uae_license_issue_date_month').val();
            }

            if($('#id_vehicle_insured_value').val()) {
                data += '&vehicle_insured_value=' + Number($('#id_vehicle_insured_value').val().replace(/[^0-9\.]+/g,""))
            }

            return data;
        },

        _initGeneralTriggers: function() {
            $('select').not('.numeric-field').chosen({
                width: '100%'
            });
            $('select.numeric-field').chosen({
                width: '100%',
                is_numeric: true
            });

            // On focus, open a chosen dropdown
            $('body').on('focus', '.chosen-container-single input', function () {
                if (!$(this).closest('.chosen-container').hasClass('chosen-container-active')) {
                    $(this).closest('.chosen-container').prev().trigger('chosen:open');
                }
            });

            $('#id_nationality').on('change', function(){
                if($(SELECTORS.first_license).val() == ''){
                    $(SELECTORS.first_license).val($('#id_nationality').val()).trigger('chosen:updated');
                }
                $(SELECTORS.first_license).trigger('change');
            });

            //Hide tooltip divs if clicked outside it
            $(document).click(function (e)
            {
                if($('.help-trigger-layout').is(":visible")) {
                    var container = $(SELECTORS.tooltip + ', ' + SELECTORS.helpButton);

                    if (!container.is(e.target) // if the target of the click isn't the container...
                        && container.has(e.target).length === 0) // ... nor a descendant of the container
                    {
                        if(Utilities.Check.isMobile() 
                            && (
                                $(e.target).parents('.felix-lightbox').length || $(e.target).hasClass('felix-lightbox')
                            )
                        )
                            return;

                        $(SELECTORS.tooltip).hide();
                    }
                }
            });

            $(SELECTORS.first_license).on('change', function(e){
                if($(this).val() == "AE") {
                    $('#div_id_first_license_age').slideUp(200);
                    $('#id_first_license_age').attr('disabled', true);
                } else {
                    $('#div_id_first_license_age').slideDown(100);
                    $('#id_first_license_age').attr('disabled', false);
                }
            });

            $('#div_id_lead_type .field-select-buttons button').on('click', function(e){

                if($(this).data('value') == LEAD_TYPE_RENEW) {
                    $('#div_id_current_insurer, #div_id_current_insurance_type, #div_id_date_of_first_registration').slideDown(100);
                    $('#new_date_of_first_registration').removeClass('ignore');
                }

                if($(this).data('value') == LEAD_TYPE_USED) {
                    $('#div_id_date_of_first_registration').slideDown(100);
                    $('#div_id_current_insurer, #div_id_current_insurance_type, #div_id_date_of_first_registration').slideUp(100);
                    $('#new_date_of_first_registration').removeClass('ignore');
                }

                if($(this).data('value') == LEAD_TYPE_NEW) {
                    $('#div_id_current_insurer, #div_id_current_insurance_type, #div_id_date_of_first_registration').slideUp(100);
                    $('#new_date_of_first_registration').addClass('ignore');
                }

                if(Utilities.Check.elemIsOnViewPort('#div_id_lead_type')) {
                    $('html, body').animate({
                        scrollTop: $('.label-content:nth(1)').offset().top - 50
                    }, 1000);
                }
            });

            $('#div_id_years_without_claim .field-select-buttons button').on('click', function(e){
                var selected_val = $(this).data('value');
                var dynamic_text = '';

                if(selected_val == NCC_CANT_REMEMBER || selected_val ==  NCC_12_MONTHS || selected_val ==  NCC_NEVER) {
                    $('#div_id_claim_certificate_available').slideUp(200);
                } else {
                    $('#div_id_claim_certificate_available').slideDown(100);
                    if(selected_val == 'last year') {
                        dynamic_text = 'Can you prove that you have 1 year no claim?';    
                    } else if(selected_val == '2 years ago') {
                        dynamic_text = 'Can you prove that you have 2 years no claim?';    
                    } else if(selected_val == '3 years ago') {
                        dynamic_text = 'Can you prove that you have 3 years no claim?';    
                    } else if(selected_val == '4 years ago') {
                        dynamic_text = 'Can you prove that you have 4 years no claim?';    
                    } else if(selected_val == '5 years or more') {
                        dynamic_text = 'Can you prove that you have 5 years or more no claim?';    
                    }

                    $('#div_id_claim_certificate_available').find('span').text(dynamic_text);
                }
            });
        },

        _initOldCarOnlyTriggers: function() {
            $(SELECTORS.newCar).change(function() {
                if($(this).is(':checked')) {
                    $(SELECTORS.oldCars).hide();
                } else {
                    $(SELECTORS.oldCars).show();
                }
            });
        },

        _initModelMakeActions: function() {
            $(SELECTORS.carYear).bind('change',function(){
                //reset make and model
                var selected_year = $(this).val();

                if(selected_year == _this.cachedYear) return;

                _this._updateSelectOptions(SELECTORS.carMake, [], 'make');
                _this._updateSelectOptions(SELECTORS.carModel, [], 'model');
                
                $.get(modelEndpointUrl + '?year=' + selected_year, function(response) {
                    _this.cachedYear = selected_year;
                    if(response && 'makes' in response) {
                        _this._updateSelectOptions(SELECTORS.carMake, response.makes, 'make');
                    }
                });

                if($('#id_lead_type').val() == LEAD_TYPE_USED)
                    $('#new_date_of_first_registration').val('01 / ' + selected_year);

            });

            $(SELECTORS.carMake).bind('change',function(){
                //reset make and model
                var selected_year = $(SELECTORS.carYear).val();
                var selected_make = $(this).val();

                _this._updateSelectOptions(SELECTORS.carModel, [], 'model');

                $.get(modelEndpointUrl + '?year=' + selected_year + '&make=' + selected_make, function(response) {
                    if(response && 'models' in response) {
                        _this._updateSelectOptions(SELECTORS.carModel, response.models, 'model');

                        $(SELECTORS.carModel).attr(
                            'data-placeholder',
                            response.models.length?'Model':'Please enter car model below'
                        );
                        $('#id_cant_find_car').prop('checked', response.models.length==0).change();
                    }
                });
            });
        },

        _updateSelectOptions: function(id, options, text, selected_id) {
            if(selected_id == undefined)
                selected_id = false;

            if(typeof options == 'string')
                options = $.parseJSON(options);

            $(id).find('option').remove();
            $(id).append(new Option('', '', true));
            $.each(options, function(k, v){
                var selected = selected_id == v[0];
               $(id).append(new Option(v[1], v[0], false, selected));
            });
            $(id).trigger('chosen:updated');
        },

        _initTooltipActions: function() {
            $(SELECTORS.helpButton).bind('click',function(){
                $(SELECTORS.tooltip).hide();
                $(this).parent().find(SELECTORS.tooltip).show();
            });
            $(SELECTORS.tooltipClose).bind('click',function() {
                $(this).closest(SELECTORS.tooltip).hide();
            });
        },

        _daysInMonth: function(month, year) {
            if(year === undefined || year === '')
                year = new Date().getFullYear();

            return new Date(year, month, 0).getDate();
        },

        _showErrors: function(json) {
            var errors = '';

            if('errors' in json) {
                errors = json.errors;
            }

            if(errors) {
                _this._showErrorPopup();

                $.each(errors, function(k, v){
                    var $elem = $('#id_' + k);
                    $elem.after(
                        '<em id="id_'+k+'-error" class="error">'+v+'</em>'
                    );
                    $elem.closest('label').addClass('heading-error');
                });

                // First step has error(s)
                if($('.about-car-panel em.error').length) {
                    $('#motor_lead_form-t-0').click();
                    $('html, body').animate({
                        scrollTop: $('.about-car-panel em.error:first').offset().top - 200
                    }, 500);
                }

                // Second step has error(s)
                else if($('.about-owner-panel em.error').length) {
                    $('#motor_lead_form-t-1').click();
                    $('html, body').animate({
                        scrollTop: $('.about-owner-panel em.error:first').offset().top - 200
                    }, 500);
                }
            }

            if('custom_msg' in json) {
                $(SELECTORS.pagination).after(
                    validationTemplate.replace(
                        '{msg}',
                        json.custom_msg
                    )
                );
            }
        },

    };

    $(function() {
        __MotorLeadForm__.init();
    });
})();

if (typeof module === "object" && typeof module.exports === "object") {
    module.exports = __MotorLeadForm__;
}
