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
  const [singlePalletInfo, setSinglePalletInfo] = useState({ status: "static", type: "", content: "", position: [0, 0], final_user: "" });
  const [selection, setSelection] = useState([]); // available type/content of pallets
  const [availablePallet, setAvailablePallet] = useState({});
  const checkUserPallet = async (id) => {
    // check if the user has a pallet
    setPending(true);
    console.log("checkUserPallet in");
    sendData({ type: "checkUserPallet", payload: { userID: id } });
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
    setSinglePalletInfo({ status: "static", type: "", content: "", position: [0, 0], final_user: "" });
    setSelection([]);
    setAvailablePallet({});
  };
  const getUserPos = async (id) => {
    // get user position
    setPending(true);
    // ToDo: call get position api
    setUserPos([121.54457, 25.017855]);
  };
  // For putDown
  // get pallet info by using user's pallet id
  const getPalletInfo = async (id) => {};
  const getAvailablePallet = async (req) => {
    // for finding pallet
    console.log("getAvailablePallet in", req);
    const data = { type: "findAvailablePallet", payload: req };
    sendData(data);
  };
  const storePalletInfo = async (data) => {
    //Todo: send to mongodb
    switch (task) {
      case "addPallet": {
        data = {
          type: "addPallet",
          payload: {
            status: data.status,
            type: data.type,
            content: data.content,
            position: userPos,
            final_user: data.final_user,
          },
        };
        break;
      }
    }
    sendData(data);
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
      // display the available pallets
      case "successful": {
        alert(payload.msg);
        // reset information
        setSinglePalletInfo({ status: "static", type: "", content: "", position: [0, 0], final_user: "" });
        reset();

        break;
      }
      case "findSelections": {
        const { selected } = payload;
        console.log("selected", selected);
        setSelection(selected);
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

    // switch (task) {
    //   case "CHAT":
    //     console.log(payload);
    //     setMessages(payload);
    //     break;
    //   case "MESSAGE": {
    //     console.log(payload, "djfklskjf");
    //     setMessages(() => [...messages, payload]);
    //     break;
    //   }
    // }
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
