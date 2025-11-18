import {
  JOB_TYPE_LIST,
  ADD_JOB_TYPE,
  EDIT_JOB_TYPE,
  DELETE_JOB_TYPE,
  EXPORT_JOB_TYPE,
  IMPORT_JOB_TYPE,
  MODE_OF_SALARY_LIST,
  ADD_MODE_OF_SALARY,
  EDIT_MODE_OF_SALARY,
  DELETE_MODE_OF_SALARY,
  EXPORT_MODE_OF_SALARY,
  IMPORT_MODE_OF_SALARY,
  IT_RETURN_STATUS_LIST,
  ADD_IT_RETURN_STATUS,
  EDIT_IT_RETURN_STATUS,
  DELETE_IT_RETURN_STATUS,
  EXPORT_IT_RETURN_STATUS,
  IMPORT_IT_RETURN_STATUS,
  OCCUPATION_TYPE_LIST,
  ADD_OCCUPATION_TYPE,
  EDIT_OCCUPATION_TYPE,
  DELETE_OCCUPATION_TYPE,
  EXPORT_OCCUPATION_TYPE,
  IMPORT_OCCUPATION_TYPE,
  OCCUPATION_PROSPECT_LIST,
  ADD_OCCUPATION_PROSPECT,
  EDIT_OCCUPATION_PROSPECT,
  DELETE_OCCUPATION_PROSPECT,
  EXPORT_OCCUPATION_PROSPECT,
  IMPORT_OCCUPATION_PROSPECT,
  OCCUPATION_CATEGORY_LIST,
  ADD_OCCUPATION_CATEGORY,
  EDIT_OCCUPATION_CATEGORY,
  DELETE_OCCUPATION_CATEGORY,
  EXPORT_OCCUPATION_CATEGORY,
  IMPORT_OCCUPATION_CATEGORY,
  OCCUPATION_VERSION_LIST,
  ADD_OCCUPATION_VERSION,
  EDIT_OCCUPATION_VERSION,
  DELETE_OCCUPATION_VERSION,
  EXPORT_OCCUPATION_VERSION,
  IMPORT_OCCUPATION_VERSION,
  OCCUPATION_LEVEL_CODE_LIST,
  ADD_OCCUPATION_LEVEL_CODE,
  EDIT_OCCUPATION_LEVEL_CODE,
  DELETE_OCCUPATION_LEVEL_CODE,
  EXPORT_OCCUPATION_LEVEL_CODE,
  IMPORT_OCCUPATION_LEVEL_CODE,
  OCCUPATION_LEVEL_LIST,
  ADD_OCCUPATION_LEVEL,
  EDIT_OCCUPATION_LEVEL,
  DELETE_OCCUPATION_LEVEL,
  EXPORT_OCCUPATION_LEVEL,
  IMPORT_OCCUPATION_LEVEL,
  OCCUPATION_CODE_LIST,
  ADD_OCCUPATION_CODE,
  EDIT_OCCUPATION_CODE,
  DELETE_OCCUPATION_CODE,
  EXPORT_OCCUPATION_CODE,
  IMPORT_OCCUPATION_CODE,
  IMPORT_OCCUPATION_NAME,
  EXPORT_OCCUPATION_NAME,
  DELETE_OCCUPATION_NAME,
  EDIT_OCCUPATION_NAME,
  ADD_OCCUPATION_NAME,
  OCCUPATION_NAME_LIST,
  DESIGNATION_LIST,
  ADD_DESIGNATION,
  EDIT_DESIGNATION,
  DELETE_DESIGNATION,
  EXPORT_DESIGNATION,
  IMPORT_DESIGNATION,
  IMPORT_JOB_PROSPECT,
  EXPORT_JOB_PROSPECT,
  DELETE_JOB_PROSPECT,
  EDIT_JOB_PROSPECT,
  ADD_JOB_PROSPECT,
  JOB_PROSPECT_LIST,
  REPRESENTING_COUNTRY_LIST,
} from "./actionType";

// Job Type Actions
export const jobTypeList = (data, callback) => ({
  type: JOB_TYPE_LIST,
  data,
  callback,
});

export const jobTypeAdd = (data, callback) => ({
  type: ADD_JOB_TYPE,
  data,
  callback,
});

export const jobTypeEdit = (data, callback) => ({
  type: EDIT_JOB_TYPE,
  data,
  callback,
});

export const jobTypeDelete = (data, callback) => ({
  type: DELETE_JOB_TYPE,
  data,
  callback,
});

export const jobTypeExportData = (data, callback) => ({
  type: EXPORT_JOB_TYPE,
  data,
  callback,
});

export const jobTypeImportData = (data, callback) => ({
  type: IMPORT_JOB_TYPE,
  data,
  callback,
});

// Mode of Salary Actions
export const modeOfSalaryList = (data, callback) => ({
  type: MODE_OF_SALARY_LIST,
  data,
  callback,
});

export const modeOfSalaryAdd = (data, callback) => ({
  type: ADD_MODE_OF_SALARY,
  data,
  callback,
});

