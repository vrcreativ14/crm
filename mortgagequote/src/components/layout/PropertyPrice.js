import React from "react";
import { CurrencyFormat } from '../../helpers/utils.js'

const PropertyPrice = ({data}) => {
    return(
        <div className="property-price shadow-1">
            <h5 className="tab-title">Property Details</h5>
            <div>
                <span>Property Value<br/><small>Total Value Of Property</small></span>
                <span><CurrencyFormat num={data.deal_info.property_price} noDecimal={true}/></span>
            </div>
            <div>
                <span>Down Payment<br/><small>20% Down Payment</small></span>
                <span><CurrencyFormat num={data.deal_info.down_payment} noDecimal={true}/></span>
            </div>
            <div>
                <span>Mortgage Amount<br/><small>Total Amount Of Loan</small></span>
                <span><CurrencyFormat num={data.deal_info.loan_amount} noDecimal={true}/></span>
            </div>	
        </div>
    )
}

export default PropertyPrice