import React from "react";
import Box from "@mui/material/Box";
import { useNavigate } from "react-router";
import { useRef, useEffect, useState } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import "./palletMap.css";
import geojsonData from "./pos.json";
import { useIoT } from "../../hooks/useIoT";
import Button from "@mui/material/Button";

export default function PalletMap(props) {
  const mapRef = useRef();
  const mapContainerRef = useRef();
  const navigate = useNavigate();
  const { getUserPos, takeAwayPallet, userPos, availablePallet, tempPalletDest, setTempPalletDest, route, selected, closeEnough, setSelected, sendData, addUser } = useIoT();
  const [palletID, setPalletID] = useState("");
  var clock;
  const click = () => {
    console.log("click");	
    setSelected(true);
    clock = setInterval(getUserPos, 1000);
  };
  const takeAway = () => {
    clearInterval(clock);
    console.log("takeAway");
    takeAwayPallet(palletID);
    navigate("/home");
  };
  useEffect(()=>{
  console.log(userPos);
if (selected) {
      mapRef.current.getSource('UserPos').setData({
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'Point',
          coordinates: userPos,
        },
      });
    };
  },[userPos]);
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
      mapRef.current.addSource("pallets", {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: availablePallet,
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

      // User: add a point source (marker)
      mapRef.current.addLayer({
        id: "points-layer",
        type: "circle", // Or use "symbol" for icons
        source: "pallets",
        filter: ["==", "$type", "Point"],
        paint: {
          "circle-radius": 8,
          "circle-color": "#ff0000",
        },
      });

      // User: add a point source (marker)
      mapRef.current.addSource("UserPos", {
        type: "geojson",
        data: {
          type: "Feature",
          properties: {},
          geometry: {
            type: "Point",
            coordinates: userPos||[],
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

      // line layer (route)
      mapRef.current.addSource("route", {
        type: "geojson",
        data: {
          type: "Feature",
          properties: {},
          geometry: {
            type: "LineString",
            coordinates: route || [],
          },
        },
      });
      // line layer
      mapRef.current.addLayer({
        id: "route",
        type: "line",
        source: "route",
        layout: {
          "line-join": "round",
          "line-cap": "round",
        },
        paint: {
          "line-color": "#888",
          "line-width": 8,
        },
      });
    });

    //click event on points-layer
    mapRef.current.on("click", "points-layer", (e) => {
      const coordinates = e.features[0].geometry.coordinates.slice();
      const description = e.features[0].properties.description;
      setPalletID(description);
      // set destination
      setTempPalletDest([coordinates[0], coordinates[1]]);
      while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
        coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
      }
      // new mapboxgl.Popup().setLngLat(coordinates).setHTML(description).addTo(mapRef.current);
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

  // Todo: turn off click not finished!!!!!!!!!!
  useEffect(() => {
    console.log("selected", selected);
    mapRef.current.off("click", "points-layer", (e) => {
      console.log(e);
      const coordinates = e.features[0].geometry.coordinates.slice();
      const description = e.features[0].properties.description;

      // set destination
      setTempPalletDest([coordinates[0], coordinates[1]]);
      while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
        coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
      }
      // new mapboxgl.Popup().setLngLat(coordinates).setHTML(description).addTo(mapRef.current);
    });
  }, [selected]);

  return (
    <div id="map">
      <>
        <div id="map-container" ref={mapContainerRef} />
      </>
      <>
        <div id="button">
          {route.length === 0 ? (
            // not selected a pallet
            <Box sx={{ width: "100%", fontSize: "30px", display: "flex", alignContent: "center", justifyContent: "center" }}>請選擇一塊棧板</Box>
          ) : !selected ? (
            // start navigation == selected
            <Button variant="contained" color="success" sx={{ width: "40%", fontSize: "40px" }} onClick={() => click()}>
              開始導航
            </Button>
          ) : (
            // if close enough => able to take
            <Button disabled={closeEnough} variant="contained" color="success" sx={{ width: "40%", fontSize: "40px" }} onClick={() => takeAway()}>
              確認領取
              {/* {!closeEnough} */}
            </Button>
          )}
        </div>
      </>
    </div>
  );
}
