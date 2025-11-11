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
  ACCREDITATION_CATEGORY_LIST,
  ADD_ACCREDITATION_CATEGORY,
  EDIT_ACCREDITATION_CATEGORY,
  DELETE_ACCREDITATION_CATEGORY,
  EXPORT_ACCREDITATION_CATEGORY,
  IMPORT_ACCREDITATION_CATEGORY,
  LICENCE_NAME_LIST,
  ADD_LICENCE_NAME,
  EDIT_LICENCE_NAME,
  DELETE_LICENCE_NAME,
  EXPORT_LICENCE_NAME,
  IMPORT_LICENCE_NAME,
  ACCREDITATION_NAME_LIST,
  ADD_ACCREDITATION_NAME,
  EDIT_ACCREDITATION_NAME,
  DELETE_ACCREDITATION_NAME,
  EXPORT_ACCREDITATION_NAME,
  COUNTRY_LIST_DEMO,

} from "./actionTypes";

import {
  addAccreditationCategoryDataAPI,
  addBankAccountTypeDataAPI,
  addOwnershipTypeDataAPI,
  addStakeholderTypeDataAPI,
  deleteAccreditationCategoryDataAPI,
  deleteBankAccountTypeDataAPI,
  deleteOwnershipTypeDataAPI,
  deleteStakeholderTypeDataAPI,
  editAccreditationCategoryDataAPI,
  editBankAccountTypeDataAPI,
  editOwnershipTypeDataAPI,
  editStakeholderTypeDataAPI,
  exportAccreditationCategoryDataAPI,
  exportBankAccountTypeDataAPI,
  exportOwnershipTypeDataAPI,
  exportStakeholderTypeDataAPI,
  getAccreditationCategoryListDataAPI,
  getBankAccountTypeListDataAPI,
  getOwnershipTypeListDataAPI,
  getStakeholderTypeListDataAPI,
  importAccreditationCategoryDataAPI,
  importBankAccountTypeDataAPI,
  importOwnershipTypeDataAPI,
  importStakeholderTypeDataAPI,
  getLicenceNameListDataAPI,
  addLicenceNameDataAPI,
  editLicenceNameDataAPI,
  deleteLicenceNameDataAPI,
  exportLicenceNameDataAPI,
  importLicenceNameDataAPI,
  exportAccreditationNameDataAPI,
  importAccreditationNameDataAPI,
  deleteAccreditationNameDataAPI,
  editAccreditationNameDataAPI,
  addAccreditationNameDataAPI,
  getAccreditationNameListDataAPI,
  getCountryListDataAPI,
} from "../../../service/api_helper";
import { IMPORT_ACCREDITATION_NAME_API } from "../../../service/api_url";
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

// Accreditation Category
function* accreditationCategoryListSaga(action) {
  try {
    const response = yield call(getAccreditationCategoryListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* accreditationCategoryAddSaga(action) {
  try {
    const response = yield call(addAccreditationCategoryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* accreditationCategoryEditSaga(action) {
  try {
    const response = yield call(editAccreditationCategoryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* accreditationCategoryDeleteSaga(action) {
  try {
    const response = yield call(deleteAccreditationCategoryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* accreditationCategoryExportDataSaga(action) {
  try {
    const response = yield call(exportAccreditationCategoryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* accreditationCategoryImportDataSaga(action) {
  try {
    const response = yield call(importAccreditationCategoryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

// Licence Name
function* licenceNameListSaga(action) {
  try {
    const response = yield call(getLicenceNameListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* licenceNameAddSaga(action) {
  try {
    const response = yield call(addLicenceNameDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* licenceNameEditSaga(action) {
  try {
    const response = yield call(editLicenceNameDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* licenceNameDeleteSaga(action) {
  try {
    const response = yield call(deleteLicenceNameDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* licenceNameExportDataSaga(action) {
  try {
    const response = yield call(exportLicenceNameDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* licenceNameImportDataSaga(action) {
  try {
    const response = yield call(importLicenceNameDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

// Accreditation Name
function* accreditationNameListSaga(action) {
  try {
    const response = yield call(getAccreditationNameListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* accreditationNameAddSaga(action) {
  try {
    const response = yield call(addAccreditationNameDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* accreditationNameEditSaga(action) {
  try {
    const response = yield call(editAccreditationNameDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* accreditationNameDeleteSaga(action) {
  try {
    const response = yield call(deleteAccreditationNameDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* accreditationNameExportDataSaga(action) {
  try {
    const response = yield call(exportAccreditationNameDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* accreditationNameImportDataSaga(action) {
  try {
    const response = yield call(importAccreditationNameDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* countryDemoSaga(action) {
  try {
    const response = yield call(getCountryListDataAPI, action?.data);
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
  // Accreditation Category
  yield takeEvery(ACCREDITATION_CATEGORY_LIST, accreditationCategoryListSaga);
  yield takeEvery(ADD_ACCREDITATION_CATEGORY, accreditationCategoryAddSaga);
  yield takeEvery(EDIT_ACCREDITATION_CATEGORY, accreditationCategoryEditSaga);
  yield takeEvery(DELETE_ACCREDITATION_CATEGORY, accreditationCategoryDeleteSaga);
  yield takeEvery(EXPORT_ACCREDITATION_CATEGORY, accreditationCategoryExportDataSaga);
  yield takeEvery(IMPORT_ACCREDITATION_CATEGORY, accreditationCategoryImportDataSaga);

  // Licence Name
  yield takeEvery(LICENCE_NAME_LIST, licenceNameListSaga);
  yield takeEvery(ADD_LICENCE_NAME, licenceNameAddSaga);
  yield takeEvery(EDIT_LICENCE_NAME, licenceNameEditSaga);
  yield takeEvery(DELETE_LICENCE_NAME, licenceNameDeleteSaga);
  yield takeEvery(EXPORT_LICENCE_NAME, licenceNameExportDataSaga);
  yield takeEvery(IMPORT_LICENCE_NAME, licenceNameImportDataSaga)
  // ACCREDITATION_NAME
  yield takeEvery(ACCREDITATION_NAME_LIST, accreditationNameListSaga);
  yield takeEvery(ADD_ACCREDITATION_NAME, accreditationNameAddSaga);
  yield takeEvery(EDIT_ACCREDITATION_NAME, accreditationNameEditSaga);
  yield takeEvery(DELETE_ACCREDITATION_NAME, accreditationNameDeleteSaga);
  yield takeEvery(EXPORT_ACCREDITATION_NAME, accreditationNameExportDataSaga);
  yield takeEvery(IMPORT_ACCREDITATION_NAME_API, accreditationNameImportDataSaga);

  yield takeEvery(COUNTRY_LIST_DEMO, countryDemoSaga);

}

export default companyMasterSaga;
