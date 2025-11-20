import {
    REPRESENTING_COUNTRY_LIST,
    ADD_REPRESENTING_COUNTRY,
    EDIT_REPRESENTING_COUNTRY,
    DELETE_REPRESENTING_COUNTRY,
    EXPORT_REPRESENTING_COUNTRY,
    IMPORT_REPRESENTING_COUNTRY
} from "./actionType";


// Representing Country Actions
export const representingCountryData = (data, callback) => ({
    type: REPRESENTING_COUNTRY_LIST,
    data,
    callback,
});

export const representingCountryAdd = (data, callback) => ({
    type: ADD_REPRESENTING_COUNTRY,
    data,
    callback,
});

export const representingCountryEdit = (data, callback) => ({
    type: EDIT_REPRESENTING_COUNTRY,
    data,
    callback,
});

export const representingCountryDelete = (data, callback) => ({
    type: DELETE_REPRESENTING_COUNTRY,
    data,
    callback,
});

export const representingCountryExportData = (data, callback) => ({
    type: EXPORT_REPRESENTING_COUNTRY,
    data,
    callback,
});

export const representingCountryImportData = (data, callback) => ({
    type: IMPORT_REPRESENTING_COUNTRY,
    data,
    callback,
});
