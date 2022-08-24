import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import Link from '@mui/material/Link';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Dashboard from '@mui/icons-material/Dashboard';
import AccountBalance from '@mui/icons-material/AccountBalance';

const drawerWidth = 240;

export default function Sidebar(props) {
    const { window, mobileOpen, handleDrawerToggle } = props;

    const drawer = <>
        <Toolbar sx={{ backgroundColor: 'primary.light' }}>
            <Typography variant="h6" noWrap component="div" >
                Billy
            </Typography>
        </Toolbar>
        <Divider />
        <List>
            <ListItem key="dashboard" disablePadding component={Link} href="/dashboard">
                <ListItemButton>
                    <ListItemIcon>
                        <Dashboard />
                    </ListItemIcon>
                    <ListItemText primary="Dasboard" />
                </ListItemButton>
            </ListItem>
            <ListItem key="bank_statements" disablePadding component={Link} href="/bank-statements">
                <ListItemButton>
                    <ListItemIcon>
                        <AccountBalance />
                    </ListItemIcon>
                    <ListItemText primary="Bank Statements" />
                </ListItemButton>
            </ListItem>
            <ListItem key="jobs" disablePadding component={Link} href="/jobs">
                <ListItemButton>
                    <ListItemIcon>
                        <AccountBalance />
                    </ListItemIcon>
                    <ListItemText primary="Jobs" />
                </ListItemButton>
            </ListItem>
        </List>
    </>
    const container = window !== undefined ? () => window().document.body : undefined;

    return (
        <Box sx={{ display: 'flex' }}>
            <CssBaseline />
            <Drawer
                container={container}
                variant="temporary"
                open={mobileOpen}
                onClose={handleDrawerToggle}
                ModalProps={{
                    keepMounted: true, // Better open performance on mobile.
                }}
                sx={{
                    display: { xs: 'block', sm: 'none' },
                    '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                }}
            >
                {drawer}
            </Drawer>
            <Drawer
                variant="permanent"
                sx={{ 
                    display: { xs: 'none', sm: 'block' },
                    width: drawerWidth,
                    '& .MuiDrawer-paper': {
                        width: drawerWidth,
                        boxSizing: 'border-box',
                    },
                }}
                open
                anchor='left'
            >
                {drawer}
            </Drawer>
        </Box>
    );
}
