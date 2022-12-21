import React, { useRef, useState } from 'react';
import RequestHandler from '../helper/RequestHandler';

const ContactForm = () => {
    const[loader,setLoader] = useState(false)
    const closeRef = useRef();

    async function handleContactFormSubmission(event){
        event.preventDefault()
        // var rawData = new FormData(event.currentTarget)
        // const { data: res } = await RequestHandler.post('health-insurance/quote-api/',rawData,{headers: { 'Content-Type': 'multipart/form-data'}})
        // setLoader(false)
        // if(res.success){
        //     Notifications('Success','Your query has been received, one of our customer representative will contact you within 24hours.','success')
        //     closeRef.current.click()
        // }else{
        //     Notifications('Error','Something went wrong, pls contact us directly.','error')
        //     closeRef.current.click()
        // }
    }

    return(
        <>
            <div className="modal fade" id="exampleModal" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
            <div className="modal-dialog">
                <div className="modal-content">
                    <div className="modal-header">
                        <h5 className="modal-title text-golden" id="exampleModalLabel">Contact Form</h5>
                        <button ref={closeRef} type="button" className="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                    </div>
                    <div className="modal-body">
                        <form action='' method='post' onSubmit={(event) => handleContactFormSubmission(event)}>
                            <input type="text" name="name" className='form-control' placeholder='Enter your name*' required/>
                            <input type="email" name="email" className='form-control mt-2' placeholder='Enter your email address*' required/>
                            <input type="text" name="phone" className='form-control mt-2' placeholder='Enter your phone number*' required/>
                            <textarea name='message' className='form-control mt-2' required placeholder='Your message*'></textarea>
                            <button type={(!loader) ? "submit":"button"} class="btn-nexus btn-golden mt-2">Submit{loader ? <i className="ms-1 fas fa-circle-notch fa-spin"></i>:''}</button>
                        </form>   
                    </div>
                </div>
            </div>
            </div>
        </>
    )
}

export default ContactForm