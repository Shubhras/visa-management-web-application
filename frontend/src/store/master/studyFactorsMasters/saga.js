import { call, takeEvery } from "redux-saga/effects";
import {
    addAcademicResultGroupAPI,
  addAgeGroupAPI,
  addBacklogsGroupAPI,
  addFactorForAPI,
  addGapGroupAPI,
  deleteAcademicResultGroupAPI,
  deleteAgeGroupAPI,
  deleteBacklogsGroupAPI,
  deleteFactorForAPI,
  deleteGapGroupAPI,
  editAcademicResultGroupAPI,
  editAgeGroupAPI,
  editBacklogsGroupAPI,
  editFactorForAPI,
  editGapGroupAPI,
  exportAcademicResultGroupAPI,
  exportAgeGroupAPI,
  exportBacklogsGroupAPI,
  exportFactorForAPI,
  exportGapGroupAPI,
  getAcademicResultGroupListAPI,
  getAgeGroupListAPI,
  getBacklogsGroupListAPI,
  getFactorForListAPI,
  getGapGroupListAPI,
  importAcademicResultGroupAPI,
  importAgeGroupAPI,
  importBacklogsGroupAPI,
  importFactorForAPI,
  importGapGroupAPI,
} from "../../../service/api_helper";
import {
    ACADEMIC_RESULT_GROUP_LIST,
  ADD_ACADEMIC_RESULT_GROUP,
  ADD_AGE_GROUP,
  ADD_BACKLOGS_GROUP,
  ADD_FACTOR_FOR,
  ADD_GAP_GROUP,
  AGE_GROUP_LIST,
  BACKLOGS_GROUP_LIST,
  DELETE_ACADEMIC_RESULT_GROUP,
  DELETE_AGE_GROUP,
  DELETE_BACKLOGS_GROUP,
  DELETE_FACTOR_FOR,
  DELETE_GAP_GROUP,
  EDIT_ACADEMIC_RESULT_GROUP,
  EDIT_AGE_GROUP,
  EDIT_BACKLOGS_GROUP,
  EDIT_FACTOR_FOR,
  EDIT_GAP_GROUP,
  EXPORT_ACADEMIC_RESULT_GROUP,
  EXPORT_AGE_GROUP,
  EXPORT_BACKLOGS_GROUP,
  EXPORT_FACTOR_FOR,
  EXPORT_GAP_GROUP,
  FACTOR_FOR_LIST,
  GAP_GROUP_LIST,
  IMPORT_ACADEMIC_RESULT_GROUP,
  IMPORT_AGE_GROUP,
  IMPORT_BACKLOGS_GROUP,
  IMPORT_FACTOR_FOR,
  IMPORT_GAP_GROUP,
} from "./actionType";

