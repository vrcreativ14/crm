/* Custom Config and helpers */

// Ajax Setup on Load
$.ajaxSetup({
    data: {
        ajax: true
    },
    complete: function(jqxhr, status) {
        if(jqxhr.responseJSON && 'redirect' in jqxhr.responseJSON) {
            window.location.href = jqxhr.responseJSON.url;
        }
    }
});

$.ajaxPrefilter(function( options ) {
    if(options.type == 'get' && options.data && options.data.indexOf('ajax=true') < 0) {
        options.data += '&ajax=true';
    }
});

//modify buttons style for editable select dropdown
$.fn.editableform.buttons =
    '<button type="submit" class="btn btn-success editable-submit btn-sm"><i class="ti-check"></i></button>' +
    '<button type="button" class="btn btn-danger editable-cancel btn-sm"><i class="ti-close"></i></button>';

// Custom global closures
$.fn.fadeInOrOut = function(status) {
    return status ? this.fadeIn(100) : this.fadeOut(100);
};
$.fn.addRemoveClass = function(status, class_name) {
    return status ? this.addClass(class_name) : this.removeClass(class_name);
};

$.fn.toggleProp = function(status, prop, val1, val2) {
    return status ? this.prop(prop, val1) : this.prop(prop, val2);
};

// Text editor global config
$.trumbowyg.config = {
    btns: [
        ['strong', 'em', 'del'],
        ['undo', 'redo'], // Only supported in Blink browsers
        ['link'],
        ['unorderedList', 'orderedList'],
    ],
    autogrow: true
};

//Handlebar custom helpers
Handlebars.registerHelper('times', function(n, block) {
    var accum = '';
    for(var i = 1; i <= n; ++i) accum += block.fn(i);
    return accum;
});

Handlebars.registerHelper('ifCond', function(v1, v2, options) {
    if(v1 === v2) {
        return options.fn(this);
    }
    return options.inverse(this);
});

Handlebars.registerHelper('replaceWith', function(str, find, replacewith) {
    return str.replace(new RegExp(find , 'g'), replacewith);
});

Handlebars.registerHelper('slugify', function(text) {      
  return Utilities.General.slugify(text);
});

Handlebars.registerHelper('lowercase', function(text) {      
  return text.toLowerCase();
});

Handlebars.registerHelper('felixUrl', function(str, params) {      
  return DjangoUrls[str](params);
});

Handlebars.registerHelper('money', function(number, decimals) {
  if(decimals === undefined) decimals = 0;
  if(number) return accounting.format(number, decimals);

  return number;
});

Handlebars.registerHelper('json_stringify', function(obj) {
    return (typeof(obj) == 'object') ? JSON.stringify(obj) : obj;
});

Handlebars.registerHelper('userDealUpdateDD', function(deal_id, user_id, text, app_name) {
    var user_list = "{'value': -1, 'text': '-----'},";
    var i = 0;
    var empty_class = '';
    $('#id_assigned_to option').each(function() { 
        var text = $(this).text();
        text = (text + '').replace(/[\\"']/g, '\\$&').replace(/\u0000/g, '\\0');

        if($(this).val() != 'unassigned' && $(this).val()) {
            user_list += "{'value': '" + $(this).val() + "', 'text': '" + text + "'},";
        }
    });

    if(app_name === undefined)
        app_name = 'motorinsurance';

    if(text && text.toLowerCase() == 'unassigned') {
        text = '';
        user_id = '';
    }

    return '<a href="javascript:"' +
            'class="deal-inline-update-field select-editable editable"' +
            'data-name="assigned_to_id"' +
            'data-type="select"' +
            'data-emptytext="Add"' +
            'data-pk="' + deal_id + '"' +
            'data-value="' + user_id + '"' +
            'data-source="[' + user_list + ']"' +
            'data-url="' + DjangoUrls[app_name + ':update-deal-field'](deal_id, 'deal') + '"' +
            'data-title="Select">' + text +
        '</a>';
});

Handlebars.registerHelper('producerDealUpdateDD', function(deal_id, user_id, text) {
    var user_list = "{'value': -1, 'text': '-----'},";
    var i = 0;
    var empty_class = '';
    $('#id_producer option').each(function() {
        var text = $(this).text();
        text = (text + '').replace(/[\\"']/g, '\\$&').replace(/\u0000/g, '\\0');
        if($(this).val() != 'unassigned' && $(this).val()) {
            user_list += "{'value': '" + $(this).val() + "', 'text': '" + text + "'},";
        }
    });

    if(text === undefined) {
        text = '';
        user_id = '';
    } else if(text && text.toLowerCase() == 'unassigned') {
        text = '';
        user_id = '';
    }

    return '<a href="javascript:"' +
            'class="deal-inline-update-field select-editable editable"' +
            'data-name="producer_id"' +
            'data-type="select"' +
            'data-emptytext="Add"' +
            'data-pk="' + deal_id + '"' +
            'data-value="' + user_id + '"' +
            'data-source="[' + user_list + ']"' +
            'data-url="' + DjangoUrls['motorinsurance:update-deal-field'](deal_id, 'deal') + '"' +
            'data-title="Select">' + text +
        '</a>';
});

Handlebars.registerHelper('policyStatus', function(expiry_date) {
    return (get_date_difference_from_today(expiry_date)>=0)?'active':'expired';
});

Handlebars.registerHelper('policyExpiresIn', function(expiry_date) {
    return get_date_difference_from_today(expiry_date);
});

function get_date_difference_from_today(date) {
    var t1 = new Date().getTime();
    var t2 = new Date(date * 1000).getTime(); // Converting unixtimestamp for expiry date to datetimestamp

    return parseInt((t2-t1)/(24*3600*1000));
}
