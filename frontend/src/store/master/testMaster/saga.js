import { call, takeEvery } from "redux-saga/effects";
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
import {
    getLanguageNameTestListAPI,
    addLanguageNameTestAPI,
    editLanguageNameTestAPI,
    deleteLanguageNameTestAPI,
    exportLanguageNameTestAPI,
    importLanguageNameTestAPI,
    getLanguageTestNameListAPI,
    addLanguageTestNameAPI,
    editLanguageTestNameAPI,
    deleteLanguageTestNameAPI,
    exportLanguageTestNameAPI,
    importLanguageTestNameAPI
} from "../../../service/api_helper";

// --- LANGUAGE NAME TEST SAGAS ---
function* languageNameTestListSaga(action) {
    try {
        const response = yield call(getLanguageNameTestListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageNameTestAddSaga(action) {
    try {
        const response = yield call(addLanguageNameTestAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageNameTestEditSaga(action) {
    try {
        const response = yield call(editLanguageNameTestAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageNameTestDeleteSaga(action) {
    try {
        const response = yield call(deleteLanguageNameTestAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageNameTestExportDataSaga(action) {
    try {
        const response = yield call(exportLanguageNameTestAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageNameTestImportDataSaga(action) {
    try {
        const response = yield call(importLanguageNameTestAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// --- LANGUAGE TEST NAME SAGAS ---
function* languageTestNameListSaga(action) {
    try {
        const response = yield call(getLanguageTestNameListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageTestNameAddSaga(action) {
    try {
        const response = yield call(addLanguageTestNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageTestNameEditSaga(action) {
    try {
        const response = yield call(editLanguageTestNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageTestNameDeleteSaga(action) {
    try {
        const response = yield call(deleteLanguageTestNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageTestNameExportDataSaga(action) {
    try {
        const response = yield call(exportLanguageTestNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageTestNameImportDataSaga(action) {
    try {
        const response = yield call(importLanguageTestNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}


function* testMasterSaga() {
    yield takeEvery(LANGUAGE_NAME_TEST_LIST, languageNameTestListSaga);
    yield takeEvery(ADD_LANGUAGE_NAME_TEST, languageNameTestAddSaga);
    yield takeEvery(EDIT_LANGUAGE_NAME_TEST, languageNameTestEditSaga);
    yield takeEvery(DELETE_LANGUAGE_NAME_TEST, languageNameTestDeleteSaga);
    yield takeEvery(EXPORT_LANGUAGE_NAME_TEST, languageNameTestExportDataSaga);
    yield takeEvery(IMPORT_LANGUAGE_NAME_TEST, languageNameTestImportDataSaga);
    yield takeEvery(LANGUAGE_TEST_NAME_LIST, languageTestNameListSaga);
    yield takeEvery(ADD_LANGUAGE_TEST_NAME, languageTestNameAddSaga);
    yield takeEvery(EDIT_LANGUAGE_TEST_NAME, languageTestNameEditSaga);
    yield takeEvery(DELETE_LANGUAGE_TEST_NAME, languageTestNameDeleteSaga);
    yield takeEvery(EXPORT_LANGUAGE_TEST_NAME, languageTestNameExportDataSaga);
    yield takeEvery(IMPORT_LANGUAGE_TEST_NAME, languageTestNameImportDataSaga);

}
export default testMasterSaga;
