import React, { useEffect, useRef, useState } from 'react';
import ReactFlagsSelect from "react-flags-select";
import DatePicker from "react-datepicker";
import { Countries } from './Countries';
import CreatableSelect from 'react-select/creatable';
import Select from 'react-select'
import { components } from "react-select";
import { default as ReactSelect } from "react-select";

const FormFields = ({country_of_stay = false,type,name,placeholder = "",labelName = "",options = false,formData,setFormData = false,defaultValue,updateStateData = false,index = false,indexName = false,isRequired = true,isMultiple = false}) => {
    const[inputValue, setInputValue] = useState((defaultValue) ? defaultValue:(name in formData) ? formData[name]:false)
    const[selectValue, setSelectValue] = useState(null)
    const[search, setSearch] = useState('')
    const[initSearch, setInitSearch] = useState(false)
    const selectInput = useRef(null)

    const Countries_sort = Countries.sort((a, b) => {
        if (a.name < b.name) {
            return -1;
        }
        if (a.name > b.name) {
            return 1;
        }
        return 0;
    });

    // console.log(Countries_sort)

    // if(type=='date' && index !== false)console.log(formData,'inputValue',inputValue)

    useEffect(() => {
        console.log('123')
        if(initSearch)selectInput.current.focus()
    },[initSearch])

    const onChangeFetch = (value) => {
        const newData = formData
        newData[name] = value
        if(type=='date'){
            const d = new Date(value)
            if(index !== false){
                // newData[name] = (d.getMonth()+1)+"/"+d.getDate()+"/"+d.getFullYear()
                newData[name] = d.getDate()+ "/"+(d.getMonth()+1)+"/"+d.getFullYear()
                newData[name+'s'] = value
            }else{
                newData[name+'s'] = d.getDate()+ "/"+(d.getMonth()+1)+"/"+d.getFullYear()
            }
        }
        if(type=='multipleSelect'){
            setSelectValue(value)
            value = value.map((val) => val.value)
            newData[name] = value
        }
        // console.log(value)
        if(setFormData)setFormData(newData)
        if(setFormData)setFormData(prevState => ({...prevState,data:0}))
        setInputValue(value)
        if(updateStateData){
            if(type=='date'){
                updateStateData(index,newData[name],indexName)
            }else{
                updateStateData(index,value,indexName)
            }
        }
        setInitSearch(false)
        setSearch('')
    }

    // const restrictedCountry = {'AE':'AE','BH':'BH','QA':'QA','KW':'KW','JO':'JO'}
    const restrictedCountry = {'AE':'AE'}

    return(
        <div className={'form-parent-div '+type+' '+name}>
            {(() => {
                switch(type){
                    case 'text':
                    case 'number':
                    case 'email':
                        return(
                            <input type={type} name={name} placeholder={placeholder} onChange={(event) => onChangeFetch(event.target.value)} value={(name in formData) ? formData[name]:(inputValue) ? inputValue:''} required={(isRequired) ? isRequired:false} autoComplete="Off"/>
                        )
                        break;
                    
                    case 'checkbox':
                    case 'radio':
                        return(
                            <>
                                {name=='is_customer_insurance' && <label>{labelName}<sup>*</sup></label>}
                                <ul className="mb-0">
                                    {/* {console.log(name,formData[name],'sdaf')} */}
                                    {(options) && options.map((value,index) => {
                                        return(
                                            <li key={name+'-'+index}>
                                                <div className="input-select">
                                                    <label className={(indexName in formData && formData[indexName]==value.value) ? 'active':'deactive'}>
                                                        <span><i className="uncheck far fa-circle"></i></span>
                                                        <span><i className="check fas fa-dot-circle"></i></span>
                                                        <input type={type} name={name} value={value.value} checked={(indexName in formData && formData[indexName]==value.value) ? true:(inputValue && inputValue==value.value) ? true:false} onChange={(event) => onChangeFetch(event.target.value)} required={(isRequired) ? isRequired:false}/>
                                                        <span className='ms-1'>{value.label}</span>
                                                    </label>
                                                </div>
                                            </li>
                                        )
                                    })}
                                </ul>
                            </>
                        )
                        break;

                    case 'select':
                        return(
                            <select multiple={(isMultiple) ? true:false} name={(isMultiple) ? name+'[]':name} className="form-select" required={(isRequired) ? isRequired:false} onChange={(event) => onChangeFetch(event.target.value)} value={(name in formData) ? formData[name]:(inputValue) ? inputValue:(isMultiple) ? []:''}>
                            {/* // <select multiple={(isMultiple) ? true:false} name={(isMultiple) ? name+'[]':name} className="form-select" required={(isRequired) ? isRequired:false} onChange={(event) => onChangeFetch(event.target.value)}> */}
                                {options.map((value,index) => {
                                    return(
                                        <option key={name+'-'+index} value={value.value} defaultValue={(name in formData && formData[name]==value.value) ? true:(inputValue && inputValue==value.value) ? true:false}>{value.label}</option>
                                    )
                                })}
                            </select>
                        )
                        break;
                    
                    case 'multipleSelect':
                        // return(
                        //     <>
                        //     <Select onChange={onChangeFetch} isMulti allowSelectAll={true} options={options} placeholder="Select additional benefits"/>
                        //     <input type="text" className='dummy-input-hidden' value={(name in formData) ? formData[name]:(inputValue) ? inputValue:''}/>
                        //     </>
                        // )
                        return(
                            <>
                            <ReactSelect
                            options={options}
                            isMulti
                            closeMenuOnSelect={false}
                            hideSelectedOptions={false}
                            components={{
                                Option
                            }}
                            onChange={onChangeFetch}
                            allowSelectAll={true}
                            value={selectValue}
                            placeholder="Select additional benefits"
                            />
                            <input type="text" className='dummy-input-hidden' value={(name in formData) ? formData[name]:(inputValue) ? inputValue:''}/>
                            </>
                        )
                        break; 

                    case 'flag':
                        return(
                            <>
                            {initSearch && <div className='overlay-close' onClick={() => setInitSearch(false)}></div>}
                            <div className='dummy-input form-select' onClick={() => {setInitSearch(true),selectInput.current.focus()}}>
                                <span>
                                    {(!inputValue && !(name in formData) && !formData[name]) ? <>{placeholder}</>:(inputValue=='other') ? 'Other':
                                    <>
                                        <img src={(inputValue || name in formData) && Countries.filter((country) => (country.code==inputValue || country.code==formData[name])).map((country,index) => {return(country.image)})}/>
                                        <span>{(inputValue || name in formData) && Countries.filter((country) => (country.code==inputValue || country.code==formData[name])).map((country,index) => {return(country.name)})}</span>
                                    </>}
                                </span>
                                <input autoComplete="off" type="text" className='opacity-0' name={name} placeholder={placeholder} onChange={(event) => onChangeFetch(event.target.value)} value={(name in formData) ? formData[name]:(inputValue) ? inputValue:''} required={(isRequired) ? isRequired:false}/>
                            </div>
                            {initSearch && 
                            <div className='country-selection shadow-1-strong'>
                            <input ref={selectInput} autoComplete="off" placeholder='Search...' type="text" value={(search) ? search:''} onChange={(event) => setSearch(event.target.value)}/>
                            <ul>
                                {Countries_sort.filter((country) => (country.name.toLowerCase()).includes(search.toLowerCase())
                                ).map((country,index) => {
                                    if(index>=15 && search!='' && name!='country_of_stay')return
                                    if(country_of_stay && !(country.code in restrictedCountry))return
                                    return(
                                        <li onClick={() => onChangeFetch(country.code)} key={name+'-'+index}><img src={country.image}/><span>{country.name}</span></li>
                                    )
                                })}
                                {(country_of_stay) && <li onClick={() => onChangeFetch('other')} ><span>Other</span></li>}
                            </ul></div>}
                            </>
                        )
                        // return(<ReactFlagsSelect countries={(options) ? options:false} selected={(inputValue) ? inputValue:false} onSelect={(code) => onChangeFetch(code)}/>)
                        break;

                    case 'date':
                        return(
                            <>
                            {(index === false) ? 
                            
                                (name == 'start_date') ? 
                                <>
                                <DatePicker 
                                    dateFormat="MMMM d, yyyy"
                                    showMonthDropdown
                                    showYearDropdown
                                    minDate={new Date()}
                                    placeholderText={'Please select a date'} 
                                    dropdownMode="select"
                                    selected={(name in formData) ? formData[name]:(inputValue) ? inputValue:false} onChange={(date) => onChangeFetch(date)}/>
                                <input type="hidden" name={name} value={(name+'s' in formData) ? formData[name+'s']:(inputValue) ? inputValue:''}/>
                                </>
                                :
                                <>
                                <DatePicker 
                                    required
                                    dateFormat="MMMM d, yyyy"
                                    showMonthDropdown
                                    showYearDropdown
                                    maxDate={new Date()}
                                    placeholderText={'Please select a date'} 
                                    dropdownMode="select"
                                    selected={(name in formData) ? formData[name]:(inputValue) ? inputValue:false} onChange={(date) => onChangeFetch(date)}/>
                                <input type="hidden" name={name} value={(name+'s' in formData) ? formData[name+'s']:(inputValue) ? inputValue:''}/>
                                </>

                            :
                            <>
                            <DatePicker 
                                required
                                dateFormat="MMMM d, yyyy"
                                showMonthDropdown
                                showYearDropdown
                                maxDate={new Date()}
                                placeholderText={'Please select a date'} 
                                dropdownMode="select"
                                selected={(name+'s' in formData) ? formData[name+'s']:(inputValue) ? inputValue:false} onChange={(date) => onChangeFetch(date)} 
                            />
                            </>}
                            <span className="calender-icon"><i className="fas fa-calendar-alt"></i></span>
                            </>
                        )
                        break;

                    case 'textarea':
                        return(
                            <textarea rows={4} name={name} placeholder={placeholder} onChange={(event) => onChangeFetch(event.target.value)} required={(isRequired) ? isRequired:false} value={(name in formData) ? formData[name]:(inputValue) ? inputValue:''}>{(name in formData) ? formData[name]:(inputValue) ? inputValue:''}</textarea>
                        )
                        break;

                    default:
                        return('')
                        break;
                }
            })()}
            {name!='is_customer_insurance' && <label>{labelName}{(isRequired && name!='member-relation') && <sup>*</sup>}</label>}
        </div>
    )
}

export default FormFields

const Option = (props) => {
    return (
      <div>
        <components.Option {...props}>
            <div className='d-flex'>
                <input
                    type="checkbox"
                    checked={props.isSelected}
                    onChange={() => null}
                    className="me-2"
                />
                <span>{props.label}</span>
          </div>
        </components.Option>
      </div>
    );
};