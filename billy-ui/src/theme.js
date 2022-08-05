import { createTheme } from '@mui/material/styles';
// A custom theme for this app
const myTheme = createTheme({
    overrides: {
        MuiPaper: {
            root: {
                padding: '20px 10px',
                margin: '10px',
                // backgroundColor: '#fff', // 5d737e
            },
        },
        MuiButton: {
            root: {
                margin: '5px',
            },
        },
    },
});
export default myTheme;