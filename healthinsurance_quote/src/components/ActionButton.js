import React, { useState } from 'react'
import { useNavigate, useParams } from "react-router-dom"
import parse from 'html-react-parser';

const ActionButton = ({url = '',text = '',customClass = '', golden = true,submit = false,loader = false}) => {
    const navigate = useNavigate()
    // const [loader,setLoader] = useState(false)
    const { id, secretCode } = useParams()
    const actionLink = () => {
        if(submit)return
        navigate((url) ? '/health-insurance-quote/'+secretCode+'/'+id+'/'+url+'/':'/health-insurance-quote/'+secretCode+'/'+id+'/')
    }
    return(
        <button type={(submit && !loader) ? 'submit':'button'} className={(golden) ? "btn-nexus btn-golden "+customClass:"btn-nexus btn-grey "+customClass} onClick={() => actionLink()}>
            {parse(text)}
            {loader ? <i className="ms-1 fas fa-circle-notch fa-spin"></i>:''}
        </button>
    )
}

export default ActionButton