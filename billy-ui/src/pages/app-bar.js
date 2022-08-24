import Typography from '@mui/material/Typography';
import { Toolbar, Link, AppBar, Button, IconButton } from '@mui/material';
import { useNavigate } from 'react-router';
import AuthService from '../services/auth-service'
import { useState, useEffect } from 'react';
import { API_URL } from "../pages/config";
import MenuIcon from '@mui/icons-material/Menu';
const drawerWidth = 240;

function AppBarMenu({ handleDrawerToggle }) {

    const sign_in_url = `${API_URL}/billy/auth/sign_in/cognito`
    const navigate = useNavigate()
    const [currentUser, setCurrentUser] = useState();
    useEffect(() => {
        const user = AuthService.getCurrentUser();
        user && setCurrentUser(user);
    }, []);
    return (
        <AppBar position="fixed" sx={{
            width: { sm: `calc(100% - ${drawerWidth}px)` },
            ml: { sm: `${drawerWidth}px` }
        }}>
            <Toolbar>
                <IconButton
                    color="inherit"
                    aria-label="open drawer"
                    edge="start"
                    onClick={handleDrawerToggle}
                    sx={{ mr: 2, display: { sm: 'none' } }}
                >
                    <MenuIcon />
                </IconButton>
                <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                    <Button color='inherit' onClick={() => { navigate('/home') }}>Home</Button>
                </Typography>
                {currentUser ? (
                    <Button color='inherit' onClick={() => {
                        AuthService.logout();                        
                    }}>Logout</Button>
                ) : (
                    <Button color='inherit' onClick={() => { window.location.replace(sign_in_url) }}>Login</Button>
                )}
            </Toolbar>
        </AppBar>
    );
}

export default AppBarMenu;

