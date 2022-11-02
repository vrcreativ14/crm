import React, { useState } from 'react';

const CollapseDetails = ({children,title = false,insurar = false,insurar1 = false,defaultTab = false}) => {
    const[collapse,setCollapse] = useState(defaultTab)
    return(
        <li className={(collapse) ? 'open-tab':'close-tab'}>
            {title &&
            <div className='tab d-flex w-100'>
                <label className='fw-bold'>{title}</label>
                {insurar && <strong className='text-light-grey w-100'>{insurar}</strong>}
                {insurar1 && <strong className='text-light-grey w-100'>{insurar1}</strong>}
                <span className='w-100 text-end' onClick={() => setCollapse(!collapse)}><i className="fas fa-chevron-circle-up"></i><i className="fas fa-chevron-circle-down"></i></span>
            </div>}
            <div className='overlay-content'>
                <div className={(collapse && title) ? 'content-div animate__animated animate__fadeIn':(title) ? 'content-div animate__animated animate__fadeOut':'content-div'}>
                    <table className="table table-hover table-striped mb-0">
                        <tbody>{children}</tbody>
                    </table>
                </div>
            </div>
        </li>
    )
}

export default CollapseDetails