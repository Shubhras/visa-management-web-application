import {
  DEPARTMENT_LIST,
  ADD_DEPARTMENT,
  EDIT_DEPARTMENT,
  DELETE_DEPARTMENT,
  EXPORT_DEPARTMENT,
  IMPORT_DEPARTMENT,

COUNTRY_LIST,
ADD_COUNTRY,
EDIT_COUNTRY,
DELETE_COUNTRY,
EXPORT_COUNTRY,
IMPORT_COUNTRY,

STATE_LIST,
ADD_STATE,
EDIT_STATE,
DELETE_STATE,
EXPORT_STATE,
IMPORT_STATE,

  



    EMPLOYEE_TYPE_LIST,
  ADD_EMPLOYEE_TYPE,
  EDIT_EMPLOYEE_TYPE,
  DELETE_EMPLOYEE_TYPE,
  EXPORT_EMPLOYEE_TYPE,
  IMPORT_EMPLOYEE_TYPE
} from "./actionTypes"

export const departmentList = (data, callback) => ({
    type: DEPARTMENT_LIST,
    data,
    callback,
});

export const departmentAdd = (data, callback) => ({
    type: ADD_DEPARTMENT,
    data,
    callback,
});
export const departmentEdit = (data, callback) => ({
    type: EDIT_DEPARTMENT,
    data,
    callback,
});

export const departmentDelete = (data, callback) => ({
    type: DELETE_DEPARTMENT,
    data,
    callback,
});

export const departmentExportData = (data, callback) => ({
    type: EXPORT_DEPARTMENT,
    data,
    callback,
});
export const departmentImportData = (data, callback) => ({
    type: IMPORT_DEPARTMENT,
    data,
    callback,
});



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



//STATE TYPE
export const stateList = (data, callback) => ({
    type: STATE_LIST,
    data,
    callback,
});

export const stateAdd = (data, callback) => ({
    type: ADD_STATE,
    data,
    callback,
});
export const stateEdit = (data, callback) => ({
    type: EDIT_STATE,
    data,
    callback,
});

export const stateDelete = (data, callback) => ({
    type: DELETE_STATE,
    data,
    callback,
});

export const stateExportData = (data, callback) => ({
    type: EXPORT_STATE,
    data,
    callback,
});
export const stateImportData = (data, callback) => ({
    type: IMPORT_STATE,
    data,
    callback,
});







//EMPLOYEE_TYPE 
export const employeeTypeList = (data, callback) => ({
    type: EMPLOYEE_TYPE_LIST,
    data,
    callback,
});

export const employeeTypeAdd = (data, callback) => ({
    type: ADD_EMPLOYEE_TYPE,
    data,
    callback,
});
export const employeeTypeEdit = (data, callback) => ({
    type: EDIT_EMPLOYEE_TYPE,
    data,
    callback,
});

export const employeeTypeDelete = (data, callback) => ({
    type: DELETE_EMPLOYEE_TYPE,
    data,
    callback,
});

export const employeeTypeExportData = (data, callback) => ({
    type: EXPORT_EMPLOYEE_TYPE,
    data,
    callback,
});
export const demployeeTypeImportData = (data, callback) => ({
    type: IMPORT_EMPLOYEE_TYPE,
    data,
    callback,
});