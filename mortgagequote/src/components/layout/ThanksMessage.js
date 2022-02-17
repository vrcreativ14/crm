import React, { useContext } from "react"
import SandLoading from '../../assets/stages/sand-clock.svg'
import FireWorks from '../../assets/stages/fireworks.svg'
import { DataContext } from '../../helpers/context.js'
import { BrowserRouter as Router, useParams } from "react-router-dom"
import Banks from "./Banks"

export default function ThankYou({currentTab = false}){
    const[data] = useContext(DataContext)
    let { quoteID } = useParams()
    return(
        <>
        <img className="static-images mb-4" src={(currentTab=='mortgageIssued') ? FireWorks:SandLoading} alt="process"/>
        <p className="fw-light-bold">Thank you for uploading your documents!</p>
        <p>Our customer success team has been notified and is now checking your documents to make sure that all of the information we have is correct.</p>
        <p>If all of the information is correct we will get in touch with you to proceed further. If there are things missing we’ll get in touch with you to let you know.</p>
        <div className="thank-you-bank-details"><Banks data={data} bank={data.quote_details[quoteID]}/></div>
        </>
    )
}