import React from 'react'

const SearchBenefits = ({search,setSearch,falseDiv = true}) => {
    return(
        <div>
            <div className={falseDiv ? 'header mb-0 mb-md-5 pb-0 pb-md-5':'header'}>
                <p className="mb-0"><small>Need some help? Call us</small></p>
                <a href="tel:97143231111">+971 4 323 1111</a>
            </div>
            <div className='mt-2'><input type="text" className='form-control' placeholder='Search for benefits' onChange={(event) => setSearch(event.target.value)} value={(search) ? search:''}/></div>
        </div>
    )
}

export default SearchBenefits