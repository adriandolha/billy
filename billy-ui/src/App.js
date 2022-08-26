import React, { Component } from "react";
import { Routes, Route } from "react-router-dom";
import "./App.css";
import NotFoundPage from "./pages/not-found";
import Home from "./pages/home";
import { Container, Grid, Box, Typography } from "@mui/material";
import Login from "./components/login";
// import Register from "./components/register";
// import Profile from "./pages/profile";
import Dashboard from './pages/dashboard';
import BankStatements from './pages/bank-statements';
import AppBarMenu from "./pages/app-bar";
import Sidebar from './pages/sidebar';
import { ThemeProvider } from "@mui/material/styles";
import myTheme from "./theme";
import authService from "./services/auth-service";
import JobsView from "./pages/jobs-view";
import CategoriesView from "./pages/categories-view";
const drawerWidth = 240;

class App extends Component {
  constructor(props) {
    super(props);
  }
  state = {
    mobileOpen: false
  }


  render() {
    const handleDrawerToggle = () => {
      this.setState({ mobileOpen: !this.state.mobileOpen })

    };
    const mobileOpen = this.state.mobileOpen;
    const currentUser = authService.getCurrentUser()
    return (
      <Box sx={{ display: 'flex' }}>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"></meta>
        {currentUser && <AppBarMenu handleDrawerToggle={handleDrawerToggle} />}
        {currentUser && <Sidebar mobileOpen={mobileOpen} handleDrawerToggle={handleDrawerToggle} />}
        <ThemeProvider theme={myTheme}>
          <Box
            component="main"
            sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` }, marginTop: '30px'}}
          >
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/home" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/jobs" element={<JobsView />} />
              <Route path="/categories" element={<CategoriesView />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/bank-statements" element={<BankStatements />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Box>
        </ThemeProvider>

      </Box>
    );
  }
}

export default App;