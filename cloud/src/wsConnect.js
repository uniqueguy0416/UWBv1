import PalletModel from "../models/pallet.js";
import UserModel from "../models/User.js";

const sendData = (data, ws) => {
  console.log("server sendData", data);
  ws.send(JSON.stringify(data));
};

const checkUser = async (userID, pwd) => {
  const user = await UserModel.findOne({ userID });
  console.log(user, userID.pwd);
  var data = {};
  if (!user) data = { status: false, msg: "User not found" };
  else if (user.pwd !== pwd) data = { status: false, msg: "wrong password" };
  else data = { status: true, msg: user.userID };
  if (data.status) {
    user.status = "active";
    await user.save();
  }
  return data;
};

export default {
  onMessage: (ws) => async (byteString) => {
    const { data } = byteString;
    const { type, payload } = JSON.parse(data);
    console.log("onmessage", data);

    switch (type) {
      case "checkUserPallet": {
        console.log("checkUserPallet");
        const { userID, task } = payload;
        const user = await UserModel.findOne({ userID: userID });
        console.log(payload, user);
        console.log(user.palletID, "user");
        if (user.palletID === "" || user.palletID === undefined) {
          if (task === "putDown") {
            sendData({ type: "checkUserPallet", payload: { status: false, msg: "You don't have a pallet" } }, ws);
          } else {
            sendData({ type: "checkUserPallet", payload: { status: true, msg: "You don't have a pallet" } }, ws);
          }
        } else {
          if (task == "find") sendData({ type: "checkUserPallet", payload: { status: false, msg: "You already have pallet" } }, ws);
          else sendData({ type: "checkUserPallet", payload: { status: true, msg: "You already have pallet" } }, ws);
        }

        break;
      }
      case "findSelections": {
        console.log("hi");
        const { content } = payload;
        var pallets = {};
        if (content) {
          pallets = await PalletModel.find({ status: "static" }).distinct("content");
          pallets = ["物品", ...pallets];
          pallets.filter((item) => item !== "");
        } else {
          //Todo: add currently don't have this data
          pallets = await PalletModel.find({ content: "", status: "static" }).distinct("type");
          pallets = ["棧板種類", ...pallets];
        }

        console.log(pallets);
        sendData({ type: "findSelections", payload: { selected: pallets } }, ws);
        break;
      }
      case "findAvailablePallet": {
        // find all available pallets based on request info
        // todo : not tested
        // for findPallet
        console.log("findAvailablePallet");
        const { thing, target } = payload;

        var pallets = [];

        if (target === "type") {
          pallets = await PalletModel.find({ status: "static", type: thing, content: "" });
          console.log(pallets);
        } else {
          pallets = await PalletModel.find({ status: "static", content: thing });
          console.log(pallets);
        }

        if (!pallets) {
          sendData({ type: "findAvailablePallet", payload: { msg: "Pallet not found" } }, ws);
        } else {
          pallets = pallets.map((pallet) => {
            return {
              type: "Feature",
              properties: {
                title: "Mapbox",
                description: pallet._id,
                use: "marker",
              },
              geometry: {
                type: "Point",
                coordinates: pallet.position,
              },
            };
          });
          console.log(pallets);
          sendData({ type: "findAvailablePallet", payload: pallets }, ws);
        }
        break;
      }
      case "takeAway": {
        console.log("takeAway", payload);
        const { palletID, userID } = payload;
        var pallet = await PalletModel.findOne({ _id: palletID.toString() });
        pallet.status = "take-away";
        pallet.final_user = userID;
        console.log(pallet);
        await pallet.save();
        var user = await UserModel.findOne({ userID });
        user.palletID = palletID;
        await user.save();
        sendData({ type: "successful", payload: { msg: "Pallet taken successfully" } }, ws);
        break;
      }
      case "findAllPallet": {
        // find all pallets
        // Todo: not tested, need to change to geojson
        const pallets = await PalletModel.find();
        if (!pallets) {
          sendData({ type: "findAllPallet", payload: { msg: "Pallet not found" } }, ws);
        }
        sendData({ type: "findPallet", payload: pallets }, ws);
        break;
      }
      case "findOnePallet": {
        // find one pallet by palletID
        // Todo: not tested
        const { userID } = payload;
        console.log("findOnePallet");
        const user = await UserModel.findOne({ userID });

        const pallet = await PalletModel.findById(user.palletID);
        console.log("findOnePallet", pallet);
        if (!pallet) {
          sendData({ type: "findOnePallet", payload: { msg: "Pallet not found" } }, ws);
        } else {
          sendData({ type: "findOnePallet", payload: pallet }, ws);
        }
        break;
      }
      case "addPallet": {
        const { status, type, content, position, final_user } = payload;

        try {
          const newPallet = new PalletModel({ status, type, content, position, final_user });
          await newPallet.save();
          //sendStatus({ type: "success", msg: "User added successfully" }, ws);
          console.log("save new pallet");
          sendData({ type: "successful", payload: { msg: "Pallet added successfully" } }, ws);
        } catch (error) {
          //console.log({ type: "error", msg: "Failed to add user" }, ws);
          console.log(error);
        }
        break;
      }
      case "updatePallet": {
        const { id, status, type, content, position, final_user } = payload;
        const updatedPallet = await PalletModel.findByIdAndUpdate(
          id,
          { status, type, content, position, final_user },
          { new: true } // Return the updated document
        );

        break;
      }
      case "updateUser": {
        const { userID, palletID } = payload;
        const updatedUser = await UserModel.findOneAndUpdate({ userID }, { palletID }, { new: true });
        sendData({ type: "successful", payload: { msg: "Successfully put down" } });
        break;
      }
      case "checkUser": {
        const { userID, pwd } = payload;
        console.log(userID, pwd);
        const result = await checkUser(userID, pwd);

        sendData({ type: "checkUser", payload: result }, ws);
        break;
      }
      case "logout": {
        break;
      }
      case "addUser": {
        const { userID, pwd, status, last_position, palletID } = payload;

        try {
          const newUser = new UserModel({ userID, pwd, status, last_position, palletID });
          await newUser.save();
          sendData({ type: "successful", payload: { msg: "User added successfully" } }, ws);
          console.log("hi");
        } catch (error) {
          //console.log({ type: "error", msg: "Failed to add user" }, ws);
          console.log(error);
        }
        break;
      }
      default:
        break;
    }
  },
};
