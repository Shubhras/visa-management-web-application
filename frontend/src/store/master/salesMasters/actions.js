import {
    IMPORT_ACTIVITY_TYPE,
    EXPORT_ACTIVITY_TYPE,
    DELETE_ACTIVITY_TYPE,
    EDIT_ACTIVITY_TYPE,
    ADD_ACTIVITY_TYPE,
    ACTIVITY_TYPE_LIST,
} from "./actionTypes"

// ACTIVITY_TYPE
export const activityTypeList = (data, callback) => ({
    type: ACTIVITY_TYPE_LIST,
    data,
    callback,
});

export const activityTypeAdd = (data, callback) => ({
    type: ADD_ACTIVITY_TYPE,
    data,
    callback,
});

export const activityTypeEdit = (data, callback) => ({
    type: EDIT_ACTIVITY_TYPE,
    data,
    callback,
});

export const activityTypeDelete = (data, callback) => ({
    type: DELETE_ACTIVITY_TYPE,
    data,
    callback,
});

export const activityTypeExportData = (data, callback) => ({
    type: EXPORT_ACTIVITY_TYPE,
    data,
    callback,
});

export const activityTypeImportData = (data, callback) => ({
    type: IMPORT_ACTIVITY_TYPE,
    data,
    callback,
});