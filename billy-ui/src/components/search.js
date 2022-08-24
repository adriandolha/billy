import InputAdornment from "@mui/material/InputAdornment";
import Search from '@mui/icons-material/Search';
import { TextField, IconButton } from "@mui/material";
import { debounce } from "lodash"
import {useMemo} from 'react'



export default function SearchInput({ handleSearch }) {
    const debouncedSearch = useMemo(
        () => debounce(handleSearch, 300)
        , []);


    return (
        <TextField sx={{ marginBottom: 2, width: '100%' }}
            label="Search bank statements..."
            InputProps={{
                endAdornment: (
                    <InputAdornment position="end">
                        <IconButton >
                            <Search />
                        </IconButton>
                    </InputAdornment>
                )
            }}
            onChange={debouncedSearch}
        />
    );
}
