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
  CONTINENT_LIST,
  ADD_CONTINENT,
  EDIT_CONTINENT,
  DELETE_CONTINENT,
  EXPORT_CONTINENT,
  IMPORT_CONTINENT,
} from "./actionTypes";

import {
  addContinentDataAPI,
  addGenderDataAPI,
  addMaritalStatusDataAPI,
  deleteContinentDataAPI,
  deleteGenderDataAPI,
  deleteMaritalStatusDataAPI,
  editContinentDataAPI,
  editGenderDataAPI,
  editMaritalStatusDataAPI,
  exportContinentDataAPI,
  exportGenderDataAPI,
  exportMaritalStatusDataAPI,
  getContinentListDataAPI,
  getGenderListDataAPI,
  getMaritalStatusListDataAPI,
  importContinentDataAPI,
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
//Continent
function* continentListSaga(action) {
  try {
    const response = yield call(getContinentListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}
 
function* continentAddSaga(action) {
  try {
    const response = yield call(addContinentDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}
 
function* continentEditSaga(action) {
  try {
    const response = yield call(editContinentDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}
 
function* continentDeleteSaga(action) {
  try {
    const response = yield call(deleteContinentDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}
 
function* continentExportDataSaga(action) {
  try {
    const response = yield call(exportContinentDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}
 
function* continentImportDataSaga(action) {
  try {
    const response = yield call(importContinentDataAPI, action?.data);
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

  //Continents
  yield takeEvery(CONTINENT_LIST, continentListSaga);
  yield takeEvery(ADD_CONTINENT, continentAddSaga);
  yield takeEvery(EDIT_CONTINENT, continentEditSaga);
  yield takeEvery(DELETE_CONTINENT, continentDeleteSaga);
  yield takeEvery(EXPORT_CONTINENT, continentExportDataSaga);
  yield takeEvery(IMPORT_CONTINENT, continentImportDataSaga);
}

export default generalMasterSaga;