import BankStatementService from '../services/bank-statements';
import { useEffect, useState } from 'react';
import { Box, CircularProgress } from '@mui/material';
import DataTable from '../components/data-table';
import SearchInput from '../components/search'


function BankStatements({ }) {
    const [data, setData] = useState()
    const [query, setQuery] = useState('')
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState()
    const [page, setPage] = useState(0);
    const [pageSize, setPageSize] = useState(20);

    const columns = [
        { field: 'id', headerName: 'ID', width: 70 },
        { field: 'category', headerName: 'Category', width: 130, sortable: false },
        { field: 'date', headerName: 'Date', width: 130, sortable: false },
        { field: 'desc', headerName: 'Description', width: 500, sortable: false },
        {
            field: 'suma',
            headerName: 'Amount',
            type: 'number',
            width: 90,
            sortable: false
        },
    ];


    const fetch_bank_statements = () => BankStatementService.search(query, pageSize, page * pageSize)
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
        fetch_bank_statements();
    }, [page, pageSize, query]);
    const handleSearch = event => {
        const q = event.target.value || ''
        console.log(q);
        setQuery(q)
    };
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
                <SearchInput handleSearch={handleSearch} />
                <DataTable columns={columns} rows={rows} rowCount={rowCount}
                    page={page} pageSize={pageSize}
                    setPage={setPage} setPageSize={setPageSize} />
            </>

        );

    }
    return null
}

export default BankStatements;
