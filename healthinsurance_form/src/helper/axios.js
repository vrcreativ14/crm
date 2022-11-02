import React from 'react';
import Axios from "axios";

const api = Axios.create({
    baseURL: '',
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
});

export default api;