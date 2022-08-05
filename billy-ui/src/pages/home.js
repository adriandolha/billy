import { Fragment } from 'react';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';

export default function Home() {
    return (
        <Fragment>
            {/* <Box
                component="main"
                sx={{ flexGrow: 1, bgcolor: 'background.default', p: 3 }}
            > */}
                {/* <Toolbar /> */}
                <Typography paragraph>
                    Billy is an application for expenses and bills analytics.
                </Typography>
                <Typography paragraph>
                    Depending on the bank and provider, they may provide some reporting, usually on a monthly basis.
                    They may also include grouping by categories and show how much you spend on food, travel, etc.
                    Still, it’s difficult to get a general overview of spending trends and provider increases, if any.
                    Billy can answer the following questions:
                    - How much do you spend on monthly average per category?
                    - Are there any increases in provider bills? It considers price per unit.
                    In order to do this we need to collect data from different providers:
                    - bank statements, scraped from mail or generated from banking apps
                    - Bills, scraped from provider’s sites: eon, orange, rcs rds, yahoo mails for apartment
                </Typography>
            {/* </Box> */}
        </Fragment>
    );
}
