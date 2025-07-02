import React from 'react';
import NexusLogo from '../../assets/nexus-logo.svg'

const Header = () => {
    return(
        <header className="header">
            <img src={NexusLogo} alt="nexus"/>
            <div>
                <p className="mb-0"><small>Need some help? Call us</small></p>
                <a href="tel:97142378294">+971 4 237 8294</a>
            </div>
        </header>
    )
}

export default Header;