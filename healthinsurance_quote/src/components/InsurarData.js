import React from 'react'

const InsurerData = ({insurer,keyIndex,type}) => {
    let outpatient = ''
    if(customCol.includes(keyIndex)){
        outpatient = handleCoPayment(insurer.consultation_copay)
    }
    if(keyIndex in insurer || customCol.includes(keyIndex)){
        return (
            <li className={type+'-column'}>
                <span className='d-block d-md-none'>{columnTitle[keyIndex]}</span>
                {(keyIndex=='outpatient') ? 
                <ul className='outpatient d-inline-block'>
                    {(outpatient && outpatient.length>1) ?
                    <li>
                        <div className='d-flex'>
                            <i className="me-2 fas fa-check"></i>
                            <span className='w-50'>Consultation:</span>
                        </div>
                        <ul>
                            {outpatient.map((copayment,index) => {
                                return(
                                    <li key={'outpatient-'+index+insurer.id} className="text-start">{copayment}</li>
                                )
                            })}
                        </ul>
                    </li>
                    :
                    <li className='d-flex'><i className="me-2 fas fa-check"></i><span>Consultation: {outpatient[0]}</span></li>
                    }
                    <li className='d-flex'><i className="me-2 fas fa-check"></i><span>Diagnostics and Labs: {insurer.diagnostics_copay}</span></li>
                    <li className='d-flex'><i className="me-2 fas fa-check"></i><span>Pharmacy: {insurer.pharmacy_copay}</span></li>
                </ul>
                :
                insurer[keyIndex]
                }
            </li>
        )
    }else{
        return('')
    }
}

export default InsurerData

export const columnTitle = {
    "annual_limit":"Annual Limit",
    "geographical_cover":"Geographical Cover",
    "outpatient":"Outpatient Co-payment",
    "network":"Network",
    "pre_existing_cover":"Pre-Existing Cover",
    "dental_benefits":"Dental Benefits",
    "optical_benefits":"Optical",

    "inpatient_deductible":"In Patient Deductible / Coinsurance",

    "maf":"Cover",
    "table_of_benefits":"Table of Benefits",
    "policy_wording":"Policy Wording",
    "network_list":"Network List",

    "Maternity_waiting_period":"Maternity Waiting Period",
    "maternity_benefits":"Maternity Benefits",

    "wellness_benefits":"Wellness Benefits / Health Screening",
    "physiotherapy":"Physiotherapy",
    "alternative_medicine":"Alternative Medicine",

    "consultation_copay":"Consultation Co-payment",
    "diagnostics_copay":"Diagnostics Co-payment",
    "pharmacy_copay":"Pharmaceuticals Co-payment",

    "repatriation_benefits":"Medical repatriation*",
    "accompanying_person_expense":"Expenses for one person accompanying a repatriated person*",
    "family_members_travel_expense":"Travel costs of insured family members in the event of a repatriation*",
    "members_with_critical_patient_travel_expense":"Travel costs of insured members to be with a family member who is at persil of death or who has died"
}

const isDoc = ['maf','table_of_benefits','policy_wording','network_list']
const customCol = ['inpatient','outpatient']
const customColRepat = ['accompanying_person_expense','family_members_travel_expense','members_with_critical_patient_travel_expense']

