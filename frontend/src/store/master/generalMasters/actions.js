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
  CONTINENT_LIST,
  ADD_CONTINENT,
  EDIT_CONTINENT,
  DELETE_CONTINENT,
  EXPORT_CONTINENT,
  IMPORT_CONTINENT,
  EXPORT_CIVIL_ID_NAME,
  IMPORT_CIVIL_ID_NAME,
  DELETE_CIVIL_ID_NAME,
  EDIT_CIVIL_ID_NAME,
  ADD_CIVIL_ID_NAME,
  CIVIL_ID_NAME_LIST,
  RELATION_LIST,
  ADD_RELATION,
  EDIT_RELATION,
  DELETE_RELATION,
  EXPORT_RELATION,
  IMPORT_RELATION,
  EXPORT_TIME_ZONE,
  IMPORT_TIME_ZONE,
  DELETE_TIME_ZONE,
  EDIT_TIME_ZONE,
  ADD_TIME_ZONE,
  TIME_ZONE_LIST,
  IMPORT_COUNTRY,
  EXPORT_COUNTRY,
  DELETE_COUNTRY,
  EDIT_COUNTRY,
  ADD_COUNTRY,
  COUNTRY_LIST,
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

// CONTINENT
export const continentList = (data, callback) => ({
  type: CONTINENT_LIST,
  data,
  callback,
});
 
export const continentAdd = (data, callback) => ({
  type: ADD_CONTINENT,
  data,
  callback,
});
 
export const continentEdit = (data, callback) => ({
  type: EDIT_CONTINENT,
  data,
  callback,
});
 
export const continentDelete = (data, callback) => ({
  type: DELETE_CONTINENT,
  data,
  callback,
});
 
export const continentExportData = (data, callback) => ({
  type: EXPORT_CONTINENT,
  data,
  callback,
});
 
export const continentImportData = (data, callback) => ({
  type: IMPORT_CONTINENT,
  data,
  callback,
});

// CIVIL_ID_NAME
export const civilIdNameList = (data, callback) => ({
  type: CIVIL_ID_NAME_LIST,
  data,
  callback,
});
 
export const civilIdNameAdd = (data, callback) => ({
  type: ADD_CIVIL_ID_NAME,
  data,
  callback,
});
 
export const civilIdNameEdit = (data, callback) => ({
  type: EDIT_CIVIL_ID_NAME,
  data,
  callback,
});
 
export const civilIdNameDelete = (data, callback) => ({
  type: DELETE_CIVIL_ID_NAME,
  data,
  callback,
});
 
export const civilIdNameExportData = (data, callback) => ({
  type: EXPORT_CIVIL_ID_NAME,
  data,
  callback,
});
 
export const civilIdNameImportData = (data, callback) => ({
  type: IMPORT_CIVIL_ID_NAME,
  data,
  callback,
});

// RELATION
export const relationList = (data, callback) => ({
  type: RELATION_LIST,
  data,
  callback,
});

export const relationAdd = (data, callback) => ({
  type: ADD_RELATION,
  data,
  callback,
});

export const relationEdit = (data, callback) => ({
  type: EDIT_RELATION,
  data,
  callback,
});

export const relationDelete = (data, callback) => ({
  type: DELETE_RELATION,
  data,
  callback,
});

export const relationExportData = (data, callback) => ({
  type: EXPORT_RELATION,
  data,
  callback,
});

export const relationImportData = (data, callback) => ({
  type: IMPORT_RELATION,
  data,
  callback,
});

// TIME_ZONE
export const timeZoneList = (data, callback) => ({
  type: TIME_ZONE_LIST,
  data,
  callback,
});

export const timeZoneAdd = (data, callback) => ({
  type: ADD_TIME_ZONE,
  data,
  callback,
});

export const timeZoneEdit = (data, callback) => ({
  type: EDIT_TIME_ZONE,
  data,
  callback,
});

export const timeZoneDelete = (data, callback) => ({
  type: DELETE_TIME_ZONE,
  data,
  callback,
});

export const timeZoneExportData = (data, callback) => ({
  type: EXPORT_TIME_ZONE,
  data,
  callback,
});

export const timeZoneImportData = (data, callback) => ({
  type: IMPORT_TIME_ZONE,
  data,
  callback,
});

//COUNTRY
export const countryList = (data, callback) => ({
  type: COUNTRY_LIST,
  data,
  callback,
});

export const countryAdd = (data, callback) => ({
  type: ADD_COUNTRY,
  data,
  callback,
});

export const countryEdit = (data, callback) => ({
  type: EDIT_COUNTRY,
  data,
  callback,
});

export const countryDelete = (data, callback) => ({
  type: DELETE_COUNTRY,
  data,
  callback,
});

export const countryExportData = (data, callback) => ({
  type: EXPORT_COUNTRY,
  data,
  callback,
});

export const countryImportData = (data, callback) => ({
  type: IMPORT_COUNTRY,
  data,
  callback,
});
