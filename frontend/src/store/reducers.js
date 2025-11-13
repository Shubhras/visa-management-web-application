import { combineReducers } from "redux";
// Authentication
import Login from "./auth/login/reducer";
import MastertReducer from "./master/reducer";
import SalesMastertReducer from "./master/salesMasters/reducer";
import CompanyMastertReducer from "./master/companyMasters/reducer";
import GeneralMastertReducer from "./master/generalMasters/reducer";
import EducationMasterReducer from "./master/educationMaster/reducer";
import TestMasterReducer from "./master/testMaster/reducer";
import occupationMasterReducer from "./master/occupationMaster/reducer";
import instituteMasterReducer from "./master/instituteMaster/reducer";


const rootReducer = combineReducers({
    Login,
    MastertReducer,
    SalesMastertReducer,
    CompanyMastertReducer,
    GeneralMastertReducer,
    EducationMasterReducer,
    TestMasterReducer,
    occupationMasterReducer,
    instituteMasterReducer,
});

export default rootReducer;
