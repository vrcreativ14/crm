import React from "react";
import { CurrencyFormat } from '../../helpers/utils.js'
import SelectButton from "./Button.js";

const Details = ({data,selectedBank,setShowDetails = false}) => {
    return(
        <table className="table table-hover">
            <tbody>
                {(selectedBank.length>1) ? 
                <>
                <tr className="no-border">
                    <th></th>
                    {selectedBank.map((bankIndex) => {
                        return(
                            <td key={'button-'+bankIndex+Math.random()}>
                                <SelectButton text="Select" url="mortgageSummary" indexID={bankIndex}/>
                            </td>
                        )
                    })}
                </tr>
                <tr className="no-border m-auto">
                    <th></th>
                    {selectedBank.map((bankIndex) => {
                        return(
                            <td key={'image-'+bankIndex+Math.random()}><img src={data.quote_details[bankIndex]['bank_logo']}/></td>
                        )
                    })}
                </tr>
                </>
                :null
                }
                <tr className="sub-title">
                    <th>Monthly Payments:</th>
                    <ExtractTableColumn data={data} colName={false} selectedBank={selectedBank}/>
                </tr>
                <tr>
                    <th>Monthly Repayment</th>
                    <ExtractTableColumn data={data} colName="monthly_repayment_after__years_main_amount" selectedBank={selectedBank}/>
                </tr>
                {/* <tr className="color-4D8BFF">
                    <th>Monthly Repayment {data.deal_info.tenure} (After The Fix Period)s</th>
                    <ExtractTableColumn data={data} colName="monthly_repayment_after__years_after_the_fix_period" selectedBank={selectedBank}/>
                </tr> */}


                <tr className="sub-title">
                    <th>Bank Details And Fees:</th>
                    <ExtractTableColumn data={data} colName={false} selectedBank={selectedBank}/>
                </tr>
                <tr>
                    <th>Interest Rate</th>
                    <ExtractTableColumn data={data} colName="interest_rate" selectedBank={selectedBank} customCol={true}/>
                </tr>
                <tr>
                    <th>Post Introduction Rate</th>
                    <ExtractTableColumn data={data} colName="post_introduction_rate" selectedBank={selectedBank} customCol={true}/>
                </tr>
                <tr>
                    <th>Minimum floor rate</th>
                    <ExtractTableColumn data={data} colName="bank_minimum_floor_rate" selectedBank={selectedBank} customCol={true}/>
                </tr>
                <tr className="color-4D8BFF">
                    <th>Property Valuation Fee</th>
                    <ExtractTableColumn data={data} colName="poverty_valuation_fee" selectedBank={selectedBank}/>
                </tr>
                <tr>
                    <th>Bank Processing Fee</th>
                    <ExtractTableColumn data={data} colName="bank_processing_fee" selectedBank={selectedBank}/>
                </tr>
                <tr className="color-4D8BFF">
                    <th>Life Insurance (Monthly)</th>
                    <ExtractTableColumn data={data} colName="life_insurance_monthly" selectedBank={selectedBank}/>
                </tr>
                <tr>
                    <th>Property Insurance (Annually)</th>
                    <ExtractTableColumn data={data} colName="property_insurance_yearly" selectedBank={selectedBank}/>
                </tr>


                <tr className="sub-title">
                    <th>Government Fees:</th>
                    <ExtractTableColumn data={data} colName={false} selectedBank={selectedBank}/>
                </tr>
                <tr className="color-4D8BFF">
                    <th>Trustee Center Fee</th>
                    <ExtractTableColumn data={data} colName="trustee_center_fee_vat" selectedBank={selectedBank}/>
                </tr>
                <tr>
                    <th>Land Dep. Property Registration</th>
                    <ExtractTableColumn data={data} colName="land_dep_property_registration" selectedBank={selectedBank}/>
                </tr>
                <tr className="color-4D8BFF">
                    <th>Land Dep. Mortgage Registration</th>
                    <ExtractTableColumn data={data} colName="land_dep_mortgage_registration" selectedBank={selectedBank}/>
                </tr>


                <tr className="sub-title">
                    <th>Real Estate Fee 2%:</th>
                    <ExtractTableColumn data={data} colName={false} selectedBank={selectedBank}/>
                </tr>
                <tr className="color-4D8BFF">
                    <th>Real Estate Fee 2%</th>
                    <ExtractTableColumn data={data} colName="real_estate_fee_vat" selectedBank={selectedBank}/>
                </tr>


                <tr className="sub-title">
                    <th>Early Settlement Charges:</th>
                    <ExtractTableColumn data={data} colName={false} selectedBank={selectedBank}/>
                </tr>
                {/* <tr className="color-4D8BFF">
                    <th>Monthly Repayment </th>
                    <ExtractTableColumn data={data} colName="monthly_repayment_after__years_main_amount" selectedBank={selectedBank}/>
                </tr> */}
                <tr className="no-border">
                    <th>Early Settlement</th>
                    <ExtractTableColumn data={data} colName="full_settlement_max_value" selectedBank={selectedBank} customCol={true}/>
                </tr>
                <tr className="no-border">
                    <th>Free Partial Payment/Year</th>
                    <ExtractTableColumn data={data} colName="free_partial_payment_per_year" selectedBank={selectedBank} customCol={true}/>
                </tr>
                <tr>
                    {(selectedBank.length>1) ? 
                        selectedBank.map((bankIndex,index) => {
                            return(
                                <>
                                    {(index==0) ? <th key={'image-1-'+bankIndex+Math.random()}></th>:null}
                                    <td key={'image-1-'+bankIndex+Math.random()}>
                                        <SelectButton text="select" url="mortgageSummary" indexID={bankIndex}/>
                                    </td>
                                </>
                            )
                        })
                    :
                    <>
                        <td colSpan="2" className="text-end">
                            <button className="btn-nexus btn-grey me-3" onClick={() => setShowDetails(false)}>Close</button>
                            {selectedBank.map((bankIndex) => {
                                return(
                                    <SelectButton key={'bottom-'+bankIndex+Math.random()} text="Select" url="mortgageSummary" indexID={bankIndex}/>
                                )
                            })}
                        </td>
                    </>
                    }
                </tr>
            </tbody>
        </table>   
    )
}

