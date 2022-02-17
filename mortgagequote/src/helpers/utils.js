import React, { useContext } from 'react'
import api from './axios.js'
import 'regenerator-runtime/runtime'
import { BrowserRouter as Router, useParams, useHistory } from "react-router-dom"
import { DataContext } from './context.js'

export const getData = async (stage = false) => {
    const [data, setData] = useContext(DataContext)
    let { id, secretCode, quoteID, stageType } = useParams();
    const navigate = useHistory()
    const { data: quoteData } = await api.get('mortgage/quote-api/'+id+'/')
    console.log(quoteData)
    const bankIndex = getBankIndex(quoteData)
    if('data' in quoteData){
        if(secretCode==quoteData.data.quote_info.reference_number){
            if(stage && (stage!='order' || quoteData.data.deal_info.stage=='preApproval') &&stage!=quoteData.data.deal_info.stage){//Force redirect
                setData(quoteData.data)
                const stages = ['open' , 'new', 'quote', 'preApproval', 'valuation', 'offer', 'settlement', 'loanDisbursal','propertyTransfer',  'won', 'lost'];
                switch(quoteData.data.deal_info.stage) {
                    case 'open': case 'new': case 'quote':
                        return navigate.push('/mortgage-quote/'+secretCode+'/'+id+'/')
                        break;
                    case 'preApproval':
                        return navigate.push('/mortgage-quote/'+secretCode+'/'+id+'/preApproval/'+bankIndex)
                        break;
                    case 'valuation':
                        return navigate.push('/mortgage-quote/'+secretCode+'/'+id+'/valuation/'+bankIndex)
                        break;
                    case 'won':
                        return navigate.push('/mortgage-quote/'+secretCode+'/'+id+'/mortgageIssued/mortgageIssued/'+bankIndex)
                        break;
                    case 'lost':
                        return navigate.push('/mortgage-quote/'+secretCode+'/'+id+'/mortgageIssued/mortgageIssuedLost/'+bankIndex)
                        break;

                    default:
                      return navigate.push('/mortgage-quote/'+secretCode+'/'+id+'/underProcess/underProcess/'+bankIndex)
                  }
                return navigate.push('/mortgage-quote/'+secretCode+'/'+id+'/'+url+'/'+index)
            }
            return setData(quoteData.data)
        }else{
            return setData(false)
        }
    }else{
        return setData(false)
    }
}

export const CurrencyFormat = ({num,noDecimal = false}) => {
    const price = parseFloat(num)
    let isInt = false
    if (Number.isInteger(num)) {
        isInt = true
    }
    if(isInt){
        return price.toFixed(0).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')+' AED'
    }else if(!noDecimal){
        return price.toFixed(2).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')+' AED'
    }else{
        return price.toLocaleString("en-US")+' AED'
    }
}

function getBankIndex(data){
    if(!data.data){
        return 0
    }

    let bankIndex = 'abc'
    data.data.quote_details.filter((bank,index) => {
        if(parseInt(bank.bank_pk)==parseInt(data.data.deal_bank)){
            bankIndex = index
        }
    });
    return bankIndex
}