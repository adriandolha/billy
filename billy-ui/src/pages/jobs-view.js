import JobService from '../services/jobs';
import { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Chip, Divider } from '@mui/material';
import { Paper, Grid, List, ListItem, Button } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { Error, Success } from '../components/messages'
import AddJob from './add-job';
import RefreshIcon from '@mui/icons-material/Refresh';

const Status = ({ name }) => {
    if (name === 'CREATED') {
        return <Chip size="small" label={name} color='secondary' />
    }
    if (name === 'IN_PROGRESS') {
        return <Chip size="small" label={name} color='info' />
    }
    if (name === 'COMPLETED') {
        return <Chip size="small" label={name} color='success' />
    }
    return 'n/a'
}


const LabelWithValue = ({ label, value }) => {
    return <>
        <Typography variant='body2' sx={{
            // display: 'inline'
        }}>{label}
        </Typography>
        <Typography variant='body2' color='primary' sx={{
            // margin: 1,
            // display: 'inline'
        }}>{value}</Typography>
    </>
}


function JobsView({ }) {
    const [data, setData] = useState()
    const [loading, setLoading] = useState(true)
    const [reload, setReload] = useState(false)
    const [error, setError] = useState()
    const [displayMessage, setDisplayMessage] = useState()
    const [open, setOpen] = useState(false);
    const [deleteJobId, setDeleteJobId] = useState();
    const [retryJob, setRetryJob] = useState();


    const fetch_jobs = () => JobService.get_all()
        .then(res => {
            if (!res.ok) {
                return res.text().then(message => { setLoading(false); throw new Error(message); })
            }
            return res.json();
        })
        .then(setData)
        .then(() => {
            setLoading(false)
            setError(null)
            setReload(false)
            setDisplayMessage(null)
        })
        .catch((error) => {
            console.log(`Error: ${error}`);
            setError(JSON.stringify(error, null, 2));
        });

    const retry_job = (job) => JobService.add_job(job)
        .then(res => {
            if (!res.ok) {
                return res.text().then(message => { setLoading(false); throw new Error(message); })
            }
            return res.json();
        })
        .then(setData)
        .then(() => {
            setReload(true)
            setError(null)
            setReload(false)
            setDisplayMessage(null)
        })
        .catch((error) => {
            console.log(`Error: ${error}`);
            setError(JSON.stringify(error, null, 2));
        });
    useEffect(() => {
        fetch_jobs();
    }, [reload]);

    useEffect(() => {
        if (retryJob) {
            setLoading(true)
            retry_job(retryJob);
        }
    }, [retryJob]);

    const delete_job = (job_id) => JobService.delete_job(job_id)
        .then(res => {
            if (res.ok) {
                return res;
            }
            setLoading(false);
            return res.text().then(text => { throw new Error(text) })
        })
        .then(() => {
            setLoading(false)
            setReload(true)
            setDisplayMessage(`Successfully deleted job ${job_id}`)
        })
        .catch((error) => {
            console.log(`Error: ${error}`);
            setError(error);
        });

    useEffect(() => {
        deleteJobId && delete_job(deleteJobId);
    }, [deleteJobId]);
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
        return (
            <Grid container >
                {displayMessage && <Success message={displayMessage} />}
                <Grid item xs={12}>
                    <Button variant="contained" color="primary"
                        startIcon={<AddIcon />}
                        onClick={() => {
                            console.log('add job')
                            setOpen(true)
                        }}
                    >
                        Add Job
                    </Button>
                    <Button onClick={() => {
                        setReload(true)
                    }}><RefreshIcon /></Button>
                </Grid>
                <AddJob open={open} handleClose={(message) => {
                    console.log('close')
                    setOpen(false)
                    setReload(true)
                    message && setDisplayMessage(message)
                }
                } />

                <Grid item xs={12} sx={{ marginLeft: 0 }}>
                    <List sx={{ marginLeft: 0 }}>
                        {data.items.map((job, index) => {
                            const payload_pretty = (typeof job.payload === 'string' || job.payload instanceof String) &&
                                JSON.stringify(JSON.parse(job.payload), null, 2)
                            const result_pretty = (typeof job.result === 'string' || job.result instanceof String) &&
                                job.result && JSON.stringify(JSON.parse(job.result), null, 2)
                            return (
                                <ListItem key={`job_${index}`} disableGutters sx={{ marginLeft: 0 }}>
                                    <Paper elevation={3} sx={{ padding: 2, width: '100%', marginBottom: 1, marginLeft: 0 }}>
                                        <Grid container spacing={1} item xs={12}>
                                            <Grid item container spacing={1} xs={12} alignItems='center'>
                                                <Grid item xs={12}>
                                                    <Typography variant='hsubtitle1' sx={{
                                                        display: 'inline',
                                                        fontWeight: 'bold'
                                                    }}>ID:<Typography variant='subtitle1' color='info.main' sx={{
                                                        margin: 1,
                                                        display: 'inline'
                                                    }}>{job.id}</Typography>
                                                    </Typography>

                                                </Grid>
                                            </Grid>
                                            <Grid item container spacing={1} xs={12} alignItems='center' justifyContent='flex-start'>
                                                <Grid item >
                                                    {job.created_at && <LabelWithValue label='Created at:' value={job.created_at} />}
                                                </Grid>
                                                <Grid item >
                                                    {job.started_at && <LabelWithValue label='Started at:' value={job.started_at} />}
                                                </Grid>
                                            </Grid>
                                            <Grid item container xs={12} spacing={1} justifyContent='flex-start'>
                                                <Grid item>
                                                    <Typography variant='body2' sx={{
                                                        marginBottom: 0
                                                    }}>Status:
                                                    </Typography>
                                                    <Status name={job.status} />
                                                </Grid>
                                                <Grid item>
                                                    {job.completed_at && <LabelWithValue label='Completed at:' value={job.completed_at} />}
                                                </Grid>
                                            </Grid>
                                            <Grid item container spacing={1} xs={12} justifyContent='space-between' alignItems='center'>
                                                <Grid item xs={12}>
                                                    {job.job_type && <LabelWithValue label='Job Type:' value={job.job_type} />}
                                                </Grid>
                                            </Grid>
                                            {job.payload &&
                                                <Grid item container spacing={1} xs={12} alignItems='baseline' wrap="wrap" sx={{flexGrow:1}} >
                                                    <Grid item xs={12}>
                                                        <Typography sx={{fontWeight: 'bold'}}>Payload:</Typography>
                                                    </Grid>
                                                    <Grid item xs={10} sx={{ overflow: 'scroll',
                                                        '& pre': {
                                                            whiteSpace: 'pre-wrap',
                                                            wordWrap: 'break-word',
                                                            fontSize: 12, overflow:'auto'

                                                        }
                                                    }}>
                                                        <pre>{payload_pretty}</pre>
                                                    </Grid>
                                                </Grid>
                                            }
                                            {job.result &&
                                                <Grid item container spacing={1} xs={12} alignItems='baseline' wrap="wrap" sx={{flexGrow:1}}>
                                                    <Grid item xs={12}>
                                                        <Typography sx={{fontWeight: 'bold'}}>Result:</Typography>
                                                    </Grid>
                                                    <Grid item xs={12} sx={{
                                                        overflow: 'scroll',
                                                        '& pre': {
                                                            whiteSpace: 'pre-wrap',
                                                            wordWrap: 'break-word',
                                                            fontSize: 12, overflow: 'auto'
                                                        }
                                                    }}>
                                                        <pre>{result_pretty}</pre>
                                                    </Grid>

                                                </Grid>

                                            }
                                            <Grid item container xs={12}>
                                                <Button variant="contained" color="primary"
                                                    startIcon={<DeleteIcon />}
                                                    onClick={() => {
                                                        setDeleteJobId(job.id);
                                                    }}
                                                    sx={{
                                                        display: 'flex',
                                                        marginRight: 1
                                                    }}
                                                >
                                                    Delete
                                                </Button>
                                                <Button variant="contained" color="secondary"
                                                    startIcon={<RefreshIcon />}
                                                    onClick={() => {
                                                        setRetryJob(job)
                                                    }}
                                                    sx={{
                                                        display: 'flex'
                                                    }}
                                                >
                                                    Retry
                                                </Button>
                                            </Grid>

                                        </Grid>
                                    </Paper>

                                </ListItem>
                            )
                        })}
                    </List>
                </Grid>
            </Grid>

        );

    }
    return null
}

export default JobsView;
