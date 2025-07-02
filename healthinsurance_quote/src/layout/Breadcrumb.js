import React, { useState } from 'react';

import Comparison from '../assets/stages/comparison.svg'
import Policy from '../assets/stages/policy.svg'
import Final from '../assets/stages/final.svg'
import Payment from '../assets/stages/payment.svg'
import Issued from '../assets/stages/issued.svg'

import ComparisonGold from '../assets/stages/comparison-gold.svg'
import PolicyGold from '../assets/stages/policy-gold.svg'
import FinalGold from '../assets/stages/final-gold.svg'
import PaymentGold from '../assets/stages/payment-gold.svg'
import IssuedGold from '../assets/stages/issued-gold.svg'


const Breadcrumb = ({current}) => {
    const stage = ['quote','policy','final','payment','issued']
    const currentStageIndex = stage.indexOf(current)
    const[activeBreadcrumb,setActiveBreadcrumb] = useState(false)
    return(
        <div className={(activeBreadcrumb) ? 'breadcrumb active':'breadcrumb'} onTouchMove={() => setActiveBreadcrumb(true)} onClick={() => setActiveBreadcrumb(true)}>
            <ul>
                <li className={(current=='quote') ? 'active':(currentStageIndex>0) ? 'completed':null}>
                    <img src={(current!='quote') ? (currentStageIndex>0) ? ComparisonGold:Comparison:ComparisonGold} alt="breadcrumb-comparison"/>
                    <div className="big">Indicative Quote
                    <span className="completed"><i className="fas fa-check"></i></span>
                    <span className="current"><i className="fas fa-chevron-right"></i></span>
                    </div>
                </li>
                <li className={(current=='policy') ? 'active':(currentStageIndex>1) ? 'completed':null}>
                    <img src={(current!='policy') ? (currentStageIndex>0) ? PolicyGold:Policy:PolicyGold} alt="breadcrumb-mortageSummary"/>
                    <div className="big">Documents
                    <span className="completed"><i className="fas fa-check"></i></span>
                    <span className="current"><i className="fas fa-chevron-right"></i></span>
                    </div>
                </li>
                <li className={(current=='final') ? 'active':(currentStageIndex>2) ? 'completed':null}>
                    <img src={(current!='final') ? (currentStageIndex>2) ? FinalGold:Final:FinalGold} alt="breadcrumb-preApproval"/>
                    <div className="big">Final Quote
                    <span className="completed"><i className="fas fa-check"></i></span>
                    <span className="current"><i className="fas fa-chevron-right"></i></span>
                    </div>
                </li>
                <li className={(current=='payment') ? 'active':(currentStageIndex>3) ? 'completed':null}>
                    <img src={(current!='payment') ? (currentStageIndex>3) ? PaymentGold:Payment:PaymentGold} alt="breadcrumb-valuation"/>
                    <div className="big">Payment
                    <span className="completed"><i className="fas fa-check"></i></span>
                    <span className="current"><i className="fas fa-chevron-right"></i></span>
                    </div>
                </li>
                <li className={(current=='issued') ? 'active':(currentStageIndex>4) ? 'completed':null}>
                    <img src={(current!='issued') ? (currentStageIndex>4) ? IssuedGold:Issued:IssuedGold} alt="breadcrumb-underProcess"/>
                    <div className="big">Policy Issued
                    <span className="completed"><i className="fas fa-check"></i></span>
                    <span className="current"><i className="fas fa-chevron-right"></i></span>
                    </div>
                </li>
            </ul>
        </div>
    )
}

export default Breadcrumb;