import React from "react";
import Box from "@mui/material/Box";
import { useNavigate } from "react-router";
import { useRef, useEffect, useState } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import "./find/palletMap.css";
import geojsonData from "./find/pos.json";
import { useIoT } from "../hooks/useIoT";
import Button from "@mui/material/Button";

export default function AllPallet(props) {
  const mapRef = useRef();
  const mapContainerRef = useRef();
  const navigate = useNavigate();
  const { singlePalletInfo, setSinglePalletInfo, takeAwayPallet, userPos, availablePallet, tempPalletDest, setTempPalletDest, route, closeEnough, sendData, addUser } = useIoT();
  const [selected, setSelected] = useState(false);
  // select a pallet
  const click = () => {
    console.log("click");
    console.log(singlePalletInfo);
    navigate("/palletInfo");
  };
  const takeAway = () => {};

  const clickPallet = () => {};
  // cross[-0.000015]
  // setup map
  useEffect(() => {
    mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_API_TOKEN;

    mapRef.current = new mapboxgl.Map({
      container: mapContainerRef.current,
      center: [121.54446, 25.01793],
      zoom: 19.5,
      // scrollZoom: false,
      bearing: -42, // rotate angle
      // maxBounds: [
      //   [121.544025, 25.017521],
      //   [121.544682, 25.01815],
      // ],
    });

    mapRef.current.on("style.load", () => {
      const data = geojsonData || {
        type: "FeatureCollection",
        features: [],
      };
      // add a geojson source with a polygon to be used in the clip layer.
      mapRef.current.addSource("combinedSource", {
        type: "geojson",
        data: data,
      });

      // add a layer to use the source content
      mapRef.current.addLayer({
        id: "maine",
        type: "fill",
        source: "combinedSource",
        layout: {},
        filter: ["in", ["get", "title"], "MD building||Classroom"],
        paint: {
          "fill-color": "#ffffff",
          "fill-opacity": 1,
        },
      });

      // add an outline to the Classroom and building
      mapRef.current.addLayer({
        id: "outline",
        type: "line",
        source: "combinedSource",
        layout: {},
        filter: ["in", ["get", "title"], "MD building||Classroom||Blocked"],
        paint: {
          "line-color": "#000",
          "line-width": 3,
        },
      });
      // table color
      mapRef.current.addLayer({
        id: "blocked",
        type: "fill",
        source: "combinedSource",
        layout: {},
        filter: ["in", ["get", "title"], "Blocked"],
        paint: {
          "fill-color": "#000000",
          "fill-opacity": 1,
        },
      });

      // pallet start
      mapRef.current.addSource("pallets", {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: availablePallet,
        },
      });

      mapRef.current.addLayer({
        id: "points-layer",
        type: "circle", // Or use "symbol" for icons
        source: "pallets",
        filter: ["in", ["get", "status"], "static"],
        paint: {
          "circle-radius": 8,
          "circle-color": "#ff0000",
        },
      });
      mapRef.current.addLayer({
        id: "points-layer2",
        type: "circle", // Or use "symbol" for icons
        source: "pallets",
        filter: ["in", ["get", "status"], "broken"],
        paint: {
          "circle-radius": 8,
          "circle-color": "#ffd700",
        },
      });
      // pallet end
      // User: add a point source (marker)
      mapRef.current.addSource("UserPos", {
        type: "geojson",
        data: {
          type: "Feature",
          properties: {},
          geometry: {
            type: "Point",
            coordinates: userPos,
          },
        },
      });

      mapRef.current.addLayer({
        id: "UserPoint",
        type: "circle", // Or use "symbol" for icons
        source: "UserPos",
        paint: {
          "circle-radius": 8,
          "circle-color": "#007FFF",
        },
      });
      //User end
    });

    //click event on points-layer
    mapRef.current.on("click", "points-layer", (e) => {
      const coordinates = e.features[0].geometry.coordinates.slice();
      console.log("select", e.features[0].properties);
      setSelected(true);
      setSinglePalletInfo(e.features[0].properties);
      // set popup info
      var st;
      if (e.features[0].properties.status === "broken") st = "狀態: 損壞";
      else st = "狀態: 正常";
      var con;
      if (e.features[0].properties.content === "") con = "物品: 無";
      else con = "物品: " + e.features[0].properties.content;
      const type = "種類: " + e.features[0].properties.type;
      new mapboxgl.Popup({ closeButton: false })
        .setLngLat(coordinates)
        .setHTML("<h3>" + st + "</h3><h3>" + con + "</h3><h3>" + type + "</h3>")
        .addTo(mapRef.current);
    });
    mapRef.current.on("click", "points-layer2", (e) => {
      const coordinates = e.features[0].geometry.coordinates.slice();
      console.log(e.features[0].properties);
      setSelected(true);
      setSinglePalletInfo(e.features[0].properties);
      // set popup info
      var st;
      if (e.features[0].properties.status === "broken") st = "狀態: 損壞";
      else st = "狀態: 正常";
      var con;
      if (e.features[0].properties.content === "") con = "物品: 無";
      else con = "物品: " + e.features[0].properties.content;
      const type = "種類: " + e.features[0].properties.type;
      new mapboxgl.Popup({ closeButton: false })
        .setLngLat(coordinates)
        .setHTML("<h3>" + st + "</h3><h3>" + con + "</h3><h3>" + type + "</h3>")
        .addTo(mapRef.current);
    });

    return () => {
      console.log(mapRef.current);
      mapRef.current.remove();
    };
  }, []);

  // update route
  useEffect(() => {
    console.log("route", route);
    if (mapRef.current && mapRef.current.getSource("route")) {
      mapRef.current.getSource("route").setData({
        type: "Feature",
        properties: {},
        geometry: {
          type: "LineString",
          coordinates: route,
        },
      });
    }
  }, [route]);

  return (
    <div id="map">
      <>
        <div id="map-container" ref={mapContainerRef} />
      </>
      <>
        <div id="button">
          {!selected ? (
            <Box sx={{ width: "100%", fontSize: "30px", display: "flex", alignContent: "center", justifyContent: "center" }}>請選擇一塊棧板</Box>
          ) : (
            <Button variant="contained" color="success" sx={{ width: "40%", fontSize: "40px" }} onClick={() => click()}>
              確認選取
            </Button>
          )}
        </div>
      </>
    </div>
  );
}
