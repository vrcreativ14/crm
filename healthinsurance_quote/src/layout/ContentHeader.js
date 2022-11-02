import React from 'react';
import parse from 'html-react-parser';

const ContentHeader = ({name,stepContent}) => {
    if(!name){
        return('')
    }
	return(
		<div className="content-head mt-5">
            <div className="container-fluid ms-md-2">
                <h3>{parse(name)}</h3>
                <p className="text-fade-grey fs-6">{parse(stepContent)}</p>
            </div>
        </div>
	)
}

export default ContentHeader;