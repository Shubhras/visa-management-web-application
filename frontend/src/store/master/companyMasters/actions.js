import {
  BANK_ACCOUNT_TYPE_LIST,
  ADD_BANK_ACCOUNT_TYPE,
  EDIT_BANK_ACCOUNT_TYPE,
  DELETE_BANK_ACCOUNT_TYPE,
  IMPORT_BANK_ACCOUNT_TYPE,
  EXPORT_BANK_ACCOUNT_TYPE,
} from "./actionTypes"

// BANK_ACCOUNT_TYPE
export const bankAccountTypeList = (data, callback) => ({
    type: BANK_ACCOUNT_TYPE_LIST,
    data,
    callback,
});

export const bankAccountTypeAdd = (data, callback) => ({
    type: ADD_BANK_ACCOUNT_TYPE,
    data,
    callback,
});

export const bankAccountTypeEdit = (data, callback) => ({
    type: EDIT_BANK_ACCOUNT_TYPE,
    data,
    callback,
});

export const bankAccountTypeDelete = (data, callback) => ({
    type: DELETE_BANK_ACCOUNT_TYPE,
    data,
    callback,
});

export const bankAccountTypeExportData = (data, callback) => ({
    type: EXPORT_BANK_ACCOUNT_TYPE,
    data,
    callback,
});

export const bankAccountTypeImportData = (data, callback) => ({
    type: IMPORT_BANK_ACCOUNT_TYPE,
    data,
    callback,
});