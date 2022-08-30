import BankStatementService from '../services/bank-statements';
import { useEffect, useState, MouseEvent } from 'react';
import { Box, CircularProgress, Typography, Chip, Button } from '@mui/material';
import DataTable from '../components/data-table';
import SearchInput from '../components/search'
import { Error } from '../components/messages'
import Popover from '@mui/material/Popover';

const Desc = ({ desc }) => {
    const [anchorEl, setAnchorEl] = useState(null);

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const open = Boolean(anchorEl);
    const id = open ? 'simple-popover' : undefined;

    return (
        <div>
            <Button size='small' variant="outlined" onClick={handleClick} sx={{display:'inline'}}>
                View
            </Button>
            <Typography sx={{ p: 2, display:'inline' }}>{desc}</Typography>
            
            <Popover
                id={id}
                open={open}
                anchorEl={anchorEl}
                onClose={handleClose}
                anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'left',
                }}
            >
                <Typography sx={{ p: 2 }}>{desc}</Typography>
            </Popover>
        </div>
    );
}

const Category = ({ name }) => {
    return <Chip label={name} color='secondary' variant='outlined' />
}

const Amount = ({ value }) => {
    return <Typography variant='body' sx={{ fontWeight: 'bold' }}>{value}</Typography>
}

const TransactionDate = ({ value }) => {
    return <Typography variant='body' color='primary'>{value}</Typography>
}

function BankStatements({ }) {
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
            sortable: false,
            renderCell: (params) => <Desc desc={params.value}></Desc>
        }
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
