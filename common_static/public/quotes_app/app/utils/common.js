export {
    updateItem,
    updateTotal,
    alignComparisonDivs,
    initOdometer,
    loadTooltip,
    initBulletScrolls,
    triggerCTA,
    hideTooltips,
    highlightSelectedProduct
};

function triggerCTA(obj) {
    if(typeof(obj) !== 'undefined')
        $(obj.currentTarget).closest('.item').find('button').click();
}

function updateItem(product_id, attribute_code) {
    var product = products_data[product_id];
    var all_attributes = product.tier_1_attributes.concat(product.tier_2_attributes);

    $.each(all_attributes, function(key, prop){
        if(prop.type == 'addon' && prop.code == attribute_code){
            var is_checked = $('[data-checkbox="'+product_id+'_'+attribute_code+'"]').is(':checked');
            this.selected = is_checked;
            updateTotal(product_id);
        }
    });
}

function updateTotal(product_id) {
    var product = products_data[product_id];
    var all_attributes = product.tier_1_attributes.concat(product.tier_2_attributes);

    var price = product.price;

    $.each(all_attributes, function(key, prop){
        if(prop.type == 'addon' && prop.selected){
            price = price + prop.value;
        }

        products_data[product_id].total_price = price;

        $('[data-price="price_'+product_id+'"]').each(function(){
            $(this).html(price.formatMoney());  
        });
    });
}

function initBulletScrolls() {
    $('.products-container').scroll(function() {
        controlBulletsOnScroll()
    });

    $('.scroll-buttons li').click(function(){
        var index = $(this).data('index');
        var offset = $('.products-container .item:nth('+index+')');
        $('.products-container').scrollTo(offset, 500, {offset: -50});
    });
}

function highlightSelectedProduct() {
    if(selected_product_details !== undefined && 'quoted_product_id' in selected_product_details) {
        var qp_id = selected_product_details.quoted_product_id;
        $('.products div[data-id=' + qp_id + '] .item').addClass('active');
    }
}

function controlBulletsOnScroll() {
    var items = $('.products-container .item');
    var pos_array = [];
    items.each(function(k) {
        var pos = Utilities.Check.elemVisibility($(this));
        var trimed_x = pos[0] > 0 && pos[0] < 0.8 ? pos[0] : 0;
        pos_array.push(trimed_x);
    });
    
    var li_index = pos_array.indexOf(Math.max.apply(null, pos_array));

    $('.scroll-buttons li.active').removeClass('active');
    $('.scroll-buttons li:nth('+li_index+')').addClass('active');
}

function initOdometer() {
    $('.odometer').each(function(){
        new Odometer({
            el: this,
            value: $(this).text(),
            duration: 500,
            animation: 'count',
            format: '(,ddd).dd'
        });
    });
}

function loadTooltip() {
    if(Utilities.Check.isMobile()) {
        $('[data-tooltip!=""]').qtip({
            content: { attr: 'data-tooltip'},
            style: { classes: 'qtip-light qtip-shadow qtip-rounded'},
            hide: 'unfocus',
            position: { my: 'top center'}
        });
        $('.left[data-tooltip!=""]').qtip({
            content: { attr: 'data-tooltip' },
            style: { classes: 'qtip-light qtip-shadow qtip-rounded'},
            hide: 'unfocus',
            position: { my: 'top right'}
        });
    } else {
        $('[data-tooltip!=""]').qtip({
            content: { attr: 'data-tooltip'},
            style: { classes: 'qtip-light qtip-shadow qtip-rounded'},
            hide: { fixed: true, delay: 100},
            position: { my: 'top center'}
        });
        $('.ncd-required[data-tooltip!=""]').qtip({
            content: { attr: 'data-tooltip'},
            style: { classes: 'qtip-light qtip-shadow qtip-rounded'},
            hide: { fixed: true, delay: 100},
            position: { my: 'top left'}
        });
    }
}

function setDivHeights() {
    var height = 0;
    var items = [];

    //resetting all heights first
    $('.products .attributes').css('height','auto');
    // Getting all heights
    $('.products .item').not('.drafted-product').each(function(key, val){
        var attributes = $(this).find('.attributes');

        items.push(
            attributes.map(function(){
                return $(this).height();
            })
        );
    });

    var max_number_of_attributes = Object.keys(items).map(function(key, index) {
       return items[key].length;
    });

    max_number_of_attributes = Math.max.apply(Math, max_number_of_attributes);

    // setting height for each cell in a same row
    for(var a=0; a<max_number_of_attributes; a++){
        var temp_array = [];
        for(var i=0; i<items.length; i++){
            temp_array.push(items[i][a]);
        };
        var max_cell_height = Math.max.apply(Math, temp_array);
        for(var i=1; i<=items.length; i++) {
            var item_element = $('.products .item').not('.drafted-product')[i-1];
            $($(item_element).find('.attributes')[a]).height(max_cell_height);
        }
    }
    if($('.drafted-product').length) {
        $('.drafted-product').height($('.products .item:first').height());
    }
}

function alignComparisonDivs() {
    setTimeout(function(){
        setDivHeights()
    }, 700);

    setTimeout(function(){
        setDivHeights()
    }, 2000);
}

function hideTooltips() {
    $('.qtip.qtip-default').hide();
}

//Helper
Number.prototype.formatMoney = function(c, d, t){
var n = this, 
    c = isNaN(c = Math.abs(c)) ? 2 : c, 
    d = d == undefined ? "." : d, 
    t = t == undefined ? "," : t, 
    s = n < 0 ? "-" : "", 
    i = String(parseInt(n = Math.abs(Number(n) || 0).toFixed(c))), 
    j = (j = i.length) > 3 ? j % 3 : 0;
   return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
 };