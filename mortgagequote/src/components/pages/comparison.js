import React, { useContext, useEffect, useState } from 'react'
import Layout from '../layout/Layout.js'
import { getData } from '../../helpers/utils.js'
import { DataContext } from '../../helpers/context.js'
import Loading from '../layout/Loading.js'
import Details from '../layout/Details.js'

import PropertyPrice from '../layout/PropertyPrice.js'
import Banks from '../layout/Banks.js'


const Comparison = () => {
	const[data,setData] = useContext(DataContext)
	const[loader,setLoader] = useState(true)
	const[name,setName] = useState(false)
	const[showDetails,setShowDetails] = useState(false)
	const[comparison,setComparison] = useState([])
	const currentTab = 'comparison'
	const stepContent = "We've crunched the data and here are the perfect mortgage options for you."
	useEffect(() => {
		if(data){
			setName(data.customer_info.name)
		}
	},[data])
	const fetch = () => {
		if(loader){
			getData('new')
			setLoader(false)
		}
	}
	fetch()
	if(!data){
		return(
			<Loading name={name} stepContent={stepContent} currentTab={currentTab} loader={loader}/>
		)
	}

	function handleCompare(id){
		id = parseInt(id)
		const clickedCategory = comparison.indexOf(id);
		const all = [...comparison];
	
		if (clickedCategory === -1) {
		  all.push(id);
		} else {
		  all.splice(clickedCategory, 1);
		}
		setComparison(all);
	}

	return(
		<Layout currentTab={currentTab} name={name} stepContent={stepContent}>
			<p className="fw-light-bold mb-4">Select mortgage options to compare in more detail:</p>
			<div className="row">
				<div className="col-md-9 order-2 order-md-1">
					{data.quote_details.map((bank,index) => {
						return(
							<Banks key={'bank-front-'+bank.bank_pk} data={data} bank={bank} index={index} comparison={comparison} handleCompare={handleCompare} showDetails={showDetails} setShowDetails={setShowDetails}/>
						)
					})}
				</div>
				<div className="col-md-3 order-1 order-md-2"><PropertyPrice data={data}/></div>
			</div>
			
			<div className={(comparison.length>1) ? 'compare-nav shadow-2-strong active':'compare-nav shadow-2-strong'}><i className="fas fa-copy"></i><span>{comparison.length}</span></div>
			<div className={(comparison.length>1) ? 'comparison active':'comparison'}>
				<div className="overlay"></div>
				<div className="row">
					<div className="col-12">
						<div className="d-inline-block bg-white pt-5 pe-md-3 ps-md-3">
						<span className="close" onClick={() => setComparison([])}><i className="fas fa-times"></i></span>
						{(comparison.length>1) ? <Details data={data} selectedBank={comparison}/>:null}
						</div>
					</div>
				</div>
			</div>
		</Layout>
	)
}

export default Comparison;
