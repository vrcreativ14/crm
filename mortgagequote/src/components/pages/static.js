import React, { useContext, useState, useEffect } from 'react'
import Layout from '../layout/Layout.js'
import { DataContext } from '../../helpers/context.js'
import Loading from '../layout/Loading.js'
import { getData } from '../../helpers/utils.js'
import { BrowserRouter as Router, useParams } from "react-router-dom"
import ContactInfo from '../layout/ContactInfo.js'
import ThankYou from '../layout/ThanksMessage.js'


const Static = () => {
	const[data,setData] = useContext(DataContext)
	const[loader,setLoader] = useState(true)
	const[name,setName] = useState(false)
	let { stageType } = useParams();
	const currentTab = stageType
	let stepContent = "Please wait your application is in process."
	if(currentTab=='mortgageIssued'){
		stepContent = "Thank you for your cooperation during the whole process."
	}
	useEffect(() => {
		if(data){
			setName(data.customer_info.name)
		}
	},[data])
	const fetch = () => {
		if(loader){
			getData(stageType)
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
			{(currentTab=='mortgageIssuedLost') ? <p className="fw-light-bold">This quote is closed.</p>:<ThankYou currentTab={currentTab}/>}
			<ContactInfo />
		</Layout>
	)
}

export default Static;