//Factor For
function* factorForListSaga(action) {
  try {
    const response = yield call(getFactorForListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* factorForAddSaga(action) {
  try {
    const response = yield call(addFactorForAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* factorForEditSaga(action) {
  try {
    const response = yield call(editFactorForAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* factorForDeleteSaga(action) {
  try {
    const response = yield call(deleteFactorForAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* factorForExportSaga(action) {
  try {
    const response = yield call(exportFactorForAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* factorForImportSaga(action) {
  try {
    const response = yield call(importFactorForAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

//Age Group
function* ageGroupListSaga(action) {
  try {
    const response = yield call(getAgeGroupListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* ageGroupAddSaga(action) {
  try {
    const response = yield call(addAgeGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* ageGroupEditSaga(action) {
  try {
    const response = yield call(editAgeGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* ageGroupDeleteSaga(action) {
  try {
    const response = yield call(deleteAgeGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* ageGroupExportSaga(action) {
  try {
    const response = yield call(exportAgeGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* ageGroupImportSaga(action) {
  try {
    const response = yield call(importAgeGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}
// Academic Result Group
function* academicResultGroupListSaga(action) {
  try {
    const response = yield call(getAcademicResultGroupListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* academicResultGroupAddSaga(action) {
  try {
    const response = yield call(addAcademicResultGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* academicResultGroupEditSaga(action) {
  try {
    const response = yield call(editAcademicResultGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* academicResultGroupDeleteSaga(action) {
  try {
    const response = yield call(deleteAcademicResultGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* academicResultGroupExportSaga(action) {
  try {
    const response = yield call(exportAcademicResultGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* academicResultGroupImportSaga(action) {
  try {
    const response = yield call(importAcademicResultGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}
//BACKLOGS GROUP
function* backlogsGroupListSaga(action) {
  try {
    const response = yield call(getBacklogsGroupListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* backlogsGroupAddSaga(action) {
  try {
    const response = yield call(addBacklogsGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* backlogsGroupEditSaga(action) {
  try {
    const response = yield call(editBacklogsGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* backlogsGroupDeleteSaga(action) {
  try {
    const response = yield call(deleteBacklogsGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* backlogsGroupExportSaga(action) {
  try {
    const response = yield call(exportBacklogsGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* backlogsGroupImportSaga(action) {
  try {
    const response = yield call(importBacklogsGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}
//GAP GROUP
function* gapGroupListSaga(action) {
  try {
    const response = yield call(getGapGroupListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* gapGroupAddSaga(action) {
  try {
    const response = yield call(addGapGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* gapGroupEditSaga(action) {
  try {
    const response = yield call(editGapGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* gapGroupDeleteSaga(action) {
  try {
    const response = yield call(deleteGapGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* gapGroupExportSaga(action) {
  try {
    const response = yield call(exportGapGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* gapGroupImportSaga(action) {
  try {
    const response = yield call(importGapGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorsMasterSaga() {
  yield takeEvery(FACTOR_FOR_LIST, factorForListSaga);
  yield takeEvery(ADD_FACTOR_FOR, factorForAddSaga);
  yield takeEvery(EDIT_FACTOR_FOR, factorForEditSaga);
  yield takeEvery(DELETE_FACTOR_FOR, factorForDeleteSaga);
  yield takeEvery(EXPORT_FACTOR_FOR, factorForExportSaga);
  yield takeEvery(IMPORT_FACTOR_FOR, factorForImportSaga);
  yield takeEvery(AGE_GROUP_LIST, ageGroupListSaga);
  yield takeEvery(ADD_AGE_GROUP, ageGroupAddSaga);
  yield takeEvery(EDIT_AGE_GROUP, ageGroupEditSaga);
  yield takeEvery(DELETE_AGE_GROUP, ageGroupDeleteSaga);
  yield takeEvery(EXPORT_AGE_GROUP, ageGroupExportSaga);
  yield takeEvery(IMPORT_AGE_GROUP, ageGroupImportSaga);
  yield takeEvery(ACADEMIC_RESULT_GROUP_LIST, academicResultGroupListSaga);
  yield takeEvery(ADD_ACADEMIC_RESULT_GROUP, academicResultGroupAddSaga);
  yield takeEvery(EDIT_ACADEMIC_RESULT_GROUP, academicResultGroupEditSaga);
  yield takeEvery(DELETE_ACADEMIC_RESULT_GROUP, academicResultGroupDeleteSaga);
  yield takeEvery(EXPORT_ACADEMIC_RESULT_GROUP, academicResultGroupExportSaga);
  yield takeEvery(IMPORT_ACADEMIC_RESULT_GROUP, academicResultGroupImportSaga);
  yield takeEvery(BACKLOGS_GROUP_LIST, backlogsGroupListSaga);
  yield takeEvery(ADD_BACKLOGS_GROUP, backlogsGroupAddSaga);
  yield takeEvery(EDIT_BACKLOGS_GROUP, backlogsGroupEditSaga);
  yield takeEvery(DELETE_BACKLOGS_GROUP, backlogsGroupDeleteSaga);
  yield takeEvery(EXPORT_BACKLOGS_GROUP, backlogsGroupExportSaga);
  yield takeEvery(IMPORT_BACKLOGS_GROUP, backlogsGroupImportSaga);
  yield takeEvery(GAP_GROUP_LIST, gapGroupListSaga);
  yield takeEvery(ADD_GAP_GROUP, gapGroupAddSaga);
  yield takeEvery(EDIT_GAP_GROUP, gapGroupEditSaga);
  yield takeEvery(DELETE_GAP_GROUP, gapGroupDeleteSaga);
  yield takeEvery(EXPORT_GAP_GROUP, gapGroupExportSaga);
  yield takeEvery(IMPORT_GAP_GROUP, gapGroupImportSaga);
}
export default studyFactorsMasterSaga;
