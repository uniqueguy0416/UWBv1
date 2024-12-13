import React, { useEffect, useState } from "react";
// import NestedCard from "../../components/card";
import styled from "styled-components";
import Box from "@mui/material/Box";
// import { useNMLab } from "../hooks/useNMLab";
import { useNavigate } from "react-router";
// import AdCard from "../../components/funcCard";
// import AdCard2 from "../../components/adCard2";
import Button from "@mui/material/Button";
import ButtonGroup from "@mui/material/ButtonGroup";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useIoT } from "../../hooks/useIoT";
import CircularProgress from "@mui/material/CircularProgress";
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
// overflow-y: scroll;

const types = ["尋找棧板", "放下棧板", "更新棧板資料", "新增棧板"];

export default function SelectType(props) {
  const { selection, findSelection, pending, setPending } = useIoT();
  const [task, setTask] = useState("");
  const navigate = useNavigate();
  useEffect(() => {
    if (task == "setContent") {
      findSelection(true);
      console.log("setContent");
    } else if (task == "empty") {
      findSelection(false);
      console.log("empty");
    }
  }, [task]);
  useEffect(() => {
    if (selection.length > 0) {
      console.log("selection", selection);
      setPending(false);
      navigate("/selectContent");
    }
  }, [selection]);
  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
      {pending ? (
        <CircularProgress />
      ) : (
        <Stack spacing={2} sx={{ width: 1 / 3, textAlign: "center" }}>
          {/* <ButtonGroup sx={{ width: 1 / 4 }} orientation="vertical" aria-label="Vertical navigation group"> */}
          <Typography variant="h2" component="h2">
            棧板種類
          </Typography>
          <Button variant="outlined" onClick={() => setTask("empty")}>
            空的棧板
          </Button>
          <Button variant="outlined" onClick={() => setTask("setContent")}>
            物品
          </Button>
        </Stack>
      )}
    </Box>
  );
}
