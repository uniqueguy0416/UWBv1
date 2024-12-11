import { useContext, createContext, useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import XMLHttpRequest from "xhr2";
var client = new XMLHttpRequest();

const IoTContext = createContext({
  tempPalletDest: [],
  route: [],
});
const IoTProvider = (props) => {
  const [tempPalletDest, setTempPalletDest] = useState([]);
  const [route, setRoute] = useState([]);

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

  return <IoTContext.Provider value={{ tempPalletDest, setTempPalletDest, route }} {...props} />;
};
const useIoT = () => useContext(IoTContext);
export { IoTProvider, useIoT };
