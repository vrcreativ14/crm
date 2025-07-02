import React from 'react'
import { createRoot } from "react-dom/client";
import { BrowserRouter as Router, Route, Routes} from 'react-router-dom'
import { ReactNotifications } from 'react-notifications-component'
import 'react-notifications-component/dist/theme.css'

import Quote from '../pages/Quote'
import QuoteBasic from '../pages/QuoteBasic'
import Summary from '../pages/Summary';
import Documents from '../pages/Documents';
import ThankyouPage from '../pages/ThankyouPage';
import FinalQuote from '../pages/FinalQuote';
import Payments from '../pages/Payments';
import Policy from '../pages/Policy';
import InvalidPage from '../pages/InvalidPage';
import ExpiredPage from '../pages/ExpiryPolicy';

const App = () => {
	
	return (
		<>
			<ReactNotifications />
			<Router>
				<Routes>
					<Route exact path="/health-insurance-quote/404/" element={<InvalidPage/>} />
					<Route exact path="/health-insurance-quote/expired/" element={<ExpiredPage/>} />
					<Route exact path="/health-insurance-quote/:secretCode/:id/" element={<Quote/>} />
					<Route exact path="/health-insurance-quote/:secretCode/:id/basic-quote" element={<QuoteBasic/>} />
					<Route exact path="/health-insurance-quote/:secretCode/:id/summary/:quoteID" element={<Summary/>} />
					<Route exact path="/health-insurance-quote/:secretCode/:id/policy-documents/:quoteID/" element={<Documents/>}/>
					<Route exact path="/health-insurance-quote/:secretCode/:id/policy-thankyou/:quoteID/" element={<ThankyouPage type="1"/>}/>
					<Route exact path="/health-insurance-quote/:secretCode/:id/final-quote/:quoteID/" element={<FinalQuote/>}/>
					<Route exact path="/health-insurance-quote/:secretCode/:id/finalquote-thankyou/:quoteID/" element={<ThankyouPage type="2"/>}/>
					<Route exact path="/health-insurance-quote/:secretCode/:id/payment/:quoteID/" element={<Payments/>}/>
					<Route exact path="/health-insurance-quote/:secretCode/:id/payment-thankyou/:quoteID/" element={<ThankyouPage type="3"/>}/>
					<Route exact path="/health-insurance-quote/:secretCode/:id/policy-issued/:quoteID/" element={<Policy/>}/>
					{/* <Route exact path="/health-insurance-quote/:secretCode/:id/payment/:stageType/:quoteID/" component={Static}></Route> */}
					{/* <Route exact path="/health-insurance-quote/:secretCode/:id/issued/:stageType/:quoteID/" component={Static}></Route> */}
				</Routes>
			</Router>
		</>
	)
}

export default App

const container = document.getElementById("app")
const root = createRoot(container)
root.render(<App />)