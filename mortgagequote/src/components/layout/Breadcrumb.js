import React, { useState } from 'react';
import Comparison from '../../assets/stages/comparison.svg'
import MortageSummary from '../../assets/stages/mortgage-summary.svg'
import PreApproval from '../../assets/stages/pre-approval.svg'
import Valuation from '../../assets/stages/valuation.svg'
import UnderProcess from '../../assets/stages/under-process.svg'
import MortgageIssued from '../../assets/stages/mortgage-issued.svg'

import ComparisonGold from '../../assets/stages/comparison-gold.svg'
import MortageSummaryGold from '../../assets/stages/mortgage-summary-gold.svg'
import PreApprovalGold from '../../assets/stages/pre-approval-gold.svg'
import ValuationGold from '../../assets/stages/valuation-gold.svg'
import UnderProcessGold from '../../assets/stages/under-process-gold.svg'
import MortgageIssuedGold from '../../assets/stages/mortgage-issued-gold.svg'


const Breadcrumb = ({current}) => {
    const stage = ['comparison','mortageSummary','preApproval','valuation','underProcess','mortgageIssued']
    const currentStageIndex = stage.indexOf(current)
    const[activeBreadcrumb,setActiveBreadcrumb] = useState(false)
    return(
        <div className={(activeBreadcrumb) ? 'breadcrumb active':'breadcrumb'} onTouchMove={() => setActiveBreadcrumb(true)} onClick={() => setActiveBreadcrumb(true)}>
            <ul>
                <li className={(current=='comparison') ? 'active':(currentStageIndex>0) ? 'completed':null}>
                    <img src={(current!='comparison') ? (currentStageIndex>0) ? ComparisonGold:Comparison:ComparisonGold} alt="breadcrumb-comparison"/>
                    <div>Comparison
                    <span className="completed"><i className="fas fa-check"></i></span>
                    <span className="current"><i className="fas fa-chevron-right"></i></span>
                    </div>
                </li>
                <li className={(current=='mortageSummary') ? 'active':(currentStageIndex>1) ? 'completed':null}>
                    <img src={(current!='mortageSummary') ? (currentStageIndex>0) ? MortageSummaryGold:MortageSummary:MortageSummaryGold} alt="breadcrumb-mortageSummary"/>
                    <div className="big">Mortage summary
                    <span className="completed"><i className="fas fa-check"></i></span>
                    <span className="current"><i className="fas fa-chevron-right"></i></span>
                    </div>
                </li>
                <li className={(current=='preApproval') ? 'active':(currentStageIndex>2) ? 'completed':null}>
                    <img src={(current!='preApproval') ? (currentStageIndex>2) ? PreApprovalGold:PreApproval:PreApprovalGold} alt="breadcrumb-preApproval"/>
                    <div className="big">Pre-approval
                    <span className="completed"><i className="fas fa-check"></i></span>
                    <span className="current"><i className="fas fa-chevron-right"></i></span>
                    </div>
                </li>
                <li className={(current=='valuation') ? 'active':(currentStageIndex>3) ? 'completed':null}>
                    <img src={(current!='valuation') ? (currentStageIndex>3) ? ValuationGold:Valuation:ValuationGold} alt="breadcrumb-valuation"/>
                    <div>Valuation
                    <span className="completed"><i className="fas fa-check"></i></span>
                    <span className="current"><i className="fas fa-chevron-right"></i></span>
                    </div>
                </li>
                <li className={(current=='underProcess') ? 'active':(currentStageIndex>4) ? 'completed':null}>
                    <img src={(current!='underProcess') ? (currentStageIndex>4) ? UnderProcessGold:UnderProcess:UnderProcessGold} alt="breadcrumb-underProcess"/>
                    <div className="big">Under process
                    <span className="completed"><i className="fas fa-check"></i></span>
                    <span className="current"><i className="fas fa-chevron-right"></i></span>
                    </div>
                </li>
                <li className={(current=='mortgageIssued') ? 'active':(currentStageIndex>5) ? 'completed':null}>
                    <img src={(current!='mortgageIssued') ? (currentStageIndex>5) ? MortgageIssuedGold:MortgageIssued:MortgageIssuedGold} alt="breadcrumb-mortgageIssued"/>
                    <div className="big">Mortgage issued
                    <span className="completed"><i className="fas fa-check"></i></span>
                    <span className="current"><i className="fas fa-chevron-right"></i></span>
                    </div>
                </li>
            </ul>
        </div>
    )
}

export default Breadcrumb;