'use strict'

var React = require('react');
var createReactClass = require('create-react-class');
var Currency = require('./Currency');
var AppConstants = require('../Constants');


module.exports = createReactClass({
    handleClick:function(e) {
        e.preventDefault();

        var code = this.props.url;
        if(this.props.url) {
            window.location.href = this.props.url;
        }

        if(this.props.type == 'checkout') {
            var addons = [];
            var quoted_product_index = this.props.product;

            $('input:checked').each(function(){
                addons.push($(this).data('code'));
            });
            var selected_product = {
                'addons': addons,
                'quoted_product_id': products_data[quoted_product_index].qp_id
            };

            $('.note.loader').show();

            $.post(AppConstants['buy_product_path'], selected_product, function(response) {
                if(response.status) {
                    setTimeout(function() {
                        window.location = AppConstants['order_summary'];
                    }, 2000);
                } else {
                    Utilities.Notify.error(response.error_message, 'Error!');
                }
            });
        }
    },
    render: function(){
        if(this.props.price !== undefined) {
            var button = (
                <button onClick={this.handleClick} className={"btn " + this.props.classname}>
                    <Currency /> <span className="odometer" data-price={this.props.elemid}>{this.props.price}</span> - {this.props.label}
                </button>
            );
        } else {
            var button = (<button data-tooltip={this.props.tooltip} onClick={this.handleClick} className={"btn " + this.props.classname}>{this.props.label}</button>);
        }
        return button;
    }
});
