import { combineReducers } from "redux";
// Authentication
import Login from "./auth/login/reducer";
import MastertReducer from "./master/reducer";
import SalesMastertReducer from "./master/salesMasters/reducer";
const rootReducer = combineReducers({
Login,
MastertReducer,
SalesMastertReducer
});

export default rootReducer;
