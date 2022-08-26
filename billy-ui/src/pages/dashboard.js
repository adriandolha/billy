import Typography from '@mui/material/Typography';
import ExpensesPerMonth from '../components/expenses-per-month'
import AvgExpensesPerCategory from '../components/avg-expenses-per-category';
import { Grid } from '@mui/material';

function Dashboard({ }) {
    return (
        <Grid container spacing={2} sx={{ marginTop: 3 }}>
            <Grid item container md={6} spacing={0} direction='column' >
                <Grid item container sx={{
                    backgroundColor: 'secondary.main',
                    borderRadius: 1,
                    color: 'white'
                }}
                    justifyContent='center'
                >
                    <Typography variant='h5' alignContent="center" sx={{ padding: 1 }}>Expenses per Month</Typography>
                </Grid>
                <Grid item>
                    <ExpensesPerMonth />
                </Grid>
            </Grid>
            <Grid item container md={6} spacing={0} direction='column' >
                <Grid item container sx={{
                    backgroundColor: 'secondary.main',
                    borderRadius: 1,
                    color: 'white'
                }}
                    justifyContent='center'
                >
                    <Typography variant='h5' alignContent="center" sx={{ padding: 1 }}>Avg Expenses per Category</Typography>
                </Grid>
                <Grid item>
                    <AvgExpensesPerCategory />
                </Grid>
            </Grid>

        </Grid>
    );
}

export default Dashboard;
