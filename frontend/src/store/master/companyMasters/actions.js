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
  OWNERSHIP_TYPE_LIST,
  ADD_OWNERSHIP_TYPE,
  EDIT_OWNERSHIP_TYPE,
  DELETE_OWNERSHIP_TYPE,
  EXPORT_OWNERSHIP_TYPE,
  IMPORT_OWNERSHIP_TYPE,
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

// STAKEHOLDER_TYPE
export const stakeholderTypeList = (data, callback) => ({
    type: STAKEHOLDER_TYPE_LIST,
    data,
    callback,
});

export const stakeholderTypeAdd = (data, callback) => ({
    type: ADD_STAKEHOLDER_TYPE,
    data,
    callback,
});

export const stakeholderTypeEdit = (data, callback) => ({
    type: EDIT_STAKEHOLDER_TYPE,
    data,
    callback,
});

export const stakeholderTypeDelete = (data, callback) => ({
    type: DELETE_STAKEHOLDER_TYPE,
    data,
    callback,
});

export const stakeholderTypeExportData = (data, callback) => ({
    type: EXPORT_STAKEHOLDER_TYPE,
    data,
    callback,
});

export const stakeholderTypeImportData = (data, callback) => ({
    type: IMPORT_STAKEHOLDER_TYPE,
    data,
    callback,
});

// OWNERSHIP_TYPE
export const ownershipTypeList = (data, callback) => ({
    type: OWNERSHIP_TYPE_LIST,
    data,
    callback,
});

export const ownershipTypeAdd = (data, callback) => ({
    type: ADD_OWNERSHIP_TYPE,
    data,
    callback,
});

export const ownershipTypeEdit = (data, callback) => ({
    type: EDIT_OWNERSHIP_TYPE,
    data,
    callback,
});

export const ownershipTypeDelete = (data, callback) => ({
    type: DELETE_OWNERSHIP_TYPE,
    data,
    callback,
});

export const ownershipTypeExportData = (data, callback) => ({
    type: EXPORT_OWNERSHIP_TYPE,
    data,
    callback,
});

export const ownershipTypeImportData = (data, callback) => ({
    type: IMPORT_OWNERSHIP_TYPE,
    data,
    callback,
});