import React, { useEffect, useState } from 'react'
import parse from 'html-react-parser';

const UploadDoc = ({setuploadDoc,uploadDoc,name,filekey,desc,info = false,required = true,classCustom = 'col-md-6 mb-3'}) => {
    const[hasFile,setHasFile] = useState([])
    const[dragAction,setDragAction] = useState(false)

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
        setDragAction(false)
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
        <div className={classCustom}>
            {(hasFile && hasFile.length>0) ? 
            <div className="parent-file-upload shadow-1-strong">
                <div className={(dragAction) ? "uploading file-upload":"file-upload"} onDragOver={() => {(!dragAction) && setDragAction(true)}} onDragLeave={() => {(dragAction) && setDragAction(false)}}>
                    <span className="name">
                        <i className="far fa-file"></i>
                        <span className="ms-2">
                            {name}
                            {(required) ? '*':null}
                            {(info) && <span className='info-content'><i className="text-fade-grey ms-1 fas fa-info-circle"></i><span className='info-text shadow-1'>{info}</span></span>} 
                            <br/><small>{parse(desc)}</small><span className="uploader"></span>
                        </span>
                    </span>
                    <span className="file">
                        <label>
                            <i className="fas fa-cloud-upload-alt"></i>
                            <small>Drag and Drop or Browse</small>
                        </label>
                    </span>
                    <span className="drag-action-text">Drop</span>
                    <input type="file" onChange={(event) => setUploadState(event)} multiple required={(required && !(filekey in uploadDoc && uploadDoc[filekey].length>0)) ? true:false}/>
                </div>
                {hasFile.map((file,index) => {
                    return(
                        <div className="file-upload border-0 done" key={'files-'+filekey+index}>
                            <div className="d-flex">
                                <span className="name">
                                    <i className="far fa-file"></i>
                                </span>
                                <span className="file">
                                    <label className="bg-white pt-0 pb-0 pe-3 mb-3 text-start">{file['name']}<i onClick={() => removeFile(index)} className="float-end far fa-times-circle"></i><span className="uploader"></span></label>
                                </span>
                            </div>
                        </div>
                    )
                })}
            </div>
            :
            <div className={(dragAction) ? "uploading file-upload shadow-1-strong":"file-upload shadow-1-strong"} onDragOver={() => {(!dragAction) && setDragAction(true)}} onDragLeave={() => {(dragAction) && setDragAction(false)}}>
                <span className="name">
                    <i className="far fa-file"></i>
                    <span className="ms-2 fs-6">
                        {name}
                        {(required) ? '*':null}
                        {(info) && <span className='info-content'><i className="text-fade-grey ms-1 fas fa-info-circle"></i><span className='info-text shadow-1'>{info}</span></span>}
                        <br/><small>{parse(desc)}</small><span className="uploader"></span>
                    </span>
                </span>
                <span className="file">
                    <label>
                        <i className="fas fa-cloud-upload-alt"></i>
                        <small>Drag and Drop or Browse</small>
                    </label>
                </span>
                <span className="drag-action-text">Drop</span>
                <input type="file" onChange={(event) => setUploadState(event)} multiple required={(required && !(filekey in uploadDoc && uploadDoc[filekey].length>0)) ? true:false}/>
            </div>
            }
        </div>
    )
}

export default UploadDoc