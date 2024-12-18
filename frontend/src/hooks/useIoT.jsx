import { useContext, createContext, useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";

//backend of routing and positioning
import XMLHttpRequest from "xhr2";
var client = new XMLHttpRequest();

// backend of mongodb

const DBclient = new WebSocket("ws://localhost:4000");
DBclient.onopen = () => {
  console.log("backend socket server connected");
  // sendData();
};

const IoTContext = createContext({
  tempPalletDest: [],
  route: [],
  selected: Boolean,
  closeEnough: Boolean,
  sendData: () => {},
  userID: String,
  addUser: () => {},
  checkUser: () => {},
  checkUserPallet: () => {}, // check if the user has a pallet
  pending: Boolean,
  islogin: Boolean,
  userPos: [],
  getUserPos: () => {},
  task: "",
  singlePalletInfo: {},
  getPalletInfo: () => {}, //Todo
  getNearPallet: () => {}, //Todo
  selection: [],
  findSelection: () => {},
  getAvailablePallet: () => {},
  availablePallet: {},
  takeAwayPallet: () => {},
  check: Boolean,
  updateUser: () => {},
});
const IoTProvider = (props) => {
  const [tempPalletDest, setTempPalletDest] = useState([]);
  const [route, setRoute] = useState([]);
  const [selected, setSelected] = useState(false); // check if the pallet is selected(take-away)
  const [closeEnough, setCloseEnough] = useState(false);
  const [userID, setUserID] = useState(""); // get user id
  const [pending, setPending] = useState(false); // check if the request is pending
  const [islogin, setIslogin] = useState(false); // check if user is login
  const [userPos, setUserPos] = useState([121.54457, 25.017855]); //get user position
  const [task, setTask] = useState(""); // find, putDown, update, addPallet
  const [singlePalletInfo, setSinglePalletInfo] = useState({});
  const [selection, setSelection] = useState([]); // available type/content of pallets
  const [availablePallet, setAvailablePallet] = useState({});
  const [check, setCheck] = useState(false);
  const getNearPallet = async () => {
    // get near pallet (all)
    setPending(true);
    console.log("getNearPallet in");
    sendData({ type: "findAllPallet", payload: {} });
  };

  const checkUserPallet = async () => {
    // check if the user has a pallet
    setPending(true);
    console.log("checkUserPallet in");
    sendData({ type: "checkUserPallet", payload: { userID: userID, task: task } });
  };
  const findSelection = (content) => {
    // find available type/content of pallets
    setPending(true);
    console.log("findSelection in");
    sendData({ type: "findSelections", payload: { content: content } });
  };
  const takeAwayPallet = async (palletID) => {
    console.log("takeAwayPallet", { palletID: palletID, userID: userID });
    sendData({ type: "takeAway", payload: { palletID: palletID, userID: userID } });
    setTask("");
  };
  const reset = () => {
    console.log("reset");
    setTask("");
    setUserPos([]);
    setAvailablePallet({});
    setCloseEnough(false);
    setRoute([]);
    setTempPalletDest([]);
    setSelected(false);
    setPending(false);
    setSinglePalletInfo({});
    setSelection([]);
    setAvailablePallet({});
    setCheck(false);
  };
  const getUserPos = async (id) => {
    // get user position
    setPending(true);
    fetch("http://localhost:5500/pos")
      .then((response) => response.json())
      .then((data) => {
        setUserPos([data[1], data[0]]);
      })
      .catch((error) => {
        console.error("Error fetching position:", error);
      });
  };
  // For putDown
  // get pallet info by using user's pallet id
  const getPalletInfo = async () => {
    sendData({ type: "findOnePallet", payload: { userID: userID } });
  };
  const getAvailablePallet = async (req) => {
    // for finding pallet
    console.log("getAvailablePallet in", req);
    const data = { type: "findAvailablePallet", payload: req };
    sendData(data);
  };
  const updateUser = async () => {
    sendData({ type: "updateUser", payload: { userID: userID, palletID: "" } });
  };
  const storePalletInfo = async (data) => {
    //Todo: send to mongodb
    switch (task) {
      case "addPallet": {
        data = {
          type: "addPallet",
          payload: data,
        };
        sendData(data);
        break;
      }
      case "putDown": {
        data = {
          type: "updatePallet",
          payload: data,
        };
        sendData(data);
        break;
      }
      case "update": {
        data = {
          type: "updatePallet",
          payload: data,
        };
        sendData(data);
        break;
      }
    }
  };

  // send to mongodb
  const sendData = async (data) => {
    await DBclient.send(JSON.stringify(data));
  };

  // receive from mongodb
  DBclient.onmessage = (byteString) => {
    const { data } = byteString;
    const { type, payload } = JSON.parse(data);
    switch (type) {
      case "successfulUpdate": {
        if (task === "update") {
          console.log("recive");
          alert(payload.msg);
          setTask("");
        }
        break;
      }
      case "findAllPallet": {
        console.log(payload);
        setAvailablePallet(payload);
        break;
      }
      // display the available pallets
      case "findOnePallet": {
        console.log(payload);
        setSinglePalletInfo(payload);
        break;
      }
      case "successful": {
        alert(payload.msg);
        // reset information
        reset();

        break;
      }
      case "findSelections": {
        const { selected } = payload;
        console.log("selected", selected);
        setSelection(selected);
        break;
      }
      case "checkUserPallet": {
        const { status, msg } = payload;
        console.log("checkUserPallet", payload);
        if (status) {
          setCheck(true);
        } else {
          alert(msg);
          setTask("");
        }
        setPending(false);
        break;
      }
      case "checkUser": {
        console.log("res", payload);
        const { status, msg } = payload;

        if (status) {
          setUserID(msg);
        } else {
          alert(msg);
        }
        break;
      }
      case "findPallet": {
        break;
      }
      case "Modify": {
        break;
      }
      case "findAvailablePallet": {
        console.log("findAvailablePallet", payload);
        setAvailablePallet(payload);
        break;
      }
      default:
        break;
    }
  };
  //JSON.stringify() converting object to string
  //JSON.parse(str[,reviver]) converting string to object

  // find route
  useEffect(() => {
    fetch("http://localhost:5500/dest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dest: tempPalletDest, st: userPos }),
    })
      .then((response) => {
        return response.json(); // async and returns a Promise
      })
      .then((data) => {
        console.log(data["route"]); // Log the received JSON
        setRoute(data["route"]); // Update the state with the received JSON
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
      });
  }, [tempPalletDest]);

  const addUser = (id, pwd) => {
    console.log(id, pwd);
    const data = { type: "addUser", payload: { userID: id, pwd: pwd, status: "not-active", last_position: [0, 0], palletID: "" } };
    sendData(data);
  };
  const checkUser = (id, pwd) => {
    const data = { type: "checkUser", payload: { userID: id, pwd: pwd, status: "not-active" } };
    sendData(data);
  };
  return (
    <IoTContext.Provider
      value={{
        getNearPallet,
        updateUser,
        getPalletInfo,
        check,
        setCheck,
        checkUserPallet,
        takeAwayPallet,
        availablePallet,
        getAvailablePallet,
        findSelection,
        selection,
        storePalletInfo,
        singlePalletInfo,
        setSinglePalletInfo,
        task,
        setTask,
        userPos,
        getUserPos,
        islogin,
        setIslogin,
        pending,
        setPending,
        checkUser,
        addUser,
        userID,
        tempPalletDest,
        setTempPalletDest,
        route,
        setSelected,
        selected,
        closeEnough,
        sendData,
      }}
      {...props}
    />
  );
};
const useIoT = () => useContext(IoTContext);
export { IoTProvider, useIoT };
