import React, { useEffect, useState } from 'react'
import parse from 'html-react-parser';

const UploadDoc = ({setuploadDoc,uploadDoc,name,filekey,desc,required = true}) => {
    const[hasFile,setHasFile] = useState([])

    useEffect(() => {
        setHasFile(uploadDoc[filekey])
    },[hasFile])

    function setUploadState(event){
        var newData = uploadDoc
        Object.values(event.target.files).forEach(file => {
            if(filekey in newData){
                newData[filekey].push(file)
            }else{
                newData[filekey] = [file]
            }
        })
        setuploadDoc(newData)
        setHasFile([])
    }

    function removeFile(index){
        var newData = uploadDoc
        newData[filekey] = newData[filekey].filter((file,keyIndex) => {
            if(index==keyIndex){
                return false
            }
            return file
        }).map((file) => {return(file)});
        setuploadDoc(newData)
        setHasFile(newData[filekey])
    }

    return(
        <div className="col-md-6 mb-3">
            {(hasFile && hasFile.length>0) ? 
            <div className="parent-file-upload">
                <div className="file-upload shadow-1">
                    <span className="name">
                        <i className="far fa-file"></i>
                        <span className="ms-2">
                            {name}{(required) ? '*':null}<br/><small>{desc && parse(desc)}</small><br/><span className="uploader"></span>
                        </span>
                    </span>
                    <span className="file">
                        <label>
                            <i className="fas fa-cloud-upload-alt"></i>
                            <small>Drag and Drop or Browse</small>
                            <input type="file" onChange={(event) => setUploadState(event)} multiple/>
                        </label>
                    </span>
                </div>
                {hasFile.map((file,index) => {
                    return(
                        <div className="file-upload border-0 done" key={'files-'+filekey+index}>
                            <div className="d-flex">
                                <span className="name">
                                    <i className="far fa-file"></i>
                                </span>
                                <span className="file">
                                    <label className="bg-white pt-0 pb-0 pe-3 mb-3 text-start">{file['name']}<i onClick={() => removeFile(index)} className="float-end far fa-times-circle"></i></label>
                                </span>
                            </div>
                        </div>
                    )
                })}
            </div>
            :
            <div className="file-upload shadow-1">
                <span className="name">
                    <i className="far fa-file"></i>
                    <span className="ms-2">
                        {name}{(required) ? '*':null}<br/><small>{desc && parse(desc)}</small><br/><span className="uploader"></span>
                    </span>
                </span>
                <span className="file">
                    <label>
                        <i className="fas fa-cloud-upload-alt"></i>
                        <small>Drag and Drop or Browse</small>
                        <input type="file" onChange={(event) => setUploadState(event)} multiple/>
                    </label>
                </span>
            </div>
            }
        </div>
    )
}

export default UploadDoc