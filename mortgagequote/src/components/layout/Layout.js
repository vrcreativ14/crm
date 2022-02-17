import React from 'react';
import Breadcrumb from '../layout/Breadcrumb';
import Header from '../layout/Header';
import ContentHeader from '../layout/ContentHeader';


const Layout = ({children,currentTab,name,stepContent}) => {
	return(
		<>
		<Header />
		<main>
			<Breadcrumb current={currentTab}/>
			<div className="content w-100">
                <ContentHeader name={name} stepContent={stepContent}/>
                <div className="container-fluid ms-md-2 pe-md-5">
                    {children}
                </div>
			</div>
		</main>
		</>
	)
}

export default Layout;