import React, { useEffect, useState } from 'react'
import CollapseDetails from '../components/CollapseDetails'
import Details from '../components/Details'
import Insurer from '../components/Insurer'
import InsurerHead from '../components/InsurerHead'
import SearchBenefits from '../components/SearchBeneifts'
import { GetData } from '../helper/GetData'
import Layout from '../layout/Layout'
import InvalidPage from './InvalidPage'
import LoadingPage from './LoadingPage'
import { Store } from 'react-notifications-component'
import { columnTitle, InsurarTableData } from '../components/InsurarData'
import { useNavigate } from 'react-router-dom'

const Quote = () => {
	const[data,setData] = useState(false)
	const[comparison,setComparison] = useState(false)
	const[startComparison,setStartComparison] = useState(false)
	const[showComparisonOption,setShowComparisonOption] = useState(false)
    const[search,setSearch] = useState(false)
    const[searchResults,setSearchResults] = useState(false)
    const navigate = useNavigate()

    useEffect(() => {
        window.scrollTo(0, 0)
    }, [])

    useEffect(() => {
        if(comparison && comparison.length>1){
            setShowComparisonOption(true)
        }else{
            setShowComparisonOption(false)
        }
    },[comparison])

    useEffect(() => {
        if(search){
            setSearchResults(Object.keys(columnTitle).filter((title) => {
                if(columnTitle[title].toLowerCase().includes(search.toLowerCase())){
                    return title
                }
            }))
        }else{
            setSearchResults(false)
        }
    },[search])
    
    const fetch = async () => {
        const res = await GetData('quote',navigate)
        if(res)setData(res)
    }

    if(!data){
        fetch()
        return <LoadingPage/>
    }
    if(data=='invalid')return <InvalidPage/>

    function handleComparison(event,insurar){
        if(event.currentTarget.checked){
            const data = (comparison && comparison.length>0) ? setComparison(prevArray => [...prevArray, insurar]):setComparison([insurar])
        }else{
            const data = (comparison && comparison.length>0) ? setComparison(comparison.filter((index) => index!=insurar)):setComparison(false)
        }
    }

    function handleNotification(){
        if(showComparisonOption)return setStartComparison(true)
        Store.addNotification({
            title: "Info!",
            message: "Please select any two plans to compare.",
            type: "info",
            insert: "top",
            container: "top-right",
            animationIn: ["animate__animated", "animate__fadeIn"],
            animationOut: ["animate__animated", "animate__fadeOut"],
            dismiss: {
            duration: 6000,
            onScreen: true,
            showIcon: true
            }
        });
    }

    const name = 'Hi <span class="text-capitalize">'+data.primary_member.name+'</span>,'
    const currentTab = 'quote'
	const stepContent = "Nexus offers a variety of health insurance plans from the best insurers. Please take a look at the plans we have carefully selected for you below. If you have any questions, please feel free to reach out to us."

    return(
        <Layout currentTab={currentTab} name={name} stepContent={stepContent} comparison={startComparison}>
            <p className="fs-6 fw-light-bold mb-4">Best and affordable plans chosen for you</p>

            <div className="row">
                <div className='col-md-12'>
                    <div className='insurer-info shadow-1 header-content d-none d-lg-block'>
                        <ul className='quote-short-detail'>
                            <li className='image-column'>Insurer</li>    
                            <li className='small-column'>Annual Limit</li>    
                            <li className='small-column'>Geographical Cover</li>    
                            <li className='large-column'>Outpatient Co-payment</li>    
                            <li className='small-column'>Network</li>    
                            <li className='small-column'>Pre-Existing Cover</li>    
                            <li className='small-column'>Dental Benefits</li>    
                            <li className='small-column'>Optical</li>    
                            <li className='action-column'><button className="btn-nexus btn-golden" onClick={() => handleNotification(true)} disabled={showComparisonOption ? false:true}>Show Comparison</button></li>    
                        </ul>
                    </div>
                </div>
				<div className="col-md-12">
                    {('quoted_plans' in data) && data.quoted_plans.map((insurer,index) => {
                        return(
                            <Insurer key={'insurer-'+index} data={data} insurer={insurer} index={index} comparison={comparison} handleComparison={handleComparison}/>
                        )
                    })}
				</div>
			</div>
			
            {startComparison &&
			<div className='comparison active'>
				<div className="overlay"></div>
				<div className="row">
					<div className="col-12">
						<div className="d-inline-block bg-white pt-2 pt-md-5 pe-md-3 ps-md-5">
                            <span className="close" onClick={() => setStartComparison(false)}><i className="fas fa-times"></i></span>
                            <div className='left-content mb-3 d-inline-block'>
                                <SearchBenefits search={search} setSearch={setSearch}/>
                            </div>
                            <div className='right-content mb-3 d-flex d-md-inline-block'>
                                <div className='d-block d-md-none hidden-content'>a</div>
                                <InsurerHead data={data.quoted_plans} comparison={comparison}/>
                            </div>
                            {(search) ?
                                <ul className='details-benefits'>
                                    <CollapseDetails defaultTab={true}>
                                        {(searchResults && searchResults.length>0) && searchResults.map((result,index) => {
                                            return(
                                                <InsurarTableData key={'search-results-'+index} data={data.quoted_plans} selectedInsurar={false} comparison={comparison} keyIndex={result}/>
                                            )
                                        })}
                                    </CollapseDetails>
                                </ul>
                                :(comparison) && <Details data={data.quoted_plans} selectedInsurar={false} comparison={comparison}/>}
                            {(!search) &&
                            <>
                                <div className='left-content mb-3 d-none d-md-inline-block invisible'>
                                    <SearchBenefits search={search} setSearch={setSearch} falseDiv={false}/>
                                </div>
                                <div className='right-content mb-3 d-flex d-md-inline-block'>
                                    <div className='d-block d-md-none hidden-content'>a</div>
                                    <InsurerHead data={data.quoted_plans} image={false} comparison={comparison}/>
                                </div>
                            </>}
						</div>
					</div>
				</div>
			</div>
            }
            {(showComparisonOption) ? <span className='animate__delay-2s animate__repeat-2 animate__animated animate__heartBeat compare-action shadow-1-strong text-golden' onClick={() => setStartComparison(true)}><i className="fas fa-clone me-1"></i>Compare</span>:''}
        </Layout>
    )
}

export default Quote