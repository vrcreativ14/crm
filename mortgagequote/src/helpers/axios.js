import React from 'react';
import Axios from "axios";

const api = Axios.create({
    baseURL: 'https://s1.insurenex.io/',
    // baseURL: 'http://127.0.0.1:8000/',
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
});

export default api;