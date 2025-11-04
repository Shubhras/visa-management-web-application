import { call, takeEvery } from "redux-saga/effects";
import {
  BANK_ACCOUNT_TYPE_LIST,
  ADD_BANK_ACCOUNT_TYPE,
  EDIT_BANK_ACCOUNT_TYPE,
  DELETE_BANK_ACCOUNT_TYPE,
  IMPORT_BANK_ACCOUNT_TYPE,
  EXPORT_BANK_ACCOUNT_TYPE,
   STAKEHOLDER_TYPE_LIST,
  ADD_STAKEHOLDER_TYPE,
  EDIT_STAKEHOLDER_TYPE,
  DELETE_STAKEHOLDER_TYPE,
  IMPORT_STAKEHOLDER_TYPE,
  EXPORT_STAKEHOLDER_TYPE,
  ADD_OWNERSHIP_TYPE,
  EDIT_OWNERSHIP_TYPE,
  DELETE_OWNERSHIP_TYPE,
  EXPORT_OWNERSHIP_TYPE,
  IMPORT_OWNERSHIP_TYPE,
  OWNERSHIP_TYPE_LIST,
  
} from "./actionTypes";

import { addBankAccountTypeDataAPI, addOwnershipTypeDataAPI, addStakeholderTypeDataAPI, deleteBankAccountTypeDataAPI, deleteOwnershipTypeDataAPI, deleteStakeholderTypeDataAPI, editBankAccountTypeDataAPI, editOwnershipTypeDataAPI, editStakeholderTypeDataAPI, exportBankAccountTypeDataAPI, exportOwnershipTypeDataAPI, exportStakeholderTypeDataAPI, getBankAccountTypeListDataAPI, getOwnershipTypeListDataAPI, getStakeholderTypeListDataAPI, importBankAccountTypeDataAPI, importOwnershipTypeDataAPI, importStakeholderTypeDataAPI } from "../../../service/api_helper";
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

// Stakeholder Type
function* stakeholderTypeListSaga(action) {
  try {
    const response = yield call(getStakeholderTypeListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* stakeholderTypeAddSaga(action) {
  try {
    const response = yield call(addStakeholderTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* stakeholderTypeEditSaga(action) {
  try {
    const response = yield call(editStakeholderTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* stakeholderTypeDeleteSaga(action) {
  try {
    const response = yield call(deleteStakeholderTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* stakeholderTypeExportDataSaga(action) {
  try {
    const response = yield call(exportStakeholderTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* stakeholderTypeImportDataSaga(action) {
  try {
    const response = yield call(importStakeholderTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}
// Ownership Type
function* ownershipTypeListSaga(action) {
  try {
    const response = yield call(getOwnershipTypeListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* ownershipTypeAddSaga(action) {
  try {
    const response = yield call(addOwnershipTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* ownershipTypeEditSaga(action) {
  try {
    const response = yield call(editOwnershipTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* ownershipTypeDeleteSaga(action) {
  try {
    const response = yield call(deleteOwnershipTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* ownershipTypeExportDataSaga(action) {
  try {
    const response = yield call(exportOwnershipTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* ownershipTypeImportDataSaga(action) {
  try {
    const response = yield call(importOwnershipTypeDataAPI, action?.data);
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
    // Stakeholder Type
  yield takeEvery(STAKEHOLDER_TYPE_LIST, stakeholderTypeListSaga);
  yield takeEvery(ADD_STAKEHOLDER_TYPE, stakeholderTypeAddSaga);
  yield takeEvery(EDIT_STAKEHOLDER_TYPE, stakeholderTypeEditSaga);
  yield takeEvery(DELETE_STAKEHOLDER_TYPE, stakeholderTypeDeleteSaga);
  yield takeEvery(EXPORT_STAKEHOLDER_TYPE, stakeholderTypeExportDataSaga);
  yield takeEvery(IMPORT_STAKEHOLDER_TYPE, stakeholderTypeImportDataSaga);
  // Ownership Type
yield takeEvery(OWNERSHIP_TYPE_LIST, ownershipTypeListSaga);
yield takeEvery(ADD_OWNERSHIP_TYPE, ownershipTypeAddSaga);
yield takeEvery(EDIT_OWNERSHIP_TYPE, ownershipTypeEditSaga);
yield takeEvery(DELETE_OWNERSHIP_TYPE, ownershipTypeDeleteSaga);
yield takeEvery(EXPORT_OWNERSHIP_TYPE, ownershipTypeExportDataSaga);
yield takeEvery(IMPORT_OWNERSHIP_TYPE, ownershipTypeImportDataSaga);

}

export default companyMasterSaga;
