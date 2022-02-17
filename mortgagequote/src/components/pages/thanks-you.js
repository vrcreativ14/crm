import React from 'react';
import Header from '../layout/Header';



const ThankYou = () => {
	return(
		<div id="document-upload" className="react-loaded">
			<Header />
			<Content />
		</div>
	)
}

export default ThankYou;

function Content(){
	return(
		<div className="sub-container">
			<div className="inner-small-container form-headings step-1">
				<h1 className="down-arrow">
						Thank you for uploading your documents!
						<p>Our customer success team has been notified and is now checking your documents to make sure that all of the information we have is correct.</p>
						<p>If all of the information is correct we will get in touch with you to collect payment and issue your policy. If there are things missing we’ll get in touch with you to let you know.</p>
						<div className="blue-line"></div>
				</h1>
				<h1>
						IMPORTANT:
						<p>Your order is still in process and your new insurance is NOT active yet. Your car will only be insured when your new policy has been issued and sent to you by email.</p>
						<p>&nbsp;</p>
				</h1>
			</div>
		</div>
	)
}