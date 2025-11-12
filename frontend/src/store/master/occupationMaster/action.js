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






