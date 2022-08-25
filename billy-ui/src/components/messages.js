import { Snackbar, Alert } from '@mui/material';

const Message = ({message, severity}) => {
    return (
        <Snackbar open={true} autoHideDuration={6000}>
            <Alert severity={severity} sx={{ width: '100%' }}>
                {message}
            </Alert>
        </Snackbar>
    );

}
function Error({ message }) {
    return (
        <Message message={message} severity="error"/>
    );
}

function Success({ message }) {
    return (
        <Message message={message} severity="success"/>
    );
}

export {Error, Success};
