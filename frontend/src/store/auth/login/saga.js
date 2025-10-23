import { call, takeEvery } from "redux-saga/effects";
import {  LOGIN_USER} from "./actionTypes";
// import { apiError } from "./actions";
import {  postLogin,  } from "../../../service/api_helper";

function* loginUser({ payload: { user, history }, callback },) {
  try {
    const response = yield call(postLogin, user);
    if (response?.statusCode === 200) {
      //console.log('aaaaaaaaaaaaaaaaaaaaaaaaaaaa',response?.data)
      // callback(response?.data)
      callback(response)
    }
  } catch (error) {
    //console.log('bbbbbbbbbbbbbbbbbbbbbbbbbbb',error?.response?.data)
    // callback(null, error?.response?.data)
    //yield put(apiError(error?.response?.data?.message));
     callback(null, error)
  }
}

// function* logoutUser(action) {
//   try {
//     const response = yield call(logoutUserAPI, action?.data);
//     if (response?.status === 200) {
//       action.callback(response)
//     }
//   } catch (error) {
//     action.callback(null, error)

//   }
// }
// function* twoStepVerification(action) {
//   try {
//     const response = yield call(twoStepVerificationAPI, action?.payload?.data);
//     localStorage.setItem('authUser', JSON.stringify(response.data));
//     if (response?.data?.userData?.role?.machineName === "control_admin") {
//       action.callback(response);
//     } else {
//       action.callback(response);
//     }
//   } catch (error) {
//     action.callback(null, error);
//   }
// }
// function* forgotpasswordWithEmail(action) {
//   try {
//     const response = yield call(forgetPasswordAPI, action?.payload?.user);
//     if (response?.status === 200) {
//       action.callback(response)
//     }
//   } catch (error) {
//     action.callback(null, error)
//   }
// }
// function* resetPasswordWithToken(action) {
//   try {
//     const response = yield call(resetPasswordAPI, action?.payload?.user);
//     if (response?.status === 200) {
//       action.callback(response)
//     }
//   } catch (error) {
//     action.callback(null, error)
//   }
// }
function* authSaga() {
  yield takeEvery(LOGIN_USER, loginUser);
  // yield takeEvery(TWO_STEP_VERIFICATION, twoStepVerification);
  // yield takeEvery(LOGOUT_USER, logoutUser);
  // yield takeEvery(FORGET_PASSWORD, forgotpasswordWithEmail)
  // yield takeEvery(RESET_PASSWORD, resetPasswordWithToken)
}

export default authSaga;
