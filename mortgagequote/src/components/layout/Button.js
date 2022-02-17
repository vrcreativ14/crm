import React, { useContext } from "react"
import { BrowserRouter as Router, useParams, useHistory } from "react-router-dom"
import { DataContext } from '../../helpers/context.js'
import api from "../../helpers/axios.js"
import { store } from 'react-notifications-component'

const SelectButton = ({indexID = '',url = '',text = ''}) => {
    const[data, setData, uploadDoc, setuploadDoc] = useContext(DataContext)
    let { id, secretCode, quoteID } = useParams()
	const navigate = useHistory()
    let subStages = {}
    subStages['Waiting for Pre Approval Documments'] = 'WAIT_PREAPPROVAL_DOC';
    subStages['Waiting for Valuation Documents'] = 'WAITING_FOR_VALUATION_DOCUMENTS';

    const csrfmiddlewaretoken = document.getElementById("sub-stage-csrf").children[0].value

    const updateDB = async () => {
        if(url=='preApproval'){
            var fromData = new FormData();
            fromData.append('bank', data.quote_details[quoteID].bank_pk);
            fromData.append('deal', parseInt(id));
            fromData.append('stage', 'quote');
            let fieldMessage = false
            if('name' in uploadDoc && uploadDoc.name!=''){
                fromData.append('customer_name', uploadDoc.name);
                var fromData_name = new FormData();
                fromData_name.append('ajax', true);
                fromData_name.append('name', 'name');
                fromData_name.append('value', uploadDoc.name);
                fromData_name.append('pk', data.customer_info.id);
                try{
                    const { data: res } = await api.post('/people/update-field/'+data.customer_info.id+'/customer/',fromData_name)
                } catch(e){

                }
            }else{
                fieldMessage = 'Name is required'
            }
            if('email' in uploadDoc && uploadDoc.email!=''){
                fromData.append('customer_email', uploadDoc.email);
                var fromData_name = new FormData();
                fromData_name.append('ajax', true);
                fromData_name.append('name', 'email');
                fromData_name.append('value', uploadDoc.email);
                fromData_name.append('pk', data.customer_info.id);
                try{
                    const { data: res } = await api.post('/people/update-field/'+data.customer_info.id+'/customer/',fromData_name)
                } catch(e){

                }
            }else{
                fieldMessage = 'Email address is required'
            }
            if('phone' in uploadDoc && uploadDoc.phone!=''){
                fromData.append('customer_phone', uploadDoc.phone);
                var fromData_name = new FormData();
                fromData_name.append('ajax', true);
                fromData_name.append('name', 'phone');
                fromData_name.append('value', uploadDoc.phone);
                fromData_name.append('pk', data.customer_info.id);
                try{
                    const { data: res } = await api.post('/people/update-field/'+data.customer_info.id+'/customer/',fromData_name)
                } catch(e){

                }
            }else{
                fieldMessage = 'Phone number is required'
            }
            if(fieldMessage){
                return store.addNotification({
                    title: "Error!",
                    message: fieldMessage,
                    type: "danger",
                    insert: "top",
                    container: "top-right",
                    animationIn: ["animate__animated", "animate__fadeIn"],
                    animationOut: ["animate__animated", "animate__fadeOut"],
                    dismiss: {
                    duration: 0,
                    onScreen: true,
                    showIcon: true
                    }
                });
            }
            try{
                const { data: res } = await api.post('mortgage/stage/',fromData)
            } catch(e){
                let message = "Something went wrong please contact us on the above number."
                if(data.customer_info.email==''){
                    message = "Email address is required"
                }
                return store.addNotification({
                    title: "Error!",
                    message: message,
                    type: "danger",
                    insert: "top",
                    container: "top-right",
                    animationIn: ["animate__animated", "animate__fadeIn"],
                    animationOut: ["animate__animated", "animate__fadeOut"],
                    dismiss: {
                    duration: 0,
                    onScreen: true,
                    showIcon: true
                    }
                });
            }
            setuploadDoc({})
        }


        if(url=='valuation'){
            const files = {'passport':'Passport',
            'salary-certificate':'Salary Certificate',
            'visa':'Visa',
            'bank-statement':'Bank Statement',
            'emirates-id-front':'Emirates ID Front',
            'payslips':'Payslips',
            'emirates-id-back':'Emirates ID Back',
            'bank-application-form':'Bank Application Form'}
            let gotAllFiles = true
            Object.keys(files).map((index) => {
                if(!(index in uploadDoc)){
                    gotAllFiles = false
                    return store.addNotification({
                        title: "Error!",
                        message: files[index]+' is required',
                        type: "danger",
                        insert: "top",
                        container: "top-right",
                        animationIn: ["animate__animated", "animate__fadeIn"],
                        animationOut: ["animate__animated", "animate__fadeOut"],
                        dismiss: {
                        duration: 5000,
                        onScreen: true,
                        showIcon: true
                        }
                    });
                }
            })
            if(!gotAllFiles){return}
            // var fromData = new FormData();
            // fromData.append('deal', parseInt(id));
            // console.log(uploadDoc)
            // Object.values(uploadDoc).forEach(file => {
            //     fromData.append('file', file[0]);
            // })
            // file_name.map((file_name) => {
            //     fromData.append('file_names', file_name);
            // })
            try{
                Object.keys(uploadDoc).forEach(index => {
                    uploadDoc[index].map(async (file) => {
                        console.log(file)
                        var fromData = new FormData();
                        fromData.append('file', file);
                        await api.post('mortgage/deals/'+id+'/attachment/add/preapproval/?type='+index,fromData,{headers: { 'Content-Type': 'multipart/form-data'}})
                    })
                })
            } catch(e){
                let message = "Something went wrong please contact us on the above number."
                if(data.customer_info.email==''){
                    message = "Email address is required"
                }
                return store.addNotification({
                    title: "Error!",
                    message: message,
                    type: "danger",
                    insert: "top",
                    container: "top-right",
                    animationIn: ["animate__animated", "animate__fadeIn"],
                    animationOut: ["animate__animated", "animate__fadeOut"],
                    dismiss: {
                    duration: 0,
                    onScreen: true,
                    showIcon: true
                    }
                });
            }

            try{
                var fromDataStage = new FormData();
                fromDataStage.append('deal', parseInt(id));
                fromDataStage.append('sub_stage', subStages[data.sub_stage.sub_stage]);
                fromDataStage.append('change_sub_stage', 'SENT_TO_BANK_FOR_PREAPPROVAL');
                fromDataStage.append('csrfmiddlewaretoken', csrfmiddlewaretoken);
                const { data: resStage } = await api.post('mortgage/substage/',fromDataStage)
            } catch(e){
                let message = "Something went wrong please contact us on the above number."
                if(data.customer_info.email==''){
                    message = "Email address is required"
                }
                return store.addNotification({
                    title: "Error!",
                    message: message,
                    type: "danger",
                    insert: "top",
                    container: "top-right",
                    animationIn: ["animate__animated", "animate__fadeIn"],
                    animationOut: ["animate__animated", "animate__fadeOut"],
                    dismiss: {
                    duration: 0,
                    onScreen: true,
                    showIcon: true
                    }
                });
            }

            store.addNotification({
                title: "Success!",
                message: 'Uploaded successfully.',
                type: "success",
                insert: "top",
                container: "top-right",
                animationIn: ["animate__animated", "animate__fadeIn"],
                animationOut: ["animate__animated", "animate__fadeOut"],
                dismiss: {
                duration: 5000,
                onScreen: true,
                showIcon: true
                }
            });
        }


        if(url=='underProcess'){
            const files = {'memorandum-of-understanding':'Memorandum of Understanding','property-title-deed':'Property title deed'}
            let gotAllFiles = true
            Object.keys(files).map((index) => {
                if(!(index in uploadDoc)){
                    gotAllFiles = false
                    return store.addNotification({
                        title: "Error!",
                        message: files[index]+' is required',
                        type: "danger",
                        insert: "top",
                        container: "top-right",
                        animationIn: ["animate__animated", "animate__fadeIn"],
                        animationOut: ["animate__animated", "animate__fadeOut"],
                        dismiss: {
                        duration: 5000,
                        onScreen: true,
                        showIcon: true
                        }
                    });
                }
            })
            if(!gotAllFiles){return}
            // var fromData = new FormData();
            // fromData.append('deal', parseInt(id));
            // console.log(uploadDoc)
            // Object.values(uploadDoc).forEach((file) => {
            //     fromData.append('file', file[0]);
            // })
            // file_name.map((file_name,index) => {
            //     if(index in uploadDoc){
            //         fromData.append('file_names', file_name);
            //     }
            // })
            try{
                Object.keys(uploadDoc).forEach(index => {
                    uploadDoc[index].map(async (file) => {
                        console.log(file)
                        var fromData = new FormData();
                        fromData.append('file', file);
                        await api.post('mortgage/deals/'+id+'/attachment/add/postapproval/?type='+index,fromData,{headers: { 'Content-Type': 'multipart/form-data'}})
                    })
                })
            } catch(e){
                let message = "Something went wrong please contact us on the above number."
                if(data.customer_info.email==''){
                    message = "Email address is required"
                }
                return store.addNotification({
                    title: "Error!",
                    message: message,
                    type: "danger",
                    insert: "top",
                    container: "top-right",
                    animationIn: ["animate__animated", "animate__fadeIn"],
                    animationOut: ["animate__animated", "animate__fadeOut"],
                    dismiss: {
                    duration: 0,
                    onScreen: true,
                    showIcon: true
                    }
                });
            }

            try{
                var fromDataStage = new FormData();
                fromDataStage.append('deal', parseInt(id));
                fromDataStage.append('sub_stage', subStages[data.sub_stage.sub_stage]);
                fromDataStage.append('change_sub_stage', 'SENT_TO_BANK_FOR_APPROVAL');
                fromDataStage.append('csrfmiddlewaretoken', csrfmiddlewaretoken);
                const { data: resStage } = await api.post('mortgage/substage/',fromDataStage)
            } catch(e){
                let message = "Something went wrong please contact us on the above number."
                if(data.customer_info.email==''){
                    message = "Email address is required"
                }
                return store.addNotification({
                    title: "Error!",
                    message: message,
                    type: "danger",
                    insert: "top",
                    container: "top-right",
                    animationIn: ["animate__animated", "animate__fadeIn"],
                    animationOut: ["animate__animated", "animate__fadeOut"],
                    dismiss: {
                    duration: 0,
                    onScreen: true,
                    showIcon: true
                    }
                });
            }

            store.addNotification({
                title: "Success!",
                message: 'Uploaded successfully.',
                type: "success",
                insert: "top",
                container: "top-right",
                animationIn: ["animate__animated", "animate__fadeIn"],
                animationOut: ["animate__animated", "animate__fadeOut"],
                dismiss: {
                duration: 5000,
                onScreen: true,
                showIcon: true
                }
            });
        }
        if(url=='valuation'){
            url = 'preApproval'
        }else if(url=='underProcess'){
            url = 'valuation'
        }
        if(url!='mortgageSummary'){
            return navigate.push('/mortgage-quote/'+secretCode+'/'+id+'/')
        }
        return navigate.push('/mortgage-quote/'+secretCode+'/'+id+'/'+url+'/'+indexID)
    }
    return(
        <button className="btn-nexus btn-golden" onClick={() => updateDB()}>{text}</button>
    )
}

export default SelectButton