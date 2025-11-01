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
  IMPORT_MARITAL_STATUS,
  EXPORT_MARITAL_STATUS,
} from "./actionTypes";

// GENDER
export const genderList = (data, callback) => ({
  type: GENDER_LIST,
  data,
  callback,
});

export const genderAdd = (data, callback) => ({
  type: ADD_GENDER,
  data,
  callback,
});

export const genderEdit = (data, callback) => ({
  type: EDIT_GENDER,
  data,
  callback,
});

export const genderDelete = (data, callback) => ({
  type: DELETE_GENDER,
  data,
  callback,
});

export const genderExportData = (data, callback) => ({
  type: EXPORT_GENDER,
  data,
  callback,
});

export const genderImportData = (data, callback) => ({
  type: IMPORT_GENDER,
  data,
  callback,
});

// MARITAL_STATUS
export const maritalStatusList = (data, callback) => ({
  type: MARITAL_STATUS_LIST,
  data,
  callback,
});

export const maritalStatusAdd = (data, callback) => ({
  type: ADD_MARITAL_STATUS,
  data,
  callback,
});

export const maritalStatusEdit = (data, callback) => ({
  type: EDIT_MARITAL_STATUS,
  data,
  callback,
});

export const maritalStatusDelete = (data, callback) => ({
  type: DELETE_MARITAL_STATUS,
  data,
  callback,
});

export const maritalStatusExportData = (data, callback) => ({
  type: EXPORT_MARITAL_STATUS,
  data,
  callback,
});

export const maritalStatusImportData = (data, callback) => ({
  type: IMPORT_MARITAL_STATUS,
  data,
  callback,
})