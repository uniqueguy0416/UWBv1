import React from "react";
import styled from "styled-components";
import Box from "@mui/material/Box";
import { useNavigate } from "react-router";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
const Wrapper = styled.div`
  width: 70%;
  height: 100%;
  margin: 5px 5px 5px 5px; // top right bottom left
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  align-items: start;
  justify-content: center;
`;

const pages = ["尋找棧板", "放下棧板", "更新棧板資料", "新增棧板"];

export default function Home(props) {
  //   const { login, setLogin } = useNMLab();
  //   const navigate = useNavigate();
  //   const selectCard = (title) => {
  //     if (title === "註冊帳號") navigate("/register");
  //     else if (title === "列印／掃描") navigate("/printMenu");
  //   };
  console.log(import.meta.env.VITE_Mapbox_API_Token);
  const navigate = useNavigate();
  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="90vh">
      <Stack spacing={2} sx={{ width: 1 / 3, textAlign: "center" }}>
        <Typography variant="h2" component="h2">
          棧板管理系統
        </Typography>
        <Button variant="outlined" onClick={() => navigate("/selectType")}>
          尋找棧板
        </Button>
        <Button variant="outlined" onClick={() => navigate("/drop")}>
          放下棧板
        </Button>
        <Button variant="outlined" onClick={() => navigate("/update")}>
          更新棧板資料
        </Button>
        <Button variant="outlined" onClick={() => navigate("/add")}>
          新增棧板
        </Button>
      </Stack>
    </Box>
  );
}
