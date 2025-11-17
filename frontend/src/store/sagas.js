import { all, fork } from "redux-saga/effects";

//public
import AuthSaga from "./auth/login/saga";
import masterSaga from "./master/saga";
import salesMasterSaga from "./master/salesMasters/saga";
import companyMasterSaga from "./master/companyMasters/saga";
import generalMasterSaga from "./master/generalMasters/saga";
import educationmasterSaga from "./master/educationMaster/saga";
import testMasterSaga from "./master/testMaster/saga";
import occupationMasterSaga from "./master/occupationMaster/saga";
 
export default function* rootSaga() {
  yield all([

    fork(AuthSaga),
    fork(masterSaga),
    fork(salesMasterSaga),
    fork(companyMasterSaga),
    fork(generalMasterSaga),
    fork(educationmasterSaga),
    fork(testMasterSaga),
     fork(occupationMasterSaga),
  ]);
}
