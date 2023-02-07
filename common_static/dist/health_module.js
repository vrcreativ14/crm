'Use Strict';

const DOCUMENT_SUB_STAGES = {
    1: 'documents received',
    2:'documents send to insurer',
    3:'world check' 
}

const FINAL_QUOTE_SUB_STAGES = {
    1:'final quote send to client',
    2:'final quote signed',
    3:'final quote send to insurer',
}
const PAYMENT_SUB_STAGES = {
    1:'payment sent to client',
    2:'payment confirmation',
    3:'payment send to insurer',
}

const POLICY_ISSUANCE = {
    1 : "policy_issuance"
}

const HOUSE_KEEPING = {
    1 : "housekeeping"
}

const CLOSED = {
    1 : "closed"
}

const SUB_STAGES = {
    3 : DOCUMENT_SUB_STAGES,
    4 : FINAL_QUOTE_SUB_STAGES,
    5 : PAYMENT_SUB_STAGES,
    6 : POLICY_ISSUANCE,
    7 : HOUSE_KEEPING,
    8 : CLOSED,
}

const STAGES = {
    1 : "new",
    2 : "quote",
    3 : "documents",
    4 : "final_quote",
    5 : "payment",
    6 : "policy",
    7 : "housekeeping",
}


function updateQuoteForm(e, action, id=""){
    debugger
    let plan_id = e.value
    data = {}
    if(!plan_id){
        if(id)
        plan_id = id
    }
    let url = DjangoUrls['health-insurance:plan-details'](plan_id)
    window.products_data[e.value];
    if(action)
        data = {'action':'edit'}
    
$.ajax({
        url: url ,
            method: 'GET',
            data: data,
            success: function( result ) {
                debugger
                console.log(result)
                window.products_data = result
                let saved_am = ''
                let saved_annual_limit = ''
                let saved_dental_benefits = ''
                let saved_copayment = ''
                let saved_deductible = ''
                let saved_optical_benefits = ''
                let insurer_quote_reference = ''
                let is_renewal = ''
                let saved_maternity_benefits = ''
                let saved_maternity_waiting_period = ''
                let saved_network = ''
                let saved_payment_frequency = ''
                let saved_physiotherapy = ''
                let saved_total_premium = ''
                let saved_wellness_benefits = ''
                if(result['quoted_plan']){
                    saved_am = result['quoted_plan']['alternative_medicine']
                    saved_annual_limit = result['quoted_plan']['annual_limit']
                    saved_dental_benefits = result['quoted_plan']['dental_benefits']
                    saved_copayment = result['quoted_plan']['copayment']
                    saved_deductible = result['quoted_plan']['deductible']
                    saved_optical_benefits = result['quoted_plan']['optical_benefits']
                    insurer_quote_reference = result['quoted_plan']['insurer_quote_reference']
                    is_renewal = result['quoted_plan']['is_renewal']
                    saved_maternity_benefits = result['quoted_plan']['maternity_benefits']
                    saved_maternity_waiting_period = result['quoted_plan']['maternity_waiting_period']
                    saved_network = result['quoted_plan']['network']
                    saved_payment_frequency = result['quoted_plan']['payment_frequency']
                    saved_physiotherapy = result['quoted_plan']['physiotherapy']
                    saved_total_premium = result['quoted_plan']['total_premium']
                    saved_wellness_benefits = result['quoted_plan']['wellness_benefits']
                }
                
                let networks = result['data']['network']
                $(".network select option").remove();
                    $(".network").toggleClass("hide", false);
                    for (let i in networks) {
                    //const element = array[index];
                    $(".network select").append($("<option></option>")
                    .attr("value", networks[i]['id']).text(networks[i]['network']));
                    

                    if(result['data']['is_network_fixed'])
                        $(".network select").val(networks[i]['id'])
                }
                if( ! result['data']['is_network_fixed']){
                    $(".network").toggleClass("hide", false);
                }
                else{
                    $(".network").toggleClass("hide", true)
                }
                if (saved_network)
                        $(".network select").val(saved_network)

                
                let deductibles = result['data']['deductible']
                    $(".deductible select option").remove();
                    for (let i in deductibles) {
                    //const element = array[index];
                    $(".deductible select").append($("<option></option>")
                    .attr("value", deductibles[i]['id']).text(deductibles[i]['deductible']));                    

                    if(result['data']['is_deductible_fixed'])
                        $(".deductible select").val(deductibles[i]['id'])
                }

                if( ! result['data']['is_deductible_fixed']){
                    $(".deductible").toggleClass("hide", false);                            
                }
                else{
                    $(".deductible").toggleClass("hide", true)                          
                }
                if (saved_deductible)
                        $(".deductible select").val(saved_deductible)

             

                $(".payment_frequency select option").remove();
                let frequencies = result['data']['payment_frequency']
                for (let i in frequencies) {
                        $(".payment_frequency select").append($("<option></option>")
                    .attr("value", frequencies[i]['id']).text(frequencies[i]['frequency']));
                    
                    if(result['data']['is_payment_frequency_fixed'])
                        $(".payment_frequency select").val(frequencies[i]['id'])
                }
                if( !result['data']['is_payment_frequency_fixed']){
                    
                    $(".payment_frequency").toggleClass("hide", false);
                }
                else{
                    $(".payment_frequency").toggleClass("hide", true)
                    
                }

                if (saved_payment_frequency)
                        $(".payment_frequency select").val(saved_payment_frequency)

                $(".copayment select option").remove();
                let copayments = result['data']['copayment']
                    for (let i in copayments) {
                        $(".copayment select").append($("<option></option>")
                    .attr("value", copayments[i]['id']).text(copayments[i]['copayment']));
                    if(result['data']['is_copayment_fixed'])
                        $(".copayment select").val(copayments[i]['id'])
                }
                if( ! result['data']['is_copayment_fixed']){
                    $(".copayment").toggleClass("hide", false);                                                        
                }
                else{
                    $(".copayment").toggleClass("hide", true);                            
                }
                if (saved_copayment)
                        $(".copayment select").val(saved_copayment)
              
                $(".annual_limit select option").remove();
                let limits = result['data']['annual_limit']
                    for (let i in limits) {
                        $(".annual_limit select").append($("<option></option>")
                    .attr("value", limits[i]['id']).text(limits[i]['limit']));
                    if(result['data']['is_annual_limit_fixed'])
                        $(".annual_limit select").val(limits[i]['id'])
                }

                if( ! result['data']['is_annual_limit_fixed']){                            
                    $(".annual_limit").toggleClass("hide", false);                            
                }
                else{
                    $(".annual_limit").toggleClass("hide", true)                            
                }
                if (saved_annual_limit)
                        $(".annual_limit select").val(saved_annual_limit)


                $(".physiotherapy select option").remove();
                limits = result['data']['physiotherapy']
                    for (let i in limits) {
                        $(".physiotherapy select").append($("<option></option>")
                    .attr("value", limits[i]['id']).text(limits[i]['sessions']));
                    if(result['data']['is_physiotherapy_session_fixed'])
                        $(".physiotherapy select").val(limits[i]['id'])
                }
                if( ! result['data']['is_physiotherapy_session_fixed']){                            
                    $(".physiotherapy").toggleClass("hide", false);                            
                }
                else{
                    $(".physiotherapy").toggleClass("hide", true)                            
                }
                if (saved_physiotherapy)
                        $(".physiotherapy select").val(saved_physiotherapy)

                $(".alternative_medicine select option").remove();
                limits = result['data']['alternative_medicine']
                    for (let i in limits) {
                        $(".alternative_medicine select").append($("<option></option>")
                    .attr("value", limits[i]['id']).text(limits[i]['medicine']));
                    if(result['data']['is_alternative_medicine_fixed'])
                        $(".alternative_medicine select").val(limits[i]['id'])
                }

                if( ! result['data']['is_alternative_medicine_fixed']){                            
                    $(".alternative_medicine").toggleClass("hide", false);
                }
                else{
                    $(".alternative_medicine").toggleClass("hide", true)                            
                }
                if (saved_am)
                        $(".alternative_medicine select").val(saved_am)

                $(".maternity_waiting_period select option").remove();
                limits = result['data']['maternity_waiting_period']
                    for (let i in limits) {
                        $(".maternity_waiting_period select").append($("<option></option>")
                    .attr("value", limits[i]['id']).text(limits[i]['period']));
                    if(result['data']['is_maternity_waiting_period_fixed'])
                    $(".maternity_waiting_period select").val(limits[i]['id'])
                }
                if( ! result['data']['is_maternity_waiting_period_fixed']){                            
                    $(".maternity_waiting_period").toggleClass("hide", false);                            
                }
                else{
                    $(".maternity_waiting_period").toggleClass("hide", true)                            
                }
                if (saved_maternity_waiting_period)
                        $(".maternity_waiting_period select").val(saved_maternity_waiting_period)

                $(".optical_benefits select option").remove();
                limits = result['data']['optical_benefits']
                    for (let i in limits) {
                        $(".optical_benefits select").append($("<option></option>")
                    .attr("value", limits[i]['id']).text(limits[i]['benefit']));
                    if(result['data']['is_optical_benefits_fixed'])
                    $(".optical_benefits select").val(limits[i]['id'])
                }

                if( ! result['data']['is_optical_benefits_fixed']){
                    $(".optical_benefits").toggleClass("hide", false);                            
                }
                else{
                    $(".optical_benefits").toggleClass("hide", true)                            
                }
                if (saved_optical_benefits)
                    $(".optical_benefits select").val(saved_optical_benefits)

                $(".dental_benefits select option").remove();
                limits = result['data']['dental_benefits']
                    for (let i in limits) {
                        $(".dental_benefits select").append($("<option></option>")
                    .attr("value", limits[i]['id']).text(limits[i]['benefit']));
                    if(result['data']['is_dental_benefit_fixed'])
                    $(".dental_benefits select").val(limits[i]['id'])
                }
                if( ! result['data']['is_dental_benefit_fixed']){
                    $(".dental_benefits").toggleClass("hide", false);
                }
                else{
                    $(".dental_benefits").toggleClass("hide", true)
                }
                if (saved_dental_benefits)
                    $(".dental_benefits select").val(saved_dental_benefits)


                $(".wellness_benefits select option").remove();
                limits = result['data']['wellness_benefits']
                    for (let i in limits) {
                        $(".wellness_benefits select").append($("<option></option>")
                    .attr("value", limits[i]['id']).text(limits[i]['benefit']));
                    if(result['data']['is_wellness_benefit_fixed'])
                    $(".wellness_benefits select").val(limits[i]['id'])
                }
                if( ! result['data']['is_wellness_benefit_fixed']){
                    $(".wellness_benefits").toggleClass("hide", false);                            
                }
                else{
                    $(".wellness_benefits").toggleClass("hide", true)                            
                }
                if (saved_wellness_benefits)
                    $(".wellness_benefits select").val(saved_wellness_benefits)
                if(insurer_quote_reference)
                    $('#id_insurer_quote_reference').val(insurer_quote_reference)
                if(saved_total_premium)
                    $('#id_total_premium').val(saved_total_premium)
                //Utilities.Notify.success('Note deleted', 'Success');
            },
            error: function(data){
                //Utilities.Notify.error('Note not deleted', 'Error');
            }
    })
}


