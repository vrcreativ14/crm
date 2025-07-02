import React from 'react';
import Breadcrumb from './Breadcrumb';
import Header from './Header';
import ContentHeader from './ContentHeader';
import BGImage from '../assets/bg-img.svg'
import Message from '../assets/Message.svg'
import ContactForm from '../components/ContactForm';

const Layout = ({children,currentTab,name,stepContent,comparison = false}) => {
	return(
		<>
		<Header />
		<main>
			{currentTab!='quoteBasic' && <Breadcrumb current={currentTab}/>}
			<div className="content w-100">
                <ContentHeader name={name} stepContent={stepContent}/>
                <div className={currentTab!='quoteBasic' ? "container-fluid ms-md-2 pe-md-5":"container-fluid ms-md-2 pe-md-4"}>
                    {children}
                </div>
				<div className='background-image'>
					<div className='overlay-bg'>
						<img src={BGImage}/>
					</div>
				</div>
			</div>
			<div className={comparison ? 'message active':'message active'}>
				<a href="tel:97142378294"><img src={Message}/></a>
				{/* <a href="tel:97142378294" data-toggle="modal" data-target="#exampleModal"><img src={Message}/></a> */}
			</div>
			<ContactForm />
		</main>
		</>
	)
}

export default Layout;