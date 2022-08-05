import React from 'react';
import Typography from '@mui/material/Typography';

const NotFoundPage = () => {
    return (
        <div className="text-center m-5 align-items-center justify-content-center">
            <Typography variant="h1">Oops!</Typography>
            <Typography variant="h2">404 Not Found</Typography>
            <Typography variant="body1">Sorry, an error has occured, Requested page not found!</Typography>
            <div className="mt-2">
                <a href="/home" className="btn btn-primary btn-lg"><span><i className="fas fa-solid fa-home pe-1"></i></span>
                    Take Me Home </a>
            </div>
        </div>
    )
}
export default NotFoundPage;