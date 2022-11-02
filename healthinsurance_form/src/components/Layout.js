import React from 'react';
import Form from './Form';
import Header from './Header';


const Layout = ({children}) => {
	return(
		<main>
			<Header />
			<div className="container"><Form/></div>
		</main>
	)
}

export default Layout;