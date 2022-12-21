import React, { useEffect, useState } from 'react';
import FormFields from './FormFields';
import { Notification } from './Notification';

const AddtionalMemebers = ({formData,setFormData}) => {
    const[totalMembers, setTotalMembers] = useState(('total_members' in formData) ? formData.total_members:0)
    const[memberData,setMemberData] = useState(('additional_members' in formData ) ? formData.additional_members:[])

    useEffect(() => {
        setTotalMembers(('total_members' in formData) ? formData.total_members:totalMembers)
        setMemberData(('additional_members' in formData) ? formData.additional_members:memberData)
    })

    const members = [
        {label:'Spouse',value:'Spouse'},
        {label:'Son',value:'Son'},
        {label:'Daughter',value:'Daughter'},
        {label:'Father',value:'Father'},
        {label:'Mother',value:'Mother'},
    ]

    const handleAddMembers = () => {
        if(totalMembers==0)return setTotalMembers(1)
        let error = false
        Array(totalMembers).fill(null).map((value, index) => {
            if(index in memberData){
                if(!('relation' in memberData[index])){Notification('Info','Please select the Relation of member '+(index+1));error = true}
                if(!('name' in memberData[index])){Notification('Info','Please enter the Full name of member '+(index+1));error = true}
                if(!('dob' in memberData[index])){Notification('Info','Please select the DOB of member '+(index+1));error = true}
                // if(!('nationality' in memberData[index])){Notification('Info','Please select the Nationality of member '+(index+1));error = true}
                // if(!('country_of_stay' in memberData[index])){Notification('Info','Please select the Country of Residance of member '+(index+1));error = true}
            }else{
                Notification('Info','Please fill all the details of Member '+(index+1));error = true
            }
        })
        if(error)return
        setTotalMembers(totalMembers+1)
    }

    const updateStateData = (index,value,name) => {
        const data = memberData
        if(!(index in data))data[index] = {}
        data[index][name] = value
        setMemberData(data)
        const fullData = formData
        fullData['additional_members'] = data
        setFormData(fullData)
        setFormData(prevState => ({...prevState,data:0}))
    }

    const removeMember = (key) => {
        const data = memberData.filter((member,index) => (index!=key))
        setMemberData(data)
        const fullData = formData
        fullData['additional_members'] = data
        setFormData(fullData)
        setFormData(prevState => ({...prevState,data:0}))
        setTotalMembers(totalMembers-1)
    }

    return(
        <>
        {(totalMembers && totalMembers != 0 && totalMembers>0) ? Array(totalMembers).fill(null).map((value, index) => {
            return(
                <div className="member-parent-div mb-3" key={'members-'+index}>
                    <div className="text-end text-danger float-end"><i className="cursor-pointer fas fa-trash text-golden" onClick={() => removeMember(index)}></i></div>
                    <div className="memeber-info">
                        <h4 className='mb-4'>Member {index+1}</h4>
                        <div className='bg-white p-2 p-md-4'>
                            <div className='select-member'><FormFields index={index} indexName={"relation"} updateStateData={updateStateData} type="radio" name={"member-relation"} options={members} formData={(index in memberData) ? memberData[index]:{}}/></div>
                            <FormFields index={index} indexName="name" updateStateData={updateStateData} type="text" name={"member-name"} labelName="Full name" placeholder="Enter first name and last name" formData={(index in memberData) ? memberData[index]:{}}/>
                            <FormFields index={index} indexName="dob" updateStateData={updateStateData} type="date" name={"member-dob"} labelName="Date of birth" formData={(index in memberData) ? memberData[index]:{}}/>
                            <FormFields index={index} indexName="nationality" updateStateData={updateStateData} type="flag" name={"member-nationality"} labelName="Nationality" placeholder="Select the country" defaultValue={('nationality' in formData) ? formData.nationality:false} formData={(index in memberData) ? memberData[index]:{}}/>
                            <FormFields index={index} indexName="country_of_stay" updateStateData={updateStateData} type="flag" name={"member-country_of_stay"} labelName="Country of residence" placeholder="Select the country" defaultValue={('country_of_stay' in formData) ? formData.country_of_stay:false} formData={(index in memberData) ? memberData[index]:{}}/>
                        </div>
                    </div>
                </div>
            )
        }):null}
        <button type="button" className="btn-nexus btn-golden mt-2" onClick={() => handleAddMembers()}>Add {(totalMembers>0) && 'another '}member</button>
        </>
    )
}

export default AddtionalMemebers