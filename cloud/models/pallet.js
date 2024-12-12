import mongoose from "mongoose";
const Schema = mongoose.Schema;

const PalletSchema = new Schema({
  ID: { type: String, required: [true, "ID field is required."] },
  type: {
    type: String,
    // required: [true, "Body field is required."],
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
    type: [number, number],
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
