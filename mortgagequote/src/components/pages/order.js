import React, { useContext, useEffect, useState } from 'react'
import Layout from '../layout/Layout.js'
import { getData, CurrencyFormat } from '../../helpers/utils.js'
import { DataContext } from '../../helpers/context.js'
import Loading from '../layout/Loading.js'
import SelectButton from '../layout/Button.js'
import { BrowserRouter as Router, useParams, useHistory } from "react-router-dom"
import PropertyPrice from '../layout/PropertyPrice.js'
import Banks from '../layout/Banks.js'



const Order = () => {
	const[data,setData, uploadDoc, setuploadDoc] = useContext(DataContext)
	const[loader,setLoader] = useState(true)
	const[name,setName] = useState(false)
	const navigate = useHistory()
	let { id, secretCode, quoteID } = useParams();
	const currentTab = 'mortageSummary'
	const stepContent = "Here's your mortgage summary."
	useEffect(() => {
		if(data){
			setName(data.customer_info.name)
			setuploadDoc(prevState => ({...prevState,name:data.customer_info.name}))
			setuploadDoc(prevState => ({...prevState,email:data.customer_info.email}))
			setuploadDoc(prevState => ({...prevState,phone:data.customer_info.phone}))
		}
	},[data])
	const fetch = () => {
		if(loader){
			getData('order')
			setLoader(false)
		}
	}
	fetch()
	if(!data){
		return(
			<Loading name={name} stepContent={stepContent} currentTab={currentTab} loader={loader}/>
		)
	}

	return(
		<Layout currentTab={currentTab} name={name} stepContent={stepContent}>
			<p className="fw-light-bold mb-4">Pricing based on the following information:</p>
			<div className="row">
				<div className="col-md-12 col-xl-12">
					<Banks data={data} bank={data.quote_details[quoteID]}/>
				</div>
				<div className="col-md-5 col-xl-4">
					<div className="property-price user-info shadow-1">
						<h5 className="tab-title">Your Details</h5>
						<div>
							<span>Name</span>
							<span><input autoComplete="new-password" className="form-control shadow-3" type="text" value={('name' in uploadDoc) ? uploadDoc.name:''} onChange={(e) => setuploadDoc(prevState => ({...prevState,name:e.target.value}))}/></span>
						</div>
						<div>
							<span>Email</span>
							<span><input autoComplete="new-password" className="form-control shadow-3" type="email" value={('email' in uploadDoc) ? uploadDoc.email:''} onChange={(e) => setuploadDoc(prevState => ({...prevState,email:e.target.value}))} /></span>
						</div>
						<div>
							<span>Phone</span>
							<span><input autoComplete="new-password" className="form-control shadow-3" type="text" value={('phone' in uploadDoc) ? uploadDoc.phone:''} onChange={(e) => setuploadDoc(prevState => ({...prevState,phone:e.target.value}))} /></span>
						</div>							
					</div>
				</div>
			</div>
			<div className="mt-5">
				<button className="me-3 btn-nexus btn-grey" onClick={() => navigate.push('/mortgage-quote/'+secretCode+'/'+id)}>Go Back</button>	
				<SelectButton text="Next Step" url="preApproval" indexID={data.quote_details[quoteID].bank_pk}/>	
			</div>
		</Layout>
	)
}

export default Order;