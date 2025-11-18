import { call, takeEvery } from "redux-saga/effects";
import {
  JOB_TYPE_LIST,
  ADD_JOB_TYPE,
  EDIT_JOB_TYPE,
  DELETE_JOB_TYPE,
  EXPORT_JOB_TYPE,
  IMPORT_JOB_TYPE,
  MODE_OF_SALARY_LIST,
  ADD_MODE_OF_SALARY,
  EDIT_MODE_OF_SALARY,
  DELETE_MODE_OF_SALARY,
  EXPORT_MODE_OF_SALARY,
  IMPORT_MODE_OF_SALARY,
  IT_RETURN_STATUS_LIST,
  ADD_IT_RETURN_STATUS,
  EDIT_IT_RETURN_STATUS,
  DELETE_IT_RETURN_STATUS,
  EXPORT_IT_RETURN_STATUS,
  IMPORT_IT_RETURN_STATUS,
  OCCUPATION_TYPE_LIST,
  ADD_OCCUPATION_TYPE,
  EDIT_OCCUPATION_TYPE,
  DELETE_OCCUPATION_TYPE,
  EXPORT_OCCUPATION_TYPE,
  IMPORT_OCCUPATION_TYPE,
  OCCUPATION_PROSPECT_LIST,
  ADD_OCCUPATION_PROSPECT,
  EDIT_OCCUPATION_PROSPECT,
  DELETE_OCCUPATION_PROSPECT,
  EXPORT_OCCUPATION_PROSPECT,
  IMPORT_OCCUPATION_PROSPECT,
  OCCUPATION_CATEGORY_LIST,
  ADD_OCCUPATION_CATEGORY,
  EDIT_OCCUPATION_CATEGORY,
  DELETE_OCCUPATION_CATEGORY,
  EXPORT_OCCUPATION_CATEGORY,
  IMPORT_OCCUPATION_CATEGORY,
  OCCUPATION_VERSION_LIST,
  ADD_OCCUPATION_VERSION,
  EDIT_OCCUPATION_VERSION,
  DELETE_OCCUPATION_VERSION,
  EXPORT_OCCUPATION_VERSION,
  IMPORT_OCCUPATION_VERSION,
  OCCUPATION_LEVEL_CODE_LIST,
  ADD_OCCUPATION_LEVEL_CODE,
  EDIT_OCCUPATION_LEVEL_CODE,
  DELETE_OCCUPATION_LEVEL_CODE,
  EXPORT_OCCUPATION_LEVEL_CODE,
  IMPORT_OCCUPATION_LEVEL_CODE,
  OCCUPATION_LEVEL_LIST,
  ADD_OCCUPATION_LEVEL,
  EDIT_OCCUPATION_LEVEL,
  DELETE_OCCUPATION_LEVEL,
  EXPORT_OCCUPATION_LEVEL,
  IMPORT_OCCUPATION_LEVEL,
  OCCUPATION_CODE_LIST,
  ADD_OCCUPATION_CODE,
  EDIT_OCCUPATION_CODE,
  DELETE_OCCUPATION_CODE,
  EXPORT_OCCUPATION_CODE,
  IMPORT_OCCUPATION_CODE,
  OCCUPATION_NAME_LIST,
  ADD_OCCUPATION_NAME,
  EDIT_OCCUPATION_NAME,
  DELETE_OCCUPATION_NAME,
  EXPORT_OCCUPATION_NAME,
  IMPORT_OCCUPATION_NAME,
  IMPORT_DESIGNATION,
  EXPORT_DESIGNATION,
  DELETE_DESIGNATION,
  EDIT_DESIGNATION,
  ADD_DESIGNATION,
  DESIGNATION_LIST,
  JOB_PROSPECT_LIST,
  ADD_JOB_PROSPECT,
  EDIT_JOB_PROSPECT,
  DELETE_JOB_PROSPECT,
  EXPORT_JOB_PROSPECT,
  IMPORT_JOB_PROSPECT,
  REPRESENTING_COUNTRY_LIST,
} from "./actionType";

