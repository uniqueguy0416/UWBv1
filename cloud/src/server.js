import express from "express";
//import cors from "cors";
import mongo from "./mongo.js";
import mongoose from "mongoose";
import http from "http";
import WebSocket, { WebSocketServer } from "ws";
import wsConnect from "./wsConnect.js";
import dotenv from "dotenv-defaults";
//import routes from "./routes"

mongo.connect();

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

const db = mongoose.connection;
db.once("open", () => {
  console.log("MongoDB connected!");
  //console.log(typeof wss);
  wss.on("connection", (ws) => {
    //wsConnect.initData(ws);
    ws.box = ""; //record active ChatBox name
    ws.onmessage = wsConnect.onMessage(ws);
    //ws = Client-Side WebSocket
    //Define WebSocket connection logic
  });
});
const PORT = process.env.PORT || 4000;
server.listen(PORT, () => {
  console.log("Listening on http://localhost:" + PORT);
});
