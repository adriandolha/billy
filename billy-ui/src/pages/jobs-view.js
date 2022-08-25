import JobService from '../services/jobs';
import { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Chip } from '@mui/material';
import SimpleTable from '../components/simple-table';
import { Error } from '../components/messages'

const Status = ({ name }) => {
    if (name === 'CREATED'){
        return <Chip label={name} color='secondary' />
    }
    if (name === 'IN_PROGRESS'){
        return <Chip label={name} color='info' />
    }
    if (name === 'COMPLETED'){
        return <Chip label={name} color='success' />
    }
    return 'n/a'
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
        { field: 'id', headerName: 'ID', width: 200 },
        {
            field: 'status',
            headerName: 'Status',
            sortable: false,
            width: 150,
            renderCell: (params) => <Status name={params.value} />
        },
        {
            field: 'created_at',
            headerName: 'Created at',
            sortable: false,
            width: 210,
            renderCell: (params) => <TransactionDate value={params.value} />
        },
        {
            field: 'completed_at',
            headerName: 'Completed at',
            type: 'number',
            sortable: false,
            width: 210,
            renderCell: (params) => <TransactionDate value={params.value} />
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
        const rows = data.items
        const rowCount = data.total
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
