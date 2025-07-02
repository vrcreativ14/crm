import React, { useEffect } from 'react'
import ContactInfo from '../layout/ContactInfo'
import Layout from "../layout/Layout"

const InvalidPage = () => {
    useEffect(() => {
        window.scrollTo(0, 0)
    }, [])
    return(
        <Layout currentTab={''} name={''} stepContent={''}>
            <div className='text-center mt-5 pt-5 invalid-page'>
                <h2>Page Not found</h2>
                <ContactInfo/>
            </div>
        </Layout>
    )
}

export default InvalidPage