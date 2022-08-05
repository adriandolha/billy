import Typography from '@mui/material/Typography';
import ExpensesPerMonth from '../components/expenses-per-month'
import { Grid } from '@mui/material';

function Dashboard({ }) {
    return (
        <>
            <Grid container spacing={2}>
                <Grid item container md={6} spacing={0} direction='column' >
                    <Grid item container sx={{
                        backgroundColor: 'secondary.main',
                        borderRadius: 1,
                        color: 'white'
                    }}
                        justifyContent='center'
                        disableGutters={true}>
                        <Typography variant='h5' alignContent="center" sx={{padding: 1}}>Expenses per Month</Typography>
                    </Grid>
                    <Grid item>
                        <ExpensesPerMonth />
                    </Grid>
                </Grid>

            </Grid>
        </>
    );
}

export default Dashboard;
