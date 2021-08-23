'use strict'

var React = require('react');
var createReactClass = require('create-react-class');

var AppConstants = require('../Constants');

var Addon = require('./Addon');
var Attribute = require('./Attribute');
var Currency = require('./Currency');
var MyButton = require('./Button');
var MyCheckbox = require('./Checkbox');

import {triggerCTA} from '../utils/common.js';

module.exports = createReactClass({
    render: function(){
        var disabled_checkbox = this.props.disabled_checkbox;
        var drafted_product_element = '';

        if(drafted_product) {
            drafted_product_element = <div>
                <div className="drafted-product item">
                    <div className="content">
                        <p>We're working on putting some more great options together for you.</p>
                        <p>Expect an update from us soon!</p>
                    </div>
                </div>
            </div>
        }

        var products = (
            <div className="products">
                {Object.keys(products_data).map(function(key){
                    var product = products_data[key];
                    var product_price = product.total_price;
                    var premium = product.premium;
                    var tier_1_attributes = product.tier_1_attributes;
                    var tier_2_attributes = product.tier_2_attributes;
                    var tier_2_attributes_length = tier_2_attributes.length;
                    var document_url = product.document_url;
                    var garage_list_url = product.garage_list_url;
                    var checkout_url = AppConstants['app_path'] + 'checkout/' + key;
                    var compare_checkbox = '';
                    var action_button = '';
                    var action_button_variant_1 = '';
                    var action_button_variant_2 = '';
                    var modal_key = 'modal_' + key;
                    var agency_repair_ribbon = '';
                    var ncd_required = '';
                    var garage_list_url = '';
                    var product_document_url = '';

                    if(product.document_url) {
                        product_document_url = <a className='document-link' href={product.document_url} target="_blank">Policy Booklet</a>
                    }

                    if(product.ncd_required) {
                        ncd_required = <div className="ncd-required info-tip" data-tooltip="We've quoted you this great rate because you notified us that you can get a No Claims Letter from your previous insurer. If you can't provide us with this letter then this rate will change.">&nbsp;</div>
                    }

                    var product_price_block = <span>
                                                <span className='small'>starting at</span>
                                                <Currency /> <span className="odometer" data-price={"price_"+key }>{product_price}</span>
                                                {ncd_required}
                                              </span>;

                    if(product_price != premium) {
                        var product_price_block = <span>
                                                    <span className='small'>starting at
                                                        <span className="original-product-price info-tip felix-tooltip-bottom" data-tooltip="Public price - before your special discount">
                                                            <Currency /> {product.premium_display}
                                                        </span>
                                                    </span>
                                                    <Currency /> <span className="odometer" data-price={"price_"+key }>{product_price}</span>
                                                    {ncd_required}                                                    
                                                  </span>;
                    }

                    if(product.garage_list_url) {
                        garage_list_url = <a className='document-link' href={product.garage_list_url} target="_blank">Garage List</a>
                    }

                    if(!payment_captured) {
                        action_button = <MyButton url={checkout_url} tooltip="See add-ons, options and prices" label="Select" classname="btn-primary left" />
                    }
                    if(product.agency_repair) {
                        agency_repair_ribbon = <div className="ribbon"><span>Agency Repair</span></div>
                    }

                    if(Object.keys(products_data).length > 1) {
                        compare_checkbox = <div className="checkbox-section item-selection">
                            <MyCheckbox name={"chk_" + key} id={"id_chk_" + key} value={key} />
                            <div className="label">Compare</div>
                        </div>
                    }

                    return <div data-id={product.qp_id} key={key + '_parent'}>
                        <div className="item" key={key}>
                            {agency_repair_ribbon}
                            {compare_checkbox}
                            <div className="logo-container responsive-image-container">
                                <div className="spacer"></div>

                                <div className="img-container">
                                    <img src={product.logo} />
                                </div>
                            </div>
                            <div className="title">
                                <h2>{product.name}</h2>
                                <div className="price">
                                    {product_price_block}
                                    <span className="vat">(Incl. 5% VAT)</span>
                                </div>
                                <span className="original" onClick={triggerCTA.bind(this)}>{action_button}</span>
                                <span className="variant_1" onClick={triggerCTA.bind(this)}>{action_button_variant_1}</span>
                                <span className="variant_2" onClick={triggerCTA.bind(this)}>{action_button_variant_2}</span>
                            </div>

                            <div className="attributes car-value">
                                <span>Vehicle Insured Value:  <Currency/ > {product.insured_car_value}</span>
                            </div>

                            {Object.keys(tier_1_attributes).map(function(attribute_key, x) {
                                if(attribute_key) {
                                    var attribute = tier_1_attributes[attribute_key];
                                    var childkey = (key + "_" + x).toString();
                                    if(attribute.type == 'addon') {
                                        return <Addon attributes={attribute} key={childkey} product={key} id={childkey} disabled_checkbox={disabled_checkbox} />
                                    } else {
                                        return <Attribute attributes={attribute} key={childkey} product={key} id={childkey} disabled_checkbox={disabled_checkbox} />
                                    }
                                }
                            })}
                            <div className="attributes more-attributes">
                                + {tier_2_attributes_length} more attributes
                            </div>

                            <div className="actions">
                                <a href='javascript:' data-felix-modal={modal_key}>Learn more about this policy</a>
                            </div>
                        </div>

                        <div id={modal_key} className="felix-modal-container">
                            <div className="felix-modal">
                                <div className="logo-container responsive-image-container">
                                    <div className="spacer"></div>
                                    <div className="img-container">
                                        <img src={product.logo} />
                                    </div>
                                </div>
                                <div className="title">
                                    <h2>{product.name}</h2>
                                    <span className='small'>starting at</span> <Currency /> <span className="odometer" data-price={"price_"+key }>{product_price}</span><br />
                                    {product_document_url}
                                    {garage_list_url}
                                </div>
                                <div className="attributes-container">
                                    <div className="attributes attributes-title">Policy highlights:</div>
                                    {Object.keys(tier_1_attributes).map(function(attribute_key, x) {
                                        if(attribute_key) {
                                            var childkey = (key + "_modal_" + x).toString();
                                            return <Attribute tooltip_position="left" attributes={tier_1_attributes[attribute_key]} key={childkey} product={key} id={childkey} check_for_default="true" />
                                        }
                                    })}

                                    <div className="attributes attributes-title">Other important features:</div>
                                    {Object.keys(tier_2_attributes).map(function(attribute_key, x) {
                                        if(attribute_key) {
                                            var childkey = (key + "_modal_" + x).toString();
                                            return <Attribute tooltip_position="left" attributes={tier_2_attributes[attribute_key]} key={childkey} product={key} id={childkey} check_for_default="true" />
                                        }
                                    })}
                                </div>
                            </div>
                        </div>
                    </div>
                })}
                {drafted_product_element}
            </div>
        );

        return products;
    }
});
