import { combineReducers } from "redux";
// Authentication
import Login from "./auth/login/reducer";
import MastertReducer from "./master/reducer";
const rootReducer = combineReducers({
Login,
MastertReducer
});

export default rootReducer;
