import Chart from "react-apexcharts";
import { useState, useEffect } from 'react';
import StatsService from '../services/stats'
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import { GlobalStyles } from "@mui/material";

function ExpensesPerMonth({ }) {
    const styles = <GlobalStyles styles={{
        '.myChart': {
            width: '100%',
            backgroundColor: 'primary'
        }

    }} />
    const [data, setData] = useState()
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(false)

    useEffect(() => {
        StatsService.expenses_per_month()
            .then(data => data.json())
            .then(setData)
            .then(() => setLoading(false))
            .catch((error) => {
                console.log(error);
                setError(error);
            });
    }, []);

    if (loading) {
        return (
            <Box sx={{ display: 'flex' }}>
                <CircularProgress />
            </Box>
        );

    }
    if (data) {
        const _categories = data.items.map(item => `${item[0]}-${item[1]}`)
        const _values = data.items.map(item => item[2])
        const state = {
            options: {
                chart: {
                    id: "expenses_per_month"
                },
                xaxis: {
                    categories: _categories
                }
            },
            series: [
                {
                    name: "amount",
                    data: _values
                }
            ]
        };

        const dynamicWidth = _values.length * 6;
        const chartWidth = dynamicWidth < window.innerWidth ? '100%' : dynamicWidth;
        return (
            <>
                {styles}
                <Box className='myChart' >
                    <Chart
                        options={state.options}
                        series={state.series}
                        type="line"
                        height="400"
                    />
                </Box>
            </>
        );
    }
    return null

}

export default ExpensesPerMonth;

