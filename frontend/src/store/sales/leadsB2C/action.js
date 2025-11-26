import {
    LEADS_B2C_LIST,
    ADD_LEADS_B2C,
    EDIT_LEADS_B2C,
    DELETE_LEADS_B2C,
    EXPORT_LEADS_B2C,
    IMPORT_LEADS_B2C,
} from "./actionType";


// Leads B2C
export const leadsB2CList = (data, callback) => ({
    type: LEADS_B2C_LIST,
    data,
    callback,
});

export const leadsB2CAdd = (data, callback) => ({
    type: ADD_LEADS_B2C,
    data,
    callback,
});

export const leadsB2CEdit = (data, callback) => ({
    type: EDIT_LEADS_B2C,
    data,
    callback,
});

export const leadsB2CDelete = (data, callback) => ({
    type: DELETE_LEADS_B2C,
    data,
    callback,
});

export const leadsB2CExportData = (data, callback) => ({
    type: EXPORT_LEADS_B2C,
    data,
    callback,
});

export const leadsB2CImportData = (data, callback) => ({
    type: IMPORT_LEADS_B2C,
    data,
    callback,
});
