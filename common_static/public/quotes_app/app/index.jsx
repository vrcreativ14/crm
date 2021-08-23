'use strict'

import React from 'react';
import ReactDOM from 'react-dom';

import { Router, Route, hashHistory } from 'react-router';

import Quotes from './pages/Quotes';
import Comparison from './pages/Comparison';
import Checkout from './pages/Checkout';

var el = document.getElementById('app-container');

function renderDomElement(app, elem_id) {
    const elem = document.getElementById(elem_id);

    if(elem)
        ReactDOM.render(app, elem);
}

hashHistory.listen( location =>  {
	window.scroll(0, 0);
});

function logPageView() {
	if (typeof ga !== 'undefined' && window.location.hash.length > 2) {
		ga('set', 'page', window.location.pathname + window.location.hash);
		ga('send', 'pageview');
	}
}

ReactDOM.render((
  <Router history={hashHistory} onUpdate={logPageView}>
    <Route name="quotes" path="/" component={Quotes}/>
    <Route name="compairson" path="/comparison/:prod1/:prod2" component={Comparison}/>
    <Route name="checkout" path="/checkout/:id" component={Checkout}/>
  </Router>
), el);

renderDomElement(routing, 'app-container');
