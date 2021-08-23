'use strict'

var React = require('react');
var createReactClass = require('create-react-class');


module.exports = createReactClass({
  render: function(){
  	return (<div>
  		<h2 className="trustpilot-heading">Loved and trusted by our customers</h2>
		<iframe className="trustpilot-iframe" frameborder="0" scrolling="no" title="Customer reviews powered by Trustpilot" src="https://widget.trustpilot.com/trustboxes/5419b6ffb0d04a076446a9af/index.html?locale=en-GB&templateId=5419b6ffb0d04a076446a9af&businessunitId=596dbc5a0000ff0005a6e601&styleHeight=20px&styleWidth=100%25&theme=light"></iframe>
	</div>);
  }
});
