import React from 'react';
import ReactFlagsSelect from "react-flags-select";

const SelectListLabel = ({lists,value,type = false}) => {
    const onChangeFetch = (code) => {
        
    }
    if(type=='additional_benefits'){
        return(
            <>
                {lists.map((list,index) => {
                    if(value.filter(val => list.value==val).length==0)return
                    return(
                        <span className="list-value" key={list.value}>{index ? ', ':null}{list.label}</span>
                    )
                })}
            </>
        )
    }
    return(
        <>
        {(type && type=='flag') ? (value=='other') ? <span className='d-flex align-items-center me-0'><strong>{lists}: </strong><span className='ms-2'>Other</span></span>:
            <span className='d-flex align-items-center me-0'><strong>{lists}: </strong><span className='ms-2'><ReactFlagsSelect countries={(value) ? [value]:false} selected={(value) ? value:false} onSelect={(code) => onChangeFetch(code)}/></span></span>
        :
            <>
            {lists.map((list) => {
                if(list.value!=value)return
                return(
                    <span className="list-value" key={list.value}>{list.label}</span>
                )
            })}
            </>
        }
        </>
    )
}

export default SelectListLabel