export const InsurarTableData = ({data,selectedInsurar,keyIndex,comparison}) => {
    comparison = (comparison) ? comparison.sort():false
    return(
        <>
        {!comparison ? ((keyIndex in data[selectedInsurar] && keyIndex!='repatriation_benefits') || customCol.includes(keyIndex)) ?
            <tr>
                <th>{columnTitle[keyIndex]}</th>
                {(customCol.includes(keyIndex) && keyIndex!='inpatient') ? 
                <td>
                    <PrepareColumn keyIndex={'consultation_copay'} value={data[selectedInsurar]['consultation_copay']}/>
                    Diagnostics and Labs Copay: <PrepareColumn keyIndex={'diagnostics_copay'} value={data[selectedInsurar]['diagnostics_copay']}/><br/>
                    Pharmacy Copay: <PrepareColumn keyIndex={'pharmacy_copay'} value={data[selectedInsurar]['pharmacy_copay']}/>
                </td>
                :
                <td><PrepareColumn keyIndex={keyIndex} value={(keyIndex=='inpatient_deductible') ? (data[selectedInsurar][keyIndex]) ? data[selectedInsurar][keyIndex]:'Nil':(data[selectedInsurar][keyIndex]) ? data[selectedInsurar][keyIndex]:' N/A '}/></td>
                }
            </tr>
            :
            (keyIndex=='repatriation_benefits') ? 
            <HandleMedicalPrepatriation columnTitle={columnTitle} keyIndex={keyIndex} data={data[selectedInsurar]}/>
            :
            (customColRepat.includes(keyIndex)) ?
            <tr><th>{columnTitle[keyIndex]}</th><td><PrepareColumn keyIndex={keyIndex} value={(data[selectedInsurar]['repatriation_benefits'][keyIndex]) ? data[selectedInsurar]['repatriation_benefits'][keyIndex]:' N/A '}/></td></tr>
            :
            <tr><th>{columnTitle[keyIndex]}</th><td>N/A</td></tr>
            :
            (keyIndex=='repatriation_benefits') ? 
            <HandleMedicalPrepatriation columnTitle={columnTitle} keyIndex={keyIndex} data={data} comparison={comparison}/>:
            <tr>
                <th>{columnTitle[keyIndex]}</th>
                {comparison.map((comparisonIndex,index) => {
                    if(!(keyIndex in data[comparisonIndex]) || !data[comparisonIndex][keyIndex]){
                        if(data[comparisonIndex]['is_repatriation_benefit_enabled'] && customColRepat.includes(keyIndex)){
                            return <td key={'compare-td-'+keyIndex+index}>{data[comparisonIndex]['repatriation_benefits'][keyIndex]}</td>
                        }
                        if(!customCol.includes(keyIndex))return <td key={'compare-td-'+keyIndex+index}>{(keyIndex=='inpatient_deductible') ? 'Nill':'N/A'}</td>
                    }
                    return(
                        <td key={'compare-td-'+keyIndex+index}>
                            {(customCol.includes(keyIndex) && keyIndex!='inpatient') ? 
                            <>
                                <PrepareColumn keyIndex={'consultation_copay'} value={data[comparisonIndex]['consultation_copay']}/>
                                Diagnostics and Labs Copay: <PrepareColumn keyIndex={'diagnostics_copay'} value={data[comparisonIndex]['diagnostics_copay']}/><br/>
                                Pharmacy Copay: <PrepareColumn keyIndex={'pharmacy_copay'} value={data[comparisonIndex]['pharmacy_copay']}/>
                            </>
                            :
                            <PrepareColumn key={'compare-index'+comparisonIndex} keyIndex={keyIndex} value={(keyIndex=='inpatient_deductible') ? (data[comparisonIndex][keyIndex]) ? data[comparisonIndex][keyIndex]:'Nil':data[comparisonIndex][keyIndex]}/>}
                        </td>
                    )
                })}       
            </tr>
        }
        </>
    )
}

export const PrepareColumn = ({value,keyIndex}) => {
    if(keyIndex=='consultation_copay' && value!=''){
        value = handleCoPayment(value)
        return(
            <div>
                Consultation Copay:&nbsp;
                {(value && value.length>1) ?
                <ul>
                    {value.map((value,index) => {
                        return(
                            <li key={'co-payment-'+keyIndex+index}>{value}</li>
                        )
                    })}
                </ul>
                :value[0]}
            </div>
        )
    }
    return(
        <>{(isDoc.includes(keyIndex)) ? (value && value!=' - ') ? <a href={value} target="_blank">Download<i className="text-golden ms-2 fas fa-arrow-alt-circle-down"></i></a>:'N/A':value}</>
    )
}

export const handleCoPayment = (value) => {
    const data = value.split(';')
    if(!(1 in data)){
        value = value.split('/')
    }else{
        value = data
    }
    return value
}

