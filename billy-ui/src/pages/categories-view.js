import CategoryService from '../services/categories';
import { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Chip, List, ListItem, Link, Divider, Stack } from '@mui/material';
import { Grid, Paper, Button } from '@mui/material';
import TextField from '@mui/material/TextField';
import AddIcon from '@mui/icons-material/Add';
import SaveIcon from '@mui/icons-material/Save';
import { Error, Success } from '../components/messages';

const KeyWords = ({ key_words }) => {
    return key_words.map((kew_word) => <Chip color='secondary' key={kew_word} label={kew_word} />)
}

const Category = ({ category, handleSave }) => {
    const [keyWord, setKeyWord] = useState()
    const [keyWords, setKeyWords] = useState(category.key_words)
    const [name, setName] = useState(category.name)
    const [save, setSave] = useState(false)
    const [data, setData] = useState()
    // const [loading, setLoading] = useState(true)
    const [error, setError] = useState()
    const [displayMessage, setDisplayMessage] = useState()

    const saveCategory = (category) => CategoryService.save_category(category)
        .then(res => {
            if (!res.ok) {
                return res.text().then(message => { setSave(false); throw new Error(message); })
            }
            return res.json();
        })
        .then(setData)
        .then(() => {
            setError(null)
            setSave(false)
            setDisplayMessage(`Successfully updated category ${category.name}.`)
            handleSave()
        })
        .catch((error) => {
            console.log(`Error`);
            console.log(error);
            setError(error.message);
        });
    useEffect(() => {
        const category = { 'name': name, key_words: keyWords }
        console.log(category)
        save && saveCategory(category);
    }, [save]);
    if (error) {
        return <Error message={error} />
    }

    return <ListItem key={category.name} href="/dashboard">
        <Paper elevation={1} sx={{ width: '100%', padding: 2 }}>
            <Grid container spacing={1}>
                <Grid item xs={12}>
                    <Box>
                        <Chip label={category.name} color='primary' variant='contained' />
                    </Box>
                </Grid>
                <Grid item xs={12}>
                    <Divider />
                </Grid>
                <Grid item container xs={12} justifyContent={'space-between'} >
                    <Grid item>
                        <TextField
                            id="key-word"
                            label=""
                            placeholder="Key word..."
                            size="small"
                            value={keyWord}
                            onChange={(e) => {
                                const val = e.target.value
                                console.log(e.target.value)
                                setKeyWord(val)
                            }}
                            sx={{
                                display: 'flex'
                            }}
                        />

                    </Grid>

                    <Button variant="outlined" size="small" color="secondary"
                        startIcon={<AddIcon />}
                        onClick={(e) => {
                            e.preventDefault()

                            console.log(keyWord)
                            if (keyWord) {
                                console.log(`Adding key word ${keyWord}...`)
                                const _keyWords = [keyWord, ...keyWords]
                                // console.log(_keyWords)
                                setKeyWord('')
                                setKeyWords(_keyWords)
                            } else {
                                console.log('Empty key word.')
                            }
                        }}
                        sx={{
                            display: 'flex'
                        }}
                    >
                        Add
                    </Button>


                </Grid>

                <Grid item xs={12} >
                    {keyWords.map((kew_word) => {
                        const _key_word = kew_word
                        return (<Chip color='secondary' key={kew_word} label={kew_word} sx={{
                            margin: 0.5
                        }} onDelete={() => {
                            console.log(`Removing key word ${_key_word}`)
                            setKeyWords(keyWords.filter(kw => kw !== _key_word))
                        }} variant='outlined' />)

                    })}
                </Grid>
                <Grid item xs={12}>
                    <Divider />
                </Grid>
                <Grid item xs={12}>
                    <Button variant="contained" size="small" color="primary"
                        startIcon={<SaveIcon />}
                        onClick={(e) => {
                            e.preventDefault()
                            console.log('Saving category..')
                            setSave(true)
                        }}
                        sx={{
                            display: 'flex'
                        }}
                    >
                        Save
                    </Button>
                    {displayMessage && <Success message={displayMessage}></Success>}
                </Grid>
            </Grid>
        </Paper>

    </ListItem>

}
function CategoriesView({ }) {
    const [data, setData] = useState()
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState()
    const [reload, setReload] = useState(false)

    const fetch_categories = () => CategoryService.get_all()
        .then(res => {
            if (!res.ok) {
                return res.json().then(message => { setLoading(false); throw new Error(message); })
            }
            return res.json();
        })
        .then(setData)
        .then(() => {
            setLoading(false)
            setReload(false)
        })
        .catch((error) => {
            console.log(`Error: ${error}`);
            setError(error);
        });
    useEffect(() => {
        fetch_categories();
    }, [reload]);
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
                            <Category category={category} handleSave={() => {
                                setReload(true)
                            }} />
                        )
                    })}
                </List>
            </>

        );

    }
    return null
}

export default CategoriesView;
