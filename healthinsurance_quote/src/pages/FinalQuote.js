import React, { useEffect, useState } from 'react'
import ActionButton from '../components/ActionButton'
import SelectedPolicy from '../components/SelectedPolicy'
import UploadDoc from '../components/Uploads'
import Layout from "../layout/Layout"
import Arrow from "../assets/arrow.svg"
import { useNavigate, useParams } from 'react-router-dom'
import { GetData } from '../helper/GetData'
import LoadingPage from './LoadingPage'
import InvalidPage from './InvalidPage'
import { Notifications } from '../components/Notifications'
import RequestHandler from '../helper/RequestHandler'

const FinalQuote = ({type = 1}) => {
    const[uploadDoc,setuploadDoc] = useState({})
    const{ id, secretCode, quoteID } = useParams()
    const[data,setData] = useState(false)
    const[loader,setLoader] = useState(false)
    const navigate = useNavigate()

    useEffect(() => {
        window.scrollTo(0, 0)
    }, [])

    const fetch = async () => {
        const res = await GetData('final_quote',navigate)
        if(res)setData(res)
    }

    if(!data){
        fetch()
        return <LoadingPage/>
    }
    if(data=='invalid')return <InvalidPage/>

    async function handleFormSubmit(event){
        event.preventDefault()
        const docsPrim = ['signed_final_quote','signed_final_quote_additional_document']
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
        })
        try{
            const { data: res } = await RequestHandler.post('health-insurance/quote-api/',rawData,{headers: { 'Content-Type': 'multipart/form-data'}})
            if(res.success){
                // rawData.append('email', data.primary_member.email)
                // RequestHandler.post('health-insurance/deals/'+id+'/email/final_quote_submitted/',rawData)
                Notifications('Success','Document was uploaded.','success')
                return navigate('/health-insurance-quote/'+secretCode+'/'+id+'/finalquote-thankyou/'+quoteID)
            }else{
                Notifications('Error','Something went wrong, pls contact us.','error')
            }
        }catch(e){
            Notifications('Error','Something went wrong, pls contact us.','error')
        }
        setLoader(false)
    }

    const name = 'Hi <span class="text-capitalize">'+data.primary_member.name+'</span>,'
    const currentTab = 'final'
	const stepContent = "Great news, we have received the final quote from the insurer! Please download and check the document. If you are happy, kindly sign it and upload it below."

    return(
        <Layout currentTab={currentTab} name={name} stepContent={stepContent}>
            <p className="fs-6 fw-light-bold mb-4">You have selected the below policy.</p>
            <form onSubmit={(event) => handleFormSubmit(event)}>
                <div className="row">
                    <div className="col-md-12">
                        <SelectedPolicy data={data} insurer={data.selected_plan} type="2"/>
                    </div>
                    <div className='col-md-6'>
                        <div className='row'>
                            <div className='col-md-12'>
                                <div className='d-flex'>
                                    <a href={('final_quote_document' in data) ? decodeURI(data.final_quote_document).replace(/&amp;/g, "&"):'#'} target="_blank" className="btn-nexus btn-golden btn-height d-quote text-white">Download Final Quote</a>
                                    <img className='ms-3' src={Arrow} />
                                </div>
                            </div>
                            <div className='col-md-12 mt-4'>
                                <div className='row'>
                                    <UploadDoc classCustom='mb-3 col-md-12' setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Upload Signed Quote" filekey="signed_final_quote" desc=''/>
                                </div>
                            </div>
                        </div>
                    </div>
                    {('final_quote_additional_document' in data) &&
                    <div className='col-md-6'>
                        <div className='row'>
                            <div className='col-md-12'>
                                <div className='d-flex'>
                                    <a href={('final_quote_document' in data) ? decodeURI(data.final_quote_additional_document).replace(/&amp;/g, "&"):'#'} target="_blank" className="btn-nexus btn-golden btn-height d-quote text-white">Download Additional Document</a>
                                    <img className='ms-3' src={Arrow} />
                                </div>
                            </div>
                            <div className='col-md-12 mt-4'>
                                <div className='row'>
                                    <UploadDoc classCustom='mb-3 col-md-12' setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Upload Signed Additional Document" filekey="signed_final_quote_additional_document" desc=''/>
                                </div>
                            </div>
                        </div>
                    </div>
                    }
                    <div className='col-md-12 mt-4'>
                        <ActionButton submit={true} url={'finalquote-thankyou/'} text={'Submit'} loader={loader}/>
                    </div>
                </div>
            </form>
        </Layout>
    )
}
export default FinalQuote