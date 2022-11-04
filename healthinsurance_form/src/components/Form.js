import React, { useEffect, useRef, useState } from 'react';
import api from '../helper/axios';
import AddtionalMemebers from './AddtionalMembers';
import FormFields from './FormFields';
import { Notification } from './Notification';
import SelectListLabel from './SelectListLable';
import { useParams } from 'react-router-dom'

const Form = () => {
    const[formData, setFormData] = useState({})
    const[currentSection, setCurrentSection] = useState(1)
    const[submitting, setSubmitting] = useState(false)
    const primaryRef = useRef(null)
    const memberRef = useRef(null)
    const policyRef = useRef(null)
    const{ id, deal_id } = useParams()

    useEffect(() => {
        async function getDeal(){
            if(deal_id){
                const { data: quoteData } = await api.get('/health-insurance/insurers/'+deal_id+'/basic-plans')

                let dealData = {}
                dealData['name'] = quoteData.primary_member.name
                dealData['email'] = quoteData.primary_member.email
                dealData['phone'] = quoteData.primary_member.phone
                dealData['gender'] = quoteData.primary_member.gender
                const d = new Date(quoteData.primary_member.dob)
                dealData['dob'] = d
                dealData['dobs'] = d.getDate()+ "/"+(d.getMonth()+1)+"/"+d.getFullYear()
                dealData['marital_status'] = quoteData.primary_member.marital_status
                dealData['country_of_stay'] = quoteData.primary_member.country_of_stay
                dealData['nationality'] = quoteData.primary_member.nationality
                dealData['salary_band'] = quoteData.primary_member.salary_band
                dealData['visa'] = (visa.filter(emirates => emirates.label.toLowerCase()==quoteData.primary_member.visa.toLowerCase())) ? visa.filter(emirates => emirates.label.toLowerCase()==quoteData.primary_member.visa.toLowerCase())[0].value:''

                dealData['geographical_coverage'] = quoteData.deal.geographical_coverage.toLowerCase()
                dealData['indicative_budget'] = (quoteData.deal.indicative_budget.toLowerCase()).replace(" ","")
                dealData['level_of_cover'] = quoteData.deal.level_of_cover
                dealData['other_benefits'] = (quoteData.deal.other_benefits) ? quoteData.deal.other_benefits.toString():''
                if(quoteData.deal.start_date){
                    const s = new Date(quoteData.deal.start_date)
                    dealData['start_date'] = s
                    dealData['start_dates'] = s.getDate()+ "/"+(s.getMonth()+1)+"/"+s.getFullYear()
                }
                dealData['preferred_hospitals'] = quoteData.primary_member.preferred_hospitals

                if(quoteData.additional_members){
                    dealData['total_members'] = quoteData.additional_members.length
                    dealData['additional_members'] = []
                    quoteData.additional_members.map((member,index) => {
                        dealData['additional_members'][index] = {}
                        dealData['additional_members'][index]['relation'] = member.relation
                        dealData['additional_members'][index]['member-relation'] = member.relation
                        dealData['additional_members'][index]['name'] = member.name
                        dealData['additional_members'][index]['member-name'] = member.name
                        let m = new Date(member.dob)
                        dealData['additional_members'][index]['dobs'] = m
                        dealData['additional_members'][index]['member-dobs'] = m
                        dealData['additional_members'][index]['dob'] = m.getDate()+ "/"+(m.getMonth()+1)+"/"+m.getFullYear()
                        dealData['additional_members'][index]['member-dob'] = m.getDate()+ "/"+(m.getMonth()+1)+"/"+m.getFullYear()
                        dealData['additional_members'][index]['nationality'] = member.nationality
                        dealData['additional_members'][index]['member-nationality'] = member.nationality
                        dealData['additional_members'][index]['country_of_stay'] = member.country_of_stay
                        dealData['additional_members'][index]['member-country_of_stay'] = member.country_of_stay
                    })
                }

                setFormData(dealData)
                setFormData(prevState => ({...prevState,data:0}))

                setTimeout(() => {
                    policyRef.current.scrollIntoView()
                    Notification('Message','Change the type of cover to "Comprehensive" and Indicative Budget to more than 2K AED.','info',15000)
                },500)
            }
        }
        getDeal()
    },[])

    useEffect(() => {
        const handleScroll = () => {
            const currentScrollY = window.scrollY;
            if(policyRef.current.offsetTop<currentScrollY){
                if(currentSection!=3)setCurrentSection(3)
                return
            }
            if(memberRef.current.offsetTop<currentScrollY){
                if(currentSection!=2)setCurrentSection(2)
                return
            }
            if(currentSection!=1){
                setCurrentSection(1)
            }
        }
      
        window.addEventListener("scroll", handleScroll, { passive: true })
      
        return () => window.removeEventListener("scroll", handleScroll);
    });

    const gender = [
        {label:'Select gender',value:''},
        {label:'Male',value:'m'},
        {label:'Female',value:'f'},
    ]

    const status = [
        {label:'Select marital status',value:''},
        {label:'Single',value:'single'},
        {label:'Married',value:'married'}
    ]

    const visa = [
        {label:'Select visa',value:''},
        {label:'Dubai',value:'DU'},
        {label:'Abu Dhabi',value:'AD'},
        {label:'Sharjah',value:'SJ'},
        {label:'Ajman',value:'AJ'},
        {label:'Ras Al Khaimah',value:'RK'},
        {label:'Fujairah',value:'FJ'},
        {label:'Umm Al Quwain',value:'UQ'}
    ]

    const salary = {
        'AE':[
            {label:'Select salary band',value:''},
            {label:'Below 4000 AED',value:'below_4k'},
            {label:'Above 4000 AED',value:'above_4k'}
        ],
        'BH':[
            {label:'Select salary band',value:''},
            {label:'Below 400 BD',value:'below_4k'},
            {label:'Above 400 BD',value:'above_4k'}
        ],
        'QA':[
            {label:'Select salary band',value:''},
            {label:'Below 4000 QR',value:'below_4k'},
            {label:'Above 4000 QR',value:'above_4k'}
        ],
        'KW':[
            {label:'Select salary band',value:''},
            {label:'Below 350 KWD',value:'below_4k'},
            {label:'Above 350 KWD',value:'above_4k'}
        ],
        'JO':[
            {label:'Select salary band',value:''},
            {label:'Below 20,000 JOD',value:'below_4k'},
            {label:'Above 20,000 JOD',value:'above_4k'}
        ],
    }

    const geo = [
        {label:'Select geographical coverage',value:''},
        {label:'Local',value:'local'},
        {label:'Regional',value:'regional'},
        {label:'Worldwide Except US',value:'worldwide_except_us'},
        {label:'Worldwide',value:'worldwide'}
    ]

    const benefits = [
        // {label:'Select additional benefits',value:''},
        {label:'Health Screening',value:'health_screen'},
        {label:'Dental',value:'dental'},
        {label:'Optical',value:'optical'},
        {label:'Other',value:'other'}
    ]

    const buget = [
        {label:'Select budget',value:''},
        {label:'Below 1K AED',value:'below1k'},
        {label:'2-4K AED',value:'2to4k'},
        {label:'4-8K AED',value:'4to8k'},
        {label:'8K+',value:'8kplus'},
        // {label:'Not Sure',value:'notsure'}
    ]

    const cover = [
        {label:'Select cover',value:''},
        {label:'Comprehensive',value:'comprehensive'},
        {label:'Basic',value:'basic'}
    ]

    function membersArray(){
        let data = formData.additional_members
        formData.additional_members.map((member,index) => {
            if(!('nationality' in data[index]))data[index]['nationality'] = formData.nationality
            if(!('country_of_stay' in data[index]))data[index]['country_of_stay'] = formData.country_of_stay
            data[index]['order'] = index+1
        })
        return JSON.stringify(data)
    }

    async function handleSubmit(event){
        event.preventDefault()
        const csrfmiddlewaretoken = document.getElementById("sub-stage-csrf").children[0].value

        if(!('country_of_stay' in formData) || !formData.country_of_stay){
            return Notification('Country of stay is required.','Error','danger')
        }
        if(!('nationality' in formData) || !formData.nationality){
            return Notification('Nationality is required.','Error','danger')
        }

        if(deal_id && (formData.level_of_cover=='basic' || formData.indicative_budget=='below1k')){
            policyRef.current.scrollIntoView()
            return Notification('Message','Change the type of cover to "Comprehensive" and Indicative Budget to more than 2K AED inorder to proceed.','danger',15000)
        }
        
        setSubmitting(true)

        var rawData = new FormData(event.currentTarget)

        rawData.append('csrfmiddlewaretoken', csrfmiddlewaretoken)
        rawData.append('stage', 'new')
        rawData.append('premium', 0)
        rawData.append('additional_benefits', formData.additional_benefits)
        rawData.append('additional_members', (!('additional_members' in formData)) ? '':membersArray())

        if(deal_id){
            const { data: res } = await api.post('/health-insurance/deals/edit/'+deal_id,rawData)
            if(res.success)return window.location.href = "https://forms.nexusadvice.com/thank-you/";
            return Notification('Response',(res.success) ? 'Success':'Error',(res.success) ? 'success':'danger')
        }
        const { data: res } = await api.post('/health-insurance/deals/add',rawData)
        // if(res.success){
        //     await api.post('/health-insurance/deals/'+res.deal+'/email/new deal/',rawData)
        // }

        Notification('Response',(res.success) ? 'Success':'Error',(res.success) ? 'success':'danger')
        setSubmitting(false)
        if(res.success && formData.indicative_budget=='below1k')return window.location.href = "/health-insurance-quote/"+res.quote_reference_number+'/'+res.deal;
        if(res.success)return window.location.href = "https://forms.nexusadvice.com/thank-you/";
    }

    // console.log(formData.additional_members)

    return(
        <div className="row">
            <div className="col-12 col-md-7">
                <div className="static-form">
                    <div className="header-content">
                        <h2>Get Your Health Insurance Quote</h2>
                        <p>Nexus offers a variety of medical plans from the best providers. In order to help us provide you with an optimal quote that meets all your requirements, please take a few minutes to answer this questionnaire.</p>
                    </div>
                    <form onSubmit={(event) => handleSubmit(event)} action='' method='post'>
                        <div ref={primaryRef} onClick={() => setCurrentSection(1)}>
                            <h4 className="sub-title">Primary member details</h4>
                            <FormFields type="text" name="name" labelName="Full Name" placeholder="Enter First Name and Last Name" formData={formData} setFormData={setFormData}/>
                            <FormFields type="text" name="phone" labelName="Phone" placeholder="Enter Phone Number" formData={formData} setFormData={setFormData}/>
                            <FormFields type="email" name="email" labelName="Email" placeholder="Enter Email Address" formData={formData} setFormData={setFormData}/>
                            <FormFields type="select" name="gender" labelName="Gender" options={gender} formData={formData} setFormData={setFormData}/>
                            <FormFields type="select" name="marital_status" labelName="Marital Status" options={status} formData={formData} setFormData={setFormData}/>
                            <FormFields type="date" name="dob" labelName="Date of Birth" formData={formData} setFormData={setFormData}/>
                            <FormFields type="flag" name="nationality" labelName="Nationality" placeholder="Select the country" formData={formData} setFormData={setFormData} defaultValue={('nationality' in formData) ? formData.nationality:false}/>
                            {/* <FormFields country_of_stay={true} type="flag" name="country_of_stay" labelName="Country of Residence" placeholder="Select the country" formData={formData} setFormData={setFormData}/> */}
                            <FormFields type="flag" name="country_of_stay" labelName="Country of Residence" placeholder="Select the country" formData={formData} setFormData={setFormData} defaultValue={('country_of_stay' in formData) ? formData.country_of_stay:false}/>
                            {(!formData || !('country_of_stay' in formData) || ('country_of_stay' in formData && formData.country_of_stay=='AE')) && <FormFields type="select" name="visa" labelName="Visa" options={visa} formData={formData} setFormData={setFormData}/>}
                            <FormFields type="select" name="salary_band" labelName="Salary Band" options={('country_of_stay' in formData && formData.country_of_stay in salary) ? salary[formData.country_of_stay]:salary['AE']} formData={formData} setFormData={setFormData}/>
                        </div>
                        <div ref={memberRef} className="mb-5 mt-5 pt-3 pb-4" onClick={() => setCurrentSection(2)}>
                            <h4 className="sub-title mb-2">Any additional members to be added?</h4>
                            <AddtionalMemebers formData={formData} setFormData={setFormData}/>
                        </div>
                        <div ref={policyRef} onClick={() => setCurrentSection(3)}>
                            <h4 className="sub-title">Policy coverage</h4>
                            {(deal_id) ? <div className='outline-highlight'><FormFields type="select" name="level_of_cover" labelName="Type of Cover" options={cover} formData={formData} setFormData={setFormData}/></div>:<FormFields type="select" name="level_of_cover" labelName="Type of Cover" options={cover} formData={formData} setFormData={setFormData}/>
                            }
                            <FormFields type="select" name="geographical_coverage" labelName="Geographical Coverage" options={geo} formData={formData} setFormData={setFormData}/>
                            <FormFields isRequired={false} type="multipleSelect" name="additional_benefits" labelName="Additional Benefits" options={benefits} formData={formData} setFormData={setFormData} isMultiple={true}/>
                            {('additional_benefits' in formData && formData.additional_benefits.filter((benefits) => benefits == 'other').length>0) && <FormFields type="text" name="other_benefits" labelName="Other Benefits" formData={formData} setFormData={setFormData} placeholder="Enter other benefits"/>}
                            {(deal_id) ? <div className='outline-highlight'><FormFields type="select" name="indicative_budget" labelName="Indicative Budget" options={buget} formData={formData} setFormData={setFormData}/></div>:<FormFields type="select" name="indicative_budget" labelName="Indicative Budget" options={buget} formData={formData} setFormData={setFormData}/>}
                            <FormFields isRequired={false} type="date" name="start_date" labelName="When would you like the policy to start" formData={formData} setFormData={setFormData}/>
                            <FormFields isRequired={false} type="textarea" name="preferred_hospitals" placeholder='Please seperate hospital or clinic name by comma for multiple values.' labelName="Preferred Hospitals/ Clinics" formData={formData} setFormData={setFormData}/>
                        </div>
                        <input type="hidden" name="referrer" value={(id) ? id:''}/>
                        {submitting ? <button type="button" className="btn-nexus btn-golden">Submit<i class="ms-1 fas fa-circle-notch fa-spin"></i></button>:
                        <button type="submit" className="btn-nexus btn-golden">Submit</button>}
                    </form>
                </div>
            </div>
            <div className="col-12 col-md-5 bg-grey d-none d-md-block">
                <div className='sticky-parent-div'>
                    <div onClick={() => {setCurrentSection(1),primaryRef.current.scrollIntoView()}} className={(currentSection==1) ? "sticky-div active":"sticky-div"}>
                        <div className="row">
                            <div className="col-3 pe-4">
                                <div className="number">1</div>
                            </div>
                            <div className="col-9">
                                <div className="content shadow-1-strong">
                                    <h6 className="sticky-content-title">Primary member details<span className='float-end'><i className="fas fa-pen"></i></span></h6>
                                    <div className="inner-details">
                                    {('name' in formData && formData.name) && <span><strong>Name: </strong>{formData.name}</span>}
                                    {('phone' in formData && formData.phone) && <span><strong>Phone: </strong>{formData.phone}</span>}
                                    {('email' in formData && formData.email) && <span><strong>Email: </strong>{formData.email}</span>}
                                    {('gender' in formData && formData.gender) && <span><strong>Gender: </strong>{(formData.gender=='f') ? 'Female':'Male'}</span>}
                                    {('marital_status' in formData && formData.marital_status) && <span><strong>Marital status: </strong>{(formData.marital_status=='single') ? 'Single':'Married'}</span>}
                                    {('dobs' in formData && formData.dobs) && <span><strong>DOB: </strong>{formData.dobs}</span>}
                                    {('nationality' in formData && formData.nationality) && <SelectListLabel lists='Nationality' value={formData.nationality} type='flag'/>}
                                    {('country_of_stay' in formData && formData.country_of_stay) && <SelectListLabel lists='Country of residance' value={formData.country_of_stay} type='flag'/>}
                                    {('visa' in formData && formData.visa) && <span><strong>Visa: </strong><SelectListLabel lists={visa} value={formData.visa}/></span>}
                                    {('salary_band' in formData && formData.salary_band) && <span><strong>Salary Band: </strong><SelectListLabel lists={('country_of_stay' in formData && formData.country_of_stay in salary) ? salary[formData.country_of_stay]:salary['AE']} value={formData.salary_band}/></span>}
                                    </div>
                                    <div className='overlay-transparent'></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div onClick={() => {setCurrentSection(2),memberRef.current.scrollIntoView()}} className={(currentSection==2) ? "sticky-div active":"sticky-div"}>
                        <div className="row">
                            <div className="col-3 pe-4">
                                <div className="number">2</div>
                            </div>
                            <div className="col-9">
                                <div className="content shadow-1-strong">
                                    <h6 className="sticky-content-title">Additional members details<span className='float-end'><i className="fas fa-pen"></i></span></h6>
                                    <div className="inner-details">
                                        {('additional_members' in formData && formData.additional_members) && formData.additional_members.map((member,index) => {
                                            return(
                                                <>
                                                    <label><strong>Member {index+1}</strong></label>
                                                    <p className='mb-1'>
                                                        {("relation" in member && member["relation"]) && <span className='me-2'><strong>Relation: </strong>{member["relation"]}</span>}
                                                        {("name" in member && member["name"]) && <span><strong>Name: </strong>{member["name"]}</span>}
                                                    </p>
                                                </>
                                            )
                                        })}
                                    </div>
                                    <div className='overlay-transparent'></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div onClick={() => {setCurrentSection(3),policyRef.current.scrollIntoView()}} className={(currentSection==3) ? "sticky-div active":"sticky-div"}>
                        <div className="row">
                            <div className="col-3 pe-4">
                                <div className="number">3</div>
                            </div>
                            <div className="col-9">
                                <div className="content shadow-1-strong">
                                    <h6 className="sticky-content-title">Policy coverage<span className='float-end'><i className="fas fa-pen"></i></span></h6>
                                    <div className="inner-details">
                                    {('level_of_cover' in formData && formData.level_of_cover) && <span><strong>Type of cover: </strong><SelectListLabel lists={cover} value={formData.level_of_cover}/></span>}
                                    {('geographical_coverage' in formData && formData.geographical_coverage) && <span><strong>Geographical coverage: </strong><SelectListLabel lists={geo} value={formData.geographical_coverage}/></span>}
                                    {('additional_benefits' in formData && formData.additional_benefits) && <span><strong>Additional benefits: </strong><SelectListLabel lists={benefits} value={formData.additional_benefits} type="additional_benefits"/></span>}
                                    {('other_benefits' in formData && formData.other_benefits) && <span><strong>Other benefits: </strong>{formData.other_benefits}</span>}
                                    {('indicative_budget' in formData && formData.indicative_budget) && <span><strong>Indicative budget: </strong><SelectListLabel lists={buget} value={formData.indicative_budget}/></span>}
                                    {('start_dates' in formData && formData.start_dates) && <span><strong>Start Date: </strong>{formData.start_dates}</span>}
                                    </div>
                                    <div className='overlay-transparent'></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Form