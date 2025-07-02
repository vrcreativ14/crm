import React from 'react'
import { Countries } from './Countries'

export const CurrencyFormat = (num,noDecimal = false,currentSymbol = 'AED') => {
    if(isNaN(num))return num
    const price = parseFloat(num)
    let isInt = false
    if (Number.isInteger(num)) {
        isInt = true
    }
    if(isInt){
        return currentSymbol+' '+price.toFixed(0).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
    }else if(!noDecimal){
        return currentSymbol+' '+price.toFixed(2).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')+' AED'
    }else{
        return currentSymbol+' '+price.toLocaleString("en-US")
    }
}

export const CountryFullForm = ({code, classname = ''}) => {
    if(!code)return ''
    let country = Countries.filter((country) => country.code==code)
    if(!country || !('0' in country))return ''
    country = country[0]
    return(
        <>
            <span className={'d-flex align-items-center country w-100'+classname}><img src={country.image} className="me-1"/><small>{country.name}</small></span>
        </>
    )
}

export const DateFormatNexus = ({date}) => {
    var moment = require('moment'); // require
    const FormatedDate = moment(date,'YYYY-MM-DD').format('ll')
    return FormatedDate
}