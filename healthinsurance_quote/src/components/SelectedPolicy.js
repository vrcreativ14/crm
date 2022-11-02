import React from 'react'
import { CurrencyFormat } from '../helper/Utils'
import { handleCoPayment } from './InsurarData'
import Members from './Members'

const SelectedPolicy = ({data,insurer,type = 1}) => {
    return(
        <>
        <div className='selected-policy insurer-info shadow-1'>
            <ul className='quote-short-detail'>
                <li className='image-column d-flex d-md-table-cell align-items-center'>
                    <div className='w-100 image'><div className='renewal-parent'><img className='shadow-1' src={insurer.insurer_logo} />{insurer.is_renewal && <span className='renewel'>Renewal</span>}</div><br/></div>
                    <span className='w-100 text-end'>
                        <strong className='mt-0 mt-md-4 d-inline-block fs-6'>{insurer.insurer_name} - {insurer.plan_name}</strong><br/>
                        <>
                        {(type==1) ? 
                        <>
                            <strong className='mt-3 fs-6'>Indicative Premium</strong>
                            <span className='info-content right-zero-mobile'>
                                <i className="text-fade-grey ms-1 fas fa-info-circle"></i>
                                <span className='info-text shadow-1'>Premiums are indicative and based on standard rates - Final premium amount is subject to underwriting.</span>
                            </span>
                        </>:<strong className='mt-3 fs-6'>Final Premium</strong>
                        }
                        </><br/>
                        <strong className='mt-2 fw-bold fs-6 text-golden'>{(type==1) ? CurrencyFormat(insurer.total_premium,true,insurer.currency):CurrencyFormat(data.deal.total_premium,true,('currency' in data.deal) ? data.deal.currency:'AED')}{(type!=1) && <small> (Inc. VAT)</small>}</strong>
                    </span>
                </li>
                <li className='large-column multiple-column-mobile'>
                    {(type!=2) ? <span><b>Annual Limit</b><br/>{insurer.annual_limit}</span>:''}
                    <span><b>Geographical Cover</b><br/>{insurer.geographical_cover}</span>
                    <span><b>Dental Benefits</b><br/>{insurer.dental_benefits}</span>
                    <span><b>Pre-Existing Cover</b><br/>{insurer.pre_existing_cover}</span>
                    <span><b className='d-block d-md-inline-block me-1'>Network:</b>{insurer.network}</span>
                    <span className='no-border'><b className='d-block d-md-inline-block me-1'>Alternative Medicines:</b>{insurer.alternative_medicine}</span>
                </li>
                <li className='large-column'>
                    <span className='d-block'>
                        <b>Outpatient Co-payment</b><br/>
                        <ul className='outpatient'>
                            {(insurer.consultation_copay) && handleCoPayment(insurer.consultation_copay).length>1 ?
                            <>
                                <li><i className="me-2 fas fa-check"></i><span>Consultation Copay:</span></li>
                                <ul>
                                    {(insurer.consultation_copay) && handleCoPayment(insurer.consultation_copay).map((copay,index) => {
                                        return(
                                            <li key={'key-'+index}>{copay}</li>
                                        )
                                    })}
                                </ul>
                            </>
                            :
                            <li className='d-flex'><i className="me-2 fas fa-check"></i><span>Consultation Copay: {insurer.consultation_copay}</span></li>
                            }
                            <li className='d-flex'><i className="me-2 fas fa-check"></i><span>Diagnostics and Labs Copay: {insurer.diagnostics_copay}</span></li>
                            <li className='d-flex'><i className="me-2 fas fa-check"></i><span>Pharmacy Copay: {insurer.pharmacy_copay}</span></li>
                        </ul>
                    </span>
                    <span><b>Network List: </b>{(insurer.network_list) ? <a target="_blank" className="text-fade-grey" href={decodeURI(insurer.network_list).replace(/&amp;/g, "&")}>Download <i className="text-golden fas fa-arrow-circle-down"></i></a>:''}</span>
                    <span><b>Table of Benefits: </b>{(insurer.table_of_benefits) ? <a target="_blank" className="text-fade-grey" href={decodeURI(insurer.table_of_benefits).replace(/&amp;/g, "&")}>Download <i className="text-golden fas fa-arrow-circle-down"></i></a>:''}</span>
                    <span className='no-border'><b>Policy Wording: </b>{(insurer.policy_wording) ? <a target="_blank" className="text-fade-grey" href={decodeURI(insurer.policy_wording).replace(/&amp;/g, "&")}>Download <i className="text-golden fas fa-arrow-circle-down"></i></a>:''}</span>
                </li>
                {type == 2 &&
                <li className='large-column'>
                    <span><b>Pharmacy Limit</b><br/>{insurer.pharmacy_copay}</span>
                    <span><b>Network</b><br/>{insurer.network}</span>
                    <span><b>Optical Benefits</b><br/>{insurer.optical_benefits}</span>
                    <span className='no-border'><b>Wellness Benefits</b><br/>{insurer.wellness_benefits}</span>
                </li>
                }           
            </ul>
        </div>
        {type == 1 && <Members data={data}/>}
        </>
    )
}

export default SelectedPolicy