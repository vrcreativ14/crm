import React from 'react';
import RequestHandler from '../helper/RequestHandler';
import parse from 'html-react-parser';
import { Notifications } from './Notifications';

const BasicPopUpPlanDetails = ({data,plan,setShowBasicPopup = false}) => {
    async function handlePlanSelection(){
        var rawData = new FormData()
        rawData.append('pk', data.deal.deal_id)
        rawData.append('plan', plan.id)
        const { data: res } = await RequestHandler.post('health-insurance/quote-api/',rawData)
        if(res.success){
            Notifications('Success','Redirecting to '+plan.insurer_name+'...','success')
            return window.location.href = ('basic_plan_url' in plan) ? plan.basic_plan_url:"https://www.orientonline.ae/MED/GuestLogin.aspx?MasterId=ItTyaHEgqa8QMBVWnEJcNg==";
        }else{
            Notifications('Error','Something went wrong, pls contact us.','error')
        }
    }
    return(
        <div className='basic-plan-pop-up'>
            <div className='parent-div shadow-1'>
                <h3 className='mb-3'>{plan.insurer_name}<span className='text-end' onClick={() => setShowBasicPopup(false)}><i className="fas fa-times-circle"></i></span></h3>
                {('popup_template' in plan && plan.popup_template) ? parse(plan.popup_template):<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>}
                <button className="btn-nexus btn-golden mt-2" onClick={() => handlePlanSelection()}>Go to {plan.insurer_name}</button>
            </div> 
        </div>
    )
}

export default BasicPopUpPlanDetails