import { Fragment } from 'react';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import { Typography, Avatar, Card, CardContent, CardActions, Button } from '@mui/material';
import { API_URL } from "../pages/config";
import authService from '../services/auth-service';
const sign_in_url = `${API_URL}/billy/auth/sign_in/cognito`

export default function Home() {
    const currentUser = authService.getCurrentUser()
    console.log(window.location.origin)
    return (
        <Fragment>
            {/* <Box
                component="main"
                sx={{ flexGrow: 1, bgcolor: 'background.default', p: 3 }}
            > */}
            {/* <Toolbar /> */}

            <Card sx={{ minWidth: 275 }}>
                <CardContent>
                    <Typography variant='h6' component="h1" align='center' gutterBottom sx={{
                        color: 'white',
                        backgroundColor: 'primary.main',
                        textTransform: 'uppercase',
                        padding: 2,
                        borderRadius: '10px'

                    }}>
                        Welcome to Billy
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                        <Avatar alt="" src={`${window.location.origin}/logo.png`} sx={{ width: 200, height: 100 }} />
                    </Box>
                    <Typography variant="h6" sx={{
                        borderRadius: '10px',
                        marginTop: 1,
                        marginBottom: 1
                    }}>
                        Billy is an application for expenses and bills analytics, which collects, processes and analyzes 
                        bank statements, providing a general view on your expenses. It generates reports that show how much 
                        you spend on food, travel, etc.
                        Give it a try!
                    </Typography>
                </CardContent>
                <CardActions sx={{ marginBottom: 2 }}>
                    {currentUser ? (
                        <Button onClick={() => {
                            window.location.href = '/bank-statements'
                        }} sx={{
                            color: 'white',
                            backgroundColor: 'primary.main',
                            width: '100%'
                        }}>Let's go</Button>
                    ) : (
                        <Button onClick={() => { window.location.replace(sign_in_url) }} sx={{
                            color: 'white',
                            backgroundColor: 'primary.main',
                            width: '100%',
                            '&:hover': {
                                backgroundColor: 'secondary.main',
                                color: 'white',
                            }
                        }}>Login</Button>
                    )}
                </CardActions>
            </Card>

        </Fragment>
    );
}
