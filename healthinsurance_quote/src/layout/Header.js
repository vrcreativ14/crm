import React from 'react';
import NexusLogo from '../assets/nexus-logo.svg'
import ContactInfo from './ContactInfo';

const Header = () => {
    return(
        <header className="header">
            <img src={NexusLogo} alt="nexus"/>
            <ContactInfo/>
        </header>
    )
}

export default Header;