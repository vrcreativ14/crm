import React, { useState } from 'react'
import parse from 'html-react-parser';

const DocumentSection = ({children,title = false,defaultTab = false}) => {
    const[DocumentSection,SetdocumentSection] = useState(defaultTab)
    return(
        <div className='insurer-info shadow-1 header-content'>
            <div className='details-benefits'>
                <div className={(DocumentSection) ? 'open-tab':'close-tab'}>
                    {title &&
                    <div className='tab mb-3 d-flex w-100 align-items-center'>
                        <label className='fw-bold mt-2 mb-2 text-capitalize'>{parse(title)}</label>
                        <span className='w-100 text-end' onClick={() => SetdocumentSection(!DocumentSection)}><i className="fas fa-chevron-circle-up"></i><i className="fas fa-chevron-circle-down"></i></span>
                    </div>}
                    <div className='overlay-content m-3'>
                        <div className={(DocumentSection && title) ? 'content-div animate__animated animate__fadeIn':(title) ? 'content-div animate__animated animate__fadeOut':'content-div'}>
                            <div className='row'>{children}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
export default DocumentSection