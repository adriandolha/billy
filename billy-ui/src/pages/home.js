import { Fragment } from 'react';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import { Typography, Card, CardContent, CardActions, Button } from '@mui/material';
import { API_URL } from "../pages/config";
import authService from '../services/auth-service';
const sign_in_url = `${API_URL}/billy/auth/sign_in/cognito`

export default function Home() {
    const currentUser = authService.getCurrentUser()
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
                    <Typography variant="h6" sx={{
                        // color: 'white',
                        // backgroundColor: 'info.main',
                        // padding: 2,
                        borderRadius: '10px'
                    }}>
                        Billy is an application for expenses and bills analytics.
                        Depending on the bank and provider, they may provide some reporting, usually on a monthly basis.
                        They may also include grouping by categories and show how much you spend on food, travel, etc.
                        Still, it’s difficult to get a general overview of spending trends and provider increases, if any.
                        Billy helps you answer some of these questions.
                    </Typography>
                </CardContent>
                <CardActions>
                    {currentUser ? (
                        <Button onClick={() => {
                            window.location.href = '/bank-statements'
                        }} sx={{
                            color: 'white',
                            backgroundColor:'secondary.main'
                        }}>Let's start</Button>
                    ) : (
                        <Button  onClick={() => { window.location.replace(sign_in_url) }} sx={{
                            color: 'white',
                            backgroundColor:'secondary.main',
                            ml: 'auto'
                        }}>Login</Button>
                    )}
                </CardActions>
            </Card>

        </Fragment>
    );
}
