import React, { useState } from 'react'
import Details from './Details'
import ActionButton from './ActionButton'
import InsurerData from './InsurarData'
import { CurrencyFormat } from '../helper/Utils'
import BasicPopUpPlanDetails from './BasicPopUpPlanDetails'

const Insurer = ({data,insurer,index,handleComparison,comparison}) => {
    const[showDetails,setShowDetails] = useState(false)
    const[showBasicPopup,setShowBasicPopup] = useState(false)
	return(
        <div className='insurer-info shadow-1'>
            <ul className='quote-short-detail'>
                <li className='image-column d-flex d-md-table-cell align-items-center'>
                    <div className='w-100 image'><div className='renewal-parent'><img src={insurer.insurer_logo} />{insurer.is_renewal && <span className='renewel'>Renewal</span>}</div><br/></div>
                    <span className='w-100 text-end text-center-desktop'>
                        <div className='d-block d-md-none'><label className='d-flex align-items-center mt-1 justify-content-end'><span>Compare</span><input onChange={(event) => handleComparison(event,index)} className='ms-2' type="checkbox" checked={(comparison && comparison.includes(index)) ? true:false}/></label></div>
                        <strong className='mt-0 mt-md-4 d-inline-block'>{insurer.insurer_name} - {insurer.plan_name}</strong>
                    </span>
                </li>
                <InsurerData insurer={insurer} keyIndex={'annual_limit'} type="small"/>
                <InsurerData insurer={insurer} keyIndex={'geographical_cover'} type="small"/>
                <InsurerData insurer={insurer} keyIndex={'outpatient'} type="large"/>
                <InsurerData insurer={insurer} keyIndex={'network'} type="small"/>
                <InsurerData insurer={insurer} keyIndex={'pre_existing_cover'} type="small"/>
                <InsurerData insurer={insurer} keyIndex={'dental_benefits'} type="small"/>
                <InsurerData insurer={insurer} keyIndex={'optical_benefits'} type="small"/>
                <li className='action-column d-flex d-md-table-cell justify-content-center'>
                    {('coverage_type' in insurer && insurer.coverage_type=='basic') ? <button className='w-100 btn-nexus btn-golden me-3 me-md-0 fw-bold ps-1 pe-1' onClick={() => setShowBasicPopup(true)}>Select<br/>{CurrencyFormat(insurer.total_premium,true,insurer.currency)}<br/>{insurer.payment_frequency}</button>
                    :
                    <ActionButton customClass="w-100 me-3 me-md-0 fw-bold ps-1 pe-1" url={'summary/'+insurer.id} text={'Select<br/>'+CurrencyFormat(insurer.total_premium,true,insurer.currency)+'<br/>'+insurer.payment_frequency}/>
                    }
                    <button className="w-100 btn-nexus btn-grey ps-1 pe-1" onClick={() => setShowDetails(!showDetails)}>Click here for more details</button>
                    <div className='d-none d-md-block'><label className='d-flex align-items-center mt-1 justify-content-center'><span>Compare</span><input onChange={(event) => handleComparison(event,index)} className='ms-2' type="checkbox" checked={(comparison && comparison.includes(index)) ? true:false}/></label></div>
                </li>
            </ul>
            {(showDetails) && <div className='mt-3 p-2 summary-page'><Details data={data.quoted_plans} selectedInsurar={index} setShowDetails={setShowDetails} setShowBasicPopup={setShowBasicPopup}/></div>}
            {(showBasicPopup) && <BasicPopUpPlanDetails data={data} plan={insurer} setShowBasicPopup={setShowBasicPopup}/>}
        </div>
    )
}

export default Insurer;