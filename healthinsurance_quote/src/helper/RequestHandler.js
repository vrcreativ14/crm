import React from 'react';
import Axios from "axios";

const RequestHandler = Axios.create({
    baseURL: '/',
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
});

export default RequestHandler