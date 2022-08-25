import JobService from '../services/jobs';
import { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Chip, Divider } from '@mui/material';
import { Paper, Grid, List, ListItem } from '@mui/material';
import { Error } from '../components/messages'

const Status = ({ name }) => {
    if (name === 'CREATED') {
        return <Chip label={name} color='secondary' />
    }
    if (name === 'IN_PROGRESS') {
        return <Chip label={name} color='info' />
    }
    if (name === 'COMPLETED') {
        return <Chip label={name} color='success' />
    }
    return 'n/a'
}


const LabelWithValue = ({ label, value }) => {
    return <Typography variant='body2' sx={{
        display: 'inline'
    }}>{label}<Typography variant='body1' color='primary' sx={{
        margin: 1,
        display: 'inline'
    }}>{value}</Typography>
    </Typography>
}

function JobsView({ }) {
    const [data, setData] = useState()
    const [query, setQuery] = useState('')
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState()
    const [page, setPage] = useState(0);
    const [pageSize, setPageSize] = useState(20);

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
                <Grid container>
                    <Grid item xs={12}>
                        <List>
                            {data.items.map((job) => {
                                const payload_pretty = JSON.stringify(JSON.parse(job.payload), null, 2)
                                const result_pretty = job.result && JSON.stringify(JSON.parse(job.result), null, 2)
                                return (
                                    <>
                                        <ListItem key="category.name" >
                                            <Paper elevation={1} sx={{ width: '100%', margin: 2, padding: 2 }}>
                                                <Grid container spacing={1} item xs={12}>
                                                    <Grid item container spacing={1} xs={12} justifyContent='space-between' alignItems='center'>

                                                        <Typography variant='h5' sx={{
                                                            display: 'inline',
                                                            fontWeight: 'bold'
                                                        }}>ID:<Typography variant='h5' color='info.main' sx={{
                                                            margin: 1,
                                                            display: 'inline'
                                                        }}>{job.id}</Typography>
                                                        </Typography>
                                                    </Grid>
                                                    <Grid item container spacing={1} xs={12} justifyContent='space-between' alignItems='center'>
                                                        {job.created_at && <LabelWithValue label='Created at:' value={job.created_at} />}
                                                        {job.started_at && <LabelWithValue label='Started at:' value={job.started_at} />}
                                                    </Grid>
                                                    <Grid item container spacing={1} xs={12} justifyContent='space-between' alignItems='center'>
                                                        {job.status && <LabelWithValue label='Status:' value={<Status name={job.status} />} />}
                                                        {job.completed_at && <LabelWithValue label='Completed at:' value={job.completed_at} />}
                                                    </Grid>
                                                    <Grid item container spacing={1} xs={12} justifyContent='space-between' alignItems='center'>
                                                        {job.job_type && <LabelWithValue label='Job Type:' value={job.job_type} />}
                                                    </Grid>
                                                    {job.payload && <>
                                                        <Grid item container spacing={1} xs={12} alignItems='center'>
                                                            <Typography>Payload:</Typography>
                                                            <Grid item xs={12}>
                                                                <pre>{payload_pretty}</pre>
                                                            </Grid>

                                                        </Grid></>
                                                    }
                                                    {job.result && <>
                                                        <Grid item container spacing={1} xs={12} alignItems='center'>
                                                            <Typography>Result:</Typography>
                                                            <Grid item xs={12} >
                                                                <Box component='pre' sx={{
                                                                    overflow: 'scroll',
                                                                    height: '200px'
                                                                }}>{result_pretty}</Box>
                                                            </Grid>

                                                        </Grid>
                                                    </>
                                                    }
                                                </Grid>
                                            </Paper>

                                        </ListItem>
                                    </>
                                )
                            })}
                        </List>
                    </Grid>
                </Grid>
            </>

        );

    }
    return null
}

export default JobsView;