export default Details

function ExtractTableColumn({data,colName,selectedBank,customCol = false}){
    return(
        selectedBank.map((bankIndex) => {
            if(colName){
                if(!customCol){
                    return(
                        <td key={colName+'-'+bankIndex+Math.random()}><CurrencyFormat num={data.quote_details[bankIndex][colName]} /></td>
                    )
                }else{
                    if(colName=='post_introduction_rate'){
                        return(
                            <td key={colName+'-'+bankIndex+Math.random()}>{data.quote_details[bankIndex]['post_introduction_rate']}% +{data.quote_details[bankIndex]['eibor_post_duration']} Eibor</td>
                        )
                    }else if(colName=='full_settlement_max_value'){
                        return(
                            <td key={colName+'-'+bankIndex+Math.random()}>{data.quote_details[bankIndex]['full_settlement_percentage']}% max <CurrencyFormat num={data.quote_details[bankIndex][colName]} /></td>
                        )
                    }else if(colName=='free_partial_payment_per_year'){
                        return(
                            <td key={colName+'-'+bankIndex+Math.random()}>Up to {data.quote_details[bankIndex][colName]}%</td>
                        )
                    }
                    else if(colName=='bank_minimum_floor_rate'){
                        let row = data.quote_details[bankIndex][colName] == 0 ? <td key={colName+'-'+bankIndex+Math.random()}>nil</td> : <td key={colName+'-'+bankIndex+Math.random()}>{data.quote_details[bankIndex][colName]}%</td>
                        return (
                            row
                        )
                    }
                    else if(colName=='interest_rate'){
                        if(data.quote_details[bankIndex]['bank_type'] == 'fixed'){
                            return(
                                <td key={colName+'-'+bankIndex+Math.random()}>
                                {data.quote_details[bankIndex]['interest_rate']}%
                                <small> Fixed for {data.quote_details[bankIndex]['introduction_period_in_years']} years</small>
                            </td>
                            )
                        }
                        else{
                            return(
                                <td key={colName+'-'+bankIndex+Math.random()}>
                    {data.quote_details[bankIndex]['interest_rate']}%
                    <small> + {data.quote_details[bankIndex]['eibor_duration']} Eibor</small>
                </td>
                            )
                        }                                                                                           
                    }
                }
            }else{
                return(
                    <td key={'random-'+Math.random()}>-</td>
                )
            }
        })
    )
}