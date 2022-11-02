import React from 'react'
import { render } from 'react-dom'
import Layout from './Layout'
import "react-datepicker/dist/react-datepicker.css"
import { ReactNotifications } from 'react-notifications-component'
import 'react-notifications-component/dist/theme.css'
import { createRoot } from "react-dom/client";
import { BrowserRouter as Router, Route, Routes} from 'react-router-dom'

const App = () => {
	return (
		<>
			<ReactNotifications />
			<Router>
				<Routes>
					<Route exact path="/health-insurance-form/get-quotes/start/:string/" element={<Layout/>} />
					<Route exact path="/health-insurance-form/get-quotes/start/:string/:id" element={<Layout/>} />
					<Route exact path="/health-insurance-form/get-quotes/start/:string/:id/:deal_id" element={<Layout/>} />
				</Routes>
			</Router>
		</>
	)
}

export default App

const container = document.getElementById("app")
const root = createRoot(container)
root.render(<App />)