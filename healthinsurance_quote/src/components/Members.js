import React from 'react'
import { CountryFullForm, DateFormatNexus } from '../helper/Utils'

const Members = ({data}) => {
    return(
        <>
        <div className='insurer-info shadow-1 p-0 primary-member-info'>
            <p className='fs-6 border-bottom mb-0 p-3 fw-bold'>
                Primary Member Details
                <span className='info-content'>
                    <i className="text-fade-grey ms-1 fas fa-info-circle"></i>
                    <span className='info-text shadow-1'>If you would like to change any details, please click the chat icon below to contact the team.</span>
                </span>
            </p>
            <ul className='quote-short-detail'>
                <li className='small-column'><small className='d-block'>Name</small><strong>{data.primary_member.name}</strong></li>
                <li className='small-column'><small className='d-block'>Phone Number</small><strong>{data.primary_member.phone}</strong></li>
                <li className='small-column'><small className='d-block'>Email</small><strong>{data.primary_member.email}</strong></li>
                <li className='small-column'><small className='d-block'>Date of Birth</small><strong><DateFormatNexus date={data.primary_member.dob}/></strong></li>
                <li className='small-column'><small className='d-block'>Nationality</small><strong><CountryFullForm classname=' justify-content-center' code={data.primary_member.nationality}/></strong></li>
                <li className='small-column'><small className='d-block'>Country of Stay</small><strong><CountryFullForm classname=' justify-content-center' code={data.primary_member.country_of_stay}/></strong></li>
                <li className='small-column'><small className='d-block'>Visa</small><strong>{('visa' in data.primary_member) && data.primary_member.visa}</strong></li>
                <li className='small-column'><small className='d-block'>Salary Band</small><strong>{data.primary_member.salary_band}</strong></li>
            </ul>
        </div>
        {data.additional_members.length>0 && data.additional_members.map((member,index) => {
            return(
                <SecondaryMembers key={'member-'+index} member={member}/>
            )
        })}
        </>
    )
}

export default Members

export function SecondaryMembers({member}){
    return(
        <div className='insurer-info shadow-1 p-0 secondary-member-info'>
            <p className='fs-6 border-bottom mb-0 p-3 fw-bold'>
                <span className='text-capitalize'>{member.name} <small>({member.relation})</small></span>
                <span className='info-content'>
                    <i className="text-fade-grey ms-1 fas fa-info-circle"></i>
                    <span className='info-text shadow-1'>If you would like to change any details, please click the chat icon below to contact the team.</span>
                </span>
            </p>
            <ul className='quote-short-detail'>
                <li className='small-column'><small className='d-block'>Name</small><strong>{member.name}</strong></li>
                <li className='small-column'><small className='d-block'>Date of Birth</small><strong><DateFormatNexus date={member.dob}/></strong></li>
                <li className='small-column'><small className='d-block'>Nationality</small><strong><CountryFullForm code={member.nationality}/></strong></li>
                <li className='small-column'><small className='d-block'>Country of Stay</small><strong><CountryFullForm code={member.country_of_stay}/></strong></li>
            </ul>
        </div>
    )
}