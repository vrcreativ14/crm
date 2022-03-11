import React, { useContext, useEffect, useState } from 'react'
import Layout from '../layout/Layout.js'
import { getData } from '../../helpers/utils.js'
import { DataContext } from '../../helpers/context.js'
import Loading from '../layout/Loading.js'
import { BrowserRouter as Router, useParams, useHistory } from "react-router-dom"
import SelectButton from '../layout/Button.js'
import Attached from '../../assets/lorem-ipsum.pdf'
import UploadDoc from '../layout/Uploads.js'
import ThankYou from '../layout/ThanksMessage.js'
import ContactInfo from '../layout/ContactInfo.js'


const Documents = () => {
	const[data, setData, uploadDoc, setuploadDoc] = useContext(DataContext)
	const[loader,setLoader] = useState(true)
	const[name,setName] = useState(false)
	let { id, secretCode, quoteID } = useParams();
	const navigate = useHistory()
	const currentTab = 'preApproval'
    const stepContent = (data && data.sub_stage.sub_stage=='Waiting for Pre Approval Documments') ? "Please submit the below documents for pre approval.":"";

	useEffect(() => {
		if(data){
			setName(data.customer_info.name)
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
	let bankForm = false
	data.quote_details.map((bank,index) => {
		if(bank.bank_pk == parseInt(quoteID)){
			quoteID = index
			bankForm = bank.sample_form
		}
	})
	return(
		<Layout currentTab={currentTab} name={name} stepContent={stepContent}>
			{(data.sub_stage.sub_stage=='Waiting for Pre Approval Documments') ?
			<>
            <p className="fw-light-bold mb-4">Please submit the below documents for pre approval:</p>
			<div className="row align-items-center">

				<UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Bank Application Form" filekey="bank-application-form" desc={(bankForm) ? '<p className="font-size-bigger-upload">Download Sample Form <a target="_blank" className="text-fade-grey" href="'+bankForm+'"><i className="fas fa-arrow-circle-down"></i></a></p>':null}/>
				<UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Passport" filekey="passport" desc=""/>
				<UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Salary Certificate" filekey="salary-certificate" desc="Addressed to the chosen bank"/>
				<UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Visa" filekey="visa" desc=""/>
				<UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Bank Statement" filekey="bank-statement" desc="Last 6 months bank statement (a/c of the salary credit)"/>
				<UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Emirates ID Front" filekey="emirates-id-front" desc=""/>
				<UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Payslips" filekey="payslips" desc="Last 6 salaries payslip (only in case the salary has variance month to month)"/>
				<UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Emirates ID Back" filekey="emirates-id-back" desc=""/>

			</div>
			<div className="mt-5 mb-5">
				<button className="me-3 btn-nexus btn-grey d-none" onClick={() => navigate.push('/mortgage-quote/'+secretCode+'/'+id+'/mortgageSummary/'+quoteID)}>Go Back</button>	
				<SelectButton text="Submit" url="valuation" indexID={quoteID}/>	
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

export default Documents;