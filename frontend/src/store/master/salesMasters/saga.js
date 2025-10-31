import { call, takeEvery } from "redux-saga/effects";
import {
  ACTIVITY_TYPE_LIST,
  DELETE_ACTIVITY_TYPE,
  IMPORT_ACTIVITY_TYPE,
  EXPORT_ACTIVITY_TYPE,
  ADD_ACTIVITY_TYPE,
  EDIT_ACTIVITY_TYPE,
  LOST_REASON_B2C_LIST,
  ADD_LOST_REASON_B2C,
  EDIT_LOST_REASON_B2C,
  DELETE_LOST_REASON_B2C,
  IMPORT_LOST_REASON_B2C,
  EXPORT_LOST_REASON_B2C,
  LOST_REASON_B2B_LIST,
  ADD_LOST_REASON_B2B,
  EDIT_LOST_REASON_B2B,
  DELETE_LOST_REASON_B2B,
  IMPORT_LOST_REASON_B2B,
  EXPORT_LOST_REASON_B2B,
  LEAD_SOURCE_LIST,
  ADD_LEAD_SOURCE,
  EDIT_LEAD_SOURCE,
  DELETE_LEAD_SOURCE,
  EXPORT_LEAD_SOURCE,
  IMPORT_LEAD_SOURCE,
  INTEREST_LEVEL_LIST,
  ADD_INTEREST_LEVEL,
  EDIT_INTEREST_LEVEL,
  DELETE_INTEREST_LEVEL,
  EXPORT_INTEREST_LEVEL,
  IMPORT_INTEREST_LEVEL,
} from "./actionTypes";