function validatePrepare(elem){
    let formData = new FormData()
    elem.form.querySelectorAll('.error').forEach(elem => {elem.remove()})
    elem.form.parentElement.querySelectorAll('.error').forEach(elem => {elem.remove()})
    let errorCount = 0
    current_stage = document.getElementById('deal_stage_id').value
    current_sub_stage = document.getElementById('current_sub_stage').value
    data = {'current_stage': current_stage, 'current_sub_stage':current_sub_stage}
    formData.append('stage_data',JSON.stringify(data))
    if(elem.className.includes('payment')){
        let payment_url = ''
        if(!document.querySelector('#payment_link_checkbox').checked && !document.querySelector('#bank_transfer_checkbox').checked){            
        $(elem.form).after('<span class="error">Provide either payment url or Bank transfer details</span>')
        return false
        }
        else if(document.querySelector('#payment_link_checkbox').checked){
            payment_url = document.querySelector('#payment_url')
            if(!payment_url.value) {
                $(payment_url).after('<span class="error">This field is required</span>')
                return false
            }
            else
            formData.append('payment_url', payment_url.value)
        }
        else{
            bank_name = document.querySelector('#bank_name')
            if(!bank_name.value){
                $(bank_name).after('<span class="error">This field is required</span>')
                return false
            }
            else
            formData.append('bank_name',bank_name.value)
            iban = document.querySelector('#iban')
            if(!iban.value) {
                $(iban).after('<span class="error">This field is required</span>')
                return false
            }
            else
            formData.append('iban', iban.value)
        }
        return formData
    }
    
    elem.closest('form').querySelectorAll('input').forEach(i => {
        debugger
        let type = i.type
        if(i.classList.contains('required')){
            $(i.parentElement).find('.error').remove();
            switch(type){
                case 'checkbox':
                    if (i.checked){
                        formData.append(i.name, i.checked)
                    }
                    else{
                        if(elem.id == 'policy-issuance')
                        i.parentElement.querySelector('label').after('<span class="error">This field is required</span>')
                        else
                        $(i.parentElement).after('<span class="error">This field is required</span>')
                        errorCount++
                    }
                    break;
                case 'radio':
                    if (document.querySelector(`input[name=${i.name}]:checked`)){                
                        formData.append(i.name, document.querySelector(`input[name=${i.name}]:checked`).value)
                    }
                    else{
                        $(i.parentElement).after('<span class="error">This field is required</span>')
                        errorCount++
                    }
                    break;
                case 'file':
                    if(i.files.length == 0){
                        $(i.parentElement).after('<span class="error">This field is required</span>')
                        errorCount++
                    }
                    formData.append(i.name, i.files[0])
                    break;
                default:
                    if (i.value){
                        formData.append(i.name, i.value)
                    }
                    else{
                        if(elem.id == 'policy-issuance')
                            $(i.parentElement.querySelector('label')).after('<span class="error">This field is required</span>')
                        else
                            $(i.parentElement).after('<span class="error">This field is required</span>')
                            errorCount++
                    }
            }
        }
        else{
            let type = i.type
            switch(type){
                case 'file':
                    formData.append(i.name, i.files[0])
                    break;
                case 'radio':
                    if (document.querySelector(`input[name=${i.name}]:checked`)){                
                        formData.append(i.name, document.querySelector(`input[name=${i.name}]:checked`).value)
                    }
                    break;
                case 'checkbox':
                    if (i.checked){
                        formData.append(i.name, i.checked)
                    }
                    break;
                default:
                    formData.append(i.name, i.value)
            }
        }
    })
    if(errorCount > 0) return false
    else return formData
}


function saveForm(formData, email_type){
    let url = `/health-insurance/deals/${_deal_id}/substage`
    $.ajax({
        method: 'POST',
        url: url,
        data: formData,
        async: false,
        success: function(response){
            debugger
            if(response['saved']){
                next_substage = response['next_sub_stage']
                deal_status = response['status']
                let next = SUB_STAGES[current_stage][next_substage]
                if(current_sub_stage >= 1)
                    $('.waiting_label').addClass('hide')
                $(`li.substage_${current_sub_stage}`).toggleClass('current selected', false)
                $(`li.substage_${current_sub_stage}`).toggleClass('completed', true)
                $(`li.substage_${next_substage}`).toggleClass('current selected', true)
                $(`div.substage_${current_sub_stage}`).toggleClass('show active', false)
                $(`div.substage_${next_substage}`).toggleClass('show active', true)
                document.querySelector('#deal_status_text').innerHTML = deal_status
                document.getElementById('current_sub_stage').value = next_substage                
                $('#deal_status').attr('data-value',`${deal_status}`)
                let current_status = document.querySelector('#deal_status_text').innerHTML
                current_status = current_status.toLowerCase().trim().replaceAll(' ','-')
                deal_status = deal_status.toLowerCase().trim().replaceAll(' ','-')
                Utilities.Notify.success('Sub Stage Updated', 'Success');
                $('#deal_status_text').parent().toggleClass(`${current_status} ${deal_status}`)
                location.reload()
            }
        },
        error: function(error){
            debugger
        },
        processData: false,
        contentType: false,
        })
}

function fetchEmailDetails(type){
    debugger
    $('[data-felix-modal="modal_send_custom_email_health"]').click();
    let url = `/health-insurance/deals/${_deal_id}/email/${type}/`
        $.ajax({
            method: 'GET',
            url: url,
            data: '',
            success: function(response){
                debugger
            console.log(response)
            updateEmailForm(response)
            },
            error: function(error){
                debugger
            },
            'processData': false,
            'contentType': false,
            })
}

function downloadAllPolicyFiles(type, id){
    debugger
    let url = DjangoUrls['health-insurance:download-zipfile'](id,type)    
    url = url.replace('11', id)    
    url = url.replace('22', type)    
    window.location.href = url            
}

document.onclick = function(event) {
    let td = event.target.closest('td');
    let element = event.target.className;
    if (element.includes('add-another-product')){
        $('#modal_quote_insurers').modal('toggle');
    }
    if(element.includes('btn-cancel-generate-new-quote')){
        if(_quoted_products_data['products'].length > 0){
            $('.health-deal-add-product').addClass('hide')
            $('.products-preview').removeClass('hide')
            $('.renewal_details').addClass('hide')
            $('.renewal_details input[type="checkbox"]').prop('checked', false)
            $('.renewal_document').toggleClass('hide', true)
            $('.renewal_details .renewal_document input[type="file"]').val('')
        }
        else{
            // $('.health-deal-add-product').addClass('hide')
            // $('.deal-form').toggleClass('hide')
            // $('.show-insurer-modal').toggleClass('hide')
            location.reload()
        }
        
    }
    if (element.includes('next-substage')){
        debugger
        let formData = new FormData()
        event.preventDefault()
        formData = validatePrepare(event.target)
        if(!formData) return
        
        let url = `/health-insurance/deals/${_deal_id}/substage`
        saveForm(formData)
    }
    else if(element.includes('fetch-email')){
        debugger
        event.preventDefault()
        let formData = new FormData()
       
        formData = validatePrepare(event.target)
        if(!formData) return
        saveForm(formData, true)
       
        $('[data-felix-modal="modal_send_custom_email_health"]').click();
        request_data = {'current_stage':current_stage, 'current_sub_stage':current_sub_stage}
        __HEALTH_DEALS._triggerCustomEmailModal('latest');

        return
    }
    
    else if(element.includes('policy')){       
        if(element.includes('send-policy'))
            event.target.form.action = `/health-insurance/deals/${_deal_id}/policy/?send-email=True`
        else
            event.target.form.action = `/health-insurance/deals/${_deal_id}/policy/`
    }

    else if(element.includes('resend-quote')){
        event.preventDefault()
        document.getElementById('current_sub_stage').value = 1
        current_sub_stage = 1
        prev_substage = 2
        
        $(`li.substage_${current_sub_stage}`).toggleClass('completed', false)
        $(`li.substage_${current_sub_stage}`).toggleClass('current selected', true)
        $(`li.substage_${prev_substage}`).toggleClass('current selected', false)
        $(`div.substage_${current_sub_stage}`).toggleClass('show active', true)
        $(`div.substage_${prev_substage}`).toggleClass('show active', false)
        
        //$(`div.substage_${next_substage}`).toggleClass('show active', true)
    }
    else if(event.target.parentElement.className.includes('health-policy-row')){
        $('#modal_view_policy').find('.content').html('<p class="m-t-50 m-b-50">Loading...</p>');
            let key = event.target.parentElement.id
            if(key)
                key = key.split('_')[1]
            let url = `/health-insurance/policies/${key}/json/`            
                $.get(url, function(response) {
                    var source   = $('#health-policy-modal-template').html();
                    var template = Handlebars.compile(source);
                    $('#modal_view_policy').find('.content').html(template(response));
                    $('.modal').modal('hide');
                    $('body').removeClass('modal-open');
                    $('.modal-backdrop').remove();
                });
    }
  };

