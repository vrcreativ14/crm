import React from 'react'
import { useParams } from "react-router-dom";
import RequestHandler from './RequestHandler';

export const GetData = async (page = false,navigate) => {
    const { id, secretCode } = useParams()
    try{
        const { data: quoteData } = await RequestHandler.get('health-insurance/quote-api/'+id)
        console.log(quoteData)
        if('data' in quoteData){
            const quote = quoteData.data
            if(secretCode==quote.quote.reference_number && !quote.quote.outdated){
                if('deal' in quote && !quote.deal.is_quote_link_active){
                    return navigate('/health-insurance-quote/expired/')
                }
                if('policy' in quote && !quote.policy.is_policy_link_active){
                    // const today = new Date();
                    // const dd = String(today.getDate()).padStart(2, '0');
                    // const mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
                    // const yyyy = today.getFullYear();
                    // const currentDate = yyyy+''+mm+''+dd
                    // const expiryData = quote.policy.expiry_date.replaceAll("-", "")
                    // console.log(currentDate,expiryData)
                    // if(expiryData<=currentDate){
                    return navigate('/health-insurance-quote/expired/')
                    // }
                }

                let currentStage = quote.deal.stage
                if((currentStage=='documents' && quote.deal.substage != 'submit documents') || (currentStage=='final_quote' && quote.deal.substage == 'final quote send to client')){
                    currentStage = 'documents_thankyou'
                }
                if((currentStage=='final_quote' && quote.deal.substage == 'final quote send to insurer') || (currentStage=='payment' && quote.deal.substage == 'payment sent to client')){
                    currentStage = 'final_quote_thankyou'
                }
                if(currentStage=='payment' && quote.deal.substage != 'payment confirmation' || currentStage=='policy_issuance'){
                    currentStage = 'payment_thankyou'
                }
                if(currentStage=='basic' && quote.deal.substage!='basic quoted' && quote.deal.substage!='basic selected'){
                    currentStage = '404'
                }
                if(currentStage=='won')currentStage = 'housekeeping';
                // console.log(page,currentStage)
                if(page!=currentStage){
                    const selectedQuote = ('selected_plan' in quote) ? quote.selected_plan.id:false
                    switch(currentStage){
                        case 'new': case 'quote':
                            return navigate('/health-insurance-quote/'+secretCode+'/'+id+'/')
                            break;
                        case 'basic':
                            return navigate('/health-insurance-quote/'+secretCode+'/'+id+'/basic-quote/')
                            break;
                        case 'documents':
                            return navigate('/health-insurance-quote/'+secretCode+'/'+id+'/policy-documents/'+selectedQuote)
                            break;
                        case 'documents_thankyou':
                            return navigate('/health-insurance-quote/'+secretCode+'/'+id+'/policy-thankyou/'+selectedQuote)
                            break;
                        case 'final_quote':
                            return navigate('/health-insurance-quote/'+secretCode+'/'+id+'/final-quote/'+selectedQuote)
                            break;
                        case 'final_quote_thankyou':
                            return navigate('/health-insurance-quote/'+secretCode+'/'+id+'/finalquote-thankyou/'+selectedQuote)
                            break;
                        case 'payment':
                            return navigate('/health-insurance-quote/'+secretCode+'/'+id+'/payment/'+selectedQuote)
                            break;
                        case 'payment_thankyou':case 'policy_issuance':
                            return navigate('/health-insurance-quote/'+secretCode+'/'+id+'/payment-thankyou/'+selectedQuote)
                            break;
                        case 'housekeeping':case 'won':
                            return navigate('/health-insurance-quote/'+secretCode+'/'+id+'/policy-issued/'+selectedQuote)
                            break;
    
                        default:
                            if(page=='404')return
                            return navigate('/health-insurance-quote/404/')
                    }
                }
                return quote
            }
        }
        if(page=='404')return
        return navigate('/health-insurance-quote/404/')
    }catch(e){
        if(page=='404')return
        return navigate('/health-insurance-quote/404/')
    }
} 