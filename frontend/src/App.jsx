import { useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./containers/home";

import PalletMap from "./containers/find/palletMap";
import SelectType from "./containers/find/selectType";
import Login from "./containers/login";
import { IoTProvider } from "./hooks/useIoT";

function App() {
  return (
    <BrowserRouter>
      <IoTProvider>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/home" element={<Home />} />
          <Route path="/selectType" element={<SelectType />} />
          <Route path="/palletMap" element={<PalletMap />} />
        </Routes>
      </IoTProvider>
    </BrowserRouter>
  );
}

export default App;
