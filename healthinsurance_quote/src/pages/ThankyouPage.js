import React, { useEffect, useState } from 'react'
import Layout from "../layout/Layout"
import ThankyouImage from "../assets/thankyouimage.svg"
import ActionButton from '../components/ActionButton'
import { useNavigate } from 'react-router-dom'
import { GetData } from '../helper/GetData'
import LoadingPage from './LoadingPage'
import InvalidPage from './InvalidPage'

const ThankyouPage = ({type = 1}) => {
    const[data,setData] = useState(false)
    const navigate = useNavigate()

    useEffect(() => {
        window.scrollTo(0, 0)
    }, [])

    const fetch = async () => {
        switch(type){
            case '1':
                const res1 = await GetData('documents_thankyou',navigate)
                if(res1)setData(res1)
                break;

            case '2':
                const res2 = await GetData('final_quote_thankyou',navigate)
                if(res2)setData(res2)
                break;

            case '3':
                const res3 = await GetData('payment_thankyou',navigate)
                if(res3)setData(res3)
                break;
        }
    }

    if(!data){
        fetch()
        return <LoadingPage/>
    }
    if(data=='invalid')return <InvalidPage/>

    const name = "Thank you for selecting your medical cover, you're almost done!"
    const currentTab = (type == 1) ? 'policy':(type == 2) ? 'final':'payment'
	const stepContent = "You're a few steps away from having your policy issued, we just need to do a quick review of your documents to ensure that all our information is correct. We will then get in touch with you with the final quote from the insurer and proceed to issue your policy."

    return(
        <div className='thankyou-parent-div'>
            <Layout currentTab={currentTab} name={name} stepContent={stepContent}>
                <div className="thankyou-page-div">
                    <div className='mb-4'><img src={ThankyouImage} alt="please wait"/></div>
                    {(type == 1) && <><h4 className='mb-3'>Thank you for uploading your documents!</h4>
                    <p className="text-fade-grey fs-6">Our customer success team has been notified and is now checking your documents to make sure that all of the information we have is correct.
                    <br/>
                    <span className='mt-2 mt-md-3 d-inline-block'>If all of the information is correct we will get in touch with you to collect payment and issue your policy. If there are things missing we’ll get in touch with you to let you know.</span></p></>}
                    {/* {(type == 1) &&<ActionButton customClass="ms-2" url={'final-quote/1'} text={'Dummy next btn'}/>} */}
                    {(type == 2) && <><h4 className='mb-3'>Thank you for uploading the signed quote!</h4>
                    <p className="text-fade-grey fs-6">We are now closely working with the insurer to get your policy issued as quickly as possible. We will be in touch with you to assist with the payment and finalising the process.</p>
                    {/* <ActionButton customClass="ms-2" url={'payment/1'} text={'Dummy next btn'}/> */}
                    </>
                    }
                    {(type == 3) && <><h4 className='mb-3'>Thank you for sharing the proof of payment. </h4>
                    <p className="text-fade-grey fs-6">We are now arranging the issuance of your health insurance policy with your chosen insurer. We will soon be sending you the policy certificate along with Policy Wording, Confirmation of Cover and Receipt of Payment</p>
                    <div className='insurer-info shadow-1 rounded-0 mt-3'>
                        <h5 className='text-center mt-3'>IMPORTANT:</h5>
                        <p className="text-fade-grey fs-6">Your policy is still in process and your new health insurance plan is NOT active yet. You will only be insured when your new policy has been issued and sent to you via email.</p>
                    </div>
                    {/* <ActionButton customClass="ms-2" url={'policy/1'} text={'Dummy next btn'}/> */}
                    </>}
                </div>
            </Layout>
        </div>
    )
}
export default ThankyouPage