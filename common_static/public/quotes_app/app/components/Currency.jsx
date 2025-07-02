'use strict'

var React = require('react');
var createReactClass = require('create-react-class');

var AppConstants = require('../Constants');


module.exports = createReactClass({
  render: function(){
    return (
    	<currency>{AppConstants['currency']}</currency>
    );
  }
});