export const modeOfSalaryEdit = (data, callback) => ({
  type: EDIT_MODE_OF_SALARY,
  data,
  callback,
});

export const modeOfSalaryDelete = (data, callback) => ({
  type: DELETE_MODE_OF_SALARY,
  data,
  callback,
});

export const modeOfSalaryExportData = (data, callback) => ({
  type: EXPORT_MODE_OF_SALARY,
  data,
  callback,
});

export const modeOfSalaryImportData = (data, callback) => ({
  type: IMPORT_MODE_OF_SALARY,
  data,
  callback,
});
// IT Return Status Actions
export const itReturnStatusList = (data, callback) => ({
  type: IT_RETURN_STATUS_LIST,
  data,
  callback,
});

export const itReturnStatusAdd = (data, callback) => ({
  type: ADD_IT_RETURN_STATUS,
  data,
  callback,
});

export const itReturnStatusEdit = (data, callback) => ({
  type: EDIT_IT_RETURN_STATUS,
  data,
  callback,
});

export const itReturnStatusDelete = (data, callback) => ({
  type: DELETE_IT_RETURN_STATUS,
  data,
  callback,
});

export const itReturnStatusExportData = (data, callback) => ({
  type: EXPORT_IT_RETURN_STATUS,
  data,
  callback,
});

export const itReturnStatusImportData = (data, callback) => ({
  type: IMPORT_IT_RETURN_STATUS,
  data,
  callback,
});
// Occupation Type Actions
export const occupationTypeList = (data, callback) => ({
  type: OCCUPATION_TYPE_LIST,
  data,
  callback,
});

export const occupationTypeAdd = (data, callback) => ({
  type: ADD_OCCUPATION_TYPE,
  data,
  callback,
});

export const occupationTypeEdit = (data, callback) => ({
  type: EDIT_OCCUPATION_TYPE,
  data,
  callback,
});

export const occupationTypeDelete = (data, callback) => ({
  type: DELETE_OCCUPATION_TYPE,
  data,
  callback,
});

export const occupationTypeExportData = (data, callback) => ({
  type: EXPORT_OCCUPATION_TYPE,
  data,
  callback,
});

export const occupationTypeImportData = (data, callback) => ({
  type: IMPORT_OCCUPATION_TYPE,
  data,
  callback,
});
// Occupation Prospect Actions
export const occupationProspectList = (data, callback) => ({
  type: OCCUPATION_PROSPECT_LIST,
  data,
  callback,
});

export const occupationProspectAdd = (data, callback) => ({
  type: ADD_OCCUPATION_PROSPECT,
  data,
  callback,
});

export const occupationProspectEdit = (data, callback) => ({
  type: EDIT_OCCUPATION_PROSPECT,
  data,
  callback,
});

export const occupationProspectDelete = (data, callback) => ({
  type: DELETE_OCCUPATION_PROSPECT,
  data,
  callback,
});

export const occupationProspectExportData = (data, callback) => ({
  type: EXPORT_OCCUPATION_PROSPECT,
  data,
  callback,
});

export const occupationProspectImportData = (data, callback) => ({
  type: IMPORT_OCCUPATION_PROSPECT,
  data,
  callback,
});

// Occupation Version Actions
export const occupationVersionList = (data, callback) => ({
  type: OCCUPATION_VERSION_LIST,
  data,
  callback,
});

export const occupationVersionAdd = (data, callback) => ({
  type: ADD_OCCUPATION_VERSION,
  data,
  callback,
});

export const occupationVersionEdit = (data, callback) => ({
  type: EDIT_OCCUPATION_VERSION,
  data,
  callback,
});

export const occupationVersionDelete = (data, callback) => ({
  type: DELETE_OCCUPATION_VERSION,
  data,
  callback,
});

export const occupationVersionExportData = (data, callback) => ({
  type: EXPORT_OCCUPATION_VERSION,
  data,
  callback,
});

export const occupationVersionImportData = (data, callback) => ({
  type: IMPORT_OCCUPATION_VERSION,
  data,
  callback,
});

export const occupationCategoryList = (data, callback) => ({
  type: OCCUPATION_CATEGORY_LIST,
  data,
  callback,
});

export const occupationCategoryAdd = (data, callback) => ({
  type: ADD_OCCUPATION_CATEGORY,
  data,
  callback,
});

export const occupationCategoryEdit = (data, callback) => ({
  type: EDIT_OCCUPATION_CATEGORY,
  data,
  callback,
});

export const occupationCategoryDelete = (data, callback) => ({
  type: DELETE_OCCUPATION_CATEGORY,
  data,
  callback,
});

export const occupationCategoryExportData = (data, callback) => ({
  type: EXPORT_OCCUPATION_CATEGORY,
  data,
  callback,
});

export const occupationCategoryImportData = (data, callback) => ({
  type: IMPORT_OCCUPATION_CATEGORY,
  data,
  callback,
});

