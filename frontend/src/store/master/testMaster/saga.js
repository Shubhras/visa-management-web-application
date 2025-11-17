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
    LANGUAGE_TEST_MODULE_NAME_LIST,
    ADD_LANGUAGE_TEST_MODULE_NAME,
    EDIT_LANGUAGE_TEST_MODULE_NAME,
    DELETE_LANGUAGE_TEST_MODULE_NAME,
    EXPORT_LANGUAGE_TEST_MODULE_NAME,
    IMPORT_LANGUAGE_TEST_MODULE_NAME,
    LANGUAGE_BENCHMARK_LEVEL_LIST,
    ADD_LANGUAGE_BENCHMARK_LEVEL,
    EDIT_LANGUAGE_BENCHMARK_LEVEL,
    DELETE_LANGUAGE_BENCHMARK_LEVEL,
    EXPORT_LANGUAGE_BENCHMARK_LEVEL,
    IMPORT_LANGUAGE_BENCHMARK_LEVEL,
    CLB_LEVEL_LIST,
    ADD_CLB_LEVEL,
    EDIT_CLB_LEVEL,
    DELETE_CLB_LEVEL,
    EXPORT_CLB_LEVEL,
    IMPORT_CLB_LEVEL,
    ENTRANCE_TEST_NAME_LIST,
    ADD_ENTRANCE_TEST_NAME,
    EDIT_ENTRANCE_TEST_NAME,
    DELETE_ENTRANCE_TEST_NAME,
    EXPORT_ENTRANCE_TEST_NAME,
    IMPORT_ENTRANCE_TEST_NAME,
    ENTRANCE_TEST_MODULE_NAME_LIST,
    ADD_ENTRANCE_TEST_MODULE_NAME,
    EDIT_ENTRANCE_TEST_MODULE_NAME,
    DELETE_ENTRANCE_TEST_MODULE_NAME,
    EXPORT_ENTRANCE_TEST_MODULE_NAME,
    IMPORT_ENTRANCE_TEST_MODULE_NAME,
    ENTRANCE_TEST_RESULT_LIST,
    ADD_ENTRANCE_TEST_RESULT,
    EDIT_ENTRANCE_TEST_RESULT,
    DELETE_ENTRANCE_TEST_RESULT,
    EXPORT_ENTRANCE_TEST_RESULT,
    IMPORT_ENTRANCE_TEST_RESULT,
    LANGUAGE_TEST_RESULT_LIST,
    ADD_LANGUAGE_TEST_RESULT,
    EDIT_LANGUAGE_TEST_RESULT,
    DELETE_LANGUAGE_TEST_RESULT,
    EXPORT_LANGUAGE_TEST_RESULT,
    IMPORT_LANGUAGE_TEST_RESULT,
    ENTRANCE_TEST_ID_MODULE_LIST,
    Language_NAME_TEST_ID,
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
    importLanguageTestNameAPI,
    getLanguageTestModuleNameListAPI,
    addLanguageTestModuleNameAPI,
    editLanguageTestModuleNameAPI,
    deleteLanguageTestModuleNameAPI,
    exportLanguageTestModuleNameAPI,
    importLanguageTestModuleNameAPI,
    getLanguageBenchmarkLevelListAPI,
    addLanguageBenchmarkLevelAPI,
    editLanguageBenchmarkLevelAPI,
    deleteLanguageBenchmarkLevelAPI,
    exportLanguageBenchmarkLevelAPI,
    importLanguageBenchmarkLevelAPI,
    getClbLevelListAPI,
    addClbLevelAPI,
    editClbLevelAPI,
    deleteClbLevelAPI,
    exportClbLevelAPI,
    importClbLevelAPI,
    getEntranceTestNameListAPI,
    addEntranceTestNameAPI,
    editEntranceTestNameAPI,
    deleteEntranceTestNameAPI,
    exportEntranceTestNameAPI,
    importEntranceTestNameAPI,
    getEntranceTestModuleNameListAPI,
    addEntranceTestModuleNameAPI,
    editEntranceTestModuleNameAPI,
    deleteEntranceTestModuleNameAPI,
    exportEntranceTestModuleNameAPI,
    importEntranceTestModuleNameAPI,
    getEntranceTestResultListAPI,
    addEntranceTestResultAPI,
    editEntranceTestResultAPI,
    deleteEntranceTestResultAPI,
    exportEntranceTestResultAPI,
    importEntranceTestResultAPI,
    getLanguageTestResultListAPI,
    addLanguageTestResultAPI,
    editLanguageTestResultAPI,
    deleteLanguageTestResultAPI,
    exportLanguageTestResultAPI,
    importLanguageTestResultAPI,
    getEntranceTestIdModuleListAPI,
    getLanguageNameTestIDAPI,
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
// --- LANGUAGE TEST MODULE NAME SAGAS ---
function* languageTestModuleNameListSaga(action) {
    try {
        const response = yield call(getLanguageTestModuleNameListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageTestModuleNameAddSaga(action) {
    try {
        const response = yield call(addLanguageTestModuleNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageTestModuleNameEditSaga(action) {
    try {
        const response = yield call(editLanguageTestModuleNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageTestModuleNameDeleteSaga(action) {
    try {
        const response = yield call(deleteLanguageTestModuleNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageTestModuleNameExportDataSaga(action) {
    try {
        const response = yield call(exportLanguageTestModuleNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageTestModuleNameImportDataSaga(action) {
    try {
        const response = yield call(importLanguageTestModuleNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Language Benchmark Level
function* languageBenchmarkLevelListSaga(action) {
    try {
        const response = yield call(getLanguageBenchmarkLevelListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageBenchmarkLevelAddSaga(action) {
    try {
        const response = yield call(addLanguageBenchmarkLevelAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageBenchmarkLevelEditSaga(action) {
    try {
        const response = yield call(editLanguageBenchmarkLevelAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageBenchmarkLevelDeleteSaga(action) {
    try {
        const response = yield call(deleteLanguageBenchmarkLevelAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageBenchmarkLevelExportDataSaga(action) {
    try {
        const response = yield call(exportLanguageBenchmarkLevelAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* languageBenchmarkLevelImportDataSaga(action) {
    try {
        const response = yield call(importLanguageBenchmarkLevelAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

// CLB Level
function* clbLevelListSaga(action) {
    try {
        const response = yield call(getClbLevelListAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* clbLevelAddSaga(action) {
    try {
        const response = yield call(addClbLevelAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* clbLevelEditSaga(action) {
    try {
        const response = yield call(editClbLevelAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* clbLevelDeleteSaga(action) {
    try {
        const response = yield call(deleteClbLevelAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* clbLevelExportDataSaga(action) {
    try {
        const response = yield call(exportClbLevelAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* clbLevelImportDataSaga(action) {
    try {
        const response = yield call(importClbLevelAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}
// Entrance Test Name
function* entranceTestNameListSaga(action) {
    try {
        const response = yield call(getEntranceTestNameListAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* entranceTestNameAddSaga(action) {
    try {
        const response = yield call(addEntranceTestNameAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* entranceTestNameEditSaga(action) {
    try {
        const response = yield call(editEntranceTestNameAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* entranceTestNameDeleteSaga(action) {
    try {
        const response = yield call(deleteEntranceTestNameAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* entranceTestNameExportDataSaga(action) {
    try {
        const response = yield call(exportEntranceTestNameAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* entranceTestNameImportDataSaga(action) {
    try {
        const response = yield call(importEntranceTestNameAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

// Entrance Test Module Name
function* entranceTestModuleNameListSaga(action) {
    try {
        const response = yield call(getEntranceTestModuleNameListAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* entranceTestModuleNameAddSaga(action) {
    try {
        const response = yield call(addEntranceTestModuleNameAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* entranceTestModuleNameEditSaga(action) {
    try {
        const response = yield call(editEntranceTestModuleNameAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* entranceTestModuleNameDeleteSaga(action) {
    try {
        const response = yield call(deleteEntranceTestModuleNameAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* entranceTestModuleNameExportDataSaga(action) {
    try {
        const response = yield call(exportEntranceTestModuleNameAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* entranceTestModuleNameImportDataSaga(action) {
    try {
        const response = yield call(importEntranceTestModuleNameAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

// Entrance Test Result
function* entranceTestResultListSaga(action) {
    try {
        const response = yield call(getEntranceTestResultListAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* entranceTestResultAddSaga(action) {
    try {
        const response = yield call(addEntranceTestResultAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* entranceTestResultEditSaga(action) {
    try {
        const response = yield call(editEntranceTestResultAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* entranceTestResultDeleteSaga(action) {
    try {
        const response = yield call(deleteEntranceTestResultAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* entranceTestResultExportDataSaga(action) {
    try {
        const response = yield call(exportEntranceTestResultAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* entranceTestResultImportDataSaga(action) {
    try {
        const response = yield call(importEntranceTestResultAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}
function* entranceTestIdModuleSaga(action) {
    try {
        const response = yield call(getEntranceTestIdModuleListAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

// Language Test Result
function* languageTestResultListSaga(action) {
    try {
        const response = yield call(getLanguageTestResultListAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* languageTestResultAddSaga(action) {
    try {
        const response = yield call(addLanguageTestResultAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* languageTestResultEditSaga(action) {
    try {
        const response = yield call(editLanguageTestResultAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* languageTestResultDeleteSaga(action) {
    try {
        const response = yield call(deleteLanguageTestResultAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* languageTestResultExportDataSaga(action) {
    try {
        const response = yield call(exportLanguageTestResultAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* languageTestResultImportDataSaga(action) {
    try {
        const response = yield call(importLanguageTestResultAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}
function* languageNameTestIDSaga(action) {
    try {
        const response = yield call(getLanguageNameTestIDAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
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
    yield takeEvery(LANGUAGE_TEST_MODULE_NAME_LIST, languageTestModuleNameListSaga);
    yield takeEvery(ADD_LANGUAGE_TEST_MODULE_NAME, languageTestModuleNameAddSaga);
    yield takeEvery(EDIT_LANGUAGE_TEST_MODULE_NAME, languageTestModuleNameEditSaga);
    yield takeEvery(DELETE_LANGUAGE_TEST_MODULE_NAME, languageTestModuleNameDeleteSaga);
    yield takeEvery(EXPORT_LANGUAGE_TEST_MODULE_NAME, languageTestModuleNameExportDataSaga);
    yield takeEvery(IMPORT_LANGUAGE_TEST_MODULE_NAME, languageTestModuleNameImportDataSaga);
    yield takeEvery(LANGUAGE_BENCHMARK_LEVEL_LIST, languageBenchmarkLevelListSaga);
    yield takeEvery(ADD_LANGUAGE_BENCHMARK_LEVEL, languageBenchmarkLevelAddSaga);
    yield takeEvery(EDIT_LANGUAGE_BENCHMARK_LEVEL, languageBenchmarkLevelEditSaga);
    yield takeEvery(DELETE_LANGUAGE_BENCHMARK_LEVEL, languageBenchmarkLevelDeleteSaga);
    yield takeEvery(EXPORT_LANGUAGE_BENCHMARK_LEVEL, languageBenchmarkLevelExportDataSaga);
    yield takeEvery(IMPORT_LANGUAGE_BENCHMARK_LEVEL, languageBenchmarkLevelImportDataSaga);
    yield takeEvery(CLB_LEVEL_LIST, clbLevelListSaga);
    yield takeEvery(ADD_CLB_LEVEL, clbLevelAddSaga);
    yield takeEvery(EDIT_CLB_LEVEL, clbLevelEditSaga);
    yield takeEvery(DELETE_CLB_LEVEL, clbLevelDeleteSaga);
    yield takeEvery(EXPORT_CLB_LEVEL, clbLevelExportDataSaga);
    yield takeEvery(IMPORT_CLB_LEVEL, clbLevelImportDataSaga);
    yield takeEvery(ENTRANCE_TEST_NAME_LIST, entranceTestNameListSaga);
    yield takeEvery(ADD_ENTRANCE_TEST_NAME, entranceTestNameAddSaga);
    yield takeEvery(EDIT_ENTRANCE_TEST_NAME, entranceTestNameEditSaga);
    yield takeEvery(DELETE_ENTRANCE_TEST_NAME, entranceTestNameDeleteSaga);
    yield takeEvery(EXPORT_ENTRANCE_TEST_NAME, entranceTestNameExportDataSaga);
    yield takeEvery(IMPORT_ENTRANCE_TEST_NAME, entranceTestNameImportDataSaga);
    yield takeEvery(ENTRANCE_TEST_MODULE_NAME_LIST, entranceTestModuleNameListSaga);
    yield takeEvery(ADD_ENTRANCE_TEST_MODULE_NAME, entranceTestModuleNameAddSaga);
    yield takeEvery(EDIT_ENTRANCE_TEST_MODULE_NAME, entranceTestModuleNameEditSaga);
    yield takeEvery(DELETE_ENTRANCE_TEST_MODULE_NAME, entranceTestModuleNameDeleteSaga);
    yield takeEvery(EXPORT_ENTRANCE_TEST_MODULE_NAME, entranceTestModuleNameExportDataSaga);
    yield takeEvery(IMPORT_ENTRANCE_TEST_MODULE_NAME, entranceTestModuleNameImportDataSaga);
    yield takeEvery(ENTRANCE_TEST_RESULT_LIST, entranceTestResultListSaga);
    yield takeEvery(ADD_ENTRANCE_TEST_RESULT, entranceTestResultAddSaga);
    yield takeEvery(EDIT_ENTRANCE_TEST_RESULT, entranceTestResultEditSaga);
    yield takeEvery(DELETE_ENTRANCE_TEST_RESULT, entranceTestResultDeleteSaga);
    yield takeEvery(EXPORT_ENTRANCE_TEST_RESULT, entranceTestResultExportDataSaga);
    yield takeEvery(IMPORT_ENTRANCE_TEST_RESULT, entranceTestResultImportDataSaga);
    yield takeEvery(LANGUAGE_TEST_RESULT_LIST, languageTestResultListSaga);
    yield takeEvery(ADD_LANGUAGE_TEST_RESULT, languageTestResultAddSaga);
    yield takeEvery(EDIT_LANGUAGE_TEST_RESULT, languageTestResultEditSaga);
    yield takeEvery(DELETE_LANGUAGE_TEST_RESULT, languageTestResultDeleteSaga);
    yield takeEvery(EXPORT_LANGUAGE_TEST_RESULT, languageTestResultExportDataSaga);
    yield takeEvery(IMPORT_LANGUAGE_TEST_RESULT, languageTestResultImportDataSaga);
    yield takeEvery(ENTRANCE_TEST_ID_MODULE_LIST, entranceTestIdModuleSaga);
    yield takeEvery(Language_NAME_TEST_ID,languageNameTestIDSaga);






}
export default testMasterSaga;
