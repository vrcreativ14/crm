'use strict'

var React = require('react');
var createReactClass = require('create-react-class');
var AppConstants = require('../Constants');


module.exports = createReactClass({
  openMainPage: function() {
    window.location.href = AppConstants['app_path'];
  },
  render: function(){
    return (
    	<div className="steps clearfix">
            <ul role="tablist">
                <li role="tab" aria-disabled="false" className={"first " + (this.props.current == 'policy'?'current':'') + ' ' + (this.props.current == 'checkout'?'completed':'')}>
                    <a href="javascript:" onClick={this.openMainPage}><span className="desc"><div className="label">Choose Policy</div></span></a>
                </li>
                <li role="tab" aria-disabled="false" className={(this.props.current == 'checkout'?'current':'')}>
                    <span className="desc"><div className="label">Choose Add-Ons</div></span>
                </li>
                <li role="tab" aria-disabled="false" className="">
                    <span className="desc"><div className="label">Order Summary</div></span>
                </li>
                <li role="tab" aria-disabled="false" className="">
                    <span className="desc">
                        <div className="label">Upload Documents 
                            <span className="info-tip felix-tooltip-bottom" data-tooltip="You don't need to complete this step immediately, you have 5 days to do so."></span>
                        </div>
                    </span>
                </li>
                <li role="tab" aria-disabled="false" className="last">
                    <span className="desc"><div className="label">Policy Issued!</div></span>
                </li>
            </ul>
        </div>
    );
  }
});
