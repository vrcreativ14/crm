import React from 'react';
import { CurrencyFormat } from '../helper/Utils';
import ActionButton from './ActionButton';
import CollapseDetails from './CollapseDetails';
import { InsurarTableData } from './InsurarData';

const Details = ({data,selectedInsurar,setShowDetails = false,comparison = false,setShowBasicPopup = false}) => {
    let is_repart = false
    if(comparison)comparison.map(comparisonIndex => {
        if('is_repatriation_benefit_enabled' in data[comparisonIndex] && data[comparisonIndex].is_repatriation_benefit_enabled)is_repart = true
    })
	return(
        <>
            <ul className='details-benefits mb-4'>
                <CollapseDetails title="Core Benefits" defaultTab={true}>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="annual_limit"/>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="geographical_cover"/>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="outpatient"/>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="inpatient_deductible"/>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="pre_existing_cover"/>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="maternity_benefits"/>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="dental_benefits"/>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="optical_benefits"/>
                </CollapseDetails>
                <CollapseDetails title="Maternity Benefits" defaultTab={true}>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="Maternity_waiting_period"/>
                </CollapseDetails>
                <CollapseDetails title="Wellness Benefits" defaultTab={true}>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="wellness_benefits"/>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="physiotherapy"/>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="alternative_medicine"/>
                </CollapseDetails>
                <CollapseDetails title="Plan Documents" defaultTab={true}>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="table_of_benefits"/>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="network_list_inpatient"/>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="network_list_outpatient"/>
                    <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="policy_wording"/>
                </CollapseDetails>
                {((comparison && is_repart) || (selectedInsurar!==false && 'is_repatriation_benefit_enabled' in data[selectedInsurar] && data[selectedInsurar].is_repatriation_benefit_enabled)) &&
                    <CollapseDetails title="Repatriation Plan Benefits" defaultTab={true}>
                        <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="repatriation_benefits"/>
                        <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="accompanying_person_expense"/>
                        <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="family_members_travel_expense"/>
                        <InsurarTableData data={data} selectedInsurar={selectedInsurar} comparison={comparison} keyIndex="members_with_critical_patient_travel_expense"/>
                    </CollapseDetails>
                }
            </ul>
            {(!comparison) &&
            <div className='text-end d-flex w-100 justify-content-end'>
                <button className="btn-nexus btn-grey" onClick={() => setShowDetails(false)}>Close</button>
                {('coverage_type' in data[selectedInsurar] && data[selectedInsurar].coverage_type=='basic') ? <button className='ms-2 btn-nexus btn-golden me-3 me-md-0 fw-bold' onClick={() => setShowBasicPopup(true)}>Select <br/> {CurrencyFormat(data[selectedInsurar].total_premium,true,data[selectedInsurar].currency)}<br/>{('payment_frequency' in data[selectedInsurar] && data[selectedInsurar].payment_frequency) ? data[selectedInsurar].payment_frequency:'Yearly'}</button>
                :
                <ActionButton customClass="ms-2 fw-bold" url={'summary/'+data[selectedInsurar].id} text={'Select<br/>'+CurrencyFormat(data[selectedInsurar].total_premium,true,data[selectedInsurar].currency)+'<br/>'+data[selectedInsurar].payment_frequency}/>
                }
            </div>
            }
        </>
    )
}

export default Details;