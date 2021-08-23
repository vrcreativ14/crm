var React = require("react");
var Quotes = require('./pages/Quotes');
var Comparison = require('./pages/Comparison');
var Checkout = require('./pages/Checkout');

import { Router, Route, hashHistory } from 'react-router';

var routes = (
        <Router history={hashHistory}>
            <Route path="/" component={Quotes}/>
            <Route path="/comparison" component={Comparison}/>
            <Route path="/checkout" component={Checkout}/>
        </Router>
    );

module.export = routes;
