var Utilities =
{
    ScreenSizes: {
        'mobile': 764,
        'tablet': 1023,
        'desktop': 1024,
    },
    General:{
        getUrlVars: function(){
            var obj = {};
            var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
            $.each(hashes, function(key, val){
                var hash = val.split('=');
                obj[hash[0]] = hash[1];
            });
            return obj;
        },
        getUrlAnchor: function(){
            var hash = location.hash.replace('#','');
            return hash;
        },
        getUrlPathname: function(){
            return window.location.pathname;
        },
        getUrlPathArray: function(){
            return window.location.pathname.split("/");
        },
        getUrlParamKeyValue: function(query){
            var query_string = {};
            var query = query?query:window.location.search.substring(1);
            var vars = query.split("&");
            for (var i=0;i<vars.length;i++) {
                var pair = vars[i].split("=");
                // If first entry with this name
                if (typeof query_string[pair[0]] === "undefined") {
                    query_string[pair[0]] = pair[1];
                // If second entry with this name
                } else if (typeof query_string[pair[0]] === "string") {
                    var arr = [ query_string[pair[0]], pair[1] ];
                    query_string[pair[0]] = arr;
                    // If third or later entry with this name
                } else {
                    query_string[pair[0]].push(pair[1]);
                }
            }
            return query_string;
        },
        getSpecificUrlPart: function(part, url) {
            var params = url?url:this.getUrlPathArray();

            if(typeof(params) == "string"){
                params = params.split("/");
            }

            var result = null;
            $.each(params, function(k, v) {
                if(v.indexOf(part) == 0 )
                    result = v;
            });
            return result;
        },
        getDomainName: function() {
            var parts = location.hostname.split('.');
            var subdomain = parts.shift();
            var upperleveldomain = parts.join('.');
            return upperleveldomain;
        },
        getSiteDataAttributes: function(attribute){
            return $("html").data(attribute);
        },
        getNonProtocolHost: function(){
            return "//" + window.location.host;
        },
        getNonProtocolHostWithLang: function(){
            return "//" + window.location.host + "/" + this.getSiteDataAttributes("lang");
        },
        copyToClipboard: function(elem) {
            var text = $('#' + elem.dataset.copyfrom)[0];
            text.select();
            document.execCommand("copy");

            $(elem).parent().find('.tooltiptext').html('Copied');
        },
        revertClipboardLabel: function(elem) {
            setTimeout(function(){
                $(elem).parent().find('.tooltiptext').html('Click to copy');
            }, 1000);
        },
        slugify: function(string) {
            var a = 'àáäâãåèéëêìíïîòóöôùúüûñçßÿœæŕśńṕẃǵǹḿǘẍźḧ·/_,:;';
            var b = 'aaaaaaeeeeiiiioooouuuuncsyoarsnpwgnmuxzh------';
            var p = new RegExp(a.split('').join('|'), 'g');
            return string.toString().toLowerCase()
                .replace(/\s+/g, '-') // Replace spaces with
                .replace(p, function(c) {return b.charAt(a.indexOf(c))}) // Replace special characters
                .replace(/&/g, '-and-') // Replace & with ‘and’
                .replace(/[^\w\-]+/g, '') // Remove all non-word characters
                .replace(/\-\-+/g, '-') // Replace multiple — with single -
                .replace(/^-+/, '') // Trim — from start of text .replace(/-+$/, '') // Trim — from end of text
        },
        AddHighlighter: function(elem, highlighter) {
            if(highlighter === undefined)
                highlighter = 'highlight-primary';

            elem.addClass(highlighter);
            setTimeout(function() {
                elem.removeClass(highlighter);
            }, 500);
        },
        generatePagination: function(current_page, total_pages) {
            let i;
            let html = '';
            let page_range = 3;

            if(!$('ul.pagination').length) return;

            $('ul.pagination').removeClass('hide');
            $('ul.pagination').fadeInOrOut(total_pages);

            current_page = current_page;


            if (current_page < 1) current_page = 1;
            if (current_page > total_pages) current_page = total_pages;

            let range_start = current_page - page_range;
            let range_end = current_page + page_range;

            if (range_end > total_pages) {
                range_end = total_pages;
                range_start = total_pages - page_range * 2;
                range_start = range_start < 1 ? 1 : range_start;
            }
            if (range_start <= 1) {
                range_start = 1;
                range_end = Math.min(page_range * 2 + 1, total_pages);
            }

            if (current_page > 1)
                html += '<li class="page-item"><a title="Previous" data-number="' + (current_page - 1) + '" class="page-link" href="javascript:">&laquo;</a></li>';

            if (range_start <= 3) {
                for (i = 1; i < range_start; i++)
                    html += '<li class="page-item"><a data-number="' + i + '" class="page-link ' + (i == current_page?'active':'') + '" href="javascript:">' + i + '</a></li>';

            } else {
                html += '<li class="page-item"><a class="page-link" data-number="1" href="javascript:">1</a></li>';
                html += '<li class="page-item"><a class="page-link ellipsis">...</a></li>';
            }

            for (i = range_start; i <= range_end; i++)
                html += '<li class="page-item ' + (i == current_page?'active':'') + '"><a data-number="' + i + '" class="page-link ' + (i == current_page?'active':'') + '" href="javascript:">' + i + '</a></li>';

            if (range_end >= total_pages - 2) {
                for (i = range_end + 1; i <= total_pages; i++)
                    html += '<li class="page-item"><a data-number="' + i + '" class="page-link" href="javascript:">' + i + '</a></li>';

            } else {
                html += '<li class="page-item"><a class="page-link ellipsis">...</a></li>';
                html += '<li class="page-item"><a class="page-link" data-number="' + total_pages + '" href="javascript:">' + total_pages + '</a></li>';
            }

            if (current_page < total_pages)
                html += '<li class="page-item"><a title="Next" data-number="' + (current_page + 1) + '" class="page-link" href="javascript:">&raquo;</a></li>';

            $('ul.pagination').html(html);
        }
    },
    Check:{
        isMobile: function(){
            var screenWidth = $(window).width();
            if(screenWidth <= Utilities.ScreenSizes.mobile){
                return true;
            }
            return false;
        },
        isTablet: function(){
            var screenWidth = $(window).width();
            if(screenWidth > Utilities.ScreenSizes.mobile && screenWidth <= Utilities.ScreenSizes.tablet){
                return true;
            }
            return false;
        },
        isTabletLandscape: function(){
            var screenWidth = $(window).width();
            if(screenWidth > Utilities.ScreenSizes.tablet && screenWidth <= Utilities.ScreenSizes.desktop){
                return true;
            }
            return false;
        },
        isDesktop: function(){
            var screenWidth = $(window).width();
            if(screenWidth >= Utilities.ScreenSizes.desktop){
                return true;
            }
            return false;
        },
        elemIsOnViewPort: function(_elem){
            if(_elem == undefined) return false;
            var partial         = true; //if true, will check the top of element in viewport else bottom of the elem
            var docViewTop      = $(window).scrollTop();
            var docViewBottom   = docViewTop + $(window).height();

            var elemTop         = $(_elem).offset().top;
            var elemBottom      = elemTop + $(_elem).height();

            var compareTop      = partial === true ? elemBottom : elemTop;
            var compareBottom   = partial === true ? elemTop : elemBottom;

            return ((compareBottom <= docViewBottom) && (compareTop >= docViewTop));
        },
        elemVisibility: function(obj) {
            var winw = jQuery(window).width(), winh = jQuery(window).height(),
                elw = obj.width(), elh = obj.height(),
                o = obj[0].getBoundingClientRect(),
                x1 = o.left - winw, x2 = o.left + elw,
                y1 = o.top - winh, y2 = o.top + elh;

            return [
                Math.max(0, Math.min((0 - x1) / (x2 - x1), 1)),
                Math.max(0, Math.min((0 - y1) / (y2 - y1), 1))
            ];
        },
        passwordStrength: function(password) {
            var strength = 0;

            if(!password.length)
                return 0;

            if (password.length > 0)
                strength += 1;
            // If password contains both lower and uppercase characters, increase strength value.
            if (password.match(/([a-z].*[A-Z])|([A-Z].*[a-z])/))
                strength += 1;
            // If it has numbers and characters, increase strength value.
            if (password.match(/([a-zA-Z])/) && password.match(/([0-9])/))
                strength += 1;
            // If it has one special character, increase strength value.
            if (password.match(/([!,%,&,@,#,$,^,*,?,_,~])/))
                strength += 1;
            // If it has two special characters, increase strength value.
            if (password.match(/(.*[!,%,&,@,#,$,^,*,?,_,~].*[!,%,&,@,#,$,^,*,?,_,~])/))
                strength += 1;

            return strength;
        }
    },
    Browser: {
        // Opera 8.0+
        isOpera: function() {
             return (!!window.opr && !!opr.addons) || !!window.opera || navigator.userAgent.indexOf(' OPR/') >= 0;   
        },

        // Firefox 1.0+
        isFirefox: function() {
             return typeof InstallTrigger !== 'undefined';   
        },

        // Safari 3.0+ "[object HTMLElementConstructor]" 
        isSafari: function() {
             return /constructor/i.test(window.HTMLElement) || (function (p) { return p.toString() === "[object SafariRemoteNotification]"; })(!window['safari'] || (typeof safari !== 'undefined' && safari.pushNotification));   
        },

        // Internet Explorer 6-11
        isIE: function() {
             return /*@cc_on!@*/false || !!document.documentMode;   
        },

        // Edge 20+
        isEdge: function() {
             return !isIE && !!window.StyleMedia;   
        },

        // Chrome 1+
        isChrome: function() {
             return !!window.chrome && !!window.chrome.webstore;   
        },

        // Blink engine detection
        isBlink: function() {
             return (isChrome || isOpera) && !!window.CSS;   
        }
    },
    Cookie:{
        get: function(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },
        set: function(name, value, days) {
            var expires;
            if (days) {
                var date = new Date();
                date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                expires = "; expires=" + date.toGMTString();
            }
            else {
                expires = "";
            }
            document.cookie = name + "=" + value + expires + "; path=/";
        },
    },
    Notify: {
        alert: function(text, title, type, icon) {
            var settings = {
                type: 'info',
                icon: icon,
                delay: 5000,
                animate_speed: 'fast',
                styling: 'bootstrap3'
            };
            if(typeof text !== 'undefined' && text) settings.text = text;
            if(typeof title !== 'undefined' && title) settings.title = title;
            if(typeof type !== 'undefined' && type) settings.type = type;

            new PNotify(settings);
        },
        success: function(text, title, icon) {
            if(typeof icon == 'undefined') icon = false;
            this.alert(text, title, 'success', icon);
        },

        error: function(text, title, icon) {
            if(typeof icon == 'undefined') icon = false;
            this.alert(text, title, 'error', icon);
        },

        info: function(text, title, icon) {
            if(typeof icon == 'undefined') icon = false;
            this.alert(text, title, 'info', icon);
        },

        notice: function(text, title, icon) {
            if(typeof icon == 'undefined') icon = false;
            this.alert(text, title, 'notice', icon);
        }
    },
    Form: {
        beforeSubmit: function(formData, form, options) {
            var loader = '<div class="ball-spinner"></div>';
            var button = form.find('button[type=submit]');

            form.find('button[type=submit]').addClass('loader');
            Utilities.Form.removeErrors(form);
        },
        onSuccess: function(response, status, xhr, form) {
            form.find('button[type=submit]').removeClass('loader');

            var module_name = form.data('module-name');
            if(!module_name) module_name = 'Record';

            if(response.success) {
                var success_message = module_name + ' updated successfully.';

                if('message' in response && response.message)
                    success_message = response.message;

                if('redirect_url' in response) {
                    success_message += '\nRedirecting...';
                    setTimeout(function() {
                        window.location = response.redirect_url;
                    }, 1000);
                }

                Utilities.Notify.success(success_message, 'Success');

                if($('.felix-modal-container').not('#modal_send_custom_email').is(':visible')) {
                    $('.felix-modal-container').find('.close').click();
                }
                __TABLE._fetch_felix_table_records();
            } else {
                Utilities.Notify.error('Please check all the required Fields.', 'Error');
                Utilities.Form.addErrors(form, response.errors);
            }
        },
        onFailure: function(response, status, xhr, form) {
            Utilities.Notify.error('Some error occurred. Please try again later.', 'Error');
        },
        addErrors: function(form, errors) {
            var general_errors = false;
            $.each(errors, function(key, val) {
                var elem = form.find('#id_' + key);
                var error_elem = '';
                if(typeof val == 'object' && val.length > 1) {
                    error_elem = '<ul class="error m-l--15">';
                    $.each(val, function(k, v) {
                        error_elem += '<li><span class="error">' + v + '</span></li>';
                    });
                    error_elem += '</ul>';
                } else {
                    error_elem = '<span class="error">' + val + '</span>';
                }

                if(elem.length) {
                    elem.removeClass('parsley-success').addClass('error-field');
                    if(elem.next('.chosen-container').length)
                        elem.next('.chosen-container').after(error_elem);
                    else
                        elem.after(error_elem);
                }
            });
        },
        passwordStrength: function (password) {
            var strength = 0;

            if(!password.length)
                return 0;

            if (password.length > 0)
                strength += 1;
            // If password contains both lower and uppercase characters, increase strength value.
            if (password.match(/([a-z].*[A-Z])|([A-Z].*[a-z])/))
                strength += 1;
            // If it has numbers and characters, increase strength value.
            if (password.match(/([a-zA-Z])/) && password.match(/([0-9])/))
                strength += 1;
            // If it has one special character, increase strength value.
            if (password.match(/([!,%,&,@,#,$,^,*,?,_,~])/))
                strength += 1;
            // If it has two special characters, increase strength value.
            if (password.match(/(.*[!,%,&,@,#,$,^,*,?,_,~].*[!,%,&,@,#,$,^,*,?,_,~])/))
                strength += 1;

            return strength;
        },
        removeErrors: function(form) {
            $(form).find('ul.error').remove();
            $(form).find('span.error').remove();
            $(form).find('.alert').remove();
            $(form).find('.error-field').removeClass('error-field');
        },
        updateSearchableSelectOptions: function(id, options, text, selected_id) {
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
            $(id).chosen({placeholder: text});
            $(id).trigger('chosen:updated');
        },
        addFilterCount: function(form) {
            var count = 0;
            $(form).find('input[type=text], select').not('#id_sort_by, #id_order_by, #id_search_term').each(function() {
                if(this.value) count++;
            });

            form.find('.filter-count').html(count).addRemoveClass(count?false:true, 'hide');
        },
        clearForm: function(form) {
            $(form).find('input[type=text], select').not('#id_order_by, #id_search_term').each(function() {
                $(this).val('').trigger('chosen:updated');
            });
        },
        validateEmail(email) {
            if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,10})+$/.test(email))
                return true;

            return false;
        }
    }
}
