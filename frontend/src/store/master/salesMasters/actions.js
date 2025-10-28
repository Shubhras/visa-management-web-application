import {
    IMPORT_ACTIVITY_TYPE,
    EXPORT_ACTIVITY_TYPE,
    DELETE_ACTIVITY_TYPE,
    EDIT_ACTIVITY_TYPE,
    ADD_ACTIVITY_TYPE,
    ACTIVITY_TYPE_LIST,
    IMPORT_LOST_REASON_B2C,
    EXPORT_LOST_REASON_B2C,
    DELETE_LOST_REASON_B2C,
    EDIT_LOST_REASON_B2C,
    ADD_LOST_REASON_B2C,
    LOST_REASON_B2C_LIST,
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

// LOST_REASON_B2C
export const lostReasonB2CList = (data, callback) => ({
    type: LOST_REASON_B2C_LIST,
    data,
    callback,
});

export const lostReasonB2CAdd = (data, callback) => ({
    type: ADD_LOST_REASON_B2C,
    data,
    callback,
});

export const lostReasonB2CEdit = (data, callback) => ({
    type: EDIT_LOST_REASON_B2C,
    data,
    callback,
});

export const lostReasonB2CDelete = (data, callback) => ({
    type: DELETE_LOST_REASON_B2C,
    data,
    callback,
});

export const lostReasonB2CExportData = (data, callback) => ({
    type: EXPORT_LOST_REASON_B2C,
    data,
    callback,
});

export const lostReasonB2CImportData = (data, callback) => ({
    type: IMPORT_LOST_REASON_B2C,
    data,
    callback,
});