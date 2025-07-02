import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import ActionButton from '../components/ActionButton'
import { Notifications } from '../components/Notifications'
import UploadDoc from '../components/Uploads'
import { GetData } from '../helper/GetData'
import RequestHandler from '../helper/RequestHandler'
import { CurrencyFormat } from '../helper/Utils'
import Layout from '../layout/Layout'
import InvalidPage from './InvalidPage'
import LoadingPage from './LoadingPage'

const Payments = () => {
    const[uploadDoc,setuploadDoc] = useState({})
    const{ id, secretCode, quoteID } = useParams()
    const[data,setData] = useState(false)
    const[loader,setLoader] = useState(false)
    const navigate = useNavigate()

    useEffect(() => {
        window.scrollTo(0, 0)
    }, [])

    const fetch = async () => {
        const res = await GetData('payment',navigate)
        if(res)setData(res)
    }

    if(!data){
        fetch()
        return <LoadingPage/>
    }
    if(data=='invalid')return <InvalidPage/>

    async function handleFormSubmit(event){
        event.preventDefault()
        const docsPrim = ['payment_proof']
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
                // RequestHandler.post('health-insurance/deals/'+id+'/email/payment_confirmation/',rawData)
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
    const currentTab = 'payment'
	const stepContent = "We are now on the final step before issuing your new health insurance policy!"
    return(
        <Layout currentTab={currentTab} name={name} stepContent={stepContent}>
            <form onSubmit={(event) => handleFormSubmit(event)}>
                <div className='row'>
                    <div className='col-md-8'>
                        <p className="fs-6 fw-light-bold">You would have received an email from us with details on how to make the payment for your policy.</p>
                        <p className="fs-6 fw-light-bold mb-4">Once the payment has been made, please share a payment proof copy by uploading it below.</p>
                    </div>
                    <div className='col-md-3'>
                        <div className='shadow-1-strong p-3 fw-bold bg-white'>
                            <p className='text-golden border-bottom-custom'>Premium</p>
                            <div className='d-flex'>
                                <span className='text-start w-100'>Final Premium</span>
                                <span className='text-end w-100'>{CurrencyFormat(data.deal.total_premium,true,data.deal.currency)}</span>
                            </div>
                        </div>
                    </div>
                    <div className='col-md-9 mt-4'>
                        <div className='row'>
                            {/* <UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Proof of Payment" filekey="payment_proof" desc='If any' required={false}/> */}
                            <UploadDoc setuploadDoc={setuploadDoc} uploadDoc={uploadDoc} name="Proof of Payment" filekey="payment_proof" desc='' required={false}/>
                        </div>
                    </div>
                    <div className='col-md-9'>
                        <label className='d-flex fs-6 align-items-center mt-2'>
                            <input required={true} name="payment_proof" className="me-2" type="checkbox" value="1"/>
                            <span>I confirm that the payment has been made.<span className='text-danger'>*</span></span>
                        </label>
                    </div>
                    <div className='col-md-12 mt-4'>
                        <ActionButton submit={true} url={'payment-thankyou/1'} text={'Submit'} loader={loader}/>
                    </div>
                </div>
            </form>
        </Layout>
    )
}

export default Payments