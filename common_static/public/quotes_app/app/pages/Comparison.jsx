'use strict'

var React = require('react');
var createReactClass = require('create-react-class');

var AppConstants = require('../Constants');

var Addon = require('../components/Addon');
var Attribute = require('../components/Attribute');
var MyButton = require('../components/Button');
var BreadCrumbs = require('../components/Breadcrumbs');
var Currency = require('../components/Currency');

import {alignComparisonDivs, initOdometer, loadTooltip, hideTooltips} from '../utils/common.js';


module.exports = createReactClass({
    componentDidMount: function(){
        alignComparisonDivs();
        initOdometer();
        loadTooltip();
        hideTooltips();
    },
    render: function() {
        var product_one_code = this.props.params.prod1;
        var product_two_code = this.props.params.prod2;

        var product_one = products_data[product_one_code];
        var product_two = products_data[product_two_code];
        
        var product_one_tier_1 = product_one.tier_1_attributes;
        var product_one_tier_2 = product_one.tier_2_attributes;
        var product_two_tier_1 = product_two.tier_1_attributes;
        var product_two_tier_2 = product_two.tier_2_attributes;

        var product_one_document_url = product_one.document_url;
        var product_two_document_url = product_two.document_url;

        var product_one_checkout_url = AppConstants['app_path'] + 'checkout/' + this.props.params.prod1;
        var product_two_checkout_url = AppConstants['app_path'] + 'checkout/' + this.props.params.prod2;

        var mobile_button_1 = '';
        var mobile_button_2 = '';

        var product_one_logo = <img src={product_one.logo} />;
        var product_two_logo = <img src={product_two.logo} />;

        var ncd_tooltip = "We've quoted you this great rate because you notified us that you can get a No Claims Letter from your previous insurer. If you can't provide us with this letter then this rate will change.";

        if(product_one.ncd_required) {
            product_one_logo = <span className="ncd-required" data-tooltip={ncd_tooltip}>{product_one_logo}</span>;
        }

        if(product_two.ncd_required) {
            product_two_logo = <span className="ncd-required" data-tooltip={ncd_tooltip}>{product_two_logo}</span>;
        }

        var action_bar = 
            <div className="inner-small-container row">
                <div className="col-xs-12 col-12 payment-captured">
                    <i className="fa fa-check-circle-o" aria-hidden="true"></i> Payment already made.
                </div>
            </div>

        if(!payment_captured) {
            var action_bar = 
                <div className="inner-small-container row">
                    <div className="col-xs-6 col-6 price for-mobile-only">
                        <Currency /> <span className="odometer" data-price={'price_' + product_one_code}>{product_one.total_price}</span>
                    </div>
                    <div className="col-xs-6 col-6 price for-mobile-only">
                        <Currency /> <span className="odometer" data-price={'price_' + product_two_code}>{product_two.total_price}</span>
                    </div>

                    <div className="col-xs-6 col-6 for-tablet-only">
                        <MyButton url={product_one_checkout_url} elemid={'price_' + product_one_code} label='Choose this' price={product_one.total_price} classname="btn-primary" />
                    </div>
                    <div className="col-xs-6 col-6 for-tablet-only">
                        <MyButton url={product_two_checkout_url} elemid={'price_' + product_two_code} label='Choose this' price={product_two.total_price} classname="btn-primary" />
                    </div>
                </div>

            mobile_button_1 = <MyButton url={product_one_checkout_url} elemid={'price_' + product_one_code} label='Choose this' classname="btn-primary for-mobile-only" />
            mobile_button_2 = <MyButton url={product_two_checkout_url} elemid={'price_' + product_two_code} label='Choose this' classname="btn-primary for-mobile-only" />
        }

        return (
            <div className="quotes-comparison">
                <BreadCrumbs current="policy" />
                <div className="sub-container">
                    <div className="inner-small-container">
                        <div className="back-string">
                            <a href="#"><i className="fa fa-angle-left" aria-hidden="true"></i> Select a different policy to compare</a>
                        </div>
                        <h1>Compare Products</h1>
                        <div className="products-container">
                            <div className="products">
                                <div className="item">
                                    <div className="logo-container responsive-image-container">
                                        <div className="spacer"></div>

                                        <div className="img-container">
                                            {product_one_logo}
                                        </div>
                                    </div>
                                    <div className="title">
                                        <h2>{product_one.name}</h2>
                                    </div>
                                    <div className="attributes-container">
                                        <div className="attributes attributes-title">Policy highlights:</div>
                                        {Object.keys(product_one_tier_1).map(function(attribute_key, x){
                                            if(attribute_key) {
                                                var attribute = product_one_tier_1[attribute_key];
                                                if(attribute.type == 'addon') {
                                                    var childkey = (product_one_code + "_" + attribute.code).toString();
                                                    return <Addon key={childkey} id={childkey} attributes={attribute} product={product_one_code} />
                                                } else {
                                                    var childkey = (product_one_code + "_" + x).toString();
                                                    return <Attribute key={childkey} id={childkey} attributes={attribute} product={product_one_code} />
                                                }
                                            }
                                        })}
                                    </div>
                                    <div className="attributes-container">
                                        <div className="attributes attributes-title">Other important features:</div>
                                        {Object.keys(product_one_tier_2).map(function(attribute_key, x){
                                            if(attribute_key) {
                                                var attribute = product_one_tier_2[attribute_key];
                                                if(attribute.type == 'addon') {
                                                    var childkey = (product_one_code + "_" + attribute.code).toString();
                                                    return <Addon key={childkey} id={childkey} attributes={attribute} product={product_one_code} />
                                                } else {
                                                    var childkey = (product_one_code + "_" + x).toString();
                                                    return <Attribute key={childkey} id={childkey} attributes={attribute} product={product_one_code} />
                                                }
                                            }
                                        })}
                                    </div>
                                    {mobile_button_1}
                                </div>

                                <div className="item">
                                    <div className="logo-container responsive-image-container">
                                        <div className="spacer"></div>

                                        <div className="img-container">
                                            {product_two_logo}
                                        </div>
                                    </div>
                                    <div className="title">
                                        <h2>{product_two.name}</h2>
                                    </div>
                                    <div className="attributes-container">
                                        <div className="attributes attributes-title">&nbsp;</div>
                                        {Object.keys(product_two_tier_1).map(function(attribute_key, x){
                                            if(attribute_key) {
                                                var attribute = product_two_tier_1[attribute_key];
                                                if(attribute.type == 'addon') {
                                                    var childkey = (product_two_code + "_" + attribute.code).toString();
                                                    return <Addon tooltip_position="left" key={childkey} id={childkey} attributes={attribute} product={product_two_code} />
                                                } else {
                                                    var childkey = (product_two_code + "_" + x).toString();
                                                    return <Attribute tooltip_position="left" key={childkey} id={childkey} attributes={attribute} product={product_two_code} />
                                                }
                                            }
                                        })}
                                    </div>
                                    <div className="attributes-container">
                                        <div className="attributes attributes-title">&nbsp;</div>
                                        {Object.keys(product_two_tier_2).map(function(attribute_key, x){
                                            if(attribute_key) {
                                                var attribute = product_two_tier_2[attribute_key];
                                                if(attribute.type == 'addon') {
                                                    var childkey = (product_two_code + "_" + attribute.code).toString();
                                                    return <Addon tooltip_position="left" key={childkey} id={childkey} attributes={attribute} product={product_two_code} />
                                                } else {
                                                    var childkey = (product_two_code + "_" + x).toString();
                                                    return <Attribute tooltip_position="left" key={childkey} id={childkey} attributes={attribute} product={product_two_code} />
                                                }
                                            }
                                        })}
                                    </div>
                                    {mobile_button_2}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="quotes-comparison-submit-container ">
                    <div className="sub-container">
                        {action_bar}
                    </div>
                </div>
            </div>
        );
    }
});
