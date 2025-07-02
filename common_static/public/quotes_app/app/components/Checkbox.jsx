'use strict'

var React = require('react');
var createReactClass = require('create-react-class');


module.exports = createReactClass({
  render: function(){
    return (
    	<div className="checkbox-container">
          <input type="checkbox" name={this.props.name} required="" id={this.props.id} value={this.props.value} />
          <label htmlFor={this.props.id}><span className="checkbox"></span> {this.props.label}</label>
        </div>
    );
  }
});
