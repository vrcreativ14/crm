import React from 'react'
import { render } from 'react-dom'
import { BrowserRouter as Router, Route, Switch} from 'react-router-dom'
import { DataProvider } from '../helpers/context.js'

import Comparison from './pages/comparison.js'
import Order from './pages/order.js'
import Documents from './pages/documents.js'
import ValuationDocuments from './pages/valutaionDocuments.js'
import Static from './pages/static.js'
import ThankYou from './pages/thanks-you.js'

import ReactNotification from 'react-notifications-component'
import 'react-dropzone-uploader/dist/styles.css'
import 'react-notifications-component/dist/theme.css'

const App = () => {
	return (
		<>	
		<DataProvider>
			<ReactNotification />
			<Router>
				<Switch>
					<Route exact path="/mortgage-quote/:secretCode/:id/" component={Comparison} />
					<Route exact path="/mortgage-quote/:secretCode/:id/mortgageSummary/:quoteID" component={Order}></Route>
					<Route exact path="/mortgage-quote/:secretCode/:id/preApproval/:quoteID/" component={Documents}></Route>
					<Route exact path="/mortgage-quote/:secretCode/:id/valuation/:quoteID/" component={ValuationDocuments}></Route>
					<Route exact path="/mortgage-quote/:secretCode/:id/underProcess/:stageType/:quoteID/" component={Static}></Route>
					<Route exact path="/mortgage-quote/:secretCode/:id/mortgageIssued/:stageType/:quoteID/" component={Static}></Route>
				</Switch>
			</Router>
		</DataProvider>
		</>
	)
}

export default App;

const container = document.getElementById("app");
render(<App />, container);