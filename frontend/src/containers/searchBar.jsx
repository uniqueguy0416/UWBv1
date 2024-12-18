import * as React from "react";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";
import AccountCircle from "@mui/icons-material/AccountCircle";
import { useIoT } from "../hooks/useIoT";
export default function SearchBar() {
  const { userID, logout } = useIoT();

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Box
            sx={{
              display: "flex",
              flexDirection: "row",
            }}
          >
            <IconButton sx={{ padding: "0", mr: "1rem" }} size="large" aria-label="account of current user" aria-controls="menu-appbar" aria-haspopup="true" color="inherit">
              <AccountCircle />
            </IconButton>
            <Typography variant="h5" component="div" sx={{ flexGrow: 1 }}>
              user: {userID}
            </Typography>
          </Box>
          <Typography variant="h5" component="div" sx={{ flexGrow: 1 }}>
            棧板管理系統
          </Typography>
          <Button color="inherit" variant="h5" onClick={() => logout()}>
            LogOut
          </Button>
        </Toolbar>
      </AppBar>
    </Box>
  );
}
