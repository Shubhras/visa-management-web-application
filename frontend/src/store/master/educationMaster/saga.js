import { call, takeEvery } from "redux-saga/effects";
import {
    EDUCATION_LEVEL_CODE_LIST,
    ADD_EDUCATION_LEVEL_CODE,
    EDIT_EDUCATION_LEVEL_CODE,
    DELETE_EDUCATION_LEVEL_CODE,
    EXPORT_EDUCATION_LEVEL_CODE,
    IMPORT_EDUCATION_LEVEL_CODE,
    EDUCATION_LEVEL_LIST,
    ADD_EDUCATION_LEVEL,
    EDIT_EDUCATION_LEVEL,
    DELETE_EDUCATION_LEVEL,
    EXPORT_EDUCATION_LEVEL,
    IMPORT_EDUCATION_LEVEL,
    STUDY_MAIN_AREA_LIST,
    ADD_STUDY_MAIN_AREA,
    EDIT_STUDY_MAIN_AREA,
    DELETE_STUDY_MAIN_AREA,
    EXPORT_STUDY_MAIN_AREA,
    IMPORT_STUDY_MAIN_AREA,
} from "./actionType";

import {
    getEducationLevelCodeListDataAPI,
    addEducationLevelCodeDataAPI,
    editEducationLevelCodeDataAPI,
    deleteEducationLevelCodeDataAPI,
    exportEducationLevelCodeDataAPI,
    importEducationLevelCodeDataAPI,
    getEducationLevelListDataAPI,
    addEducationLevelDataAPI,
    editEducationLevelDataAPI,
    deleteEducationLevelDataAPI,
    exportEducationLevelDataAPI,
    importEducationLevelDataAPI,
    getStudyMainAreaListDataAPI,
    addStudyMainAreaDataAPI,
    editStudyMainAreaDataAPI,
    deleteStudyMainAreaDataAPI,
    exportStudyMainAreaDataAPI,
    importStudyMainAreaDataAPI,
} from "../../../service/api_helper";

// --- EDUCATION LEVEL CODE SAGAS ---
function* educationLevelCodeListSaga(action) {
    try {
        const response = yield call(getEducationLevelCodeListDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationLevelCodeAddSaga(action) {
    try {
        const response = yield call(addEducationLevelCodeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationLevelCodeEditSaga(action) {
    try {
        const response = yield call(editEducationLevelCodeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationLevelCodeDeleteSaga(action) {
    try {
        const response = yield call(deleteEducationLevelCodeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationLevelCodeExportDataSaga(action) {
    try {
        const response = yield call(exportEducationLevelCodeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationLevelCodeImportDataSaga(action) {
    try {
        const response = yield call(importEducationLevelCodeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

//Education Level
// Education Level
function* educationLevelListSaga(action) {
    try {
        const response = yield call(getEducationLevelListDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationLevelAddSaga(action) {
    try {
        const response = yield call(addEducationLevelDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationLevelEditSaga(action) {
    try {
        const response = yield call(editEducationLevelDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationLevelDeleteSaga(action) {
    try {
        const response = yield call(deleteEducationLevelDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationLevelExportDataSaga(action) {
    try {
        const response = yield call(exportEducationLevelDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationLevelImportDataSaga(action) {
    try {
        const response = yield call(importEducationLevelDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

//study main area
function* studyMainAreaListSaga(action) {
    try {
        const response = yield call(getStudyMainAreaListDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* studyMainAreaAddSaga(action) {
    try {
        const response = yield call(addStudyMainAreaDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* studyMainAreaEditSaga(action) {
    try {
        const response = yield call(editStudyMainAreaDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* studyMainAreaDeleteSaga(action) {
    try {
        const response = yield call(deleteStudyMainAreaDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* studyMainAreaExportDataSaga(action) {
    try {
        const response = yield call(exportStudyMainAreaDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* studyMainAreaImportDataSaga(action) {
    try {
        const response = yield call(importStudyMainAreaDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}



// --- ROOT SAGA ---
function* educationmasterSaga() {
    yield takeEvery(EDUCATION_LEVEL_CODE_LIST, educationLevelCodeListSaga);
    yield takeEvery(ADD_EDUCATION_LEVEL_CODE, educationLevelCodeAddSaga);
    yield takeEvery(EDIT_EDUCATION_LEVEL_CODE, educationLevelCodeEditSaga);
    yield takeEvery(DELETE_EDUCATION_LEVEL_CODE, educationLevelCodeDeleteSaga);
    yield takeEvery(EXPORT_EDUCATION_LEVEL_CODE, educationLevelCodeExportDataSaga);
    yield takeEvery(IMPORT_EDUCATION_LEVEL_CODE, educationLevelCodeImportDataSaga);
    yield takeEvery(EDUCATION_LEVEL_LIST, educationLevelListSaga);
    yield takeEvery(ADD_EDUCATION_LEVEL, educationLevelAddSaga);
    yield takeEvery(EDIT_EDUCATION_LEVEL, educationLevelEditSaga);
    yield takeEvery(DELETE_EDUCATION_LEVEL, educationLevelDeleteSaga);
    yield takeEvery(EXPORT_EDUCATION_LEVEL, educationLevelExportDataSaga);
    yield takeEvery(IMPORT_EDUCATION_LEVEL, educationLevelImportDataSaga);
    yield takeEvery(STUDY_MAIN_AREA_LIST, studyMainAreaListSaga);
    yield takeEvery(ADD_STUDY_MAIN_AREA, studyMainAreaAddSaga);
    yield takeEvery(EDIT_STUDY_MAIN_AREA, studyMainAreaEditSaga);
    yield takeEvery(DELETE_STUDY_MAIN_AREA, studyMainAreaDeleteSaga);
    yield takeEvery(EXPORT_STUDY_MAIN_AREA, studyMainAreaExportDataSaga);
    yield takeEvery(IMPORT_STUDY_MAIN_AREA, studyMainAreaImportDataSaga);
}

export default educationmasterSaga;