document.oninput = function(event){
    let element = event.target.className;
    if(element.includes('member_premium')){
        debugger           
        let total_premium = 0
        document.querySelectorAll('.member_premium').forEach(elem => {
            let temp = !elem.value  ? 0 : parseFloat(elem.value)
            total_premium += temp
        })
        total_premium = total_premium + (0.05 * total_premium)
        document.querySelector('#id_total_premium').value = total_premium 
    }
}


  function updateEmailForm(response){
    var form = $('#custom_email_form');
    $('#custom_email_form').css({'opacity': '1'});
    form.find('#email_type').val(email_type);
            form.find('#id_email').val(response.to);
            form.find('#id_from_email').html(response.from);
            form.find('#id_reply_to').html(response.reply_to);
            form.find('#id_cc_emails').val(response.cc_emails);
            form.find('#id_bcc_emails').val(response.bcc_emails);
            form.find('#id_subject').val(response.subject);
            form.find('#id_content').trumbowyg($.trumbowyg.config);
            form.find('#id_content').trumbowyg('html', response.content);
            form.find('#custom_email_type option').remove();
}

function validateEmailForm(){
    var form = $('#custom_email_form');
            var email_type = form.find('#email_type').val();

            // Validations
            form.find('.error').remove();
            if(form.find('#id_email').val() == '') {
                form.find('#id_email').after('<span class="error">This field is required</span>');
                return false;
            }
            if(form.find('#id_subject').val() == '') {
                form.find('#id_subject').after('<span class="error">This field is required</span>');
                return false;
            }

            form.find('button.send-email').addClass('loader');
            return true
}


function processEmailResponse(response){
    if(response.success) {
                        Utilities.Notify.success('Email sent successfully.', 'Success');
                        $('#modal_send_custom_email_health').hide();

        }
}

function saveForm(formData, email_type){
    let url = `/health-insurance/deals/${_deal_id}/substage`
    $.ajax({
        method: 'POST',
        url: url,
        data: formData,
        async: false,
        success: function(response){
            debugger
            if(response['saved']){
                let reload = response['reload']
                if (reload) location.reload()
                next_substage = response['next_sub_stage']
                deal_status = response['status']
                let current_status = document.querySelector('#deal_status_text').innerHTML
                let next = SUB_STAGES[current_stage][next_substage]
                $(`li.substage_${current_sub_stage}`).toggleClass('current selected', false)
                $(`li.substage_${current_sub_stage}`).toggleClass('completed', true)
                $(`li.substage_${next_substage}`).toggleClass('current selected', true)
                $(`div.substage_${current_sub_stage}`).toggleClass('show active', false)
                $(`div.substage_${next_substage}`).toggleClass('show active', true)
                document.getElementById('current_sub_stage').value = next_substage
                document.querySelector('#deal_status_text').innerHTML = deal_status
                current_status = current_status.toLowerCase().trim().replaceAll(' ','-')
                deal_status = deal_status.toLowerCase().trim().replaceAll(' ','-')
                $('#deal_status_text').parent().toggleClass(`badge-${current_status} badge-${deal_status}`)
                $('.editable-input .chosen-single').html(deal_status)
                if(current_stage == 4 && current_sub_stage == 1){
                let final_premium = response.total_premium
                if (final_premium)
                    $('#final_premium_label').html(final_premium)
                let final_quote_file = response.final_quote_file
                let final_quote_filename = response.final_quote_filename
                if (final_quote_file)
                    $('#fileslist_final_quote').find('td').first().html(`<td><a class="mr-2" target="_blank" href="${final_quote_file}"><i class="fa fa-download" aria-hidden="true"></i></a>${final_quote_filename}</td>`)
                }
                Utilities.Notify.success('Sub Stage Updated', 'Success');
                $(`waiting_label_${current_stage}`).addClass('hide')
                
                if(email_type && current_stage == '6') {
                    //var email_type = updated?'quote_updated':'quote';                            
                    document.querySelector('#deal_stage_id').value = parseInt(current_stage) + 1
                    GetDealStage();
                    UpdateDealStage();
                    return
                }
            }
            else{
                let reload = response['reload']
                if (reload) {
                    location.reload()                    
                    return
                }
                if(response.errors){
                let errors = ''
                for(let i in response.errors){
                    errors += response.errors[i] + '\n'
                }
                Utilities.Notify.error(errors, 'Error');
            }
            else if(response.message)
                Utilities.Notify.info(response.message, 'Stage not updated');
            
            }
            //$(this).find('button[type=submit]').removeClass('loader');
        
        },
        error: function(error){
            debugger
        },
        'processData': false,
        'contentType': false,
        })
}



