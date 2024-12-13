import { Avatar, Box, Container, FormControlLabel, Paper, TextField, Typography, Checkbox, Button, Grid, Link } from "@mui/material";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import { Link as RouterLink } from "react-router-dom";
import { useIoT } from "../hooks/useIoT";
import { useNavigate } from "react-router";
import HowToRegOutlinedIcon from "@mui/icons-material/HowToRegOutlined";
import CircularProgress from "@mui/material/CircularProgress";
import { useState, useEffect } from "react";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import { use } from "react";

export default function PalletInfo(props) {
  //   const { login, setLogin } = useNMLab();
  //   const navigate = useNavigate();
  //   const selectCard = (title) => {
  //     if (title === "註冊帳號") navigate("/register");
  //     else if (title === "列印／掃描") navigate("/printMenu");
  //   };
  const navigate = useNavigate();

  const { storePalletInfo, singlePalletInfo, userID, task } = useIoT();

  const [content, setContent] = useState("");
  const [status, setStatus] = useState("");
  const [type, setType] = useState("");

  const statusChange = (event) => {
    setStatus(event.target.value);
  };
  const typeChange = (event) => {
    setType(event.target.value);
  };

  useEffect(() => {
    if (task === "putDown" || task === "update") {
      setContent(singlePalletInfo.content);
      setStatus(singlePalletInfo.status);
      setType(singlePalletInfo.type);
    }
  }, []);

  useEffect(() => {
    if (task === "") {
      navigate("/home");
    }
  }, [task]);
  const saveInfo = () => {
    console.log("saveInfo");
    if (status === "" || type === "") {
      alert("請填寫完整資料");
      return;
    }
    const data = { status: status, type: type, content: content, position: singlePalletInfo.position, final_user: userID };
    console.log(data);
    storePalletInfo(data);
  };
  return (
    <Container maxWidth="xs">
      <Paper elevation={10} sx={{ padding: 2 }}>
        <Box sx={{ padding: 2 }}>
          <Typography component="h1" variant="h5" sx={{ textAlign: "center" }}>
            棧板資訊
          </Typography>
        </Box>
        <Box component="form" noValidate sx={{ mt: 1, mx: 2, display: "flex", flexDirection: "column", alignItems: "center" }}>
          {/* status */}
          <FormControl variant="standard" sx={{ mt: 1, textAlign: "left", width: "60%" }}>
            <InputLabel id="demo-simple-select-standard-label">棧板狀態</InputLabel>
            <Select labelId="demo-simple-select-standard-label" id="demo-simple-select-standard" value={status} onChange={statusChange}>
              <MenuItem value={"broken"}>壞了</MenuItem>
              <MenuItem value={"static"}>正常</MenuItem>
            </Select>
          </FormControl>
          {/* type */}
          <FormControl variant="standard" sx={{ mt: 3, textAlign: "left", width: "60%" }}>
            <InputLabel id="demo-simple-select-standard-label">棧板種類</InputLabel>
            <Select labelId="demo-simple-select-standard-label" defaultValue="川字形" id="demo-simple-select-standard" value={type} onChange={typeChange}>
              {/* // 川字形, 田字型, 九宮格式, 雙面 */}
              <MenuItem value={"川字形"}>川字形</MenuItem>
              <MenuItem value={"田字型"}>田字型</MenuItem>
              <MenuItem value={"九宮格式"}>九宮格式</MenuItem>
              <MenuItem value={"雙面"}>雙面</MenuItem>
            </Select>
          </FormControl>
          {/* content */}
          <TextField id="standard-required" label="物品" defaultValue="" variant="standard" onChange={(e) => setContent(e.target.value)} sx={{ mt: 3, width: "60%" }} />
        </Box>
        <Box sx={{ padding: 3 }}>
          <Button type="submit" variant="contained" fullWidth sx={{ mt: 1 }} onClick={() => saveInfo()}>
            確認資料
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}
