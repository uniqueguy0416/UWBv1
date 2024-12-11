import { useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./containers/home";
import PalletMap from "./containers/find/palletMap";
import { IoTProvider } from "./hooks/useIoT";
function App() {
  return (
    <BrowserRouter>
      <IoTProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/palletmap" element={<PalletMap />} />
        </Routes>
      </IoTProvider>
    </BrowserRouter>
  );
}

export default App;
