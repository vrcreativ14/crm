'use strict'

var React = require('react');
var createReactClass = require('create-react-class');


module.exports = createReactClass({

  render: function(){
    var rows = [];
    var item_count = products_data.length;
    if(drafted_product)
      item_count += 1;
    for (var i=0; i < item_count; i++) {
      var classname = i==0?'active':''
      rows.push(<li className={classname} data-index={i}><span></span></li>);
    }
    
    return (
      <ul className="scroll-buttons">{rows}</ul>
    );
  }
});
