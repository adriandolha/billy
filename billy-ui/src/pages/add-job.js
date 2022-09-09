import { useState, useEffect } from 'react';
import { Grid, Input, Divider, Box, CircularProgress } from '@mui/material';
import Button from '@mui/material/Button';
import Dialog, { DialogProps } from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import AddIcon from '@mui/icons-material/Add';
import CancelIcon from '@mui/icons-material/Cancel';
import FormControl from '@mui/material/FormControl';
import MenuItem from '@mui/material/MenuItem';
import AuthService from '../services/auth-service'
import FormControlLabel from '@mui/material/FormControlLabel';
import InputLabel from '@mui/material/InputLabel';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import Switch from '@mui/material/Switch';
import JobService from '../services/jobs'
import { Error, Success } from '../components/messages'
import TextField from '@mui/material/TextField';
import BankStatementService from '../services/bank-statements';

function AddJob({ open, handleClose }) {
    const username = AuthService.getCurrentUser().user.username
    const [jobType, setJobType] = useState('LOAD_ALL')
    const [searchCriteria, setSearchCriteria] = useState('Extras de cont Star Gold - ')
    const [filesText, setFilesText] = useState('ALL')
    const [since, setSince] = useState('11-Jul-2022')
    const [data, setData] = useState()
    const [uploadFile, setUploadFile] = useState()
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState()
    const [displayMessage, setDisplayMessage] = useState()

    const get_payload = (jobType) => {
        const payload = { username: username }
        switch (jobType) {
            case 'PROCESS_ALL':
                payload.username = username
                payload.op = 'process'
                payload.search_criteria = {
                    subjects: [searchCriteria]
                }
                break;
            case 'PROCESS_LAST_THREE':
                payload.username = username
                payload.op = 'process'
                payload.search_criteria = {
                    subjects: [searchCriteria],
                    since: since
                }
                break;
            case 'TRANSFORM':
                payload.username = username
                payload.op = 'transform'
                payload.files = filesText.split(/\r?\n/)
                break;
            case 'LOAD_ALL':
                payload.username = username
                payload.op = 'load'
                payload.files = ['ALL']
                break;
            case 'TEST':
                payload.username = username
                payload.op = 'test'
                break;
        }
        return payload
    }
    const payload = get_payload(jobType)

    const handleChange = (e) => {
        const job_type = e.target.value
        setJobType(job_type)
        console.log(job_type)
    }

    const add_job = (job) => JobService.add_job(job)
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
            setDisplayMessage(null)
            handleClose('Successfully added job.')
        })
        .catch((error) => {
            console.log(`Error`);
            console.log(error);
            setError(error.message);
        });
    console.log(username)
    console.log(`files text ${filesText}`)
    if (error) {
        return <Error message={error} />
    }

    if (displayMessage) {
        return <Success message={displayMessage} />
    }

    return (
        <Dialog
            fullScreen
            open={open}
            onClose={handleClose}
        // TransitionComponent={Transition}
        >
            <DialogTitle sx={{ marginLeft: 3 }}>ADD JOB</DialogTitle>
            <Grid container spacing={2} sx={{ marginLeft: 3 }} >
                <form onSubmit={(e) => {
                    e.preventDefault()
                    /* do submit stuff here */
                }}>
                    <Grid item container spacing={2}>
                        <Grid item container spacing={1} xs={12}>
                            <Grid item container spacing={3} xs={12}>
                                <Grid item xs={12} >
                                    <FormControl >
                                        <InputLabel id="job-type">Job Type</InputLabel>
                                        <Select
                                            labelId="job-type"
                                            id="select-job-type"
                                            value={jobType}
                                            label="Job Type"
                                            onChange={handleChange}
                                        >
                                            <MenuItem value='PROCESS_ALL'>PROCESS_ALL</MenuItem>
                                            <MenuItem value='PROCESS_LAST_THREE'>PROCESS_LAST_THREE</MenuItem>
                                            <MenuItem value='TRANSFORM'>TRANSFORM</MenuItem>
                                            <MenuItem value='LOAD_ALL'>LOAD_ALL</MenuItem>
                                            <MenuItem value='TEST'>TEST</MenuItem>
                                        </Select>
                                    </FormControl>

                                </Grid>
                                {((jobType === 'PROCESS_ALL') || (jobType === 'PROCESS_LAST_THREE')) &&
                                    <Grid item xs={12} md={6}>
                                        <FormControl fullWidth>
                                            <InputLabel htmlFor="search_criteria">Search Criteria</InputLabel>
                                            <Input id="search-criteria" value={searchCriteria} onChange={(e) => {
                                                console.log(e.target.value)
                                                const val = e.target.value
                                                setSearchCriteria(e.target.value)
                                            }} />
                                        </FormControl>
                                    </Grid>
                                }
                                {jobType === 'PROCESS_LAST_THREE' &&
                                    <Grid item xs={12} md={2}>
                                        <FormControl fullWidth>
                                            <InputLabel htmlFor="since">Since</InputLabel>
                                            <Input id="since" value={since} onChange={(e) => {
                                                console.log(e.target.value)
                                                const val = e.target.value
                                                setSince(val)
                                            }} />
                                        </FormControl>
                                    </Grid>
                                }
                                {jobType === 'TRANSFORM' &&
                                    <Grid item xs={12} md={12}>
                                        <TextField
                                            id="tf-files"
                                            label="Transform Files"
                                            placeholder="Enter files to transform"
                                            multiline
                                            fullWidth
                                            value={filesText}
                                            onChange={(e) => {
                                                console.log(e.target.value)
                                                const val = e.target.value
                                                setFilesText(val)
                                            }}
                                        />
                                        <Button variant="contained" component="label">Choose File<TextField
                                            id="outlined-basic"
                                            label="Outlined"
                                            variant="outlined"
                                            type="file"
                                            sx={{ marginTop: 2, marginBottom: 1 }}
                                            onChange={(e) => {
                                                console.log(e.target.value)
                                                const val = e.target.value
                                                setUploadFile(e.target.files[0])
                                            }}
                                            sx={{display:"none"}}
                                        /></Button>
                                        <Button variant="contained" color="primary"
                                            startIcon={<AddIcon />}
                                            onClick={(e) => {
                                                e.preventDefault()
                                                console.log('upload file new job')
                                                console.log(uploadFile)
                                                BankStatementService.upload_url().then(res => {
                                                    if (!res.ok) {
                                                        
                                                        return res.json().then(message => { throw new Error(message); })
                                                    }
                                                    return res.json();
                                                })
                                                    .then((data) => {
                                                        console.log(data.upload_url); console.log(uploadFile.type)
                                                        console.log(data.key)
                                                        fetch(data.upload_url, {
                                                            method: 'PUT',
                                                            body: uploadFile,
                                                            headers: {
                                                              'Content-Type': uploadFile.type}
                                                        }).then(res => {
                                                    if (!res.ok) {
                                                        console.log(res.status)
                                                        console.log(res.statusText)
                                                        console.log(JSON.stringify(res, null, 2))
                                                        return res.text().then(message => { throw new Error(`${res.status}:${res.statusText}:${message}`); })
                                                    }
                                                    return res.text();
                                                })
                                                    .then((uploadData) => {
                                                        console.log(uploadData); console.log(data.key);console.log(filesText)
                                                        setFilesText(data.key)
                                                    })
                                                    .catch((error) => {
                                                        console.log(`Error: ${error.message}`);
                                                        setError(error.message);
                                                    });
                                                    })
                                                    .catch((error) => {
                                                        console.log(`Error: ${error.message}`);
                                                        setError(error.message);
                                                    });
                                            }}
                                            sx={{ margin: 2 }}
                                        >
                                            Upload
                                        </Button>
                                    </Grid>
                                }
                            </Grid>
                        </Grid>
                        <Grid item container spacing={1} xs={12}>
                            <Grid item>
                                <Button type="submit" variant="contained" color="primary"
                                    startIcon={<AddIcon />}
                                    onClick={(e) => {
                                        e.preventDefault()
                                        console.log('add new job')
                                        const job = { job_type: jobType, payload: JSON.stringify(get_payload(jobType)) }
                                        console.log(job)
                                        add_job(job)
                                    }}
                                >
                                    Add
                                </Button>

                            </Grid>
                            <Grid item>
                                <Button type="secondary" variant="contained" color="secondary"
                                    startIcon={<CancelIcon />}
                                    onClick={(e) => {

                                        console.log('close')
                                        handleClose()
                                    }}
                                >
                                    Cancel
                                </Button>
                            </Grid>
                        </Grid>
                    </Grid>
                </form>
            </Grid>
        </Dialog>

    );
}


export default AddJob;
