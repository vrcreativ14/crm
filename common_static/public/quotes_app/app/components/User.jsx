'use strict'

var React = require('react');
var createReactClass = require('create-react-class');
var NumberFormat = require('react-number-format');
var Currency = require('./Currency');


module.exports = createReactClass({
  toggleClass: function() {
    	$('.user-info').toggleClass('user-info-mobile-toggle');
  },
  render: function(){
    return (
    	<div>
	        <div className="row m-0">
	            <div className="col-5 label">Reference Number:</div>
	            <div className="col-7 download-pdf">
	            	<a className="info-tip felix-tooltip-bottom" data-tooltip="Click to download a PDF version of this quote." href={user_data.pdf_download_url} target="_blank">{user_data.ref_number}-{user_data.quote_pk} (Download PDF)</a>
	            </div>
	        </div>

	        <div className="row m-0">
	            <div className="col-5 label">Vehicle:</div>
	            <div className="col-7" title={user_data.vehicle}> {user_data.vehicle}</div>
	        </div>

	        <div className="row m-0 toggle">
	            <div className="col-5 label">Email:</div>
	            <div className="col-7">{user_data.email}</div>
	        </div>

	        <div className="row m-0 toggle">
	            <div className="col-5 label">Phone:</div>
	            <div className="col-7">{user_data.phone}</div>
	        </div>

	        <div className="row m-0 toggle">
	            <div className="col-5 label">Age:</div>
	            <div className="col-7">{user_data.age}</div>
	        </div>

	        <div className="row m-0 toggle">
	            <div className="col-5 label">Nationality:</div>
	            <div className="col-7">{user_data.nationality}</div>
	        </div>

	        <div className="show-more">
	            <div className="show" onClick={this.toggleClass}>
                    <img width="10" src={dropdown_arrow_icon} /> Show More
                </div>
                <div className="hide" onClick={this.toggleClass}>
                    <img width="10" src={dropdown_arrow_icon} /> Collapse
                </div>
	        </div>
	    </div>
    );
  }
});