export const occupationLevelCodeList = (data, callback) => ({
  type: OCCUPATION_LEVEL_CODE_LIST,
  data,
  callback,
});

export const occupationLevelCodeAdd = (data, callback) => ({
  type: ADD_OCCUPATION_LEVEL_CODE,
  data,
  callback,
});

export const occupationLevelCodeEdit = (data, callback) => ({
  type: EDIT_OCCUPATION_LEVEL_CODE,
  data,
  callback,
});

export const occupationLevelCodeDelete = (data, callback) => ({
  type: DELETE_OCCUPATION_LEVEL_CODE,
  data,
  callback,
});

export const occupationLevelCodeExportData = (data, callback) => ({
  type: EXPORT_OCCUPATION_LEVEL_CODE,
  data,
  callback,
});

export const occupationLevelCodeImportData = (data, callback) => ({
  type: IMPORT_OCCUPATION_LEVEL_CODE,
  data,
  callback,
});

export const occupationLevelList = (data, callback) => ({
  type: OCCUPATION_LEVEL_LIST,
  data,
  callback,
});

export const occupationLevelAdd = (data, callback) => ({
  type: ADD_OCCUPATION_LEVEL,
  data,
  callback,
});

export const occupationLevelEdit = (data, callback) => ({
  type: EDIT_OCCUPATION_LEVEL,
  data,
  callback,
});

export const occupationLevelDelete = (data, callback) => ({
  type: DELETE_OCCUPATION_LEVEL,
  data,
  callback,
});

export const occupationLevelExportData = (data, callback) => ({
  type: EXPORT_OCCUPATION_LEVEL,
  data,
  callback,
});

export const occupationLevelImportData = (data, callback) => ({
  type: IMPORT_OCCUPATION_LEVEL,
  data,
  callback,
});

export const occupationCodeList = (data, callback) => ({
  type: OCCUPATION_CODE_LIST,
  data,
  callback,
});

export const occupationCodeAdd = (data, callback) => ({
  type: ADD_OCCUPATION_CODE,
  data,
  callback,
});

export const occupationCodeEdit = (data, callback) => ({
  type: EDIT_OCCUPATION_CODE,
  data,
  callback,
});

export const occupationCodeDelete = (data, callback) => ({
  type: DELETE_OCCUPATION_CODE,
  data,
  callback,
});

export const occupationCodeExportData = (data, callback) => ({
  type: EXPORT_OCCUPATION_CODE,
  data,
  callback,
});

export const occupationCodeImportData = (data, callback) => ({
  type: IMPORT_OCCUPATION_CODE,
  data,
  callback,
});

export const occupationNameList = (data, callback) => ({
  type: OCCUPATION_NAME_LIST,
  data,
  callback,
});

export const occupationNameAdd = (data, callback) => ({
  type: ADD_OCCUPATION_NAME,
  data,
  callback,
});

export const occupationNameEdit = (data, callback) => ({
  type: EDIT_OCCUPATION_NAME,
  data,
  callback,
});

export const occupationNameDelete = (data, callback) => ({
  type: DELETE_OCCUPATION_NAME,
  data,
  callback,
});

export const occupationNameExportData = (data, callback) => ({
  type: EXPORT_OCCUPATION_NAME,
  data,
  callback,
});

export const occupationNameImportData = (data, callback) => ({
  type: IMPORT_OCCUPATION_NAME,
  data,
  callback,
});

export const designationList = (data, callback) => ({
  type: DESIGNATION_LIST,
  data,
  callback,
});

export const designationAdd = (data, callback) => ({
  type: ADD_DESIGNATION,
  data,
  callback,
});

export const designationEdit = (data, callback) => ({
  type: EDIT_DESIGNATION,
  data,
  callback,
});

export const designationDelete = (data, callback) => ({
  type: DELETE_DESIGNATION,
  data,
  callback,
});

export const designationExportData = (data, callback) => ({
  type: EXPORT_DESIGNATION,
  data,
  callback,
});

export const designationImportData = (data, callback) => ({
  type: IMPORT_DESIGNATION,
  data,
  callback,
});

export const jobProspectList = (data, callback) => ({
  type: JOB_PROSPECT_LIST,
  data,
  callback,
});

export const jobProspectAdd = (data, callback) => ({
  type: ADD_JOB_PROSPECT,
  data,
  callback,
});

export const jobProspectEdit = (data, callback) => ({
  type: EDIT_JOB_PROSPECT,
  data,
  callback,
});

export const jobProspectDelete = (data, callback) => ({
  type: DELETE_JOB_PROSPECT,
  data,
  callback,
});

export const jobProspectExportData = (data, callback) => ({
  type: EXPORT_JOB_PROSPECT,
  data,
  callback,
});

export const jobProspectImportData = (data, callback) => ({
  type: IMPORT_JOB_PROSPECT,
  data,
  callback,
});

export const representingCountryList = (data, callback) => ({
  type: REPRESENTING_COUNTRY_LIST,
  data,
  callback,
});

