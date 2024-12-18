import React from "react";
import Box from "@mui/material/Box";
import { useNavigate } from "react-router";
import { useRef, useEffect } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import "./find/palletMap.css";
import geojsonData from "./find/pos.json";
import { useIoT } from "../hooks/useIoT";
import Button from "@mui/material/Button";

export default function ShowPos(props) {
  const mapRef = useRef();
  const mapContainerRef = useRef();
  const navigate = useNavigate();
  const { userPos } = useIoT();

  // setup map
  useEffect(() => {
    console.log("userpos", userPos);
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
      mapRef.current.addSource("currentPos", {
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
      // add a point source (marker)
      mapRef.current.addLayer({
        id: "points-layer",
        type: "circle", // Or use "symbol" for icons
        source: "currentPos",
        filter: ["==", "$type", "Point"],
        paint: {
          "circle-radius": 8,
          "circle-color": "#ff0000",
        },
      });
    });

    return () => {
      console.log(mapRef.current);
      mapRef.current.remove();
    };
  }, []);

  return (
    <div id="map">
      <>
        <div id="map-container" ref={mapContainerRef} />
      </>
      <>
        <div id="button">
          {/* valid position */}
          <Button variant="contained" color="success" sx={{ width: "40%", fontSize: "40px" }} onClick={() => navigate("/palletInfo")}>
            確認位置
          </Button>
        </div>
      </>
    </div>
  );
}