import {
  getJobTypeListDataAPI,
  addJobTypeDataAPI,
  editJobTypeDataAPI,
  deleteJobTypeDataAPI,
  exportJobTypeDataAPI,
  importJobTypeDataAPI,
  getModeOfSalaryDataAPI,
  addModeOfSalaryDataAPI,
  editModeOfSalaryDataAPI,
  deleteModeOfSalaryDataAPI,
  exportModeOfSalaryDataAPI,
  importModeOfSalaryDataAPI,
  getItReturnStatusListDataAPI,
  addItReturnStatusDataAPI,
  editItReturnStatusDataAPI,
  deleteItReturnStatusDataAPI,
  exportItReturnStatusDataAPI,
  importItReturnStatusDataAPI,
  getOccupationTypeListDataAPI,
  addOccupationTypeDataAPI,
  editOccupationTypeDataAPI,
  deleteOccupationTypeDataAPI,
  exportOccupationTypeDataAPI,
  importOccupationTypeDataAPI,
  getOccupationProspectListDataAPI,
  addOccupationProspectDataAPI,
  editOccupationProspectDataAPI,
  deleteOccupationProspectDataAPI,
  exportOccupationProspectDataAPI,
  importOccupationProspectDataAPI,
  getOccupationVersionListDataAPI,
  addOccupationVersionDataAPI,
  editOccupationVersionDataAPI,
  deleteOccupationVersionDataAPI,
  exportOccupationVersionDataAPI,
  importOccupationVersionDataAPI,
  getOccupationCategoryListDataAPI,
  addOccupationCategoryDataAPI,
  editOccupationCategoryDataAPI,
  deleteOccupationCategoryDataAPI,
  exportOccupationCategoryDataAPI,
  importOccupationCategoryDataAPI,
  importOccupationLevelCodeAPI,
  exportOccupationLevelCodeAPI,
  deleteOccupationLevelCodeAPI,
  editOccupationLevelCodeAPI,
  addOccupationLevelCodeAPI,
  getOccupationLevelCodeListAPI,
  importOccupationLevelAPI,
  exportOccupationLevelAPI,
  deleteOccupationLevelAPI,
  editOccupationLevelAPI,
  addOccupationLevelAPI,
  getOccupationLevelListAPI,
  getOccupationCodeListAPI,
  addOccupationCodeAPI,
  editOccupationCodeAPI,
  deleteOccupationCodeAPI,
  exportOccupationCodeAPI,
  importOccupationCodeAPI,
  getOccupationNameListAPI,
  addOccupationNameAPI,
  editOccupationNameAPI,
  deleteOccupationNameAPI,
  exportOccupationNameAPI,
  importOccupationNameAPI,
  getDesignationListAPI,
  addDesignationAPI,
  editDesignationAPI,
  deleteDesignationAPI,
  exportDesignationAPI,
  importDesignationAPI,
  getJobProspectListAPI,
  addJobProspectAPI,
  editJobProspectAPI,
  deleteJobProspectAPI,
  exportJobProspectAPI,
  importJobProspectAPI,
  getRepresentingCountryListAPI,
} from "../../../service/api_helper";

