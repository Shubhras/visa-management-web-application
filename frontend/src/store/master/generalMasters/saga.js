import { call, takeEvery } from "redux-saga/effects";
import {
  GENDER_LIST,
  ADD_GENDER,
  EDIT_GENDER,
  DELETE_GENDER,
  IMPORT_GENDER,
  EXPORT_GENDER,
  MARITAL_STATUS_LIST,
  ADD_MARITAL_STATUS,
  EDIT_MARITAL_STATUS,
  DELETE_MARITAL_STATUS,
  EXPORT_MARITAL_STATUS,
  IMPORT_MARITAL_STATUS,
} from "./actionTypes";

import {
  addGenderDataAPI,
  addMaritalStatusDataAPI,
  deleteGenderDataAPI,
  deleteMaritalStatusDataAPI,
  editGenderDataAPI,
  editMaritalStatusDataAPI,
  exportGenderDataAPI,
  exportMaritalStatusDataAPI,
  getGenderListDataAPI,
  getMaritalStatusListDataAPI,
  importGenderDataAPI,
  importMaritalStatusDataAPI,
} from "../../../service/api_helper";

// Gender
function* genderListSaga(action) {
  try {
    const response = yield call(getGenderListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* genderAddSaga(action) {
  try {
    const response = yield call(addGenderDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* genderEditSaga(action) {
  try {
    const response = yield call(editGenderDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* genderDeleteSaga(action) {
  try {
    const response = yield call(deleteGenderDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* genderExportDataSaga(action) {
  try {
    const response = yield call(exportGenderDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* genderImportDataSaga(action) {
  try {
    const response = yield call(importGenderDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

// Marital Status
function* maritalStatusListSaga(action) {
  try {
    const response = yield call(getMaritalStatusListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* maritalStatusAddSaga(action) {
  try {
    const response = yield call(addMaritalStatusDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* maritalStatusEditSaga(action) {
  try {
    const response = yield call(editMaritalStatusDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* maritalStatusDeleteSaga(action) {
  try {
    const response = yield call(deleteMaritalStatusDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* maritalStatusExportDataSaga(action) {
  try {
    const response = yield call(exportMaritalStatusDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* maritalStatusImportDataSaga(action) {
  try {
    const response = yield call(importMaritalStatusDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* generalMasterSaga() {
  // Gender
  yield takeEvery(GENDER_LIST, genderListSaga);
  yield takeEvery(ADD_GENDER, genderAddSaga);
  yield takeEvery(EDIT_GENDER, genderEditSaga);
  yield takeEvery(DELETE_GENDER, genderDeleteSaga);
  yield takeEvery(EXPORT_GENDER, genderExportDataSaga);
  yield takeEvery(IMPORT_GENDER, genderImportDataSaga);

   // Marital Status
  yield takeEvery(MARITAL_STATUS_LIST, maritalStatusListSaga);
  yield takeEvery(ADD_MARITAL_STATUS, maritalStatusAddSaga);
  yield takeEvery(EDIT_MARITAL_STATUS, maritalStatusEditSaga);
  yield takeEvery(DELETE_MARITAL_STATUS, maritalStatusDeleteSaga);
  yield takeEvery(EXPORT_MARITAL_STATUS, maritalStatusExportDataSaga);
  yield takeEvery(IMPORT_MARITAL_STATUS, maritalStatusImportDataSaga);
}

export default generalMasterSaga;