import { call, takeEvery } from "redux-saga/effects";
import {
  BANK_ACCOUNT_TYPE_LIST,
  ADD_BANK_ACCOUNT_TYPE,
  EDIT_BANK_ACCOUNT_TYPE,
  DELETE_BANK_ACCOUNT_TYPE,
  IMPORT_BANK_ACCOUNT_TYPE,
  EXPORT_BANK_ACCOUNT_TYPE,
  
} from "./actionTypes";

import { addBankAccountTypeDataAPI, deleteBankAccountTypeDataAPI, editBankAccountTypeDataAPI, exportBankAccountTypeDataAPI, getBankAccountTypeListDataAPI, importBankAccountTypeDataAPI } from "../../../service/api_helper";
// Bank Account Type
function* bankAccountTypeListSaga(action) {
  try {
    const response = yield call(getBankAccountTypeListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* bankAccountTypeAddSaga(action) {
  try {
    const response = yield call(addBankAccountTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* bankAccountTypeEditSaga(action) {
  try {
    const response = yield call(editBankAccountTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* bankAccountTypeDeleteSaga(action) {
  try {
    const response = yield call(deleteBankAccountTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* bankAccountTypeExportDataSaga(action) {
  try {
    const response = yield call(exportBankAccountTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* bankAccountTypeImportDataSaga(action) {
  try {
    const response = yield call(importBankAccountTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* companyMasterSaga() {
    // Bank Account Type
  yield takeEvery(BANK_ACCOUNT_TYPE_LIST, bankAccountTypeListSaga);
  yield takeEvery(ADD_BANK_ACCOUNT_TYPE, bankAccountTypeAddSaga);
  yield takeEvery(EDIT_BANK_ACCOUNT_TYPE, bankAccountTypeEditSaga);
  yield takeEvery(DELETE_BANK_ACCOUNT_TYPE, bankAccountTypeDeleteSaga);
  yield takeEvery(EXPORT_BANK_ACCOUNT_TYPE, bankAccountTypeExportDataSaga);
  yield takeEvery(IMPORT_BANK_ACCOUNT_TYPE, bankAccountTypeImportDataSaga);

}

export default companyMasterSaga;
