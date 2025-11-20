import { call, takeEvery } from "redux-saga/effects";
import {
    REPRESENTING_COUNTRY_LIST,
    ADD_REPRESENTING_COUNTRY,
    EDIT_REPRESENTING_COUNTRY,
    DELETE_REPRESENTING_COUNTRY,
    EXPORT_REPRESENTING_COUNTRY,
    IMPORT_REPRESENTING_COUNTRY
} from "./actionType";

import {
    getRepresentingCountryListAPI,
    addRepresentingCountryAPI,
    editRepresentingCountryAPI,
    deleteRepresentingCountryAPI,
    exportRepresentingCountryAPI,
    importRepresentingCountryAPI
} from "../../../service/api_helper";

// --- Representing Country SAGAS ---
function* representingCountryListSaga(action) {
    try {
        const response = yield call(getRepresentingCountryListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* representingCountryAddSaga(action) {
    try {
        const response = yield call(addRepresentingCountryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* representingCountryEditSaga(action) {
    try {
        const response = yield call(editRepresentingCountryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* representingCountryDeleteSaga(action) {
    try {
        const response = yield call(deleteRepresentingCountryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* representingCountryExportDataSaga(action) {
    try {
        const response = yield call(exportRepresentingCountryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* representingCountryImportDataSaga(action) {
    try {
        const response = yield call(importRepresentingCountryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaMasterSaga() {

    yield takeEvery(REPRESENTING_COUNTRY_LIST, representingCountryListSaga);
    yield takeEvery(ADD_REPRESENTING_COUNTRY, representingCountryAddSaga);
    yield takeEvery(EDIT_REPRESENTING_COUNTRY, representingCountryEditSaga);
    yield takeEvery(DELETE_REPRESENTING_COUNTRY, representingCountryDeleteSaga);
    yield takeEvery(EXPORT_REPRESENTING_COUNTRY, representingCountryExportDataSaga);
    yield takeEvery(IMPORT_REPRESENTING_COUNTRY, representingCountryImportDataSaga);




}
export default visaMasterSaga;