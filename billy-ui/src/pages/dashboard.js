import Typography from '@mui/material/Typography';
import ExpensesPerMonth from '../components/expenses-per-month'
import AvgExpensesPerCategory from '../components/avg-expenses-per-category';
import { Grid, Box, Chip, CircularProgress } from '@mui/material';
import PaidIcon from '@mui/icons-material/Paid';
import RepeatIcon from '@mui/icons-material/Repeat';
import { useState, useEffect } from 'react';
import StatsService from '../services/stats'

const AvgRecurrentExpenses = () => {
    const [value, setValue] = useState(100)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState()
    useEffect(() => {
        const recurrentExpenses = ['food', 'gas_electricity', 'phone', 'internet', 'transport', 'apartment']
        StatsService.avg_expenses_per_category()
            .then(data => data.json())
            .then((data) => {
                console.log(data)
                let _value = 0
                data.items.map(item => {
                    console.log(item)
                    // console.log(item[0])
                    // console.log(item[1])
                    if (recurrentExpenses.includes(item[0])) {
                        _value = _value + item[1]
                    }
                })
                console.log(`Value is ${_value}`)
                setValue(_value)
            })
            .then(() => setLoading(false))
            .catch((error) => {
                console.log(error);
                setError(JSON.stringify(error));
            });
    }, []);
    console.log(error)
    console.log(loading)
    if (loading) {
        return (
            <Box sx={{ display: 'flex' }}>
                <CircularProgress />
            </Box>
        );

    }

    if (error) {
        return (
            <Box sx={{ display: 'flex' }}>
                <Typography > Error is {error}</Typography>
            </Box>
        );

    }

    if (value > 0) {
        console.log(`Display Value is ${value}`)

        return <Grid item container xs={10} md={4} spacing={1} sx={{
        }}>
            <Grid item xs={5}>
                <RepeatIcon sx={{
                    backgroundColor: 'success.light',
                    borderRadius: 1,
                    color: 'black',
                    height: '100%',
                    width: '80%'
                }} />

            </Grid>
            <Grid item container xs={7} spacing={1} direction='column'>
                <Typography justifyContent='center' sx={{
                    display: 'flex',
                    padding: 1,
                    fontSize: 12,
                    fontWeight: 'bold'
                }}>Avg Recurrent Expenses</Typography>
                <Typography justifyContent='center' sx={{
                    display: 'flex',
                    fontSize: 36,
                    color: 'success.dark',
                    fontWeight: 'bold'
                }}>{value}</Typography>
                <Chip size='small' label='monthly' variant='outlined' color='info' sx={{
                    display: 'flex'
                }}></Chip>

            </Grid>

        </Grid>
    }



}
function Dashboard({ }) {
    return (
        <Grid container spacing={2} >
            <Grid item container xs={12} spacing={2} justifyContent='center'>
                <AvgRecurrentExpenses />
            </Grid>

            <Grid item container md={6} spacing={0} direction='column' >
                <Grid item container sx={{
                    backgroundColor: 'secondary.main',
                    borderRadius: 1,
                    color: 'white'
                }}
                    justifyContent='center'
                >
                    <Typography variant='h5' alignContent="center" sx={{ padding: 1, fontSize: 14 }}>Avg Expenses per Category</Typography>
                </Grid>
                <Grid item>
                    <AvgExpensesPerCategory />
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
                    <Typography variant='h5' alignContent="center" sx={{ padding: 1, fontSize:14 }}>Expenses per Month</Typography>
                </Grid>
                <Grid item>
                    <ExpensesPerMonth />
                </Grid>
            </Grid>

        </Grid>
    );
}

export default Dashboard;
