'use strict'

var React = require('react');
var createReactClass = require('create-react-class');


module.exports = createReactClass({
  render: function(){
    var tooltip = "";
    var included = "";
    var classname = "";
    var style = {
      height: 'auto'
    }

    var attributes = this.props.attributes;

    if(this.props.check_for_default !== undefined) {
      var addon_code = attributes.code;
      var default_addons = products_data[this.props.product]['default_addons'];
      var is_default_addon = false;
      $.each(default_addons, function(k, v){ 
        if(v == addon_code) {
          is_default_addon = true;
        }
      });

      if(is_default_addon) {
        included = <span className="included">(Included)</span>
      }
    }

    var tooltip_position = this.props.tooltip_position?this.props.tooltip_position:'';

    if (attributes.tooltip){
      tooltip = <span className={"info-tip help-icon " + tooltip_position} data-tooltip={attributes.tooltip}></span>
      classname = "info";
    }

    return (
      <div style={style} className={"attributes " + classname}>
        <span dangerouslySetInnerHTML={{ __html: attributes.label }} />
        {included}
        {tooltip}
      </div>
    );
  }
});
