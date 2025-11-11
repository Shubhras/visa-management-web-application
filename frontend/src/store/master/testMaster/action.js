import {
    LANGUAGE_NAME_TEST_LIST,
    ADD_LANGUAGE_NAME_TEST,
    EDIT_LANGUAGE_NAME_TEST,
    DELETE_LANGUAGE_NAME_TEST,
    EXPORT_LANGUAGE_NAME_TEST,
    IMPORT_LANGUAGE_NAME_TEST,
    LANGUAGE_TEST_NAME_LIST,
    ADD_LANGUAGE_TEST_NAME,
    EDIT_LANGUAGE_TEST_NAME,
    DELETE_LANGUAGE_TEST_NAME,
    EXPORT_LANGUAGE_TEST_NAME,
    IMPORT_LANGUAGE_TEST_NAME,
} from "./actionType";

// Language Name (Test)
export const languageNameTestList = (data, callback) => ({
    type: LANGUAGE_NAME_TEST_LIST,
    data,
    callback,
});

export const languageNameTestAdd = (data, callback) => ({
    type: ADD_LANGUAGE_NAME_TEST,
    data,
    callback,
});

export const languageNameTestEdit = (data, callback) => ({
    type: EDIT_LANGUAGE_NAME_TEST,
    data,
    callback,
});

export const languageNameTestDelete = (data, callback) => ({
    type: DELETE_LANGUAGE_NAME_TEST,
    data,
    callback,
});

export const languageNameTestExportData = (data, callback) => ({
    type: EXPORT_LANGUAGE_NAME_TEST,
    data,
    callback,
});

export const languageNameTestImportData = (data, callback) => ({
    type: IMPORT_LANGUAGE_NAME_TEST,
    data,
    callback,
});
// Language Test Name
export const languageTestNameList = (data, callback) => ({
    type: LANGUAGE_TEST_NAME_LIST,
    data,
    callback,
});

export const languageTestNameAdd = (data, callback) => ({
    type: ADD_LANGUAGE_TEST_NAME,
    data,
    callback,
});

export const languageTestNameEdit = (data, callback) => ({
    type: EDIT_LANGUAGE_TEST_NAME,
    data,
    callback,
});

export const languageTestNameDelete = (data, callback) => ({
    type: DELETE_LANGUAGE_TEST_NAME,
    data,
    callback,
});

export const languageTestNameExportData = (data, callback) => ({
    type: EXPORT_LANGUAGE_TEST_NAME,
    data,
    callback,
});

export const languageTestNameImportData = (data, callback) => ({
    type: IMPORT_LANGUAGE_TEST_NAME,
    data,
    callback,
});

