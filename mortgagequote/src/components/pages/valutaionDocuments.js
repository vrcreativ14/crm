import React, { useContext, useEffect, useState } from 'react'
import Layout from '../layout/Layout.js'
import { getData } from '../../helpers/utils.js'
import { DataContext } from '../../helpers/context.js'
import Loading from '../layout/Loading.js'
import { BrowserRouter as Router, useParams, useHistory } from "react-router-dom"
import SelectButton from '../layout/Button.js'
import UploadDoc from '../layout/Uploads.js'
import ThankYou from '../layout/ThanksMessage.js'
import ContactInfo from '../layout/ContactInfo.js'


const ValuationDocuments = () => {
	const[data, setData, uploadDoc, setuploadDoc] = useContext(DataContext)
	const[loader,setLoader] = useState(true)
	const[name,setName] = useState(false)
	let { id, secretCode, quoteID } = useParams();
	const navigate = useHistory()
	const currentTab = 'valuation'
    const stepContent = (data && data.sub_stage.sub_stage=='Waiting for Valuation Documents') ? "Please submit the below documents for valuation.":"";
	useEffect(() => {
		if(data){
			setName(data.customer_info.name)
			setuploadDoc({})
		}
	},[data])
	const fetch = () => {
		if(loader){
			getData(currentTab)
			setLoader(false)
		}
	}
	fetch()
	if(!data){
		return(
			<Loading name={name} stepContent={stepContent} currentTab={currentTab} loader={loader}/>
		)
	}
	
	data.quote_details.map((bank,index) => {
		if(bank.bank_pk == parseInt(quoteID)){
			quoteID = index
		}
	})

	console.log(quoteID)

	return(
		<Layout currentTab={currentTab} name={name} stepContent={stepContent}>
			{(data.sub_stage.sub_stage=='Waiting for Valuation Documents') ?
			<>
            <p className="fw-light-bold mb-4">Please submit the below documents for valuation:</p>
			<div className="row align-items-center">

			<UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Memorandum of Understanding" filekey="memorandum-of-understanding" desc=""/>
			<UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Seller's Emirates ID Back" filekey="sellers-emirates-id-back" desc="If any" required={false}/>
			<UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Property title deed" filekey="property-title-deed" desc=""/>
			<UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Seller's Emirates ID Front" filekey="sellers-emirates-id-front" desc="If any" required={false}/>
			<UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Seller's Passport" filekey="sellers-passport" desc="If any" required={false}/>
			<UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Seller's Visa" filekey="sellers-visa" desc="If any" required={false}/>

			</div>
			<div className="mt-5 mb-5">	
				<button className="me-3 btn-nexus btn-grey d-none" onClick={() => navigate.push('/mortgage-quote/'+secretCode+'/'+id+'/preApproval/'+quoteID)}>Go Back</button>	
                <SelectButton text="Submit" url="underProcess" indexID="underProcess"/>
            </div>
			</>
			:
			<>
			<ThankYou />
			<ContactInfo />
			</>}
        </Layout>
	)
}

export default ValuationDocuments;