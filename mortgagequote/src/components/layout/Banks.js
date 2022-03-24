import React from 'react'
import { CurrencyFormat } from '../../helpers/utils.js'
import Details from '../layout/Details.js'
import SelectButton from '../layout/Button.js'
import upArrow from '../../assets/stages/up-arrow.svg'
import { useHistory, useParams } from 'react-router'

const Banks = ({ bank, data, index = false, comparison = false, handleCompare = false, showDetails = false, setShowDetails = false}) => {
    const navigate = useHistory()
	let { id, secretCode, quoteID } = useParams();
    return(
        <div className="bank-info shadow-1">
            <div className="bank-head">
                {(comparison) ? 
                <>
                    <h5>{bank.bank_name}</h5>
                    <label>
                        COMPARE
                        <input type="checkbox" onChange={(event) => handleCompare(index)} checked={(comparison.indexOf(index) !== -1) ? true:false}/>
                    </label>
                </>
                :<h5>Selected Mortgage Option</h5>
                }
            </div>
            <div className="bank-content">
                <div className="img"><img src={bank.bank_logo} alt={bank.bank_name}/></div>
                <div className="no-border">
                    <p className="main fw-light-bold"><CurrencyFormat num={bank.monthly_repayment} noDecimal={true}/></p>
                    <p><small>Monthly Repayment</small></p>
                </div>
                { (bank.bank_type == 'fixed') ?
                <div>
                    <p className="main">{bank.interest_rate}%</p>
                    <p><small>Interest Rate<br/> Fixed for {bank.introduction_period_in_years} years</small></p>
                </div>
                :
                <div>
                    <p className="main">{bank.interest_rate}%</p>
                    <p><small>Interest Rate<br/> +{bank.eibor_duration} Eibor</small></p>
                </div>
                }
                <div>
                    <p className="main">20 Years</p>
                    <p><small>Max Term</small></p>
                </div>
                <div>
                    <p className="main"><CurrencyFormat num={bank.total_down_payment} noDecimal={true}/></p>
                    <p><small>Total Upfront Payment</small></p>
                </div>
               
                {(comparison) ?
                <>
                {
                    (bank.bank_extra_financing_allowed && bank.bank_pk == data.quote_info.selected_bank) ?
                <div>
                    <p className="main"><CurrencyFormat num={bank.extra_financing} noDecimal={true} /></p>
                    <p><small>Extra Financing</small></p>
                </div>
                :
                <div></div>
                }
                </>
                :
                <>
                <div className="full-border">
                    <p className="main"><CurrencyFormat num={data.deal_info.property_price} noDecimal={true}/></p>
                    <p><small>Property Price</small></p>
                </div>
                <div>
                    <p className="main"><CurrencyFormat num={data.deal_info.down_payment} noDecimal={true}/></p>
                    <p><small>Down Payment</small></p>
                </div>
                </>
                }
                <div className="action">
                    {(comparison) ?
                    <>
                    <SelectButton text="Select" url="mortgageSummary" indexID={index}/>	
                    <button className="btn-nexus btn-grey" onClick={() => setShowDetails(index)}>Details</button>	
                    </>
                    :<button className="ms-3 btn-nexus btn-grey" onClick={() => navigate.push('/mortgage-quote/'+secretCode+'/'+id)}>Change Bank</button>}
                </div>
            </div>
            {(comparison) ?
            <div className={(showDetails!==false && showDetails==index) ? 'bank-details active':'bank-details'}>
                <div className="text-right"><img width="25px" src={upArrow} onClick={() => setShowDetails(false)}/></div>
                <Details data={data} selectedBank={[index]} setShowDetails={setShowDetails}/>
            </div>
            :null}
        </div>
    )
}

export default Banks