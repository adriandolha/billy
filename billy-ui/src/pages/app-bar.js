import Typography from '@mui/material/Typography';
import { Toolbar, Link, AppBar, Button } from '@mui/material';
import { useNavigate } from 'react-router';
import AuthService from '../services/auth-service'
import { useState, useEffect } from 'react';

const drawerWidth = 240;

import { API_URL } from "../pages/config";

function AppBarMenu({ }) {

    const sign_in_url = `${API_URL}/billy/auth/sign_in/cognito`
    const navigate = useNavigate()
    const [currentUser, setCurrentUser] = useState();
    useEffect(() => {
        const user = AuthService.getCurrentUser();
        user && setCurrentUser(user);
    }, []);
    return (
        <AppBar position="fixed" sx={{ width: `calc(100% - ${drawerWidth}px)`, ml: `${drawerWidth}px` }}>
            <Toolbar>
                <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                    <Button color='inherit' onClick={() => { navigate('/home') }}>Home</Button>
                </Typography>
                {currentUser ? (
                    <Button color='inherit' onClick={() => {
                        AuthService.logout();
                        window.location.reload(false);
                    }}>Logout</Button>
                ) : (
                    <Button color='inherit' onClick={() => { window.location.replace(sign_in_url) }}>Login</Button>
                )}
            </Toolbar>
        </AppBar>
    );
}

export default AppBarMenu;

