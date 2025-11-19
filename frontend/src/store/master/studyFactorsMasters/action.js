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

export const factorForList = (data, callback) => ({
  type: FACTOR_FOR_LIST,
  data,
  callback,
});

export const factorForAdd = (data, callback) => ({
  type: ADD_FACTOR_FOR,
  data,
  callback,
});

export const factorForEdit = (data, callback) => ({
  type: EDIT_FACTOR_FOR,
  data,
  callback,
});

export const factorForDelete = (data, callback) => ({
  type: DELETE_FACTOR_FOR,
  data,
  callback,
});

export const factorForExportData = (data, callback) => ({
  type: EXPORT_FACTOR_FOR,
  data,
  callback,
});

export const factorForImportData = (data, callback) => ({
  type: IMPORT_FACTOR_FOR,
  data,
  callback,
});

export const ageGroupList = (data, callback) => ({
  type: AGE_GROUP_LIST,
  data,
  callback,
});

export const ageGroupAdd = (data, callback) => ({
  type: ADD_AGE_GROUP,
  data,
  callback,
});

export const ageGroupEdit = (data, callback) => ({
  type: EDIT_AGE_GROUP,
  data,
  callback,
});

export const ageGroupDelete = (data, callback) => ({
  type: DELETE_AGE_GROUP,
  data,
  callback,
});

export const ageGroupExportData = (data, callback) => ({
  type: EXPORT_AGE_GROUP,
  data,
  callback,
});

export const ageGroupImportData = (data, callback) => ({
  type: IMPORT_AGE_GROUP,
  data,
  callback,
});
