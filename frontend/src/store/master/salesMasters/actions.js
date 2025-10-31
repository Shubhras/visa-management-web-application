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
    IMPORT_LOST_REASON_B2B,
    EXPORT_LOST_REASON_B2B,
    DELETE_LOST_REASON_B2B,
    EDIT_LOST_REASON_B2B,
    ADD_LOST_REASON_B2B,
    LOST_REASON_B2B_LIST,
    LEAD_SOURCE_LIST,
    ADD_LEAD_SOURCE,
    EDIT_LEAD_SOURCE,
    DELETE_LEAD_SOURCE,
    EXPORT_LEAD_SOURCE,
    IMPORT_LEAD_SOURCE,
    IMPORT_INTEREST_LEVEL,
    EXPORT_INTEREST_LEVEL,
    DELETE_INTEREST_LEVEL,
    EDIT_INTEREST_LEVEL,
    ADD_INTEREST_LEVEL,
    INTEREST_LEVEL_LIST,
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


// LOST_REASON_B2B
export const lostReasonB2BList = (data, callback) => ({
    type: LOST_REASON_B2B_LIST,
    data,
    callback,
});

export const lostReasonB2BAdd = (data, callback) => ({
    type: ADD_LOST_REASON_B2B,
    data,
    callback,
});

export const lostReasonB2BEdit = (data, callback) => ({
    type: EDIT_LOST_REASON_B2B,
    data,
    callback,
});

export const lostReasonB2BDelete = (data, callback) => ({
    type: DELETE_LOST_REASON_B2B,
    data,
    callback,
});

export const lostReasonB2BExportData = (data, callback) => ({
    type: EXPORT_LOST_REASON_B2B,
    data,
    callback,
});

export const lostReasonB2BImportData = (data, callback) => ({
    type: IMPORT_LOST_REASON_B2B,
    data,
    callback,
});

// LEAD_SOURCE
export const leadSourceList = (data, callback) => ({
    type: LEAD_SOURCE_LIST,
    data,
    callback,
});

export const leadSourceAdd = (data, callback) => ({
    type: ADD_LEAD_SOURCE,
    data,
    callback,
});

export const leadSourceEdit = (data, callback) => ({
    type: EDIT_LEAD_SOURCE,
    data,
    callback,
});

export const leadSourceDelete = (data, callback) => ({
    type: DELETE_LEAD_SOURCE,
    data,
    callback,
});

export const leadSourceExportData = (data, callback) => ({
    type: EXPORT_LEAD_SOURCE,
    data,
    callback,
});

export const leadSourceImportData = (data, callback) => ({
    type: IMPORT_LEAD_SOURCE,
    data,
    callback,
});

// INTEREST_LEVEL
export const interestLevelList = (data, callback) => ({
    type: INTEREST_LEVEL_LIST,
    data,
    callback,
});

export const interestLevelAdd = (data, callback) => ({
    type: ADD_INTEREST_LEVEL,
    data,
    callback,
});

export const interestLevelEdit = (data, callback) => ({
    type: EDIT_INTEREST_LEVEL,
    data,
    callback,
});

export const interestLevelDelete = (data, callback) => ({
    type: DELETE_INTEREST_LEVEL,
    data,
    callback,
});

export const interestLevelExportData = (data, callback) => ({
    type: EXPORT_INTEREST_LEVEL,
    data,
    callback,
});

export const interestLevelImportData = (data, callback) => ({
    type: IMPORT_INTEREST_LEVEL,
    data,
    callback,
});