var _quoted_products_data;
var __HEALTH_DEALS;
;(function() {

    var _this   = '';
    var _table  = $('#deals-table');
    var _form   = $('#deal_form');
    var _general_search_field = $('#general_search_field');
    var _general_search_results_container = $('.app-search .search-results-container');
    var _filter_form   = $('#deals-search');
    var _clear_product_selection = $('.clear-product-selection');
    var _show_payments = $('.show-payments');
    var _deal_id = $('.deal-container').data('id');
    var _deal_status = $('.deal-container').data('status');
    var _deal_stages_breadcrumb = $('.deal-stages-breadcrumb');
    var _deal_stage_container = $('.health-deal-processes');
    var _deal_open_or_lost_btn = $('.open-lost-deal');
    var _add_product = $('.add-product');
    
    var _show_loader_class = 'show-loader';
    var _next_substage = $('.next-substage')
    var _selected_insurer = $('.insurer-container')
    var _felix_table_action_buttons = $('.felix-table-action-buttons');
    var _felix_table = $('table.felix-table');
    var _felix_table_filters = $('.table-filters');
    var _deal_open_or_lost_btn = $('.open-lost-deal');
    var _plan_dropdown = $("#id_product");
    //var _reactivate_quote = $(".reactivate-quote");
    _quoted_products_data = {'products': [], 'quote': {'status': true, 'email': false, 'delete': false}};

    var _policy_table_row = $('.health-policy-row')
    var _plan_form_data = new FormData()

    __HEALTH_DEALS =
    {
        init: function()
        {
            _this = this;
            //_this._loadMortgageProducts();
            //_this._dealStatusInline();
            _this._addNewDealForm();
           // _this._dealStagesToggle();
            _this._dealProcessTriggers();
            _this._openLostDealTriggers();
            _this._loadHistory();
            _this._addProduct();
            _this._editProduct();
            _this._removeProduct();
            _this.initAutocompleteField();
            _this.initExportTrigger();

            $('body').on('click','.insurer-block-container', function(e){
            $('.health-deal-add-product').toggleClass('hide', false)            
            $('.deal-form').removeClass('hide')
            $('.show-insurer-modal').addClass('hide')
            $('.products-preview').addClass('hide')
            $('.deal-form .form .edit-label').addClass('hide');             
            $('.deal-form .form .add-label').removeClass('hide');            
            $('.renewal_details').removeClass('hide')
            $('.renewal_details input[type="checkbox"]').prop('checked', false)
            $('.renewal_document').toggleClass('hide', true)
            $('.renewal_details .renewal_document input[type="file"]').val('')
            $('.health-deal-add-product select').attr('disabled', false)
            let insurer_id = this.dataset['id']
            $('#id_selected_insurer').val(insurer_id)
                    let add_product = $('.deal-form').html()
                    $('.health-deal-processes').html(add_product)
                    let url = DjangoUrls['health-insurance:health-plans'](insurer_id)
                    $.ajax({
                        method: 'GET',
                        url: url,
                        data: {'deal':_deal_id},
                        success: function(response){
                            debugger
                        $('#id_product').val('')
                        $('.products-container input').val('')
                        response['plans'].forEach(i => {
                            console.log(i['name'])
                            let opt = document.createElement('option');
                            opt.value = i['id'];
                            opt.innerHTML = i['name'];
                            document.querySelector('select#id_product').appendChild(opt);
                        })
                        },
                        error: function(error){
                            debugger
                        },
                    })
                
            })

            _deal_stage_container.on('click','.reactivate-quote',function(e){
                debugger
                let url = DjangoUrls['health-insurance:quote-reactivate'](_deal_id)
                $.ajax({
                    method: 'POST',
                    url: url,
                    async: false,
                    success: function(response){
                        debugger
                        if(response['success']){                            
                            Utilities.Notify.success(response['message'], 'Success');
                            $('.reactivate-quote').parent().remove()
                        }
                    },
                    error: function(error){
                        debugger
                    },
                    })
            });

            _deal_stage_container.on('change','.consultation_copay select' ,function(){
                debugger
                if($('#copay_mode_id').val() != 'variable'){
                    let consultation_copays = products_data['data']['consultation_copay']
                    for(let i in consultation_copays){
                        if(consultation_copays[i]['id'] == $(this).val()){
                            $(".pharmacy_copay select").val(consultation_copays[i]['pharmacy_copay'])
                            $(".diagnostics_copay select").val(consultation_copays[i]['diagnostics_copay'])
                        }
                    }
                }
            })


            _next_substage.on('click', function(e){
                debugger
                let formData = new FormData()
                e.preventDefault()
                formData = _this._validatePrepare(this)
                if(!formData) return
                let url = `/health-insurance/deals/${_deal_id}/substage`
            });

            _deal_stage_container.on('click', '.edit-health-quote', function() {
                debugger
                $('.quote-summary.quote-preview').addClass('hide');
                $('.quote-summary.quote-form').removeClass('hide');
                let url = DjangoUrls['health-insurance:deal-quoted-products-json'](_deal_id),
                data = {'stage':'edit-quote'}
                $('.deal-form').removeClass('hide')
                $('.products-preview').removeClass('hide')
                $('#saved_quote_div').addClass('hide')
                _this._getQuotedProducts()
            });

            _deal_stage_container.on('change', '.product-field', function() {
                
                    // _this._getAddons(
                    //     $(this).val(),
                    //     $(this).closest('.product-row').find('.product-addons')
                    // );
                debugger
                var product = window.products_data[$(this).val()];

                // $('.quote-form .form #id_agency_repair').prop('disabled', !product.allows_agency_repair);
                // $('.quote-form .form #id_agency_repair').closest('label').addRemoveClass(!product.allows_agency_repair, 'disabled');
            });

            _deal_stage_container.on('click', '.quote-submit', function() {
                //if($(this).hasClass(_show_loader_class)) return;
                debugger
                var current_product_length = $('.products-preview .products .row.product').length;
                $(this).attr('disabled',true)
                if(!current_product_length) {
                    if(window.confirm('Are you sure you want to delete this quote? \nYou cannot undo this.')){
                        _quoted_products_data['quote']['email'] = false;
                        _quoted_products_data['quote']['delete'] = true;
                        $(this).addClass(_show_loader_class);
                        _this._submitQuoteForm(false);

                        _deal_stages_breadcrumb.find('[data-item=quote-overview] .duration').remove();
                        _deal_stages_breadcrumb.find('[data-item=quote-overview] .quote-views').remove();
                    }
                } else {
                    _quoted_products_data['quote']['email'] = false;
                    $(this).addClass(_show_loader_class);
                    if(this.className.includes('send-email'))
                        _this._submitQuoteForm(true, false);
                    else
                        _this._submitQuoteForm(false);
                }
                
            });

            _deal_stage_container.on('click', '.void-deal', function(){
                debugger
                let url = DjangoUrls['health-insurance:deal-void'](_deal_id)
                $.post(url, function(response){
                    debugger
                    if(response.success)
                        location.reload()
                    else
                        Utilities.Notify.error(response.message, 'Error')
                })
            })
            

            $('body').on('click', '.email-edit', function(){
                debugger
                $('#modal_send_custom_email_history').show()
                let url = DjangoUrls['health-insurance:processed_emails'](this.dataset.emailpk)
                $.get(url, function( data ){
                    $('#custom_email_form_history').attr('action', url)
                    $('#custom_email_form_history input[id="id_email"').val(data.content.to_address)
                    $('#custom_email_form_history input[id="id_bcc_emails"').val(data.content.bcc_addresses.join())
                    $('#custom_email_form_history input[id="id_cc_emails"').val(data.content.bcc_addresses.join())
                    $('#custom_email_form_history input[id="id_subject"').val(data.content.subject)
                    let email_msg = data.content.html
                    email_msg = email_msg.replace(/<br\s*[\/]?>/gi, "\n");
                    email_msg = email_msg.replace(/<p[^>]*>/g, '');
                    email_msg = email_msg.replace(/<\/p>/g, '');
                    $('#custom_email_form_history textarea').html(email_msg)
                    $('#custom_email_form_history #id_from_email').text(data.content.from)
                    $('#custom_email_form_history #id_reply_to').text(data.content.reply_to)
                    $.each(data.content.stages, function(key, value) {
                    $('#custom_email_form_history select')
                            .append("<option value="+ key+">"+ value +"</option>")
                    });
                    $('#custom_email_form_history select').val(data.content.current_stage)
                    });
                });

            _felix_table_action_buttons.find('.close-health-deal').on('click', function() {
                var type = $(this).data('type');
                if(window.confirm('Are you sure you want to mark selected deal(s) as lost?')) {
                    debugger
                    var ids = getSelectedIds();

                    $.each(ids, function(id) {
                        var row = $('#tr_' + this.substring());
                        $.get(DjangoUrls['health-insurance:lose-deal'](this.substring()), function(response) {
                            if(response.success){
                                Utilities.Notify.success('Deal marked as lost', 'Success');
                                //row.remove();
                                location.reload();
                            }
                               
                        });
                    });

                    _felix_table.find('.select-record-all').prop('checked', false);
                }
            });
            function getSelectedIds() {
                return $('.select-record:checked').map(function() {
                    return this.value;
                }).get();
            }

            _show_payments.click(function() {
                _this._scrollAndOpenPaymentsTab();
            });

            $("#search-clear").on("click", function () {
                window.location.href = $("#deals-search").data("reset-url");
            });

            var filter_count = Utilities.Form.addFilterCount(_filter_form);
            if(filter_count) {
                $('.filter-count').html(filter_count).removeClass('hide');
            }

            $('body.mortgage-deals').on('click', '.duplicate-deal', function() {
                _this._duplicateDeal();
            });

            if(_clear_product_selection.length) {
                _clear_product_selection.click(function() {
                    var url = $(this).data('url');
                    if(window.confirm('Are you sure you want to clear the selected product?')) {
                        $.get(url, function(response) {
                            if(response.success) {
                                Utilities.Notify.success('Product selection removed successfully', 'Success');
                                window.location.href = window.location.href;
                            } else {
                                Utilities.Notify.error(response.message, 'Error');
                            }
                        });
                    }
                });
            }

            // Load deal stage on load
            if(_deal_stage_container.length)
                _this._loadDealStage();

            $("#deal_email_field_form").ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: function(response, status, xhr, form) {
                    form.find('button[type=submit]').removeClass('loader');

                    if(response.success) {
                       $('.save-and-send:visible').click();
                       $('[data-modal-close]:visible').click();
                       $('a.text-editable[data-name=email]').editable('destroy');
                       $('a.text-editable[data-name=email]').html(response.data.value);

                       __XEDITABLE.init();
                    }
                },
                error: Utilities.Form.onFailure
            });

            // Email modal Template DD change event
            $('.deal-container').on('change', '#custom_email_type', function() {
                debugger
                if($('body').hasClass('health-deals')) {
                    _this._triggerCustomEmailModal($(this).val());
                }
            });

            $('.ranges li').on('click', function(){
                debugger
                $('.felix-table').addClass('opacity')
                range = $(this).data('range-key')
                $('.ranges li.active').removeClass('active')
                $(this).addClass('active')
                current_range = $('#renewal_date_filter').html()

                if(range != current_range && range.toLowerCase()){
                    let url = DjangoUrls['health-insurance:renewals-filter']();
                    // $.get(url, {'range':range}, function(response){
                    let table = $('.felix-table').DataTable();
                    //     let column1 = `<label class="felix-checkbox">
                    //     <input class="select-record" type="checkbox" data-id="{{ policy.pk }}" value="{{ policy.pk }}" />
                    //     <span class="checkmark"></span>
                    // </label>`
                    table.clear()
                    table.draw()                    
                    $('.felix-table').removeClass('opacity')
                    //$(this).removeClass('clicked')
                }
            })

            $('#hide-renewal-deals').on('change', function(){
                debugger
                $('.felix-table').addClass('opacity')
                filter = {}
                if(this.checked)
                    filter = {'filter':'hide_renewal'}
                let url = DjangoUrls['health-insurance:renewals-list']();
                let table = $('.felix-table').DataTable();
                table.clear()
                table.draw()
                $('.felix-table').removeClass('opacity')
                // $.get(url, filter, function(response){
                //     let table = $('.felix-table').DataTable();
                //     let column1 = `<label class="felix-checkbox">
                //     <input class="select-record" type="checkbox" data-id="{{ policy.pk }}" value="{{ policy.pk }}" />
                //     <span class="checkmark"></span>
                // </label>`
                //     table.clear()
                //     response['qs'].forEach(i => {
                //         table.row.add([`${column1}`,i['status'],i['policy_number'],i['deal'],i['customer'],i['owner'],i['insurer'],i['premium'],i['expiry_date']]).draw()
                //     })
                //     if(response['qs'].length == 0){
                //         table.clear()
                //         table.draw()
                //     }
                //     $('.felix-table').removeClass('opacity')
                // })
            })
        },

        _triggerCustomEmailModal: function(email_type) {
            debugger
            var url = DjangoUrls['health-insurance:deal-email-content'](_deal_id, email_type);
            $('#custom_email_form').css({'opacity': '.7'});

            $.get(url, function(response) {
                var form = $('#custom_email_form');
                $('#custom_email_form').css({'opacity': '1'});
                $('[data-felix-modal="modal_send_custom_email_health"]').click();

                form.find('#email_type').val(email_type);
                form.find('#id_email').val(response.to);
                form.find('#id_from_email').html(response.from);
                form.find('#id_reply_to').html(response.reply_to);
                form.find('#id_cc_emails').val(response.cc_emails);
                form.find('#id_bcc_emails').val(response.bcc_emails);
                form.find('#id_subject').val(response.subject);
                form.find('#id_content').trumbowyg($.trumbowyg.config);
                form.find('#id_content').trumbowyg('html', response.content);

                form.find('#custom_email_type option').remove();

                $.each(response.allowed_templates, function(k, v) {
                    var selected = k==response.email_type?'selected':'';
                    form.find('#custom_email_type').append(
                        `<option ${selected} value="${k}">${v}</option>`
                    );
                });
                $('#custom_email_type').trigger('chosen:updated');

                form.find('.email_type_display').html(
                    response.allowed_templates[response.email_type]
                );

                if('sms_content' in response && response.sms_content) {

                    form.find('.show-when-sms').removeClass('hide');
                    form.find('#id_sms_content').val(response.sms_content);

                    form.find('#id_send_sms').change(function() {
                        form.find('.sms_container').addRemoveClass(!$(this).is(':checked'), 'hide');
                    });

                    $('textarea[maxlength]').maxlength({
                        alwaysShow: true,
                        warningClass: "badge badge-info",
                        limitReachedClass: "badge badge-warning"
                    });
                } else {
                    form.find('.show-when-sms').addClass('hide');
                    form.find('#id_sms_content').val('');
                    form.find('#send_sms').prop('checked', false);
                }

                if('whatsapp_msg_content' in response && response.whatsapp_msg_content) {

                    form.find('.show-when-wa-msg').removeClass('hide');
                    form.find('#id_send_wa_msg').val(response.whatsapp_msg_content);

                    form.find('#id_send_wa_msg').change(function() {
                        form.find('.msg_container').addRemoveClass(!$(this).is(':checked'), 'hide');
                    });

                    $('textarea[maxlength]').maxlength({
                        alwaysShow: true,
                        warningClass: "badge badge-info",
                        limitReachedClass: "badge badge-warning"
                    });
                } else {
                    form.find('.show-when-wa-msg').addClass('hide');
                    form.find('#id_wa_msg_content').val('');
                    form.find('#id_send_wa_msg').prop('checked', false);
                }

                if('attachments' in response && response.attachments.length) {
                    form.find('.attachments').removeClass('hide');
                    form.find('.attachments ul li').remove();
                    $.each(response.attachments, function() {
                        form.find('.attachments ul').append(
                            '<li><a href="' + this.url + '" target="_blank">' + this.name + '</a></li>'
                        );
                    });
                } else {
                    form.find('.attachments').addClass('hide');
                }
            });
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

                    
                        let result = ui.item.desc.trim();
                        result = result.replace(/\s/g, "");
                        result = result.split("|");
                        const email = result[0].replace("E:", "");
                        const tel = result[1].replace("T:", "");
                        $('#id_customer_email').val(email)
                        $('#id_customer_phone').val(tel)

                        $('#modal_create_health_deal #id_email').val(email)
                        $('#modal_create_health_deal #id_phone').val(tel)
                    

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

        _validatePrepare: function(elem){
            if(!elem) return
            debugger
            let formData = new FormData()
            elem.form.querySelectorAll('.error').forEach(elem => {elem.remove()})
            let errorCount = 0
            elem.closest('form').querySelectorAll('input.required').forEach(i => {
                $(i.parentElement).find('.error').remove();
                if (i.type == 'checkbox'){
                if (i.checked){
                    console.log(i.checked)
                    formData.append(i.name, i.checked)
                }
                else{
                    $(i.parentElement).after('<span class="error">This field is required</span>')
                    errorCount++
                }
                }
                else if (i.type == 'file'){
                    if(i.files.length == 0){
                        $(i.parentElement).after('<span class="error">This field is required</span>')
                        errorCount++
                    }
                    formData.append(i.name, i.files[0])
                }
                else{
                    if (i.value){
                        formData.append(i.name, i.value)
                    }
                    else{
                        $(i.parentElement).after('<span class="error">This field is required</span>')
                        errorCount++
                    }
                }
            })
            
            data = {'current_stage': current_stage, 'current_sub_stage':current_sub_stage}
            formData.append('stage_data',JSON.stringify(data))
            if(errorCount > 0) return false
            else return formData
    
        },

        validateEmailForm: function(){
            var form = $('#custom_email_form');
                    var email_type = form.find('#email_type').val();
    
                    // Validations
                    form.find('.error').remove();
                    if(form.find('#id_email').val() == '') {
                        form.find('#id_email').after('<span class="error">This field is required</span>');
                        return false;
                    }
                    if(form.find('#id_subject').val() == '') {
                        form.find('#id_subject').after('<span class="error">This field is required</span>');
                        return false;
                    }
    
                    form.find('button.send-email').addClass('loader');
                    return true
        },

        processEmailResponse:function(response){
            if(!response) return
            if(response.success) {
                                Utilities.Notify.success('Email sent successfully.', 'Success');
                                $('#modal_send_custom_email_health').hide();
    
       
                                 }
        },

        saveForm:function(formData){
            let url = `/health-insurance/deals/${_deal_id}/substage`
            $.ajax({
                method: 'POST',
                url: url,
                data: formData,
                async: false,
                success: function(response){
                    debugger
                    if(response['saved']){
                        next_substage = response['next_sub_stage']
                        let next = SUB_STAGES[current_stage][next_substage]
                        $(`li.substage_${current_sub_stage}`).toggleClass('current selected', false)
                        $(`li.substage_${current_sub_stage}`).toggleClass('completed', true)
                        $(`li.substage_${next_substage}`).toggleClass('current selected', true)
                        $(`div.substage_${current_sub_stage}`).toggleClass('show active', false)
                        $(`div.substage_${next_substage}`).toggleClass('show active', true)
                        document.getElementById('current_sub_stage').value = next_substage
                        Utilities.Notify.success('Sub Stage Updated', 'Success');
                        let reload = response['reload']
                        if (reload) location.reload()
                    }
                },
                error: function(error){
                    debugger
                },
                'processData': false,
                'contentType': false,
                })
        },

        loadInsurerProducts: function(){
        let add_product = $('.deal-form').html()
        $('.health-deal-processes').html(add_product)
        let insurer_id = this.dataset['id']
        let url = `{% url 'health-insurance:health-plans' pk=11 %}`
        url = url.replace('11', insurer_id)
        $.ajax({
            method: 'GET',
            url: url,
            data: {'deal':_deal_id},
            success: function(response){
            console.log(response)
            response['plans'].forEach(i => {
                console.log(i['name'])
                let opt = document.createElement('option');
                opt.value = i['id'];
                opt.innerHTML = i['name'];
                document.querySelector('select#id_product').appendChild(opt);
            })
            },
            error: function(error){
                debugger
            },
            'processData': false,
            'contentType': false,
            })
        },
   
        _getQuotedProducts: function() {
            $.get(DjangoUrls[`${__app_name}:deal-quoted-products-json`](_deal_id), function(response) {
                if(response) {
                    _quoted_products_data['products'] = response;
                    _quoted_products_data['quote']['status'] = $('#id_quote_status').is(':checked');
                    _this._renderQuotedProductsPreview();
                }
            });
        },

        _loadStageWarning: function() {
            setTimeout(function() {
                $('.stage-warning').click(function() {
                    alertify
                        .okBtn("Dismiss")
                        .cancelBtn("Cancel")
                        .confirm("Some deal information has changed since you last saved your quotes. This might affect the premiums quoted. Consider reviewing  your quotes before proceeding.", function (ev) {
                            $.get(
                                DjangoUrls['mortgage:deal-remove-warning'](_deal_id),
                                function(response) {
                                    if(response.success)
                                       $('.stage-warning').addClass('hide'); 
                            });
                        });
                });
            }, 2000);
        },

        _loadHistory: function() {
            debugger
            if(!_deal_id || !$('#health_tab_history').length) return;

            $.get(DjangoUrls['health-insurance:deal-history'](_deal_id), function(response) {
                $('#health_tab_history').html(response);
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

        _setCustomerInDealForm: function(customer_id, customer_name) {
            $('#health_deal_form #id_customer').val(customer_id);
            $('#health_deal_form #id_customer_name').val(customer_name);
        },

        _triggerCustomEmailForm: function() {
                var form = $('#custom_email_form');
                var email_type = form.find('#email_type').val();

                // Validations
                form.find('.error').remove();
                if(form.find('#id_email').val() == '') {
                    form.find('#id_email').after('<span class="error">This field is required</span>');
                    return;
                }
                if(form.find('#id_subject').val() == '') {
                    form.find('#id_subject').after('<span class="error">This field is required</span>');
                    return;
                }

                form.find('button.send-email').addClass('loader');

                let formData = new FormData()
                form.find('input').each((i, elem) => {
                    console.log(elem)
                    if (elem.type == 'file')
                        formData.append(elem.name, elem.files[0])
                    else if(elem.type == 'text')
                        formData.append(elem.name, elem.value)
                    else if(elem.type == 'checkbox'){
                        formData.append(elem.name, elem.checked ? true : '')
                    }
                })

                form.find('textarea').each((i, elem) => {
                    formData.append(elem.name, elem.value)
                })

                $.ajax({
                    method: 'POST',
                    url: DjangoUrls['health-insurance:deal-email-content'](_deal_id, email_type),
                    data: formData,
                    async: false,
                    success: function(response){
                        Utilities.Notify.success('Email sent successfully.', 'Success');
                            $('#modal_send_custom_email_health').hide();

                            if(response.email_type == 'new_quote' || response.email_type == 'quote_updated') {
                                __AMPLITUDE.logEvent(
                                    __AMPLITUDE.event('health_quote_email_sent'), {
                                        'deal_id': _deal_id
                                    }
                                );
                            }

                            _this._loadHistory();
                        
                    },
                    error: function(error){
                        debugger
                        Utilities.Notify.error('Please check all the required fields and try again.', 'Error');
                        Utilities.Form.addErrors($('#custom_email_form'), response.errors);
                    },
                    processData: false,
                    contentType: false,
                    })

                
        },

        _triggerCustomEmailModal: function(email_type) {
            var url = DjangoUrls['health-insurance:deal-email-content'](_deal_id, email_type);
            $('#custom_email_form').css({'opacity': '.7'});

            $.get(url, function(response) {
                var form = $('#custom_email_form');
                $('#custom_email_form').css({'opacity': '1'});
                $('[data-felix-modal="modal_send_custom_email_health"]').click();

                form.find('#email_type').val(email_type);
                form.find('#id_email').val(response.to);
                form.find('#id_from_email').html(response.from);
                form.find('#id_reply_to').html(response.reply_to);
                form.find('#id_cc_emails').val(response.cc_emails);
                form.find('#id_bcc_emails').val(response.bcc_emails);
                form.find('#id_subject').val(response.subject);
                form.find('#id_content').trumbowyg($.trumbowyg.config);
                form.find('#id_content').trumbowyg('html', response.content);

                form.find('#custom_email_type option').remove();
                $.each(response.allowed_templates, function(k, v) {
                    console.log(k)
                    var selected = k==response.email_type?'selected':'';
                    console.log(selected)
                    form.find('#custom_email_type').append(
                        `<option ${selected} value="${k}">${v}</option>`
                    );
                });
                $('#custom_email_type').trigger('chosen:updated');

                form.find('.email_type_display').html(
                    response.allowed_templates[response.email_type]
                );

                if('sms_content' in response && response.sms_content) {

                    form.find('.show-when-sms').removeClass('hide');
                    form.find('#id_sms_content').val(response.sms_content);

                    form.find('#id_send_sms').change(function() {
                        form.find('.sms_container').addRemoveClass(!$(this).is(':checked'), 'hide');
                    });

                    $('textarea[maxlength]').maxlength({
                        alwaysShow: true,
                        warningClass: "badge badge-info",
                        limitReachedClass: "badge badge-warning"
                    });
                } else {
                    form.find('.show-when-sms').addClass('hide');
                    form.find('#id_sms_content').val('');
                    form.find('#send_sms').prop('checked', false);
                }

                if('whatsapp_msg_content' in response && response.whatsapp_msg_content) {

                    form.find('.show-when-wa-msg').removeClass('hide');
                    form.find('#id_wa_msg_content').val(response.whatsapp_msg_content);

                    form.find('#id_send_wa_msg').change(function() {
                        form.find('.msg_container').addRemoveClass(!$(this).is(':checked'), 'hide');
                    });

                    $('textarea[maxlength]').maxlength({
                        alwaysShow: true,
                        warningClass: "badge badge-info",
                        limitReachedClass: "badge badge-warning"
                    });
                } else {
                    form.find('.show-when-wa-msg').addClass('hide');
                    form.find('#id_wa_msg_content').val('');
                    form.find('#id_send_wa_msg').prop('checked', false);
                }


                // if('attachments' in response && response.attachments.length) {
                //     form.find('.attachments').removeClass('hide');
                //     form.find('.attachments ul li').remove();
                //     $.each(response.attachments, function() {
                //         form.find('.attachments ul').append(
                //             '<li><a href="' + this.url + '" target="_blank">' + this.name + '</a></li>'
                //         );
                //     });
                // } else {
                //     form.find('.attachments').addClass('hide');
                // }
            });
        },

        _openLostDealTriggers: function() {
            _deal_open_or_lost_btn.click(function() {
                if(_deal_open_or_lost_btn.hasClass('re-open')) {
                    if(window.confirm('Are you sure you want to Re-Open this deal?')) {
                        $.get(DjangoUrls['health-insurance:deal-reopen'](_deal_id), function(response) {
                            if(response.success) {
                                location.reload()                                
                            }
                        });
                    }
                } else {
                    if(window.confirm('Are you sure you want to mark this deal as a "LOST" deal?')) {
                        $.get(DjangoUrls['health-insurance:deal-mark-as-lost'](_deal_id), function(response) {
                            if(response.success) {
                                location.reload()
                                _this._loadDealStage();
                            }
                        });
                    }
                }
            });
        },

        _updateTags: function(tags) {
            // Updating Tags
            if(tags) {
                var tags_html = '';
                $.each(tags, function() {
                    tags_html += '<span class="m-t-15 m-r-4 badge badge-default badge-font-light badge-'+Utilities.General.slugify(this)+'">'+this+'</span>';
                });

                $('.deal-statuses').html(tags_html);
            }
        },

        _refreshStagesBar: function(stage) {
            var status = $('.deal-container').data('status');
            var stages = ['new', 'quote', 'preApproval', 'valuation', 'offer', 'settlement', 'loanDisbursal', 'propertyTransfer', 'closed'];

            $.get(DjangoUrls['mortgage:deal-current-stage'](_deal_id), function(response) {
                if(response)
                   status =  response.stage;

                if(stage === undefined || !stage)
                    stage = status;

                _this._updateTags(response.tags);

                _deal_stages_breadcrumb.find('li').removeClass('current completed lost won');

                // Checking for lost/won deal
                if(status == 'lost' || status == 'won' ) {
                    _deal_stages_breadcrumb.find('li').addClass(status);

                    _deal_open_or_lost_btn
                        .html('Reopen')
                        .removeClass('mark-as-lost btn-outline-danger hide')
                        .addClass('re-open btn-outline-dark');

                    return;
                } else {
                    _deal_open_or_lost_btn
                        .html('Mark as Lost')
                        .addClass('mark-as-lost btn-outline-danger')
                        .removeClass('re-open btn-outline-dark hide');
                }
                _deal_stages_breadcrumb.find('li[data-id='+ stage +']').addClass('selected');
                $.each(stages, function() {
                    if(this == status) {
                        _deal_stages_breadcrumb.find('li[data-id='+ this +']').addClass('current');
                        return false;
                    } else {
                        _deal_stages_breadcrumb.find('li[data-id='+ this +']').addClass('completed');
                    }
                });

                _this._loadHistory();
            });
        },

        _loadDealStage: function(stage) {
            if(_deal_id) {

                if(stage === undefined)
                    stage = '';
                    let url = DjangoUrls['health-insurance:get-deal-stage'](_deal_id) + '?stage=' + stage

                    $.ajax({
                        method: 'GET',
                        url: url,                        
                        async: false,
                        success: function(response){
                            _deal_stage_container.html(response);
                        },
                        error: function(error){
                            debugger
                        },                        
                        })
                    
                    _this._loadStageWarning();
                
            }
        },

        _getCustomerFromQueryParams: function() {
            var params = Utilities.General.getUrlVars();

            if('customer_id' in params && params['customer_id']) {
                return params['customer_id'];
            }

            return false;
        },

        _scrollAndOpenPaymentsTab: function() {
            var elem = $('a[href="#tab_payments"]');
            
            $([document.documentElement, document.body]).animate({
                scrollTop: elem.offset().top
            }, 100);
            elem.click();
        },

        _dealStatusInline: function() {
            $('.deal-inline-update-field').editable({
                emptytext: $(this).data('emptytext')?$(this).data('emptytext'):'-',
                mode: 'inline',
                inputclass: 'form-control-sm',
                url: $(this).data('url'),
                emptyclass: 'empty',
                source: $(this).data('options')?$.parseJSON($(this).data('options')):[],
                display: function (value, sourceData) {
                    var elem = $.grep(sourceData, function (o) {
                        return o.value == value;
                    });

                    if (elem.length) {
                        $(this).text(elem[0].text);
                    } else {
                        $(this).empty();
                    }
                },
                error: function(response) {
                    return response.responseJSON.message;
                },
                success: function(response, newValue) {
                    if(response.success) {
                        Utilities.Notify.success(response.message, 'Success');
                    } else {
                        Utilities.Notify.error(response.message, 'Error');
                        return false;
                    }
                }
            }).on('shown', function(e, editable){
                editable.input.$input.chosen();
            });
        },

        _loadQuotePreview: function() {
            $.get(DjangoUrls['mortgage:deal-quote-preview'](_deal_id), function(response) {
                $('.quote-preview').html(response);
            });
        },

        _set_quoted_product_data : function(result){
            if(result){
                if (result['insurer_id'])
                    _this._set_selected_plan_dropdown(result['insurer_id'])
                updateQuoteForm('','',result['product_id'])
                $("#id_total_premium").val(result['total_premium'])
                $(".currencies select").val(result['currency'])
                $('.plan_currency').html($(".currencies select option:selected").text())
                if(result['network'])      
                $(".network select").val(result['network'])
                if(result['inpatient_deductible'])
                $(".inpatient_deductible select").val(result['inpatient_deductible'])
                if(result['payment_frequency'])
                $(".payment_frequency select").val(result['payment_frequency'])
                if(result['consultation_copay'])
                $(".consultation_copay select").val(result['consultation_copay'])

                let consultation_copays = products_data['data']['consultation_copay']
                let copay_mode = result['copay_mode']
                if(copay_mode && copay_mode.toLowerCase() != 'variable'){
                    for(let i in consultation_copays){
                        if(result['consultation_copay'] && consultation_copays[i]['id'] == result['consultation_copay']){
                            $(".pharmacy_copay select").val(consultation_copays[i]['pharmacy_copay'])
                            $(".diagnostics_copay select").val(consultation_copays[i]['diagnostics_copay'])
                        }
                    }
                }
                else{
                    if(result['diagnostics_copay'])
                        $(".diagnostics_copay select").val(result['diagnostics_copay'])
                    if(result['pharmacy_copay'])
                        $(".pharmacy_copay select").val(result['pharmacy_copay'])                
                }
                if(result['annual_limit'])
                $(".annual_limit select").val(result['annual_limit'])
                if(result['area_of_cover'])
                $(".area_of_cover select").val(result['area_of_cover'])
                if(result['physiotherapy'])
                $(".physiotherapy select").val(result['physiotherapy'])
                if(result['alternative_medicine'])
                $(".alternative_medicine select").val(result['alternative_medicine'])
                if(result['maternity_waiting_period'])
                $(".maternity_waiting_period select").val(result['maternity_waiting_period'])
                if(result['maternity_waiting_period'])
                $(".optical_benefits select").val(result['optical_benefits'])
                if(result['dental_benefits'])
                $(".dental_benefits select").val(result['dental_benefits'])
                if(result['wellness_benefits'])
                $(".wellness_benefits select").val(result['wellness_benefits'])
                if(result['maternity_benefits'])
                $(".maternity_benefits select").val(result['maternity_benefits'])
                if(result['pre_existing_cover'])
                $(".pre_existing_cover select").val(result['pre_existing_cover'])
                if(result['pre_existing_cover'])
                $(".pre_existing_cover select").val(result['pre_existing_cover'])

                $("#id_primary_member_premium").val(result['primary_member_premium'])
                $(".additional_member").each(function(){
                    $(this).val(result[this.id])
                })
                $('.renewal_details').removeClass('hide')
                if(result['is_renewal']){
                    $('.renewal_details input[type="checkbox"]').prop('checked', true)
                    $('.renewal_document').toggleClass('hide', false)
                }
                else{
                    $('.renewal_details input[type="checkbox"]').prop('checked', false)
                    $('.renewal_document').toggleClass('hide', true)
                }
                if(result['is_repatriation_enabled']){
                    $('.enable_repatriation input[type="checkbox"]').prop('checked', true)                    
                }
                else{
                    $('.enable_repatriation input[type="checkbox"]').prop('checked', false)                    
                }
                $('.renewal_details .renewal_document input[type="file"]').next().remove()
                if(result['renewal_document'])                    
                    $('.renewal_details .renewal_document input[type="file"]').after(`<a class="renewal-file-name font-10" href=${result['renewal_document']} target="_blank"><i class="fa fa-download" aria-hidden="true"></i>${result['renewal_document_name']}<a>`)                
                else
                $('.renewal_details .renewal_document input[type="file"]').after('')

                //$('.renewal_details .renewal_document input[type="file"]').val(result['plan_renewal_document'])
            }
        },
       
        _set_selected_plan_dropdown : function(insurer_id){

            let url = DjangoUrls['health-insurance:health-plans'](insurer_id)
            
            $.ajax({
                method: 'GET',
                url: url,
                data: {'deal':_deal_id},
                async: false,
                success: function(response){
                document.querySelector('select#id_product').innerHTML = ''
                let opt = document.createElement('option');
                opt.value = "";
                opt.innerHTML = 'Select Product';
                opt.selected = true
                document.querySelector('select#id_product').appendChild(opt);
                response['plans'].forEach(i => {
                    console.log(i['name'])
                    opt = document.createElement('option');
                    opt.value = i['id'];
                    opt.innerHTML = i['name'];
                    document.querySelector('select#id_product').appendChild(opt);
                })
                },
                error: function(error){
                    
                }                
                })

        },

        ////// DEAL Stages and Processes methods
        _addNewDealForm: function() {
            $("#deal_form").ajaxForm({
                beforeSubmit: Utilities.Form.beforeSubmit,
                success: function(response, status, xhr, form) {
                    if(response.success) {
                        $.get(DjangoUrls[`${__app_name}:get-deal-json`](response.deal_id), function(r) {
                            __AMPLITUDE.logEvent(__AMPLITUDE.event('mortgage_deal_created'), {
                                'source': 'manual',

                                'deal_id': r.deal.id,

                                'client_nationality': r.customer.nationality,
                                'client_gender': r.customer.gender,
                                'client_age': r.customer.age,

                                'deal_type': 'new'
                            });
                        });
                    }

                    Utilities.Form.onSuccess(response, status, xhr, form);
                },
                error: Utilities.Form.onFailure
            });
        },

        _dealProcessTriggers: function() {
            _deal_stage_container.on('click', '.btn-cancel-generate-new-quote', function(){
                if($('.deal-overview .deal-form .products-preview .products .row').length) {
                    $('.deal-form .products-preview').removeClass('hide');
                    $('.deal-form .form').addClass('hide');
                } else if($('.quote-overview .deal-form .products-preview .products .row').length){
                    $('.deal-form .products-preview').removeClass('hide');
                    $('.deal-form .form').addClass('hide');
                } else {
                    $('.deal-overview .new-deal').addClass('display');
                    $('.deal-overview .deal-form').removeClass('display');    
                }
            });

            _deal_stage_container.on('click','.cancel-quote', function(){
                if(!$('#saved_quote_div').length)
                location.reload()
                $('.deal-form').addClass('hide')
                $('.products-preview').addClass('hide')
                $('#saved_quote_div').removeClass('hide')
            })

            $('body').on('click', '.insurer-block-container', function() {
                $('.auto-quote-insurer-field').val($(this).data('id')).change();
                $('#modal_auto_quote_form h2').html($(this).data('name'));

                $('#id_product option').addClass('hide').trigger('chosen:updated');
                $('#id_product option[data-insurer-id=' + $(this).data('id') + ']').removeClass('hide').trigger('chosen:updated');
            });

            $("#mortgage_deal_form").submit(function (e) {
            e.preventDefault();
            var form = $("#mortgage_deal_form");
            var url = form.attr('action');
            $('.mortgage-deal-form-error').html('')
            $.ajax({
                    beforeSubmit: Utilities.Form.beforeSubmit,
                    type: "POST",
                    url: url,
                    data: form.serialize(),
                    success: function(data)
                    {
                        if (data.success){
                            location = data.redirect_url
                        }
                        else{
                            $('.mortgage-deal-form-error').html('')
                            var form_el = $("#mortgage_deal_form")[0].getElementsByTagName('input');
                            var form_el_select = $("#mortgage_deal_form")[0].getElementsByTagName('select');
                            for (var key in data.errors)
                            {
                                for (let i = 0; i < form_el.length; i++) {
                                if (form_el[i].name == key){
                                    form_el[i].parentElement.getElementsByTagName('span')[0].innerText = data.errors[key][0]
                                }
                              }
                              for (let i = 0; i < form_el_select.length; i++) {
                                if (form_el_select[i].name == key){
                                    form_el_select[i].parentElement.getElementsByTagName('span')[0].innerText = data.errors[key][0]

                                }
                              }
                            }
                            debugger
                            if (data.errors.__all__){
                                form_el.property_price.parentElement.getElementsByTagName('span')[0].innerText = data.errors.__all__[0]
                            }
                        }
                    }
                });
                return false;
            });
        },


        _setDealsQuoteOutdated: function() {
            var quote_stage_container = $('.deal-stages-breadcrumb [data-id="quote"]');

            if(!quote_stage_container.length) return;

            if(quote_stage_container.hasClass('selected') || quote_stage_container.hasClass('current') || quote_stage_container.hasClass('completed')) {
                $('.stage-warning').removeClass('hide');
                __MORTGAGE_DEALS._loadStageWarning();
            }
        },

        _duplicateDeal: function() {
            if(_deal_id) {
                if(window.confirm('Are you sure you want to duplicate this deal?')) {
                    $.get(DjangoUrls['mortgage:deal-duplicate'](_deal_id), function(response) {
                        if(response.success) {
                            window.location = response.redirect_url;
                        } else {
                            Utilities.Notify.error('Something went wrong. Please contact support.', 'Error');
                        }
                    });
                }
            }
        },

        _addProduct: function() {
            $('body').on('click', '.add-another-product', function() {
                debugger
                $('#modal_quote_insurers').modal('toggle');
                $('.deal-overview .new-deal').removeClass('display');
                $('.deal-overview .deal-form').addClass('display');

                $('.deal-form .products-preview').addClass('hide');
                $('.deal-form .form').removeClass('hide');

                $('#edited_id').val('');

                $('.deal-form .form .add-label').removeClass('hide');
                $('.deal-form .form .edit-label').addClass('hide');

                // _this._scrollToProductForm();
                // _this._resetProductForm();

                // __FELIX__.initSearchableSelect();
                // __FELIX__._loadLibs();
                $('.products-preview').addClass('hide');
                $('.health-deal-add-product').addClass('hide');
                $('#id_product').val('').trigger('chosen:updated');
            });
            //for add product button while creating quote
            _deal_stage_container.on('click', '.add-product', function() {
                debugger
                // Validation
                var error = false;
                $('.error').remove();
                $.each(['#id_product','#id_total_premium'], function() {
                    var field = $(this + '');
                    if(!field.val() || parseInt(field.val()) <= 0) {
                        error = true;
                        field.closest('.form-group').append('<div class="error">This field is required</div>');
                    }
                });
                // if(document.querySelector('#is_renewal_checkbox').checked && !$('.renewal_document_file')[0].files[0]){
                //     $('.renewal_details').removeClass('hide')
                //     $('.renewal_document').after('<span class="error">Please upload renewal document</span>')
                //     error = true;
                // }

                if(error) return;

                $('.renewal_details').addClass('hide')
                var product = window.products_data['data'];
                var data = {
                    'product_id': $('#id_product').val(),
                    'plan_name': product.name,
                    'plan_logo': product.plan_logo,
                    //'currency': product.currency,
                    'currency': $(".currencies select").val(),
                    'default_add_ons': $('#id_default_add_ons').val() || [],
                    'total_premium' : $('#id_total_premium').val(),
                    'inpatient_deductible': $('.inpatient_deductible select').val(),
                    'insurer_quote_reference': $('#id_insurer_quote_reference').val(),
                    'payment_frequency': $('.payment_frequency select').val(),
                    'area_of_cover': $('.area_of_cover select').val(),
                    'consultation_copay': $(".consultation_copay select").val(),
                    'pharmacy_copay': $(".pharmacy_copay select").val(),
                    'diagnostics_copay': $(".diagnostics_copay select").val(),
                    'deductible': $('#id_deductible').val(),
                    'network': $('#id_network').val(),
                    'annual_limit': $(".annual_limit select").val(),
                    'physiotherapy': $('#id_physiotherapy').val(),
                    'pre_existing_cover': $('#id_pre_existing_cover').val(),
                    'alternative_medicine_chosen': $('#id_alternative_medicine_chosen').val(),                    
                    'wellness_benefits': $(".wellness_benefits select").val(),
                    'dental_benefits': $(".dental_benefits select").val(),
                    'optical_benefits': $(".optical_benefits select").val(),
                    'dental_benefits': $(".dental_benefits select").val(),
                    'maternity_benefits': $(".maternity_benefits select").val(),
                    'maternity_waiting_period': $(".maternity_waiting_period select").val(),
                    'alternative_medicine': $(".alternative_medicine select").val(),
                    'physiotherapy': $(".physiotherapy select").val(),
                    'is_repatriation_enabled': $("#enable_repatriation_checkbox").is(':checked'),
                    'is_renewal' : $('#is_renewal_checkbox').is(':checked'),
                    'renewal_document' : !$('.renewal_document_file')[0].files[0] ? '' : $('.renewal_document_file')[0].files[0],
                    'published': true,
                    'auto_quoted': false,
                };
                _plan_form_data.append($('#id_product').val(), $('.renewal_document_file')[0].files[0])

                $('.member_premium').each(function(){
                    if(this.id == 'id_primary_member_premium')
                        data['primary_member_premium'] = this.value
                    else
                        data[this.name] = this.value
                })
                let qp_id = document.querySelector('#edited_qp_id')
                if(qp_id)
                    qp_id = qp_id.value
                if(qp_id)
                    data['id'] = qp_id

                let highlight_index = '';

                if($('#edited_id').val().length) {
                    if($('#edited_qp_id').val().length)
                        data['id'] = parseInt($('#edited_qp_id').val());
                    $.each(_quoted_products_data['products'], function(k, v) {
                        if(k == parseInt($('#edited_id').val())) {
                            data['id'] = _quoted_products_data['products'][k]['id']
                            data['insurer_id'] = _quoted_products_data['products'][k]['insurer_id']
                            _quoted_products_data['products'][k] = data;
                        }
                    });
                    highlight_index = parseInt($('#edited_id').val());
                } else {
                    _quoted_products_data['products'].push(data);
                    highlight_index = _quoted_products_data['products'].length - 1;
                }

                _this._renderQuotedProductsPreview(highlight_index);

                $('.products-preview').removeClass('hide');
                $('.deal-form .form').removeClass('hide');
                $('.deal-form .form').removeClass('hide');
                $('.health-deal-add-product').addClass('hide');
                $('#edited_id').val('')
                $('#edited_qp_id').val('')                
            });
        },

        _removeProduct: function() {
            _deal_stage_container.on('click', '.product-remove', function() {
                $(this).closest('.row').remove();

                var index = $(this).data('id');

                $.each(_quoted_products_data['products'], function(k, v) {
                    if(k == index) {
                        if('id' in v)
                            v['deleted'] = true;
                        else
                            delete _quoted_products_data['products'][k];
                    }
                });

                _this._toggleProductFormActionButtons();
            });
        },

        _editProduct: function() {
            _deal_stage_container.on('click', '.product-edit', function() {
                debugger
                var index = $(this).data('id');
                var qp_id = $(this).data('qp-id');
                var product = _quoted_products_data['products'][index];
                $('#edited_qp_id').val(qp_id);
                $('#edited_id').val(index);
                $('.deal-form .form .add-label').addClass('hide');
                $('.deal-form .form .edit-label').removeClass('hide');
                data = {'stage':'edit-plan','qp_id':`${qp_id}`}
                $('.products-preview').addClass('hide');
                //$('.deal-form .form').addClass('hide');                
                $('.health-deal-add-product').removeClass('hide');
                $('.deal-form').removeClass('hide');
                _this._set_quoted_product_data(product)
                $("#id_product").val(product['product_id'])
            });
        },

        _resetProductForm: function() {
            $('.deal-form .form #id_product').val('');
            $('.deal-form .form #id_product').trigger('chosen:updated');
            
            $('.deal-form .form #id_default_add_ons').trigger('chosen:updated');
            $('.deal-form .form #id_premium').val('').change();
            $('.deal-form .form #id_sale_price').val('').change();
            $('.deal-form .form #id_insurer_quote_reference').val('');
            $('.deal-form .form #id_deductible').val('').change();
            $('.deal-form .form #id_deductible_extras').val('');
            $('.deal-form .form #id_agency_repair').prop('checked', false);
            $('.deal-form .form #id_agency_repair').prop('disabled', false);
            $('.deal-form .form #id_agency_repair').closest('label').removeClass('disabled');
            $('.deal-form .form #id_ncd_required').prop('checked', false);
        },

        _scrollToProductForm: function() {
            $([document.documentElement, document.body]).animate({
                scrollTop: 100
            }, 200);
        },

        __set_deal_edit_form: function(product) {
            $('.deal-form .form #id_insured_car_value').val(product['insured_car_value']).change();
            $('.deal-form .form #id_premium').val(product['premium']).change();
            $('.deal-form .form #id_sale_price').val(product['sale_price']).change();
            $('.deal-form .form #id_deductible').val(product['deductible']).change();
            $('.deal-form .form #id_deductible_extras').val(product['deductible_extras']);
            $('.deal-form .form #id_insurer_quote_reference').val(product['insurer_quote_reference']);
            $('.deal-form .form #id_agency_repair').prop('checked', product['agency_repair']);
            $('.deal-form .form #id_ncd_required').prop('checked', product['ncd_required']);

            $('.deal-form .form #id_agency_repair').prop('disabled', !product['allows_agency_repair']);
            $('.deal-form .form #id_agency_repair').closest('label').addRemoveClass(!product['allows_agency_repair'], 'disabled');

            $('#id_product option').addClass('hide').trigger('chosen:updated');
            //$('#id_product option[data-insurer-id=' + window.products_data[product.product_id].insurer_id + ']').removeClass('hide').trigger('chosen:updated');

            //__FELIX__._loadLibs();

            $('.deal-form .form #id_product').val(product['product_id']);
            $('.deal-form .form #id_product').trigger('chosen:updated');
        },

        _renderQuotedProductsPreview: function(highlight_index) {
            if(highlight_index === undefined) highlight_index = -1;

            $('.products-preview .products').html('');
            $.each(_quoted_products_data['products'], function(k, v) {
                if(v === undefined || ('deleted' in v && v.deleted)) return;
                var source   = $('#health-deal-quote-add-product-template').html();
                var template = Handlebars.compile(source);
                v['index'] = k;
                $('.products-preview .products').append(template(v));
            });
            _this._toggleProductFormActionButtons();

            if(highlight_index > -1) {
                $('.products .product[data-id=' + highlight_index + ']').addClass('highlight-success');

                setTimeout(function(){
                    $('.highlight-success').removeClass('highlight-success');
                }, 2000);
            }
        },

        _toggleProductFormActionButtons: function() {
            var quote_id = $('.deal-form').data('quote-id');
            var quoted_product_length = $('.deal-form .products-preview .products .product').length;
            $('.quote-submit-send').prop('disabled',  quoted_product_length <= 0);

            if(!quoted_product_length && !$('.deal-form').data('quote-id')) {
                // _this._resetProductForm();

                // $('.deal-overview .new-deal').addClass('display');
                // $('.deal-overview .deal-form').removeClass('display');

                // $('.deal-form .form').removeClass('hide');
                // $('.deal-form .products-preview').addClass('hide');
            }
        },

        _submitQuoteForm: function(send_email, updated){
            _plan_form_data.append('data', JSON.stringify(_quoted_products_data))
            
            $.ajax({
                type: "POST",
                url: DjangoUrls['health-insurance:deal-quoted-products-json'](_deal_id),
                data: _plan_form_data,
                
                'processData': false,
                'contentType': false,
                
                success: function(response) {
                    if(response.success) {
                        Utilities.Notify.success('Quote updated successfully', 'Success');
                        if(response.deleted) {
                            _quoted_products_data['products'] = [];
                        }
                        if(send_email) {
                            var email_type = updated?'quote_updated':'quote';
                            _this._loadDealStage(email_type);
                            __HEALTH_DEALS._triggerCustomEmailModal(email_type);
                        }

                        var selected_stage = 'quote';
                        if(!$('.products-preview .products .row.product').length)
                            selected_stage = 'new';
                        $('.stage-warning').addClass('hide');
                        if(!send_email)
                        location.reload();
                    }

                    $('.' + _show_loader_class).removeClass(_show_loader_class);
                    $(this).attr('disabled',false)
                },
                
                
            });
        },

        _resetDealForm: function() {
            Utilities.Form.removeErrors('#deal_form')
            $('#modal_create_health_deal .autocomplete-container').removeClass('new')
            $('#modal_create_health_deal #id_customer').val('')
            $('#modal_create_health_deal input[type=text]').val('')
            $('#modal_create_health_deal select').val('')
            $('#modal_create_health_deal input[type="radio"]:checked').prop('checked', false)            
        },

        initExportTrigger: function() {
            $('.options-table .dropdown-item.export').click(function() {
                window.location = $(this).data('url') + '?' +  window.location.href.slice(window.location.href.indexOf('?') + 1);
            });
        },
    };

    jQuery(function() {
        jQuery(function() {
            __HEALTH_DEALS.init();
        });
    });
})();
