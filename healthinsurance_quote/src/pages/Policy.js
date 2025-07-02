import React, { useEffect, useState } from 'react'
import SelectedPolicy from '../components/SelectedPolicy'
import Layout from '../layout/Layout'
import Orient from '../assets/orient.svg'
import { useNavigate } from 'react-router-dom'
import { GetData } from '../helper/GetData'
import LoadingPage from './LoadingPage'
import InvalidPage from './InvalidPage'
import { CurrencyFormat, DateFormatNexus } from '../helper/Utils'
import JSZipUtils from "jszip-utils";

import { saveAs } from 'file-saver';
var JSZip = require("jszip");
var zip = new JSZip();

const Policy = () => {
    const[data,setData] = useState(false)
    const navigate = useNavigate()

    useEffect(() => {
        window.scrollTo(0, 0)
    }, [])

    const fetch = async () => {
        const res = await GetData('housekeeping',navigate)
        if(res)setData(res)
    }

    if(!data){
        fetch()
        return <LoadingPage/>
    }
    if(data=='invalid')return <InvalidPage/>

    function downloadAll(e){
        e.preventDefault();

        if('policy' in data && 'medical_card' in data.policy && data.policy.medical_card)downloadSingleDoc('medical_card',true)
        if('policy' in data && 'receipt_of_payment' in data.policy && data.policy.receipt_of_payment)downloadSingleDoc('receipt_of_payment',true)
        if('policy' in data && 'tax_invoice' in data.policy && data.policy.tax_invoice)downloadSingleDoc('tax_invoice',true)
        if('policy' in data && 'certificate_of_insurance' in data.policy && data.policy.certificate_of_insurance)downloadSingleDoc('certificate_of_insurance',true)
        if('policy' in data && 'confirmation_of_cover' in data.policy && data.policy.confirmation_of_cover)downloadSingleDoc('confirmation_of_cover',true)
        if('selected_plan' in data && 'policy_wording' in data.selected_plan && data.selected_plan.policy_wording)downloadSingleDoc('policy_wording',true)

        setTimeout(() => {
            zip.generateAsync({type:"blob"})
            .then(function(content) {
                // see FileSaver.js
                saveAs(content, "Policy-documents.zip");
            })
        },2000)
    }

    function downloadSingleDoc(key,bulk = false){
        let files = (key=='policy_wording') ? data.selected_plan[key]:data.policy[key]
        if(key=='policy_wording'){
            const file = data.selected_plan[key]
            JSZipUtils.getBinaryContent(file, function (err, dataFile) {
                if(err) {
                    console.log(err)
                    throw err; // or handle the error
                    return
                }
                const fileName = (file.split('.').pop()).split('?')
                zip.file(key+'.'+fileName[0], dataFile, {binary:true});
            });
        }else{
            files.map((file,index) => {
                JSZipUtils.getBinaryContent(file, function (err, dataFile) {
                    if(err) {
                        console.log(err)
                        throw err; // or handle the error
                        return
                    }
                    const fileName = (file.split('.').pop()).split('?')
                    zip.file(key+index+'.'+fileName[0], dataFile, {binary:true});
                });
            })
        }

        if(!bulk)
        setTimeout(() => {
            zip.generateAsync({type:"blob"})
            .then(function(content) {
                // see FileSaver.js
                saveAs(content, key+"_documents.zip");
            })
        },2000)
    }

    const name = 'Hi <span class="text-capitalize">'+data.primary_member.name+'</span>,'
    const currentTab = 'issued'
	const stepContent = "<span class='text-success fs-5 fw-bold'>Your health insurance policy has now been issued!</span>"

    return(
        <Layout currentTab={currentTab} name={name} stepContent={stepContent}>
            <p className="fs-6 fw-light-bold mb-4">You can now download your policy documents along with the network list in the documents section below:</p>
            <div className='col-md-12'>
                <div className='policy-page selected-policy insurer-info shadow-1'>
                    <p className='fs-6 border-bottom mb-0 p-2 fw-bold d-none d-md-block'>Your Plan</p>
                    <ul className='quote-short-detail'>
                        <li className='image-column d-flex d-md-table-cell align-items-center'>
                            <div className='w-100 image'><img className='shadow-1 p-2 pb-0' src={data.selected_plan.insurer_logo} /><br/></div>
                            <span className='w-100 text-end'>
                                <strong className='mt-0 fs-6 mt-md-4 d-inline-block'>{data.selected_plan.insurer_name}</strong><br/>
                                <span className='mt-3 fw-bold fs-6'>Final Premium<span className='d-block text-golden text-center'>{CurrencyFormat(data.deal.total_premium,true,('currency' in data.deal) ? data.deal.currency:'AED')}</span></span>
                            </span>
                        </li>
                        <li className='large-column multiple-column-mobile'>
                            <span><b>Final Premium(Incl. VAT)</b><br/>{('policy' in data) ? CurrencyFormat(data.policy.total_premium,true,('currency' in data.policy) ? data.policy.currency:'AED'):CurrencyFormat(data.selected_plan.total_premium*1.05,true,('currency' in data.selected_plan) ? data.selected_plan.currency:'AED')}</span>
                            <span><b>Product</b><br/>{data.selected_plan.insurer_name}</span>
                        </li>
                        <li className='large-column multiple-column-mobile'>
                            <span><b>Start Date</b><br/>{('policy' in data) ? <DateFormatNexus date={data.policy.start_date}/>:<DateFormatNexus date={data.deal.start_date}/>}</span>
                            <span><b>Expiry Date</b><br/>{('policy' in data) ? <DateFormatNexus date={data.policy.expiry_date}/>:<DateFormatNexus date={data.quote.expiry_date}/>}</span>
                        </li>
                        <li className='large-column multiple-column-mobile'>
                            <span><b>No. Of Members</b><br/>{data.additional_members.length+1}</span>
                            <span><b>Policy Number</b><br/>{('policy' in data) ? data.policy.policy_number:'N/A'}</span>
                        </li>
                        <li className='large-column multiple-column-mobile align-top three-col'>
                            <span><b>Network List In-Patient: </b>{(data.selected_plan.network_list_inpatient) ? <a target="_blank" className="text-fade-grey d-inline-block" href={decodeURI(data.selected_plan.network_list_inpatient).replace(/&amp;/g, "&")}>Download <i className="text-golden fas fa-arrow-circle-down"></i></a>:''}</span>
                            <span><b>Network List Outpatient: </b>{(data.selected_plan.network_list_outpatient) ? <a target="_blank" className="text-fade-grey d-inline-block" href={decodeURI(data.selected_plan.network_list_outpatient).replace(/&amp;/g, "&")}>Download <i className="text-golden fas fa-arrow-circle-down"></i></a>:''}</span>
                            <span><b>Table of Benefits: </b>{(data.selected_plan.table_of_benefits) ? <a target="_blank" className="text-fade-grey d-inline-block" href={decodeURI(data.selected_plan.table_of_benefits).replace(/&amp;/g, "&")}>Download <i className="text-golden fas fa-arrow-circle-down"></i></a>:''}</span>
                            <span><b>Policy Wording: </b>{(data.selected_plan.policy_wording) ? <a target="_blank" className="text-fade-grey d-inline-block" href={decodeURI(data.selected_plan.policy_wording).replace(/&amp;/g, "&")}>Download <i className="text-golden fas fa-arrow-circle-down"></i></a>:''}</span>
                        </li>
                    </ul>
                </div>
            </div>
            <div className='col-md-12'>
                <div className='insurer-info shadow-1 p-0 policy secondary-member-info'>
                    <p className='fs-6 border-bottom mb-0 p-3 fw-bold d-flex'>
                        <span className='w-100'>Your Policy Documents</span>
                        <span className="text-end w-100 mb-0 font-size-bigger-upload"><small><a className="text-fade-grey" onClick={(event) => downloadAll(event)} href="#">Download all <i className="text-golden fas fa-arrow-circle-down"></i></a></small></span>
                    </p>
                    <ul className='quote-short-detail'>
                    {data.policy.medical_card.length>0 && 
                        <li className='small-column'><strong>Medical Card</strong>
                            <p className="mb-0 font-size-bigger-upload">
                                {data.policy.medical_card.length==1 ? 
                                <a target="_blank" className="text-fade-grey" href={('policy' in data) ? decodeURI(data.policy.medical_card).replace(/&amp;/g, "&"):'#'}>
                                    Download <i className="text-golden fas fa-arrow-circle-down"></i>
                                </a>
                                :
                                <span className="text-fade-grey cursor-pointer" onClick={() => downloadSingleDoc('medical_card')}> Download <i className="text-golden fas fa-arrow-circle-down"></i></span>
                                }
                            </p>
                        </li>
                    }
                    {data.policy.receipt_of_payment.length>0 && 
                        <li className='small-column'><strong>Receipt Of Payment</strong>
                            <p className="mb-0 font-size-bigger-upload">
                                {data.policy.receipt_of_payment.length==1 ? 
                                <a target="_blank" className="text-fade-grey" href={('policy' in data) ? decodeURI(data.policy.receipt_of_payment).replace(/&amp;/g, "&"):'#'}>
                                    Download <i className="text-golden fas fa-arrow-circle-down"></i>
                                </a>
                                :
                                <span className="text-fade-grey cursor-pointer" onClick={() => downloadSingleDoc('receipt_of_payment')}> Download <i className="text-golden fas fa-arrow-circle-down"></i></span>
                                }
                            </p>
                        </li>
                    }
                    {data.policy.tax_invoice.length>0 && 
                        <li className='small-column'><strong>Tax Invoice</strong>
                            <p className="mb-0 font-size-bigger-upload">
                                {data.policy.tax_invoice.length==1 ? 
                                <a target="_blank" className="text-fade-grey" href={('policy' in data) ? decodeURI(data.policy.tax_invoice).replace(/&amp;/g, "&"):'#'}>
                                    Download <i className="text-golden fas fa-arrow-circle-down"></i>
                                </a>
                                :
                                <span className="text-fade-grey cursor-pointer" onClick={() => downloadSingleDoc('tax_invoice')}> Download <i className="text-golden fas fa-arrow-circle-down"></i></span>
                                }
                            </p>
                        </li>
                    }
                    {data.policy.certificate_of_insurance.length>0 && 
                        <li className='small-column'><strong>Certificate Of Insurance </strong>
                            <p className="mb-0 font-size-bigger-upload">
                                {data.policy.certificate_of_insurance.length==1 ? 
                                <a target="_blank" className="text-fade-grey" href={('policy' in data) ? decodeURI(data.policy.certificate_of_insurance).replace(/&amp;/g, "&"):'#'}>
                                    Download <i className="text-golden fas fa-arrow-circle-down"></i>
                                </a>
                                :
                                <span className="text-fade-grey cursor-pointer" onClick={() => downloadSingleDoc('certificate_of_insurance')}> Download <i className="text-golden fas fa-arrow-circle-down"></i></span>
                                }
                            </p>
                        </li>
                    }
                    {data.policy.confirmation_of_cover.length>0 && 
                        <li className='small-column'><strong>Confirmation Of Cover</strong>
                            <p className="mb-0 font-size-bigger-upload">
                                {data.policy.confirmation_of_cover.length==1 ? 
                                <a target="_blank" className="text-fade-grey" href={('policy' in data) ? decodeURI(data.policy.confirmation_of_cover).replace(/&amp;/g, "&"):'#'}>
                                    Download <i className="text-golden fas fa-arrow-circle-down"></i>
                                </a>
                                :
                                <span className="text-fade-grey cursor-pointer" onClick={() => downloadSingleDoc('confirmation_of_cover')}> Download <i className="text-golden fas fa-arrow-circle-down"></i></span>
                                }
                            </p>
                        </li>
                    }
                    {data.selected_plan.policy_wording.length>0 && 
                        <li className='small-column'><strong>Policy Wordings</strong>
                            <p className="mb-0 font-size-bigger-upload">
                                {data.selected_plan.policy_wording ? 
                                <a target="_blank" className="text-fade-grey" href={decodeURI(data.selected_plan.policy_wording).replace(/&amp;/g, "&")}>
                                    Download <i className="text-golden fas fa-arrow-circle-down"></i>
                                </a>
                                :
                                <span className="text-fade-grey cursor-pointer" onClick={() => downloadSingleDoc('policy_wording')}> Download <i className="text-golden fas fa-arrow-circle-down"></i></span>
                                }
                            </p>
                        </li>
                    }
                    </ul>
                </div>
            </div>
            <div className='col-md-8'>
                <div className='shadow-1 p-3 bg-white rounded-5'>
                    <p className='fw-bold'>What’s next?</p>
                    <p>Your insurance policy is one of those things that you hope you never need to use. However, if you do find yourself needing help with your insurance policy then don’t hesitate to get in touch with us.</p>
                    <p>We’re standing by to assist you with whatever you need.</p>
                </div>
            </div>
        </Layout>
    )
}

export default Policy