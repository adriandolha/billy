import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useNavigate } from 'react-router';

import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';

const API_URL = 'http://localhost:3000'

function Login({ }) {
    const navigate = useNavigate()
    const [searchParams] = useSearchParams();
    const [data, setData] = useState()
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(false)
    const code = searchParams && searchParams.get('code');

    useEffect(() => {
        let queryString = searchParams.toString();
        if (code) {
            console.log(queryString);
            fetch(`${API_URL}/billy/auth/token/cognito?${queryString}`, {
                method: 'get',
                headers: new Headers({
                    'Content-Type': 'application/json'
                })
            })
                .then(data => data.json())
                .then(setData)
                .then(() => setLoading(false))
                .catch((error) => {
                    console.log(error);
                    setError(error);
                });
        }
    }, [code]);

    if (data) {
        console.log(data)
        if (data.id_token) {
            localStorage.setItem("user", JSON.stringify(data));
            navigate('/home')
            window.location.reload();
        }
    }

    return (
        <Box sx={{ display: 'flex' }}>
            <CircularProgress />
        </Box>
    );
}

export default Login;
