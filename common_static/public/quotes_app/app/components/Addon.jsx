'use strict'

var React = require('react');
var createReactClass = require('create-react-class');
var NumberFormat = require('react-number-format');

var Currency = require('./Currency');
import {updateItem} from '../utils/common.js';


module.exports = createReactClass({
  getInitialState() {
    return {disabled: this.props.disabled_checkbox}
  },
  onChange: function() {
    updateItem(this.props.product, this.props.attributes.code);
  },
  render: function(){

    var attributes = this.props.attributes;
    var addon_name = 'name_' + this.props.product + '_' + attributes.code;
    var addon_code = attributes.code;
    var classname = (attributes.tooltip)?"info":"";
    var tooltip_position = this.props.tooltip_position?this.props.tooltip_position:'';
    var default_addons = products_data[this.props.product]['default_addons'];
    var is_default_addon = false;
    $.each(default_addons, function(k, v){ 
      if(v == addon_code) {
        is_default_addon = true;
      }
    });

    var tooltip = "";
    var style = {
      height: 'auto'
    }

    if(attributes.tooltip) {
      tooltip = <span className={"info-tip help-icon " + tooltip_position} data-tooltip={attributes.tooltip}></span>
    }

    if(is_default_addon) {
      var addon = (
        <div style={style} className={"default-addon attributes sub-checkbox " + classname}>
          <div className="checkbox"></div>
          <label htmlFor={"id_" + addon_name}>
            {attributes.label} <span className="included">(Included)</span>
            {tooltip}
          </label>
        </div>
      );
    } else {
      var addon = (
        <div style={style} className={"attributes sub-checkbox " + classname}>
          <div>
            <div className="checkbox-section">
                <div className="checkbox-container">
                  <input onChange={this.onChange} data-code={attributes.code} data-checkbox={this.props.product + '_' + attributes.code} type="checkbox" name={addon_name} defaultChecked={attributes.selected} id={"id_" + addon_name} disabled={this.state.disabled} />
                  <label htmlFor={"id_" + addon_name}><span className="checkbox"></span>
                  {attributes.label} <span className="price">+ <Currency /> {attributes.value.formatMoney()}</span>
                  {tooltip}
                  </label>
                </div>
            </div>
          </div>
        </div>
      );
    }

    return addon;
  }
});