import {
  importActivityTypeDataAPI,
  exportActivityTypeDataAPI,
  deleteActivityTypeDataAPI,
  editActivityTypeDataAPI,
  addActivityTypeDataAPI,
  getActivityTypeListDataAPI,
  importLostReasonB2CDataAPI,
  exportLostReasonB2CDataAPI,
  deleteLostReasonB2CDataAPI,
  editLostReasonB2CDataAPI,
  addLostReasonB2CDataAPI,
  getLostReasonB2CListDataAPI,
  importLostReasonB2BDataAPI,
  exportLostReasonB2BDataAPI,
  deleteLostReasonB2BDataAPI,
  editLostReasonB2BDataAPI,
  addLostReasonB2BDataAPI,
  getLostReasonB2BListDataAPI,
  importLeadSourceDataAPI,
  exportLeadSourceDataAPI,
  deleteLeadSourceDataAPI,
  editLeadSourceDataAPI,
  addLeadSourceDataAPI,
  getLeadSourceListDataAPI,
  importInterestLevelDataAPI,
  exportInterestLevelDataAPI,
  deleteInterestLevelDataAPI,
  editInterestLevelDataAPI,
  addInterestLevelDataAPI,
  getInterestLevelListDataAPI,
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

// Lost Reason (B2C)
function* lostReasonB2CListSaga(action) {
  try {
    const response = yield call(getLostReasonB2CListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* lostReasonB2CAddSaga(action) {
  try {
    const response = yield call(addLostReasonB2CDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* lostReasonB2CEditSaga(action) {
  try {
    const response = yield call(editLostReasonB2CDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* lostReasonB2CDeleteSaga(action) {
  try {
    const response = yield call(deleteLostReasonB2CDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* lostReasonB2CExportDataSaga(action) {
  try {
    const response = yield call(exportLostReasonB2CDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* lostReasonB2CImportDataSaga(action) {
  try {
    const response = yield call(importLostReasonB2CDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

// Lost Reason (B2B)
function* lostReasonB2BListSaga(action) {
  try {
    const response = yield call(getLostReasonB2BListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* lostReasonB2BAddSaga(action) {
  try {
    const response = yield call(addLostReasonB2BDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* lostReasonB2BEditSaga(action) {
  try {
    const response = yield call(editLostReasonB2BDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* lostReasonB2BDeleteSaga(action) {
  try {
    const response = yield call(deleteLostReasonB2BDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* lostReasonB2BExportDataSaga(action) {
  try {
    const response = yield call(exportLostReasonB2BDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* lostReasonB2BImportDataSaga(action) {
  try {
    const response = yield call(importLostReasonB2BDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}
// Lead Source
function* leadSourceListSaga(action) {
  try {
    const response = yield call(getLeadSourceListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* leadSourceAddSaga(action) {
  try {
    const response = yield call(addLeadSourceDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* leadSourceEditSaga(action) {
  try {
    const response = yield call(editLeadSourceDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* leadSourceDeleteSaga(action) {
  try {
    const response = yield call(deleteLeadSourceDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* leadSourceExportDataSaga(action) {
  try {
    const response = yield call(exportLeadSourceDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* leadSourceImportDataSaga(action) {
  try {
    const response = yield call(importLeadSourceDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

// Interest Level Sagas
function* interestLevelListSaga(action) {
  try {
    const response = yield call(getInterestLevelListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* interestLevelAddSaga(action) {
  try {
    const response = yield call(addInterestLevelDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* interestLevelEditSaga(action) {
  try {
    const response = yield call(editInterestLevelDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* interestLevelDeleteSaga(action) {
  try {
    const response = yield call(deleteInterestLevelDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* interestLevelExportDataSaga(action) {
  try {
    const response = yield call(exportInterestLevelDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* interestLevelImportDataSaga(action) {
  try {
    const response = yield call(importInterestLevelDataAPI, action?.data);
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

  // Lost Reason (B2C)
  yield takeEvery(LOST_REASON_B2C_LIST, lostReasonB2CListSaga);
  yield takeEvery(ADD_LOST_REASON_B2C, lostReasonB2CAddSaga);
  yield takeEvery(EDIT_LOST_REASON_B2C, lostReasonB2CEditSaga);
  yield takeEvery(DELETE_LOST_REASON_B2C, lostReasonB2CDeleteSaga);
  yield takeEvery(EXPORT_LOST_REASON_B2C, lostReasonB2CExportDataSaga);
  yield takeEvery(IMPORT_LOST_REASON_B2C, lostReasonB2CImportDataSaga);

  // Lost Reason (B2B)
  yield takeEvery(LOST_REASON_B2B_LIST, lostReasonB2BListSaga);
  yield takeEvery(ADD_LOST_REASON_B2B, lostReasonB2BAddSaga);
  yield takeEvery(EDIT_LOST_REASON_B2B, lostReasonB2BEditSaga);
  yield takeEvery(DELETE_LOST_REASON_B2B, lostReasonB2BDeleteSaga);
  yield takeEvery(EXPORT_LOST_REASON_B2B, lostReasonB2BExportDataSaga);
  yield takeEvery(IMPORT_LOST_REASON_B2B, lostReasonB2BImportDataSaga);

  // Lead Source
  yield takeEvery(LEAD_SOURCE_LIST, leadSourceListSaga);
  yield takeEvery(ADD_LEAD_SOURCE, leadSourceAddSaga);
  yield takeEvery(EDIT_LEAD_SOURCE, leadSourceEditSaga);
  yield takeEvery(DELETE_LEAD_SOURCE, leadSourceDeleteSaga);
  yield takeEvery(EXPORT_LEAD_SOURCE, leadSourceExportDataSaga);
  yield takeEvery(IMPORT_LEAD_SOURCE, leadSourceImportDataSaga);

  // Interest Level
  yield takeEvery(INTEREST_LEVEL_LIST, interestLevelListSaga);
  yield takeEvery(ADD_INTEREST_LEVEL, interestLevelAddSaga);
  yield takeEvery(EDIT_INTEREST_LEVEL, interestLevelEditSaga);
  yield takeEvery(DELETE_INTEREST_LEVEL, interestLevelDeleteSaga);
  yield takeEvery(EXPORT_INTEREST_LEVEL, interestLevelExportDataSaga);
  yield takeEvery(IMPORT_INTEREST_LEVEL, interestLevelImportDataSaga);
}

export default salesMasterSaga;
