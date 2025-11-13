import {
    INSTITUTE_TYPE_LIST,
    ADD_INSTITUTE_TYPE,
    EDIT_INSTITUTE_TYPE,
    DELETE_INSTITUTE_TYPE,
    EXPORT_INSTITUTE_TYPE,
    IMPORT_INSTITUTE_TYPE,
    INSTITUTE_GROUP_NAME_LIST,
    ADD_INSTITUTE_GROUP_NAME,
    EDIT_INSTITUTE_GROUP_NAME,
    DELETE_INSTITUTE_GROUP_NAME,
    EXPORT_INSTITUTE_GROUP_NAME,
    IMPORT_INSTITUTE_GROUP_NAME,
    INSTITUTE_STATUS_LIST,
    ADD_INSTITUTE_STATUS,
    EDIT_INSTITUTE_STATUS,
    DELETE_INSTITUTE_STATUS,
    EXPORT_INSTITUTE_STATUS,
    IMPORT_INSTITUTE_STATUS,
    INSTITUTE_PRIORITY_LIST,
    ADD_INSTITUTE_PRIORITY,
    EDIT_INSTITUTE_PRIORITY,
    DELETE_INSTITUTE_PRIORITY,
    EXPORT_INSTITUTE_PRIORITY,
    IMPORT_INSTITUTE_PRIORITY,
    INSTITUTE_DEPARTMENT_LIST,
    ADD_INSTITUTE_DEPARTMENT,
    EDIT_INSTITUTE_DEPARTMENT,
    DELETE_INSTITUTE_DEPARTMENT,
    EXPORT_INSTITUTE_DEPARTMENT,
    IMPORT_INSTITUTE_DEPARTMENT,
} from "./actionType";


// Institute Type Actions
export const instituteTypeList = (data, callback) => ({
    type: INSTITUTE_TYPE_LIST,
    data,
    callback,
});

export const instituteTypeAdd = (data, callback) => ({
    type: ADD_INSTITUTE_TYPE,
    data,
    callback,
});

export const instituteTypeEdit = (data, callback) => ({
    type: EDIT_INSTITUTE_TYPE,
    data,
    callback,
});

export const instituteTypeDelete = (data, callback) => ({
    type: DELETE_INSTITUTE_TYPE,
    data,
    callback,
});

export const instituteTypeExportData = (data, callback) => ({
    type: EXPORT_INSTITUTE_TYPE,
    data,
    callback,
});

export const instituteTypeImportData = (data, callback) => ({
    type: IMPORT_INSTITUTE_TYPE,
    data,
    callback,
});

// Institute Group Name Actions
export const instituteGroupNameList = (data, callback) => ({
    type: INSTITUTE_GROUP_NAME_LIST,
    data,
    callback,
});

export const instituteGroupNameAdd = (data, callback) => ({
    type: ADD_INSTITUTE_GROUP_NAME,
    data,
    callback,
});

export const instituteGroupNameEdit = (data, callback) => ({
    type: EDIT_INSTITUTE_GROUP_NAME,
    data,
    callback,
});

export const instituteGroupNameDelete = (data, callback) => ({
    type: DELETE_INSTITUTE_GROUP_NAME,
    data,
    callback,
});

export const instituteGroupNameExportData = (data, callback) => ({
    type: EXPORT_INSTITUTE_GROUP_NAME,
    data,
    callback,
});

export const instituteGroupNameImportData = (data, callback) => ({
    type: IMPORT_INSTITUTE_GROUP_NAME,
    data,
    callback,
});

// Institute Status Actions
export const instituteStatusList = (data, callback) => ({
    type: INSTITUTE_STATUS_LIST,
    data,
    callback,
});

export const instituteStatusAdd = (data, callback) => ({
    type: ADD_INSTITUTE_STATUS,
    data,
    callback,
});

export const instituteStatusEdit = (data, callback) => ({
    type: EDIT_INSTITUTE_STATUS,
    data,
    callback,
});

export const instituteStatusDelete = (data, callback) => ({
    type: DELETE_INSTITUTE_STATUS,
    data,
    callback,
});

export const instituteStatusExportData = (data, callback) => ({
    type: EXPORT_INSTITUTE_STATUS,
    data,
    callback,
});

export const instituteStatusImportData = (data, callback) => ({
    type: IMPORT_INSTITUTE_STATUS,
    data,
    callback,
});

// Institute Priority Actions
export const institutePriorityList = (data, callback) => ({
    type: INSTITUTE_PRIORITY_LIST,
    data,
    callback,
});

export const institutePriorityAdd = (data, callback) => ({
    type: ADD_INSTITUTE_PRIORITY,
    data,
    callback,
});

export const institutePriorityEdit = (data, callback) => ({
    type: EDIT_INSTITUTE_PRIORITY,
    data,
    callback,
});

export const institutePriorityDelete = (data, callback) => ({
    type: DELETE_INSTITUTE_PRIORITY,
    data,
    callback,
});

export const institutePriorityExportData = (data, callback) => ({
    type: EXPORT_INSTITUTE_PRIORITY,
    data,
    callback,
});

export const institutePriorityImportData = (data, callback) => ({
    type: IMPORT_INSTITUTE_PRIORITY,
    data,
    callback,
});

// Institute Department Actions
export const instituteDepartmentList = (data, callback) => ({
    type: INSTITUTE_DEPARTMENT_LIST,
    data,
    callback,
});

export const instituteDepartmentAdd = (data, callback) => ({
    type: ADD_INSTITUTE_DEPARTMENT,
    data,
    callback,
});

export const instituteDepartmentEdit = (data, callback) => ({
    type: EDIT_INSTITUTE_DEPARTMENT,
    data,
    callback,
});

export const instituteDepartmentDelete = (data, callback) => ({
    type: DELETE_INSTITUTE_DEPARTMENT,
    data,
    callback,
});

export const instituteDepartmentExportData = (data, callback) => ({
    type: EXPORT_INSTITUTE_DEPARTMENT,
    data,
    callback,
});

export const instituteDepartmentImportData = (data, callback) => ({
    type: IMPORT_INSTITUTE_DEPARTMENT,
    data,
    callback,
});


