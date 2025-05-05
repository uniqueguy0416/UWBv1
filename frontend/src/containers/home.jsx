import React, { useEffect } from "react";
import styled from "styled-components";
import Box from "@mui/material/Box";
import { useNavigate } from "react-router";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useIoT } from "../hooks/useIoT";
import CircularProgress from "@mui/material/CircularProgress";
import SearchBar from "./searchBar";
// // width: 50%;
// margin: 5px 5px 5px 5px; // top right bottom left
//   display: flex;
//   flex-direction: row;
//   flex-wrap: wrap;
//   align-items: start;
//   justify-content: center;
const Wrapper = styled.div`
  height: 50%;
  padding: 0px;
  &:hover {
    background-color: darkblue; /* Background color on hover */
    color: white; /* Text color on hover */
  }
`;
const hoverStyle = {
  backgroundColor: "#bbdefb", // 滑鼠旋停顏色
  cursor: "pointer",
  transform: "scale(1.03)",
  boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.15)",
  transition: "all 0.3s ease-in-out",
};


const pages = ["尋找棧板", "放下棧板", "更新棧板資料", "新增棧板"];

export default function Home(props) {
  console.log(import.meta.env.VITE_Mapbox_API_Token);
  const navigate = useNavigate();

  const { userID, getNearPallet, availablePallet, getPalletInfo, setCheck, check, checkUserPallet, pending, setPending, userPos, getUserPos, task, setTask } = useIoT();

  useEffect(() => {
    switch (task) {
      case "find":
      case "putDown":
        // Todo: check if there is a pallet of this user
        checkUserPallet();
        break;
      case "update":
        getNearPallet();
        break;
      case "addPallet":
        setPending(false);
        navigate("/showPos");
        break;
      default:
        break;
    }
  }, [userPos]);
  useEffect(() => {
    if (userID === "") navigate("/");
  }, [userID]);
  useEffect(() => {
    // first get user position
    if (task !== "") {
      getUserPos();
      console.log("get user pos");
    }
  }, [task]);

  // check user's palletID existence
  useEffect(() => {
    console.log("check", check);
    if (check) {
      setPending(false);
      if (task === "putDown") {
        getPalletInfo();
        navigate("/showPos");
      } else if (task === "find") navigate("/selectType");
      setCheck(false);
    }
  }, [check]);
  useEffect(() => {
    if (task === "update") {
      setPending(false);
      navigate("/allPallet");
    }
  }, [availablePallet]);
  return (
    <Box sx={{ width: "100%", padding: "0px", height: "100%" }}>
      <SearchBar />
      <Box sx={{ padding: "0" }} display="flex" justifyContent="center" alignItems="center" height="80vh">
        {pending ? (
          <CircularProgress />
        ) : (
          <>
            <Box spacing={2} sx={{ width: 1 / 2, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", height: "100%" }}>
              <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                height="50%"
                width="100%"
                borderRight="4px #1976D2 solid"
                borderBottom="4px #1976D2 solid"
                sx={{
                  borderRadius: "16px",
                  backgroundColor: "#f0f4ff",
                  transition: "all 0.3s ease-in-out",
                  "&:hover": {
                    backgroundColor: "#bbdefb", // 淡藍色
                    transform: "scale(1.03)",
                    boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.15)",
                    cursor: "pointer",
                  },
                }}
                onClick={() => setTask("find")}
              >
                <Typography variant="h4" component="div" sx={{ flexGrow: 1, fontWeight: "bold", textAlign: "center" }}>
                  尋找棧板
                </Typography>
              </Box>

              <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                height="50%"
                width="100%"
                borderRight="4px #1976D2 solid"
                borderBottom="4px #1976D2 solid"
                sx={{
                  borderRadius: "16px",
                  backgroundColor: "#f1f8e9",
                  transition: "all 0.3s ease-in-out",
                  "&:hover": {
                    backgroundColor: "#c8e6c9",
                    transform: "scale(1.03)",
                    boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.15)",
                    cursor: "pointer",
                  },
                }}
                onClick={() => setTask("putDown")}
              >
                <Typography variant="h4" component="div" sx={{ flexGrow: 1, fontWeight: "bold", textAlign: "center" }}>
                  放下棧板
                </Typography>
                {/* <Button sx={{ width: "100%", height: "100%" }} variant="outlined" onClick={() => setTask("find")}>
                  尋找棧板
                </Button> */}
              </Box>
            </Box>
            <Box spacing={2} sx={{ width: 1 / 2, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", height: "100%" }}>
              <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                height="50%"
                width="100%"
                borderLeft="4px #1976D2 solid"
                borderBottom="4px #1976D2 solid"
                sx={{
                  borderRadius: "16px",
                  backgroundColor: "#fffde7",
                  transition: "all 0.3s ease-in-out",
                  "&:hover": {
                    backgroundColor: "#fff59d",
                    transform: "scale(1.03)",
                    boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.15)",
                    cursor: "pointer",
                  },
                }}
                onClick={() => setTask("update")}
              >
                <Typography variant="h4" component="div"  sx={{ flexGrow: 1, fontWeight: "bold", textAlign: "center" }}>
                  更新棧板資料
                </Typography>
              </Box>

              <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                height="50%"
                width="100%"
                borderLeft="4px #1976D2 solid"
                borderBottom="4px #1976D2 solid"
                sx={{
                  borderRadius: "16px",
                  backgroundColor: "#fff3e0",
                  transition: "all 0.3s ease-in-out",
                  "&:hover": {
                    backgroundColor: "#ffcc80",
                    transform: "scale(1.03)",
                    boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.15)",
                    cursor: "pointer",
                  },
                }}
                onClick={() => setTask("addPallet")}
              >
                <Typography variant="h4" component="div"  sx={{ flexGrow: 1, fontWeight: "bold", textAlign: "center" }}>
                  新增棧板
                </Typography>
                {/* <Button sx={{ width: "100%", height: "100%" }} variant="outlined" onClick={() => setTask("find")}>
                  尋找棧板
                </Button> */}
              </Box>
            </Box>
          </>
        )}
      </Box>
    </Box>
  );
}
