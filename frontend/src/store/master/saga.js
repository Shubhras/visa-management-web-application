import { call, put, takeEvery, takeLatest } from "redux-saga/effects";
import {  DEPARTMENT_LIST} from "./actionTypes";

import {  getDepartmentListData,  } from "../../service/api_helper";

function* departmentListSaga({ payload: { user, history }, callback },) {
  try {
    const response = yield call(getDepartmentListData, user);
    if (response?.status === 200) {
      callback(response)
    }
  } catch (error) {
    callback(null, error)
    //yield put(apiError(error?.response?.data?.message));
  }
}

function* masterSaga() {
  yield takeEvery(DEPARTMENT_LIST, departmentListSaga);
}

export default masterSaga;
