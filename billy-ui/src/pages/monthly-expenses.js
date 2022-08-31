import BankStatementService from '../services/bank-statements';
import StatsService from '../services/stats'
import { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Chip } from '@mui/material';
import DataTable from '../components/data-table';
import SimpleTable from '../components/simple-table'
import SearchInput from '../components/search'
import { Error } from '../components/messages'

const Category = ({ name }) => {
    return <Chip label={name} color='secondary' variant='outlined' />
}

const Amount = ({ value }) => {
    return <Typography variant='body' sx={{ fontWeight: 'bold' }}>{value}</Typography>
}

const TransactionDate = ({ value }) => {
    return <Typography variant='body' color='primary'>{value}</Typography>
}

function MonthlyExpenses({ }) {
    const [data, setData] = useState()
    const [query, setQuery] = useState('')
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState()
    const [page, setPage] = useState(0);
    const [pageSize, setPageSize] = useState(20);

    const columns = [
        { field: 'id', headerName: 'ID', width: 70, hide: true },
        {
            field: 'category',
            headerName: 'Category',
            sortable: true,
            renderCell: (params) => <Category name={params.value} />
        },
        
        {
            field: 'date',
            headerName: 'Date',
            sortable: true,
            renderCell: (params) => <TransactionDate value={params.value} />
        },
        
        {
            field: 'suma',
            headerName: 'Amount',
            type: 'number',
            sortable: true,
            renderCell: (params) => <Amount value={params.value} />
        }
    ];


    const fetch_monthly_expenses = () => StatsService.expenses_per_month_and_category()
        .then(res => {
            if (!res.ok) {
                return res.json().then(message => { setLoading(false); throw new Error(message); })
            }
            return res.json();
        })
        .then(setData)
        .then(() => setLoading(false))
        .catch((error) => {
            console.log(`Error: ${error}`);
            setError(error);
        });
    useEffect(() => {
        fetch_monthly_expenses();
    }, [page, pageSize, query]);
    const handleSearch = event => {
        const q = event.target.value || ''
        console.log(q);
        setQuery(q)
    };
    if (error) {
        return <Error message={error} />
    }

    if (loading) {
        return (
            <Box sx={{ display: 'flex' }}>
                <CircularProgress />
            </Box>
        );

    }
    if (data) {
        // console.log(data);
        let rows = data.items.map((item, index) => {
            const month = String(item[2]).padStart(2,'0')
            return { id: index, category: item[0], date: `${item[1]}-${month}`,year: item[1], month: item[2] ,suma: item[3] }
        });
        if (query) {
            rows = rows.filter(row => query.toLowerCase().split(/(\s+)/).some(q => row.category.includes(q) || row.date.includes(q)))
        }
        const rowCount = data.search_count
        return (
            <>
                <SearchInput handleSearch={handleSearch} />
                <SimpleTable columns={columns} rows={rows} rowCount={rowCount}
                     />
            </>

        );

    }
    return null
}

export default MonthlyExpenses;
