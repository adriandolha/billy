import JobService from '../services/jobs';
import { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Chip } from '@mui/material';
import SimpleTable from '../components/simple-table';

const Category = ({ name }) => {
    return <Chip label={name} color='secondary' variant='outlined' />
}

const Amount = ({ value }) => {
    return <Typography variant='body' sx={{ fontWeight: 'bold' }}>{value}</Typography>
}

const TransactionDate = ({ value }) => {
    return <Typography variant='body' color='primary'>{value}</Typography>
}

function JobsView({ }) {
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
            sortable: false,
            renderCell: (params) => <Category name={params.value} />
        },
        {
            field: 'date',
            headerName: 'Date',
            sortable: false,
            renderCell: (params) => <TransactionDate value={params.value} />
        },
        {
            field: 'suma',
            headerName: 'Amount',
            type: 'number',
            sortable: false,
            renderCell: (params) => <Amount value={params.value} />
        },
        {
            field: 'desc',
            headerName: 'Description',
            width: 500,
            sortable: false
        }
    ];


    const fetch_jobs = () => JobService.get_all()
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
        fetch_jobs();
    }, []);

    if (loading) {
        return (
            <Box sx={{ display: 'flex' }}>
                <CircularProgress />
            </Box>
        );

    }
    if (data) {
        // console.log(data);
        const rows = data.items.map((item, index) => {
            return { id: index, date: item[0], desc: item[1], suma: item[2], category: item[3] }
        });

        const rowCount = data.search_count
        return (
            <>
                <SimpleTable
                    columns={columns}
                    rows={rows}
                    rowCount={rowCount}
                />
            </>

        );

    }
    return null
}

export default JobsView;
