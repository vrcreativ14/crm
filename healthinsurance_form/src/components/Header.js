import React from 'react';
import NexusLogo from '../assets/nexus-logo.svg'

const Header = () => {
    return(
        <header className="header">
            <div className="container d-flex justify-content-between">
                <img src={NexusLogo} alt="nexus"/>
                <div>
                    <p className="mb-0"><small>Need some help? Call us</small></p>
                    <a href="tel:97143231111">+971 4 323 1111</a>
                </div>
            </div>
        </header>
    )
}

export default Header;