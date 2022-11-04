import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import ActionButton from '../components/ActionButton'
import DocumentSection from '../components/DocumentSection'
import UploadDoc from '../components/Uploads'
import { GetData } from '../helper/GetData'
import RequestHandler from '../helper/RequestHandler'
import Layout from '../layout/Layout'
import InvalidPage from './InvalidPage'
import LoadingPage from './LoadingPage'
import { Notifications } from '../components/Notifications'

const Documents = () => {
    const[uploadDoc,setuploadDoc] = useState({})
    const{ id, secretCode, quoteID } = useParams()
    const[data,setData] = useState(false)
    const[loader,setLoader] = useState(false)
    const navigate = useNavigate()

    useEffect(() => {
        window.scrollTo(0, 0)
    }, [])

    const fetch = async () => {
        const res = await GetData('documents',navigate)
        if(res)setData(res)
    }

    if(!data){
        fetch()
        return <LoadingPage/>
    }
    if(data=='invalid')return <InvalidPage/>

    async function handleFormSubmit(event){
        event.preventDefault()
        const docsPrim = ['primary_passport','primary_emiratesid','primary_visa','primary_maf','primary_previousinsurance','primary_other','plan_census','plan_bor']
        // const docsPrimNames = {
        //     'primary_passport':'Primary member Passport',
        //     'primary_emiratesid':'Primary member Emirates ID',
        //     'primary_visa':'Primary member Visa',
        //     'primary_maf':'Primary member MAF',
        //     'plan_census':'Primary member Census',
        //     'plan_bor':'Primary member Bor'
        // }
        
        const docMemb = ['member_passport_','member_emiratesid_','member_visa_','member_other_']
        // const docMembName = {
        //     'member_passport_':'Dependent Member Passport',
        //     'member_emiratesid_':'Dependent Member Emirates ID',
        //     'member_visa_':'Dependent Member Visa'
        // }
        setLoader(true)
        var rawData = new FormData()
        console.log(uploadDoc)
        rawData.append('pk', id)
        docsPrim.map((docIndex) => {
            if(docIndex in uploadDoc){
                uploadDoc[docIndex].map((doc) => {
                    rawData.append(docIndex, doc)
                })
            }
            // else{
            //     Notifications('Error!',docsPrimNames[docIndex]+' documents is required.','danger')
            // }
        })
        {data.additional_members.length>0 && data.additional_members.map((member,index) => {
            docMemb.map((docIndex,index) => {
                if(docIndex+''+member.id in uploadDoc){
                    uploadDoc[docIndex+''+member.id].map((doc) => {
                        rawData.append(docIndex+''+member.id, doc)
                    })
                }
                // else{
                //     Notifications('Error!',docMembName[docIndex]+' documents is required.','danger')
                // }
            })
        })}
        const { data: res } = await RequestHandler.post('health-insurance/quote-api/',rawData,{headers: { 'Content-Type': 'multipart/form-data'}})
        setLoader(false)
        if(res.success){
            // rawData.append('email', data.primary_member.email)
            // RequestHandler.post('health-insurance/deals/'+id+'/email/order_confirmation/',rawData)
            Notifications('Success','Documents was uploaded.','success')
            return navigate('/health-insurance-quote/'+secretCode+'/'+id+'/policy-thankyou/'+quoteID)
        }else{
            Notifications('Error','Something went wrong, pls contact us.','error')
        }
    }

    function validateDocUpload(){
        const docsPrim = ['primary_passport','primary_emiratesid','primary_visa','primary_maf','primary_previousinsurance','primary_other','plan_census','plan_bor']
        const docsPrimNames = {
            'primary_passport':'Primary member Passport documents',
            'primary_emiratesid':'Primary member Emirates ID documents',
            'primary_visa':'Primary member Visa documents',
            'primary_maf':'Plan document MAF',
            'plan_census':'Plan document Census',
            'plan_bor':'Plan document Bor'
        }
        
        const docMemb = ['member_passport_','member_emiratesid_','member_visa_','member_other_']
        const docMembName = {
            'member_passport_':'Dependent Member Passport',
            'member_emiratesid_':'Dependent Member Emirates ID',
            'member_visa_':'Dependent Member Visa'
        }
        let findError = false
        docsPrim.map((docIndex) => {
            if(!data.selected_plan.census && docIndex=='plan_census')return
            if(!data.selected_plan.bor && docIndex=='plan_bor')return

            if(!findError && docIndex in docsPrimNames && !(docIndex in uploadDoc)){
                Notifications('Error',docsPrimNames[docIndex]+' is required.','danger')
                findError = true
            }
        })
        {data.additional_members.length>0 && data.additional_members.map((member,index) => {
            docMemb.map((docIndex,index) => {
                if(!findError && docIndex in docMembName && !(docIndex+''+member.id in uploadDoc)){
                    Notifications('Error',docMembName[docIndex]+' documents is required.','danger')
                    findError = true
                }
            })
        })}
    }

    const name = "Thank you for selecting your medical cover, you're almost done!"
    const currentTab = 'policy'
	const stepContent = "You're a few steps away from having your policy issued, we just need to do a quick review of your documents to ensure that all our information is correct. We will then get in touch with you with the final quote from the insurer and proceed to issue your policy."

    const selectedPlan = data.quoted_plans.filter((plan) => plan.id==data.selected_plan.id)

    return(
        <Layout currentTab={currentTab} name={name} stepContent={stepContent}>
            <p className="fs-6 fw-light-bold mb-4">Please upload the documents mentioned below for all members:</p>
            <form onSubmit={(event) => handleFormSubmit(event)} action="" method="post">
                <div className="row">
                    <div className='col-md-12'>
                        <DocumentSection title="Primary Member Documents" defaultTab={true}>
                            <UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Passport" filekey="primary_passport" desc=''/>
                            <UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Emirates ID (both sides)" filekey="primary_emiratesid" desc=''/>
                            <UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Visa" filekey="primary_visa" desc=''/>
                            <UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Previous Medical Insurance (Card / Certificate)" filekey="primary_previousinsurance" desc='If any' required={false}/>
                            <UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Other Documents" filekey="primary_other" desc='If any' required={false}/>
                        </DocumentSection>
                        <DocumentSection title="Plan Documents" defaultTab={true}>
                            <UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Medical Application Form" filekey="primary_maf" info="Please download the Medical Application Form (MAF) using the link below. Kindly sign it, then upload the signed copy of the form." desc={'<p className="font-size-bigger-upload"><a target="_blank" className="text-fade-grey" href="'+decodeURI(selectedPlan[0].maf).replace(/&amp;/g, "&")+'">Download MAF <i className="fas fa-arrow-circle-down"></i></a></p>'}/>
                            {(data.selected_plan.census) &&  <UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Census" filekey="plan_census" desc={'<p className="font-size-bigger-upload"><a target="_blank" className="text-fade-grey" href="'+decodeURI(data.selected_plan.census).replace(/&amp;/g, "&")+'">Download Census <i className="fas fa-arrow-circle-down"></i></a></p>'}/>}
                            {(data.selected_plan.bor) &&  <UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Bor" filekey="plan_bor" desc={'<p className="font-size-bigger-upload"><a target="_blank" className="text-fade-grey" href="'+decodeURI(data.selected_plan.bor).replace(/&amp;/g, "&")+'">Download Bor <i className="fas fa-arrow-circle-down"></i></a></p>'}/>}
                        </DocumentSection>
                        {data.additional_members.length>0 && data.additional_members.map((member,index) => {
                            return(
                                <DocumentSection key={'members-documents-'+index} title={"Dependent: <b class='text-capitalize'>"+member.name+"</b> (<small>"+member.relation+"</small>)"} defaultTab={true}>
                                    <UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Passport" filekey={"member_passport_"+member.id} desc=''/>
                                    <UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Emirates ID (both sides)" filekey={"member_emiratesid_"+member.id} desc=''/>
                                    <UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Visa" filekey={"member_visa_"+member.id} desc=''/>
                                    <UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Other Documents" filekey={"member_other_"+member.id} desc='If any' required={false}/>
                                </DocumentSection>
                            )
                        })}
                    </div>
                </div>
                {/* <ActionButton submit={true} customClass="ms-2" url={'policy-thankyou/'+quoteID} text={'Submit'}/> */}
                <button type={(!loader) ? "submit":"button"} class="btn-nexus btn-golden ms-2" onClick={() => validateDocUpload()}>Submit{loader ? <i className="ms-1 fas fa-circle-notch fa-spin"></i>:''}</button>
            </form>
        </Layout>
    )
}

export default Documents