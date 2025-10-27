import {
    DEPARTMENT_LIST,
    ADD_DEPARTMENT,
    EDIT_DEPARTMENT,
    DELETE_DEPARTMENT,
    EXPORT_DEPARTMENT,
    IMPORT_DEPARTMENT,

    EMPLOYEE_TYPE_LIST,
    ADD_EMPLOYEE_TYPE,
    EDIT_EMPLOYEE_TYPE,
    DELETE_EMPLOYEE_TYPE,
    EXPORT_EMPLOYEE_TYPE,
    IMPORT_EMPLOYEE_TYPE,

    COMPANY_LIST,
    ADD_COMPANY,
    EDIT_COMPANY,
    DELETE_COMPANY,
    EXPORT_COMPANY,
    IMPORT_COMPANY,
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

//Company Type
export const companyList = (data, callback) => ({
    type: COMPANY_LIST,
    data,
    callback,
});

export const companyAdd = (data, callback) => ({
    type: ADD_COMPANY,
    data,
    callback,
});
export const companyEdit = (data, callback) => ({
    type: EDIT_COMPANY,
    data,
    callback,
});

export const companyDelete = (data, callback) => ({
    type: DELETE_COMPANY,
    data,
    callback,
});

export const companyExportData = (data, callback) => ({
    type: EXPORT_COMPANY,
    data,
    callback,
});
export const dcompanyImportData = (data, callback) => ({
    type: IMPORT_COMPANY,
    data,
    callback,
});


