import React from "react";
import Layout from "./Layout";

const Loading = ({currentTab,name,loader}) => {
    return(
        <Layout currentTab={currentTab} name={name}>
            <div className="loader text-center">
                {(loader) ? 
                <>
                <p>Loading...</p>
                <i className="fas fa-circle-notch spin"></i>
                </>
                :
                <div className="mt-5 header">
                    <p>Looks like its an Expired :(</p>
                    <p className="mb-0"><small>Need some help? Call us</small></p>
                    <a href="tel:97142378294">+971 4 237 8294</a>
                </div>
                }
            </div>
        </Layout>
    )
}

export default Loading