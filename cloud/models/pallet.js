import mongoose from "mongoose";
const Schema = mongoose.Schema;

const PalletSchema = new Schema({
  type: {
    type: String,
    // required: [true, "Body field is required."],
    // 川字形, 田字型, 九宮格式, 雙面
  },
  content: {
    type: String,
    // required: [true, "Body field is required."],
  },
  status: {
    type: String,
    enum: ["take-away", "broken", "static"],
    required: true,
  },
  position: {
    type: [],
    required: true,
  },
  final_user: {
    type: String,
    // required: [true, "Body field is required."],
  },
});
//creating a table within database with the defined
const PalletModel = mongoose.model("Pallet", PalletSchema);
//exporting table for querying and mutating
export default PalletModel;
