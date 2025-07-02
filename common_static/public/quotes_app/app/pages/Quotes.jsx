'use strict'

var React = require('react');
var createReactClass = require('create-react-class');

var Heading = require('../components/Heading');
var Products = require('../components/Products');
var User = require('../components/User');
var BreadCrumbs = require('../components/Breadcrumbs');
var ProductScrollButtons = require('../components/ProductScrollButtons');

import {alignComparisonDivs, initOdometer, loadTooltip, initBulletScrolls, hideTooltips, highlightSelectedProduct} from '../utils/common.js';


module.exports = createReactClass({
  componentWillMount: function() {
    products_data = JSON.parse(JSON.stringify(products_data_org));
  },
  componentDidMount: function(){
    alignComparisonDivs();
    initOdometer();
    loadTooltip();
    initBulletScrolls();
    hideTooltips();
    highlightSelectedProduct();
  },
  compareProducts: function() {
    var selected_items = $(".item .item-selection input[type='checkbox']:checked");
    var keys = $.map(selected_items, function(val, i){
        return val.value;
    });
    if(selected_items.length == 2) {
        window.location.hash = 'comparison/' + (keys.join('/'));
    }
  },
  render: function(){
    var compare_button = '';
    var custom_note_elem = '';
    var agent_note_button = '';
    var compare_title = 'Select two policies to compare in more detail:';
    var products = <div>No product found.</div>
    var product_buttons = <ProductScrollButtons />

    if(Object.keys(products_data).length) {
        products = <Products disabled_checkbox="disabled" />
    }

    if(Object.keys(products_data).length > 1) {

        compare_button = <div className="quotes-submit-container hide hide-on-mobile">
                <div className="sub-container">
                    <div className="inner-small-container">
                        <button type="button" onClick={this.compareProducts} className="btn btn-primary disabled">Compare <i className="fa fa-angle-right"></i></button>
                    </div>
                </div>
            </div>
    } else {
        compare_title = '';
    }

    if(custom_note) {
        custom_note_elem = <div>
            <div className="custom-note-heading">Agent Notes</div>
            <div className="custom-note" dangerouslySetInnerHTML={{ __html: custom_note }} />
        </div>

        agent_note_button = <a href="javascript:" className="agent-notes-button btn btn-primary">Read Agent Notes</a>
    }

    return (<div>
        <div className="hide-addons-checkboxes quotes">
            <BreadCrumbs current="policy" />
            <div className="sub-container">
                <div className="inner-small-container">
                    <div className="row">
                        <div id="main-heading" className="col-sm-12 col-md-5 col-lg-5">
                            <Heading />
                        </div>
                        <div className="col-sm-12 col-md-7 col-lg-7">
                            <div id="user-info-container" className="user-info">
                                <User />
                            </div>
                        </div>
                    </div>
                    <div className="short-line-turquoise"></div>
                    <div className="comparison-heading">
                        {agent_note_button}
                        {compare_title}
                    </div>
                    {product_buttons}
                    <div id="products-container" className="products-container">
                        {products}
                    </div>
                    {custom_note_elem}
                </div>
            </div>
            {compare_button}
        </div>  
    </div>
    );
  }
});
