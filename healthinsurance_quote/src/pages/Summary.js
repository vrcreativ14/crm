import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import ActionButton from '../components/ActionButton'
import SelectedPolicy from '../components/SelectedPolicy'
import Layout from '../layout/Layout'
import { GetData } from '../helper/GetData'
import InvalidPage from './InvalidPage'
import LoadingPage from './LoadingPage'
import RequestHandler from '../helper/RequestHandler'
import { Notifications } from '../components/Notifications'

const Summary = () => {
    const{ id, secretCode, quoteID } = useParams()
    const[data,setData] = useState(false)
    const[selectedQuote,setSelectedQuote] = useState(false)
    const[loader,setLoader] = useState(false)
    const navigate = useNavigate()

    useEffect(() => {
        window.scrollTo(0, 0)
    }, [])

    useEffect(() => {
        if(data && data!='invalid'){
            setSelectedQuote(data.quoted_plans.filter((plan) => plan.id==quoteID))
        }
    },[data])

    const fetch = async () => {
        const res = await GetData('quote',navigate)
        if(res)setData(res)
    }

    if(!data){
        fetch()
        return <LoadingPage/>
    }
    if(data=='invalid')return <InvalidPage/>
    if(!selectedQuote)return <LoadingPage/>

    async function handleFormSubmit(event){
        event.preventDefault()
        setLoader(true)
        var rawData = new FormData()
        rawData.append('pk', id)
        rawData.append('plan', quoteID)
        const { data: res } = await RequestHandler.post('health-insurance/quote-api/',rawData)
        if(res.success){
            Notifications('Success','Plan was selected.','success')
            return navigate('/health-insurance-quote/'+secretCode+'/'+id+'/policy-documents/'+quoteID)
        }else{
            Notifications('Error','Something went wrong, pls contact us.','error')
        }
    }

    const name = 'Hi <span class="text-capitalize">'+data.primary_member.name+'</span>,'
    const currentTab = 'quote'
	const stepContent = "Nexus offers a variety of health insurance plans from the best insurers. Please take a look at the plans we have carefully selected for you below. If you have any questions, please feel free to reach out to us."

    return(
        <Layout currentTab={currentTab} name={name} stepContent={stepContent}>
            <p className="fs-6 fw-light-bold mb-4">You have selected the policy below</p>
            <form onSubmit={(event) => handleFormSubmit(event)}>
                <div className="row">
                    <div className='col-md-12'>
                        <SelectedPolicy data={data} insurer={selectedQuote[0]}/>
                    </div>
                    <div className='col-md-12 mt-4'>
                        <label className='d-flex fs-6 align-items-center'>
                            <input required={true} name="info" className="me-2" type="checkbox" />
                            <span>The above information is accurate and correct<span className='text-danger'>*</span></span>
                        </label>
                        <label className='d-flex fs-6 align-items-center mt-2'>
                            <input required={true} name="appointing" className="me-2" type="checkbox" />
                            <span>I'm appointing Nexus as my insurance broker on record for this policy<span className='text-danger'>*</span></span>
                        </label>
                        <label className='d-flex fs-6 align-items-center mt-2'>
                            <input required={true} name="tandc" className="me-2" type="checkbox" />
                            <span>I have read the&nbsp;<a href="https://www.nexusadvice.com/terms-and-conditions/" target="_blank" className="text-golden">Terms & Conditions</a><span className='text-danger'>*</span></span>
                        </label>
                    </div>
                    <div className='col-md-12 mt-5'>
                        <ActionButton customClass="ms-2" url={false} text={'Go Back'} golden={false}/>
                        <ActionButton submit={true} customClass="ms-3" text={'Next'} loader={loader}/>
                    </div>
                </div>
            </form>
        </Layout>
    )
}

export default Summary