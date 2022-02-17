import React from 'react';


const ContentHeader = ({name,stepContent}) => {
    if(!name){
        return('')
    }
	return(
		<div className="content-head mt-5">
            <div className="container-fluid ms-md-2">
                <h3>Hi {name},</h3>
                <p className="text-fade-grey">{stepContent}</p>
            </div>
        </div>
	)
}

export default ContentHeader;