import { call, takeEvery } from "redux-saga/effects";
import {
  addAgeGroupAPI,
  addFactorForAPI,
  deleteAgeGroupAPI,
  deleteFactorForAPI,
  editAgeGroupAPI,
  editFactorForAPI,
  exportAgeGroupAPI,
  exportFactorForAPI,
  getAgeGroupListAPI,
  getFactorForListAPI,
  importAgeGroupAPI,
  importFactorForAPI,
} from "../../../service/api_helper";
import {
    ADD_AGE_GROUP,
  ADD_FACTOR_FOR,
  AGE_GROUP_LIST,
  DELETE_AGE_GROUP,
  DELETE_FACTOR_FOR,
  EDIT_AGE_GROUP,
  EDIT_FACTOR_FOR,
  EXPORT_AGE_GROUP,
  EXPORT_FACTOR_FOR,
  FACTOR_FOR_LIST,
  IMPORT_AGE_GROUP,
  IMPORT_FACTOR_FOR,
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
}
export default studyFactorsMasterSaga;
