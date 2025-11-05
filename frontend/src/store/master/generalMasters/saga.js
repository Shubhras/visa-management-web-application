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
  CIVIL_ID_NAME_LIST,
  ADD_CIVIL_ID_NAME,
  EDIT_CIVIL_ID_NAME,
  DELETE_CIVIL_ID_NAME,
  EXPORT_CIVIL_ID_NAME,
  IMPORT_CIVIL_ID_NAME,
  RELATION_LIST,
  ADD_RELATION,
  EDIT_RELATION,
  DELETE_RELATION,
  EXPORT_RELATION,
  IMPORT_RELATION,
  TIME_ZONE_LIST,
  ADD_TIME_ZONE,
  EDIT_TIME_ZONE,
  DELETE_TIME_ZONE,
  EXPORT_TIME_ZONE,
  IMPORT_TIME_ZONE,
  COUNTRY_LIST,
  ADD_COUNTRY,
  EDIT_COUNTRY,
  DELETE_COUNTRY,
  EXPORT_COUNTRY,
  IMPORT_COUNTRY,
} from "./actionTypes";

import {
  addCivilIdNameDataAPI,
  addContinentDataAPI,
  addCountryDataAPI,
  addGenderDataAPI,
  addMaritalStatusDataAPI,
  addRelationDataAPI,
  addTimeZoneDataAPI,
  deleteCivilIdNameDataAPI,
  deleteContinentDataAPI,
  deleteCountryDataAPI,
  deleteGenderDataAPI,
  deleteMaritalStatusDataAPI,
  deleteRelationDataAPI,
  deleteTimeZoneDataAPI,
  editCivilIdNameDataAPI,
  editContinentDataAPI,
  editCountryDataAPI,
  editGenderDataAPI,
  editMaritalStatusDataAPI,
  editRelationDataAPI,
  editTimeZoneDataAPI,
  exportCivilIdNameDataAPI,
  exportContinentDataAPI,
  exportCountryDataAPI,
  exportGenderDataAPI,
  exportMaritalStatusDataAPI,
  exportRelationDataAPI,
  exportTimeZoneDataAPI,
  getCivilIdNameListDataAPI,
  getContinentListDataAPI,
  getGenderListDataAPI,
  getMaritalStatusListDataAPI,
  getRelationListDataAPI,
  getTimeZoneListDataAPI,
  importCivilIdNameDataAPI,
  importContinentDataAPI,
  importCountryDataAPI,
  importGenderDataAPI,
  importMaritalStatusDataAPI,
  importRelationDataAPI,
  importTimeZoneDataAPI,
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

// Civil ID Name
function* civilIdNameListSaga(action) {
  try {
    const response = yield call(getCivilIdNameListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* civilIdNameAddSaga(action) {
  try {
    const response = yield call(addCivilIdNameDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* civilIdNameEditSaga(action) {
  try {
    const response = yield call(editCivilIdNameDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* civilIdNameDeleteSaga(action) {
  try {
    const response = yield call(deleteCivilIdNameDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* civilIdNameExportDataSaga(action) {
  try {
    const response = yield call(exportCivilIdNameDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* civilIdNameImportDataSaga(action) {
  try {
    const response = yield call(importCivilIdNameDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

// Relation
function* relationListSaga(action) {
  try {
    const response = yield call(getRelationListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* relationAddSaga(action) {
  try {
    const response = yield call(addRelationDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* relationEditSaga(action) {
  try {
    const response = yield call(editRelationDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* relationDeleteSaga(action) {
  try {
    const response = yield call(deleteRelationDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* relationExportDataSaga(action) {
  try {
    const response = yield call(exportRelationDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* relationImportDataSaga(action) {
  try {
    const response = yield call(importRelationDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}


// Time Zone
function* timeZoneListSaga(action) {
  try {
    const response = yield call(getTimeZoneListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* timeZoneAddSaga(action) {
  try {
    const response = yield call(addTimeZoneDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* timeZoneEditSaga(action) {
  try {
    const response = yield call(editTimeZoneDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* timeZoneDeleteSaga(action) {
  try {
    const response = yield call(deleteTimeZoneDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* timeZoneExportDataSaga(action) {
  try {
    const response = yield call(exportTimeZoneDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* timeZoneImportDataSaga(action) {
  try {
    const response = yield call(importTimeZoneDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}


function* countryListSaga(action) {
  try {
    const response = yield call(getCountryListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}
//country
function* countryAddSaga(action) {
  try {
    const response = yield call(addCountryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* countryEditSaga(action) {
  try {
    const response = yield call(editCountryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* countryDeleteSaga(action) {
  try {
    const response = yield call(deleteCountryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* countryExportDataSaga(action) {
  try {
    const response = yield call(exportCountryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* countryImportDataSaga(action) {
  try {
    const response = yield call(importCountryDataAPI, action?.data);
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

  //Civil ID Name
  yield takeEvery(CIVIL_ID_NAME_LIST, civilIdNameListSaga);
  yield takeEvery(ADD_CIVIL_ID_NAME, civilIdNameAddSaga);
  yield takeEvery(EDIT_CIVIL_ID_NAME, civilIdNameEditSaga);
  yield takeEvery(DELETE_CIVIL_ID_NAME, civilIdNameDeleteSaga);
  yield takeEvery(EXPORT_CIVIL_ID_NAME, civilIdNameExportDataSaga);
  yield takeEvery(IMPORT_CIVIL_ID_NAME, civilIdNameImportDataSaga);

  // Relation
  yield takeEvery(RELATION_LIST, relationListSaga);
  yield takeEvery(ADD_RELATION, relationAddSaga);
  yield takeEvery(EDIT_RELATION, relationEditSaga);
  yield takeEvery(DELETE_RELATION, relationDeleteSaga);
  yield takeEvery(EXPORT_RELATION, relationExportDataSaga);
  yield takeEvery(IMPORT_RELATION, relationImportDataSaga);

  // Time Zone
yield takeEvery(TIME_ZONE_LIST, timeZoneListSaga);
yield takeEvery(ADD_TIME_ZONE, timeZoneAddSaga);
yield takeEvery(EDIT_TIME_ZONE, timeZoneEditSaga);
yield takeEvery(DELETE_TIME_ZONE, timeZoneDeleteSaga);
yield takeEvery(EXPORT_TIME_ZONE, timeZoneExportDataSaga);
yield takeEvery(IMPORT_TIME_ZONE, timeZoneImportDataSaga);

  yield takeEvery(COUNTRY_LIST, countryListSaga);
  yield takeEvery(ADD_COUNTRY, countryAddSaga);
  yield takeEvery(EDIT_COUNTRY, countryEditSaga);
  yield takeEvery(DELETE_COUNTRY, countryDeleteSaga);
  yield takeEvery(EXPORT_COUNTRY, countryExportDataSaga);
  yield takeEvery(IMPORT_COUNTRY, countryImportDataSaga);
}

export default generalMasterSaga;