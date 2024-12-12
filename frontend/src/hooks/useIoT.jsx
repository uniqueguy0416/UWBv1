// import { set } from "mongoose";
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
  pending: Boolean,
  islogin: Boolean,
});
const IoTProvider = (props) => {
  const [tempPalletDest, setTempPalletDest] = useState([]);
  const [route, setRoute] = useState([]);
  const [selected, setSelected] = useState(false);
  const [closeEnough, setCloseEnough] = useState(false);
  const [userID, setUserID] = useState("");
  const [pending, setPending] = useState(false);
  const [islogin, setIslogin] = useState(false);
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
      case "checkUser": {
        console.log("res", payload);
        const { status, msg } = payload;

        if (status) {
          setUserID(msg);
        }
        break;
      }
      case "findPallet": {
        break;
      }
      case "Modify": {
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
      body: JSON.stringify({ dest: tempPalletDest }),
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
    const data = { type: "addUser", payload: { userID: id, pwd: pwd, status: "not-active", last_position: [0, 0] } };
    sendData(data);
  };
  const checkUser = (id, pwd) => {
    const data = { type: "checkUser", payload: { userID: id, pwd: pwd, status: "not-active", last_position: [0, 0] } };
    sendData(data);
  };
  return (
    <IoTContext.Provider value={{ islogin, setIslogin, pending, checkUser, addUser, userID, tempPalletDest, setTempPalletDest, route, setSelected, selected, closeEnough, sendData }} {...props} />
  );
};
const useIoT = () => useContext(IoTContext);
export { IoTProvider, useIoT };