export const HandleMedicalPrepatriation = ({columnTitle,keyIndex,data = false,comparison = false}) => {
    return(
        <>
        <tr className='medi-prat-main'>
            <th>{columnTitle[keyIndex]}</th>
            {(!comparison) ? 
                <td></td>:
                comparison.map((comparisonIndex,index) => {
                    return <td key={'compare-td-'+keyIndex+index}></td>
                })
            }
        </tr>
        <tr className='sub-td'>
            <th><div><i className="fas fa-circle me-2"></i><span>Where the necessary treatment is not available locally, you can choose to be medically repatriated to your home country instead of to the nearest appropriate medical center. This benefits only applies when your home country is within your area of cover*</span></div></th>
            {(!comparison) ? 
                <td><i className={('is_benefit_only_for_home_country' in data[keyIndex] && data[keyIndex].is_benefit_only_for_home_country) ? "fas fa-check":"fas fa-times"}></i></td>:
                comparison.map((comparisonIndex,index) => {
                    if(!(keyIndex in data[comparisonIndex]) || !data[comparisonIndex][keyIndex] || !('is_benefit_only_for_home_country' in data[comparisonIndex][keyIndex])){
                       <td key={'compare-td-'+keyIndex+index}>N/A</td>
                    }
                    return <td key={'compare-td-'+keyIndex+index}><i className={(keyIndex in data[comparisonIndex] && 'is_benefit_only_for_home_country' in data[comparisonIndex]['repatriation_benefits'] && data[comparisonIndex]['repatriation_benefits'].is_benefit_only_for_home_country) ? "fas fa-check":"fas fa-times"}></i></td>
                })
            }
        </tr>
        <tr className='sub-td'>
            <th><div><i className="fas fa-circle me-2"></i><span>Where ongoing treatment is required, we will cover hotel accommodation costs*</span></div></th>
            {(!comparison) ? 
                <td><i className={('is_accomodation_cost_covered' in data[keyIndex] && data[keyIndex].is_accomodation_cost_covered) ? "fas fa-check":"fas fa-times"}></i></td>:
                comparison.map((comparisonIndex,index) => {
                    if(!(keyIndex in data[comparisonIndex]) || !data[comparisonIndex][keyIndex] || !('is_accomodation_cost_covered' in data[comparisonIndex][keyIndex])){
                       <td key={'compare-td-'+keyIndex+index}>N/A</td>
                    }
                    return <td key={'compare-td-'+keyIndex+index}><i className={(keyIndex in data[comparisonIndex] && 'is_accomodation_cost_covered' in data[comparisonIndex]['repatriation_benefits'] && data[comparisonIndex]['repatriation_benefits'].is_accomodation_cost_covered) ? "fas fa-check":"fas fa-times"}></i></td>
                })
            }
        </tr>
        <tr className='sub-td'>
            <th><div><i className="fas fa-circle me-2"></i><span>Repatriation in the event of unavailability of adequately screened blood*</span></div></th>
            {(!comparison) ? 
                <td><i className={('do_repatriation_when_screened_blood_inavailable' in data[keyIndex] && data[keyIndex].do_repatriation_when_screened_blood_inavailable) ? "fas fa-check":"fas fa-times"}></i></td>:
                comparison.map((comparisonIndex,index) => {
                    if(!(keyIndex in data[comparisonIndex]) || !data[comparisonIndex][keyIndex] || !('do_repatriation_when_screened_blood_inavailable' in data[comparisonIndex][keyIndex])){
                       <td key={'compare-td-'+keyIndex+index}>N/A</td>
                    }
                    return <td key={'compare-td-'+keyIndex+index}><i className={(keyIndex in data[comparisonIndex] && 'do_repatriation_when_screened_blood_inavailable' in data[comparisonIndex]['repatriation_benefits'] && data[comparisonIndex]['repatriation_benefits'].do_repatriation_when_screened_blood_inavailable) ? "fas fa-check":"fas fa-times"}></i></td>
                })
            }
        </tr>
        <tr className='sub-td'>
            <th><div><i className="fas fa-circle me-2"></i><span>If medical necessity prevents an immediate return trip, following discharge from an in-patient episode of care, we will cover hotel accomodation costs*</span></div></th>
            {(!comparison) ? 
                <td>{('accomodation_cost_cover' in data[keyIndex] && data[keyIndex].accomodation_cost_cover) ? data[keyIndex].accomodation_cost_cover:"N/A"}</td>:
                comparison.map((comparisonIndex,index) => {
                    if(!(keyIndex in data[comparisonIndex]) || !data[comparisonIndex][keyIndex] || !('accomodation_cost_cover' in data[comparisonIndex][keyIndex])){
                       <td key={'compare-td-'+keyIndex+index}>N/A</td>
                    }
                    return <td key={'compare-td-'+keyIndex+index}>{(keyIndex in data[comparisonIndex] && 'accomodation_cost_cover' in data[comparisonIndex]['repatriation_benefits'] && data[comparisonIndex]['repatriation_benefits'].accomodation_cost_cover) ? data[comparisonIndex]['repatriation_benefits'].accomodation_cost_cover:"N/A"}</td>
                })
            }
        </tr>
        </>
    )
}