// --- JOB TYPE SAGAS ---
function* jobTypeListSaga(action) {
  try {
    const response = yield call(getJobTypeListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* jobTypeAddSaga(action) {
  try {
    const response = yield call(addJobTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* jobTypeEditSaga(action) {
  try {
    const response = yield call(editJobTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* jobTypeDeleteSaga(action) {
  try {
    const response = yield call(deleteJobTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* jobTypeExportDataSaga(action) {
  try {
    const response = yield call(exportJobTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* jobTypeImportDataSaga(action) {
  try {
    const response = yield call(importJobTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

// Mode of Salary
function* modeOfSalaryListSaga(action) {
  try {
    const response = yield call(getModeOfSalaryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* modeOfSalaryAddSaga(action) {
  try {
    const response = yield call(addModeOfSalaryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}
function* modeOfSalaryEditSaga(action) {
  try {
    const response = yield call(editModeOfSalaryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}
function* modeOfSalaryDeleteSaga(action) {
  try {
    const response = yield call(deleteModeOfSalaryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}
function* modeOfSalaryExportDataSaga(action) {
  try {
    const response = yield call(exportModeOfSalaryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}
function* modeOfSalaryImportDataSaga(action) {
  try {
    const response = yield call(importModeOfSalaryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

// --- IT RETURN STATUS SAGAS ---
function* itReturnStatusListSaga(action) {
  try {
    const response = yield call(getItReturnStatusListDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* itReturnStatusAddSaga(action) {
  try {
    const response = yield call(addItReturnStatusDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* itReturnStatusEditSaga(action) {
  try {
    const response = yield call(editItReturnStatusDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* itReturnStatusDeleteSaga(action) {
  try {
    const response = yield call(deleteItReturnStatusDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* itReturnStatusExportDataSaga(action) {
  try {
    const response = yield call(exportItReturnStatusDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* itReturnStatusImportDataSaga(action) {
  try {
    const response = yield call(importItReturnStatusDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// --- OCCUPATION TYPE SAGAS ---
function* occupationTypeListSaga(action) {
  try {
    const response = yield call(getOccupationTypeListDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationTypeAddSaga(action) {
  try {
    const response = yield call(addOccupationTypeDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationTypeEditSaga(action) {
  try {
    const response = yield call(editOccupationTypeDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationTypeDeleteSaga(action) {
  try {
    const response = yield call(deleteOccupationTypeDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationTypeExportDataSaga(action) {
  try {
    const response = yield call(exportOccupationTypeDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationTypeImportDataSaga(action) {
  try {
    const response = yield call(importOccupationTypeDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// --- OCCUPATION PROSPECT SAGAS ---
function* occupationProspectListSaga(action) {
  try {
    const response = yield call(getOccupationProspectListDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationProspectAddSaga(action) {
  try {
    const response = yield call(addOccupationProspectDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationProspectEditSaga(action) {
  try {
    const response = yield call(editOccupationProspectDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationProspectDeleteSaga(action) {
  try {
    const response = yield call(deleteOccupationProspectDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationProspectExportDataSaga(action) {
  try {
    const response = yield call(exportOccupationProspectDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationProspectImportDataSaga(action) {
  try {
    const response = yield call(importOccupationProspectDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}
// --- OCCUPATION VERSION SAGAS ---
function* occupationVersionListSaga(action) {
  try {
    const response = yield call(getOccupationVersionListDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// --- OCCUPATION CATEGORY SAGAS ---
function* occupationCategoryListSaga(action) {
  try {
    const response = yield call(getOccupationCategoryListDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationCategoryAddSaga(action) {
  try {
    const response = yield call(addOccupationCategoryDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}
function* occupationVersionAddSaga(action) {
  try {
    const response = yield call(addOccupationVersionDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationVersionEditSaga(action) {
  try {
    const response = yield call(editOccupationVersionDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationVersionDeleteSaga(action) {
  try {
    const response = yield call(deleteOccupationVersionDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationVersionExportDataSaga(action) {
  try {
    const response = yield call(exportOccupationVersionDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationVersionImportDataSaga(action) {
  try {
    const response = yield call(importOccupationVersionDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationCategoryEditSaga(action) {
  try {
    const response = yield call(editOccupationCategoryDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationCategoryDeleteSaga(action) {
  try {
    const response = yield call(deleteOccupationCategoryDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationCategoryExportDataSaga(action) {
  try {
    const response = yield call(exportOccupationCategoryDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationCategoryImportDataSaga(action) {
  try {
    const response = yield call(importOccupationCategoryDataAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// --- OCCUPATION LEVEL CODE SAGAS ---
function* occupationLevelCodeListSaga(action) {
  try {
    const response = yield call(getOccupationLevelCodeListAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* occupationLevelCodeAddSaga(action) {
  try {
    const response = yield call(addOccupationLevelCodeAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* occupationLevelCodeEditSaga(action) {
  try {
    const response = yield call(editOccupationLevelCodeAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* occupationLevelCodeDeleteSaga(action) {
  try {
    const response = yield call(deleteOccupationLevelCodeAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* occupationLevelCodeExportSaga(action) {
  try {
    const response = yield call(exportOccupationLevelCodeAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* occupationLevelCodeImportSaga(action) {
  try {
    const response = yield call(importOccupationLevelCodeAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

// --- OCCUPATION LEVEL SAGAS ---
function* occupationLevelListSaga(action) {
  try {
    const response = yield call(getOccupationLevelListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationLevelAddSaga(action) {
  try {
    const response = yield call(addOccupationLevelAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationLevelEditSaga(action) {
  try {
    const response = yield call(editOccupationLevelAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationLevelDeleteSaga(action) {
  try {
    const response = yield call(deleteOccupationLevelAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationLevelExportDataSaga(action) {
  try {
    const response = yield call(exportOccupationLevelAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationLevelImportDataSaga(action) {
  try {
    const response = yield call(importOccupationLevelAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// --- OCCUPATION CODE
function* occupationCodeListSaga(action) {
  try {
    const response = yield call(getOccupationCodeListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationCodeAddSaga(action) {
  try {
    const response = yield call(addOccupationCodeAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationCodeEditSaga(action) {
  try {
    const response = yield call(editOccupationCodeAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationCodeDeleteSaga(action) {
  try {
    const response = yield call(deleteOccupationCodeAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationCodeExportSaga(action) {
  try {
    const response = yield call(exportOccupationCodeAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationCodeImportSaga(action) {
  try {
    const response = yield call(importOccupationCodeAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// --- OCCUPATION NAME
function* occupationNameListSaga(action) {
  try {
    const response = yield call(getOccupationNameListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationNameAddSaga(action) {
  try {
    const response = yield call(addOccupationNameAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationNameEditSaga(action) {
  try {
    const response = yield call(editOccupationNameAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationNameDeleteSaga(action) {
  try {
    const response = yield call(deleteOccupationNameAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationNameExportSaga(action) {
  try {
    const response = yield call(exportOccupationNameAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* occupationNameImportSaga(action) {
  try {
    const response = yield call(importOccupationNameAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// ---DESIGNATION---
function* designationListSaga(action) {
  try {
    const response = yield call(getDesignationListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* designationAddSaga(action) {
  try {
    const response = yield call(addDesignationAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* designationEditSaga(action) {
  try {
    const response = yield call(editDesignationAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* designationDeleteSaga(action) {
  try {
    const response = yield call(deleteDesignationAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* designationExportSaga(action) {
  try {
    const response = yield call(exportDesignationAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* designationImportSaga(action) {
  try {
    const response = yield call(importDesignationAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// --- JOB PROSPECT ---
function* jobProspectListSaga(action) {
  try {
    const response = yield call(getJobProspectListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* jobProspectAddSaga(action) {
  try {
    const response = yield call(addJobProspectAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* jobProspectEditSaga(action) {
  try {
    const response = yield call(editJobProspectAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* jobProspectDeleteSaga(action) {
  try {
    const response = yield call(deleteJobProspectAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* jobProspectExportSaga(action) {
  try {
    const response = yield call(exportJobProspectAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* jobProspectImportSaga(action) {
  try {
    const response = yield call(importJobProspectAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

//Representing Country
function* representingCountryListSaga(action) {
  try {
    const response = yield call(getRepresentingCountryListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// Root Saga
function* occupationMasterSaga() {
  yield takeEvery(JOB_TYPE_LIST, jobTypeListSaga);
  yield takeEvery(ADD_JOB_TYPE, jobTypeAddSaga);
  yield takeEvery(EDIT_JOB_TYPE, jobTypeEditSaga);
  yield takeEvery(DELETE_JOB_TYPE, jobTypeDeleteSaga);
  yield takeEvery(EXPORT_JOB_TYPE, jobTypeExportDataSaga);
  yield takeEvery(IMPORT_JOB_TYPE, jobTypeImportDataSaga);
  yield takeEvery(MODE_OF_SALARY_LIST, modeOfSalaryListSaga);
  yield takeEvery(ADD_MODE_OF_SALARY, modeOfSalaryAddSaga);
  yield takeEvery(EDIT_MODE_OF_SALARY, modeOfSalaryEditSaga);
  yield takeEvery(DELETE_MODE_OF_SALARY, modeOfSalaryDeleteSaga);
  yield takeEvery(EXPORT_MODE_OF_SALARY, modeOfSalaryExportDataSaga);
  yield takeEvery(IMPORT_MODE_OF_SALARY, modeOfSalaryImportDataSaga);
  yield takeEvery(IT_RETURN_STATUS_LIST, itReturnStatusListSaga);
  yield takeEvery(ADD_IT_RETURN_STATUS, itReturnStatusAddSaga);
  yield takeEvery(EDIT_IT_RETURN_STATUS, itReturnStatusEditSaga);
  yield takeEvery(DELETE_IT_RETURN_STATUS, itReturnStatusDeleteSaga);
  yield takeEvery(EXPORT_IT_RETURN_STATUS, itReturnStatusExportDataSaga);
  yield takeEvery(IMPORT_IT_RETURN_STATUS, itReturnStatusImportDataSaga);
  yield takeEvery(OCCUPATION_TYPE_LIST, occupationTypeListSaga);
  yield takeEvery(ADD_OCCUPATION_TYPE, occupationTypeAddSaga);
  yield takeEvery(EDIT_OCCUPATION_TYPE, occupationTypeEditSaga);
  yield takeEvery(DELETE_OCCUPATION_TYPE, occupationTypeDeleteSaga);
  yield takeEvery(EXPORT_OCCUPATION_TYPE, occupationTypeExportDataSaga);
  yield takeEvery(IMPORT_OCCUPATION_TYPE, occupationTypeImportDataSaga);
  yield takeEvery(OCCUPATION_PROSPECT_LIST, occupationProspectListSaga);
  yield takeEvery(ADD_OCCUPATION_PROSPECT, occupationProspectAddSaga);
  yield takeEvery(EDIT_OCCUPATION_PROSPECT, occupationProspectEditSaga);
  yield takeEvery(DELETE_OCCUPATION_PROSPECT, occupationProspectDeleteSaga);
  yield takeEvery(EXPORT_OCCUPATION_PROSPECT, occupationProspectExportDataSaga);
  yield takeEvery(IMPORT_OCCUPATION_PROSPECT, occupationProspectImportDataSaga);
  yield takeEvery(OCCUPATION_CATEGORY_LIST, occupationCategoryListSaga);
  yield takeEvery(ADD_OCCUPATION_CATEGORY, occupationCategoryAddSaga);
  yield takeEvery(EDIT_OCCUPATION_CATEGORY, occupationCategoryEditSaga);
  yield takeEvery(DELETE_OCCUPATION_CATEGORY, occupationCategoryDeleteSaga);
  yield takeEvery(EXPORT_OCCUPATION_CATEGORY, occupationCategoryExportDataSaga);
  yield takeEvery(IMPORT_OCCUPATION_CATEGORY, occupationCategoryImportDataSaga);
  yield takeEvery(OCCUPATION_VERSION_LIST, occupationVersionListSaga);
  yield takeEvery(ADD_OCCUPATION_VERSION, occupationVersionAddSaga);
  yield takeEvery(EDIT_OCCUPATION_VERSION, occupationVersionEditSaga);
  yield takeEvery(DELETE_OCCUPATION_VERSION, occupationVersionDeleteSaga);
  yield takeEvery(EXPORT_OCCUPATION_VERSION, occupationVersionExportDataSaga);
  yield takeEvery(IMPORT_OCCUPATION_VERSION, occupationVersionImportDataSaga);
  yield takeEvery(OCCUPATION_LEVEL_CODE_LIST, occupationLevelCodeListSaga);
  yield takeEvery(ADD_OCCUPATION_LEVEL_CODE, occupationLevelCodeAddSaga);
  yield takeEvery(EDIT_OCCUPATION_LEVEL_CODE, occupationLevelCodeEditSaga);
  yield takeEvery(DELETE_OCCUPATION_LEVEL_CODE, occupationLevelCodeDeleteSaga);
  yield takeEvery(EXPORT_OCCUPATION_LEVEL_CODE, occupationLevelCodeExportSaga);
  yield takeEvery(IMPORT_OCCUPATION_LEVEL_CODE, occupationLevelCodeImportSaga);
  yield takeEvery(OCCUPATION_LEVEL_LIST, occupationLevelListSaga);
  yield takeEvery(ADD_OCCUPATION_LEVEL, occupationLevelAddSaga);
  yield takeEvery(EDIT_OCCUPATION_LEVEL, occupationLevelEditSaga);
  yield takeEvery(DELETE_OCCUPATION_LEVEL, occupationLevelDeleteSaga);
  yield takeEvery(EXPORT_OCCUPATION_LEVEL, occupationLevelExportDataSaga);
  yield takeEvery(IMPORT_OCCUPATION_LEVEL, occupationLevelImportDataSaga);
  yield takeEvery(OCCUPATION_CODE_LIST, occupationCodeListSaga);
  yield takeEvery(ADD_OCCUPATION_CODE, occupationCodeAddSaga);
  yield takeEvery(EDIT_OCCUPATION_CODE, occupationCodeEditSaga);
  yield takeEvery(DELETE_OCCUPATION_CODE, occupationCodeDeleteSaga);
  yield takeEvery(EXPORT_OCCUPATION_CODE, occupationCodeExportSaga);
  yield takeEvery(IMPORT_OCCUPATION_CODE, occupationCodeImportSaga);
  yield takeEvery(OCCUPATION_NAME_LIST, occupationNameListSaga);
  yield takeEvery(ADD_OCCUPATION_NAME, occupationNameAddSaga);
  yield takeEvery(EDIT_OCCUPATION_NAME, occupationNameEditSaga);
  yield takeEvery(DELETE_OCCUPATION_NAME, occupationNameDeleteSaga);
  yield takeEvery(EXPORT_OCCUPATION_NAME, occupationNameExportSaga);
  yield takeEvery(IMPORT_OCCUPATION_NAME, occupationNameImportSaga);
  yield takeEvery(DESIGNATION_LIST, designationListSaga);
  yield takeEvery(ADD_DESIGNATION, designationAddSaga);
  yield takeEvery(EDIT_DESIGNATION, designationEditSaga);
  yield takeEvery(DELETE_DESIGNATION, designationDeleteSaga);
  yield takeEvery(EXPORT_DESIGNATION, designationExportSaga);
  yield takeEvery(IMPORT_DESIGNATION, designationImportSaga);
  yield takeEvery(JOB_PROSPECT_LIST, jobProspectListSaga);
  yield takeEvery(ADD_JOB_PROSPECT, jobProspectAddSaga);
  yield takeEvery(EDIT_JOB_PROSPECT, jobProspectEditSaga);
  yield takeEvery(DELETE_JOB_PROSPECT, jobProspectDeleteSaga);
  yield takeEvery(EXPORT_JOB_PROSPECT, jobProspectExportSaga);
  yield takeEvery(IMPORT_JOB_PROSPECT, jobProspectImportSaga);

  yield takeEvery(REPRESENTING_COUNTRY_LIST, representingCountryListSaga);
}
export default occupationMasterSaga;
