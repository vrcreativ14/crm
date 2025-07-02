import React, { useEffect } from 'react'
import Layout from "../layout/Layout"

const LoadingPage = () => {
    useEffect(() => {
        window.scrollTo(0, 0)
    }, [])
    return(
        <Layout currentTab={''} name={''} stepContent={''}>
            <div className='text-center mt-5 pt-5 loading-page d-flex align-items-center justify-content-center'>
                <span className='fs-4 fw-bold'>Loading</span> <i className="ms-3 text-golden fa-3x fas fa-circle-notch fa-spin"></i>
            </div>
        </Layout>
    )
}

export default LoadingPage