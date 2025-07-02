import React, { useEffect } from 'react'
import ContactInfo from '../layout/ContactInfo'
import Layout from "../layout/Layout"

const ExpiredPage = () => {
    useEffect(() => {
        window.scrollTo(0, 0)
    }, [])
    return(
        <Layout currentTab={''} name={''} stepContent={''}>
            <div className='text-center mt-5 pt-5 invalid-page'>
                <h4>This link has expired, please contact the customer support team to re-activate the link.</h4>
                <ContactInfo/>
            </div>
        </Layout>
    )
}

export default ExpiredPage