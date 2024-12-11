import React from "react";
import Box from "@mui/material/Box";
import { useNavigate } from "react-router";
import { useRef, useEffect } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import "./palletMap.css";
import geojsonData from "./pos.json";
import { useIoT } from "../../hooks/useIoT";
export default function PalletMap(props) {
  const mapRef = useRef();
  const mapContainerRef = useRef();
  const { tempPalletDest, setTempPalletDest, route } = useIoT();
  // cross[-0.000015]
  useEffect(() => {
    mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_API_TOKEN;

    mapRef.current = new mapboxgl.Map({
      container: mapContainerRef.current,
      center: [121.54436, 25.01783],
      zoom: 20,
      scrollZoom: false,
      // bearing: -130, // rotate angle
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
        source: "combinedSource",
        filter: ["==", "$type", "Point"],
        paint: {
          "circle-radius": 8,
          "circle-color": "#ff0000",
        },
      });

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

    return () => {
      console.log(mapRef.current);
      mapRef.current.remove();
    };
  }, []);

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
    <>
      <div id="map-container" ref={mapContainerRef} />
    </>
  );
}
