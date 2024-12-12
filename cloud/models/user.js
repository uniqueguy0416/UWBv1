import mongoose from "mongoose";
const Schema = mongoose.Schema;

const UserSchema = new Schema({
  userID: { type: String, required: [true, "ID field is required."] },
  pwd: {
    type: String,
    // required: [true, "Body field is required."],
  },
  status: {
    type: String,
    enum: ["active", "not-active"],
    required: true,
  },
  last_position: {
    type: [Number],
    required: true,
  },
  palletID: {
    type: String,
  },
});
//creating a table within database with the defined
const UserModel = mongoose.model("user", UserSchema);

//exporting table for querying and mutating
export default UserModel;
