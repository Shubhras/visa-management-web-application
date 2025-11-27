import { call ,takeEvery} from "redux-saga/effects";
import {
    LEADS_B2C_LIST,
    ADD_LEADS_B2C,
    EDIT_LEADS_B2C,
    DELETE_LEADS_B2C,
    EXPORT_LEADS_B2C,
    IMPORT_LEADS_B2C,
} from "./actionType";
import {getLeadsB2CListAPI,
    addLeadsB2CDataAPI,
    editLeadsB2CDataAPI,
    deleteLeadsB2CDataAPI,
    exportLeadsB2CDataAPI,
    importLeadsB2CDataAPI} from "../../../service/api_all_pages_helper";

// --- LEADS B2C SAGAS ---
function* leadsB2CListSaga(action) {
    try {
        const response = yield call(getLeadsB2CListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* leadsB2CAddSaga(action) {
    try {
        const response = yield call(addLeadsB2CDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* leadsB2CEditSaga(action) {
    try {
        const response = yield call(editLeadsB2CDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* leadsB2CDeleteSaga(action) {
    try {
        const response = yield call(deleteLeadsB2CDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* leadsB2CExportDataSaga(action) {
    try {
        const response = yield call(exportLeadsB2CDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* leadsB2CImportDataSaga(action) {
    try {
        const response = yield call(importLeadsB2CDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
function* salesSaga() {
    yield takeEvery(LEADS_B2C_LIST, leadsB2CListSaga);
    yield takeEvery(ADD_LEADS_B2C, leadsB2CAddSaga);
    yield takeEvery(EDIT_LEADS_B2C, leadsB2CEditSaga);
    yield takeEvery(DELETE_LEADS_B2C, leadsB2CDeleteSaga);
    yield takeEvery(EXPORT_LEADS_B2C, leadsB2CExportDataSaga);
    yield takeEvery(IMPORT_LEADS_B2C, leadsB2CImportDataSaga);

}
export default salesSaga;
