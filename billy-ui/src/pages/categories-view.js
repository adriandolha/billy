import CategoryService from '../services/categories';
import { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Chip, List, ListItem, Link, Divider, Stack } from '@mui/material';
import { Grid, Paper, Card, CardContent, CardHeader, CardActions } from '@mui/material';
import { Error } from '../components/messages'

const KeyWords = ({ key_words }) => {
    return key_words.map((kew_word) => <Chip color='secondary' key={kew_word} label={kew_word} />)
}

const Category = ({ category }) => {
    return <ListItem key={category.name} href="/dashboard">
        <Paper elevation={1} sx={{ width: '100%', padding: 2 }}>
            <Grid container spacing={1}>
                <Grid item xs={12}>
                    <Box>
                        <Chip label={category.name} color='primary' variant='outlined' />
                    </Box>
                </Grid>
                <Grid item xs={12}>
                    <Divider />
                </Grid>
                <Grid item xs={12} >
                    {category.key_words.map((kew_word) => {
                        return (<Chip color='secondary' key={kew_word} label={kew_word} sx={{
                            margin: 0.5
                        }} />)

                    })}
                </Grid>
            </Grid>
        </Paper>

    </ListItem>

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
        data.items.map((item) => { item['id'] = item.name })
        const rows = data.items
        const rowCount = data.total
        return (
            <>
                <List>
                    {data.items.map((category) => {
                        return (
                            <Category category={category} />
                        )
                    })}
                </List>
            </>

        );

    }
    return null
}

export default CategoriesView;
