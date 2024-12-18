import { Avatar, Box, Container, FormControlLabel, Paper, TextField, Typography, Checkbox, Button, Grid, Link } from "@mui/material";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import { Link as RouterLink } from "react-router-dom";
import { useIoT } from "../hooks/useIoT";
import { useNavigate } from "react-router";
import HowToRegOutlinedIcon from "@mui/icons-material/HowToRegOutlined";
import CircularProgress from "@mui/material/CircularProgress";
import { useState, useEffect } from "react";
export default function Login() {
  const navigate = useNavigate();
  const { userID, addUser, checkUser, pending, islogin, setIslogin } = useIoT();
  const [id, setId] = useState("");
  const [password, setPassword] = useState("");

  const login = (id, password) => {
    console.log("login");
    checkUser(id, password);
  };
  useEffect(() => {
    if (userID != "" && !islogin) {
      setIslogin(true);
      if (userID === "admin") navigate("/adminHome");
      else navigate("/home");
    }
  }, [userID]);
  return (
    <Container maxWidth="xs">
      <Paper elevation={10} sx={{ padding: 2 }}>
        <Box sx={{ padding: 2 }}>
          <Avatar
            sx={{
              mx: "auto",
              bgcolor: "secondary.main",
              textAlign: "center",
              mb: 1,
            }}
          >
            {!islogin ? <LockOutlinedIcon /> : <HowToRegOutlinedIcon />}
          </Avatar>

          <Typography component="h1" variant="h5" sx={{ textAlign: "center" }}>
            {!islogin ? "Sign In" : "Create a new account"}
          </Typography>
        </Box>
        <Box component="form" noValidate sx={{ mt: 1, mx: 2 }}>
          <TextField placeholder="Enter userID" fullWidth required autoFocus sx={{ mb: 2 }} onChange={(e) => setId(e.target.value)} />
          <TextField placeholder="Enter password" fullWidth required onChange={(e) => setPassword(e.target.value)} />
        </Box>
        <Box sx={{ padding: 3 }}>
          {!islogin ? (
            <Button type="submit" variant="contained" fullWidth sx={{ mt: 1 }} onClick={() => login(id, password)}>
              Sign In
            </Button>
          ) : (
            <Button type="submit" variant="contained" fullWidth sx={{ mt: 1 }} onClick={() => addUser(id, password)}>
              Create a new account
            </Button>
          )}
        </Box>
      </Paper>
    </Container>
  );
}
