import { call, takeEvery } from "redux-saga/effects";
import {
  ACTIVITY_TYPE_LIST,
  DELETE_ACTIVITY_TYPE,
  IMPORT_ACTIVITY_TYPE,
  EXPORT_ACTIVITY_TYPE,
  ADD_ACTIVITY_TYPE,
  EDIT_ACTIVITY_TYPE,
} from "./actionTypes";

import {
  importActivityTypeDataAPI,
  exportActivityTypeDataAPI,
  deleteActivityTypeDataAPI,
  editActivityTypeDataAPI,
  addActivityTypeDataAPI,
  getActivityTypeListDataAPI,
} from "../../../service/api_helper";

// Activity type
function* activityTypeListSaga(action) {
  try {
    const response = yield call(getActivityTypeListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* activityTypeAddSaga(action) {
  try {
    const response = yield call(addActivityTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* activityTypeEditSaga(action) {
  try {
    const response = yield call(editActivityTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* activityTypeDeleteSaga(action) {
  try {
    const response = yield call(deleteActivityTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* activityTypeExportDataSaga(action) {
  try {
    const response = yield call(exportActivityTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* activityTypeImportDataSaga(action) {
  try {
    const response = yield call(importActivityTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* salesMasterSaga() {
  // Activity type
  yield takeEvery(ACTIVITY_TYPE_LIST, activityTypeListSaga);
  yield takeEvery(ADD_ACTIVITY_TYPE, activityTypeAddSaga);
  yield takeEvery(EDIT_ACTIVITY_TYPE, activityTypeEditSaga);
  yield takeEvery(DELETE_ACTIVITY_TYPE, activityTypeDeleteSaga);
  yield takeEvery(EXPORT_ACTIVITY_TYPE, activityTypeExportDataSaga);
  yield takeEvery(IMPORT_ACTIVITY_TYPE, activityTypeImportDataSaga);
}

export default salesMasterSaga;
