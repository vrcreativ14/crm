import React, { useState } from 'react'
import Orient from '../assets/orient.svg'
import { CurrencyFormat } from '../helper/Utils'
import ActionButton from './ActionButton'
import BasicPopUpPlanDetails from './BasicPopUpPlanDetails'

const InsurerHead = ({data, comparison,image = true}) => {
    const[showBasicPopup,setShowBasicPopup] = useState(false)
    return(
        <>
        {data && data.map((plan,index) => {
            if(!comparison.includes(index))return
            return(
                <div key={(image) ? 'compare-header-image'+index:'compare-header'+index} className='right-header d-inline-block'>
                    <div className='d-flex flex-column justify-content-end h-100 align-items-start d-md-block ps-4'>
                        {image && <div className='renewal-parent'><img src={plan.insurer_logo} />{plan.is_renewal && <span className='renewel'>Renewal</span>}</div>}
                        <div className='text-golden price-highlight'>{CurrencyFormat(plan.total_premium,true,plan.currency)} <small>{('payment_frequency' in plan && plan.payment_frequency) ? plan.payment_frequency:'Yearly'}</small></div>
                        {('coverage_type' in plan && plan.coverage_type=='basic') ? <button className='btn-nexus btn-golden me-3 me-md-0 fw-bold' onClick={() => setShowBasicPopup(plan.id)}>Select</button>
                        :
                        <ActionButton customClass='fw-bold' url={'summary/'+plan.id} text={'Select'}/>
                        }
                        {image && <p className='title-head'>{plan.insurer_name} - {plan.plan_name}</p>}
                        {/* {(plan.is_renewal) && <p className='mt-1 mb-0'>Click here for Renewal Quote</p>} */}
                    </div>
                    {(showBasicPopup == plan.id) && <BasicPopUpPlanDetails data={data} plan={plan} setShowBasicPopup={setShowBasicPopup}/>}
                </div>
            )
        })}
        </>
    )
}

export default InsurerHead