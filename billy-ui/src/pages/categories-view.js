import CategoryService from '../services/categories';
import { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Chip } from '@mui/material';
import SimpleTable from '../components/simple-table';

const KeyWords = ({ key_words }) => {
    return key_words.map((kew_word) => <Chip color='secondary' key={kew_word} label={kew_word}/>)
}

function CategoriesView({ }) {
    const [data, setData] = useState()
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState()

    const columns = [
        {
            field: 'id',
            headerName: 'ID',
            sortable: false,
            width: 150,
            hide: true
        },
        {
            field: 'name',
            headerName: 'Name',
            sortable: false,
            width: 150
        },
        {
            field: 'key_words',
            headerName: 'Key Words',
            sortable: false,
            width: 400,
            renderCell: (params) => <Box ><KeyWords key_words={params.value} /></Box>
        }
    ];


    const fetch_categories = () => CategoryService.get_all()
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
        fetch_categories();
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
        data.items.map((item) => { item['id'] = item.name })
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

export default CategoriesView;
