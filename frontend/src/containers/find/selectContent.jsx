import { Avatar, Box, Container, FormControlLabel, Paper, TextField, Typography, Checkbox, Button, Grid, Link } from "@mui/material";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import { Link as RouterLink } from "react-router-dom";
import { useIoT } from "../../hooks/useIoT";
import { useNavigate } from "react-router";
import HowToRegOutlinedIcon from "@mui/icons-material/HowToRegOutlined";
import CircularProgress from "@mui/material/CircularProgress";
import { useState, useEffect } from "react";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import { use } from "react";

export default function SelectContent(props) {
  //   const { login, setLogin } = useNMLab();
  //   const navigate = useNavigate();
  //   const selectCard = (title) => {
  //     if (title === "註冊帳號") navigate("/register");
  //     else if (title === "列印／掃描") navigate("/printMenu");
  //   };
  const navigate = useNavigate();

  const { availablePallet, getAvailablePallet, selection } = useIoT();

  const [required, setRequired] = useState({});
  const statusChange = (event) => {
    setRequired({ thing: event.target.value, target: required.target });
  };

  useEffect(() => {
    console.log("selection hihiiihih");
    if (selection[0] == "物品") {
      setRequired({ thing: "", target: "content" });
    } else {
      setRequired({ thing: "", target: "type" });
    }
  }, []);
  useEffect(() => {
    if (Object.keys(availablePallet).length !== 0) {
      // availablePallet is not an empty object
      navigate("/palletMap");
    }
  }, [availablePallet]);
  const saveInfo = () => {
    console.log("sendrequired");
    console.log(required);
    if (required.thing === "") {
      alert("請填寫完整資料");
      return;
    }
    getAvailablePallet(required);
  };
  return (
    <Container maxWidth="xs">
      <Paper elevation={10} sx={{ padding: 2 }}>
        <Box sx={{ padding: 2 }}>
          <Typography component="h1" variant="h5" sx={{ textAlign: "center" }}>
            搜尋棧板資訊
          </Typography>
        </Box>
        <Box component="form" noValidate sx={{ mt: 1, mx: 2, display: "flex", flexDirection: "column", alignItems: "center" }}>
          {/* status */}
          <FormControl variant="standard" sx={{ mt: 1, textAlign: "left", width: "60%" }}>
            <InputLabel id="demo-simple-select-standard-label">{selection[0]}</InputLabel>
            <Select labelId="demo-simple-select-standard-label" id="demo-simple-select-standard" value={required.thing} onChange={statusChange}>
              {selection.slice(1).map((item) => (
                <MenuItem value={item}>{item}</MenuItem>
              ))}
            </Select>
          </FormControl>
          {/* type */}
        </Box>
        <Box sx={{ padding: 3 }}>
          <Button variant="contained" fullWidth sx={{ mt: 1, width: "60%" }} onClick={() => saveInfo()}>
            確認搜尋
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}
