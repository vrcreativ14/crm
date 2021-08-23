'use strict'

var React = require('react');
var createReactClass = require('create-react-class');

var Addon = require('../components/Addon');
var Attribute = require('../components/Attribute');
var MyButton = require('../components/Button');
var BreadCrumbs = require('../components/Breadcrumbs');

import {loadTooltip, initOdometer, hideTooltips} from '../utils/common.js';


module.exports = createReactClass({
  componentDidMount: function(){
    initOdometer();
    loadTooltip();
    hideTooltips();
  },
  render: function(){
    var product_code = this.props.params.id;
    var product = products_data[product_code];

    var product_logo = <img src={product.logo} />;

    if(product.ncd_required) {
        var ncd_tooltip = "We've quoted you this great rate because you notified us that you can get a No Claims Letter from your previous insurer. If you can't provide us with this letter then this rate will change.";
        product_logo = <span className="ncd-required" data-tooltip={ncd_tooltip}>{product_logo}</span>;
    }

    if(!payment_captured) {
        var checkout_button = 
            <div className="inner-small-container">
                <MyButton label='Select' elemid={'price_' + product_code} price={product.total_price} product={product_code} type="checkout" classname="btn-primary" />
                <div className="note loader">Submitting request. Please wait...</div>
            </div>
    } else {
        var checkout_button = 
            <div className="inner-small-container row">
                <div className="col-xs-12 col-12 payment-captured">
                    <i className="fa fa-check-circle-o" aria-hidden="true"></i> Payment already made.
                </div>
            </div>
    }

    return (
        <div className="quotes-checkout">
            <BreadCrumbs current="checkout" />
        	<div className="sub-container">
                <div className="inner-small-container">
                    <div className="back-string">
                        <a href="#"><i className="fa fa-angle-left" aria-hidden="true"></i> Select a different policy to configure</a>
                    </div>
                    <div className="cart">
                        <div className="logo">
                            {product_logo}
                        </div>
                        <div className="title">
                            <h2>{product.name}</h2>
                        </div>

                        <div className="addons">Optional upgrades:</div>

                        {Object.keys(product.tier_1_attributes).map(function(attribute_key, x){
                            if(attribute_key) {
                                var attribute = product.tier_1_attributes[attribute_key];
                                if(attribute.type == 'addon') {
                                    var childkey = (product_code + "_" + attribute.code).toString();
                                    return <div className="standard-attribute"><Addon key={childkey} id={childkey} attributes={attribute} product={product_code} type="checkout" /></div>
                                }
                            }
                        })}

                        {Object.keys(product.tier_2_attributes).map(function(attribute_key, x){
                            if(attribute_key) {
                                var attribute = product.tier_2_attributes[attribute_key];
                                if(attribute.type == 'addon') {
                                    var childkey = (product_code + "_" + attribute.code).toString();
                                    return <div className="standard-attribute"><Addon key={childkey} id={childkey} attributes={attribute} product={product_code} type="checkout" /></div>
                                }
                            }
                        })}

                        <div className="addons">Standard features:</div>

                        {Object.keys(product.tier_1_attributes).map(function(attribute_key, x){
                            if(attribute_key) {
                                var attribute = product.tier_1_attributes[attribute_key];
                                if(attribute.type != 'addon') {
                                    var childkey = (product_code + "_1_" + x).toString();
                                    return <div className="standard-attribute"><Attribute attributes={attribute} key={childkey} product={attribute_key} id={childkey} /></div>;
                                }
                            }
                        })}

                        {Object.keys(product.tier_2_attributes).map(function(attribute_key, x){
                            if(attribute_key) {
                                var attribute = product.tier_2_attributes[attribute_key];
                                if(attribute.type != 'addon') {
                                    var childkey = (product_code + "_2_" + x).toString();
                                    return <div className="standard-attribute"><Attribute attributes={attribute} key={childkey} product={attribute_key} id={childkey} /></div>;
                                }
                            }
                        })}
                                
                    </div>
                </div>
            </div>
            <div className="quotes-checkout-submit-container ">
                <div className="sub-container">
                    {checkout_button}
                </div>
            </div>
        </div>
    );
  }
});
