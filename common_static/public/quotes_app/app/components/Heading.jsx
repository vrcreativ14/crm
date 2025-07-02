'use strict'

var React = require('react');
var createReactClass = require('create-react-class');


module.exports = createReactClass({
  render: function(){
    return (
    	<span>
        	<h1 className="name">Hi {user_data.name}!</h1>
        	<div className="message">We've crunched the data and here are the perfect car insurance quotes for you.</div>
        </span>
    );
  }
});
