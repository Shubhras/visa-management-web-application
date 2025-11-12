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
// Language Test Module Name
export const languageTestModuleNameList = (data, callback) => ({
    type: LANGUAGE_TEST_MODULE_NAME_LIST,
    data,
    callback,
});

export const languageTestModuleNameAdd = (data, callback) => ({
    type: ADD_LANGUAGE_TEST_MODULE_NAME,
    data,
    callback,
});

export const languageTestModuleNameEdit = (data, callback) => ({
    type: EDIT_LANGUAGE_TEST_MODULE_NAME,
    data,
    callback,
});

export const languageTestModuleNameDelete = (data, callback) => ({
    type: DELETE_LANGUAGE_TEST_MODULE_NAME,
    data,
    callback,
});

export const languageTestModuleNameExportData = (data, callback) => ({
    type: EXPORT_LANGUAGE_TEST_MODULE_NAME,
    data,
    callback,
});

export const languageTestModuleNameImportData = (data, callback) => ({
    type: IMPORT_LANGUAGE_TEST_MODULE_NAME,
    data,
    callback,
});
// Language Benchmark Level
export const languageBenchmarkLevelList = (data, callback) => ({
    type: LANGUAGE_BENCHMARK_LEVEL_LIST,
    data,
    callback,
});

export const languageBenchmarkLevelAdd = (data, callback) => ({
    type: ADD_LANGUAGE_BENCHMARK_LEVEL,
    data,
    callback,
});

export const languageBenchmarkLevelEdit = (data, callback) => ({
    type: EDIT_LANGUAGE_BENCHMARK_LEVEL,
    data,
    callback,
});

export const languageBenchmarkLevelDelete = (data, callback) => ({
    type: DELETE_LANGUAGE_BENCHMARK_LEVEL,
    data,
    callback,
});

export const languageBenchmarkLevelExportData = (data, callback) => ({
    type: EXPORT_LANGUAGE_BENCHMARK_LEVEL,
    data,
    callback,
});

export const languageBenchmarkLevelImportData = (data, callback) => ({
    type: IMPORT_LANGUAGE_BENCHMARK_LEVEL,
    data,
    callback,
});
// CLB Level
export const clbLevelList = (data, callback) => ({
    type: CLB_LEVEL_LIST,
    data,
    callback,
});

export const clbLevelAdd = (data, callback) => ({
    type: ADD_CLB_LEVEL,
    data,
    callback,
});

export const clbLevelEdit = (data, callback) => ({
    type: EDIT_CLB_LEVEL,
    data,
    callback,
});

export const clbLevelDelete = (data, callback) => ({
    type: DELETE_CLB_LEVEL,
    data,
    callback,
});

export const clbLevelExportData = (data, callback) => ({
    type: EXPORT_CLB_LEVEL,
    data,
    callback,
});

export const clbLevelImportData = (data, callback) => ({
    type: IMPORT_CLB_LEVEL,
    data,
    callback,
});
// Entrance Test Name
export const entranceTestNameList = (data, callback) => ({
    type: ENTRANCE_TEST_NAME_LIST,
    data,
    callback,
});

export const entranceTestNameAdd = (data, callback) => ({
    type: ADD_ENTRANCE_TEST_NAME,
    data,
    callback,
});

export const entranceTestNameEdit = (data, callback) => ({
    type: EDIT_ENTRANCE_TEST_NAME,
    data,
    callback,
});

export const entranceTestNameDelete = (data, callback) => ({
    type: DELETE_ENTRANCE_TEST_NAME,
    data,
    callback,
});

export const entranceTestNameExportData = (data, callback) => ({
    type: EXPORT_ENTRANCE_TEST_NAME,
    data,
    callback,
});

export const entranceTestNameImportData = (data, callback) => ({
    type: IMPORT_ENTRANCE_TEST_NAME,
    data,
    callback,
});
// Entrance Test Module Name
export const entranceTestModuleNameList = (data, callback) => ({
    type: ENTRANCE_TEST_MODULE_NAME_LIST,
    data,
    callback,
});

export const entranceTestModuleNameAdd = (data, callback) => ({
    type: ADD_ENTRANCE_TEST_MODULE_NAME,
    data,
    callback,
});

export const entranceTestModuleNameEdit = (data, callback) => ({
    type: EDIT_ENTRANCE_TEST_MODULE_NAME,
    data,
    callback,
});

export const entranceTestModuleNameDelete = (data, callback) => ({
    type: DELETE_ENTRANCE_TEST_MODULE_NAME,
    data,
    callback,
});

export const entranceTestModuleNameExportData = (data, callback) => ({
    type: EXPORT_ENTRANCE_TEST_MODULE_NAME,
    data,
    callback,
});

export const entranceTestModuleNameImportData = (data, callback) => ({
    type: IMPORT_ENTRANCE_TEST_MODULE_NAME,
    data,
    callback,
});

// Entrance Test Result
export const entranceTestResultList = (data, callback) => ({
    type: ENTRANCE_TEST_RESULT_LIST,
    data,
    callback,
});

export const entranceTestResultAdd = (data, callback) => ({
    type: ADD_ENTRANCE_TEST_RESULT,
    data,
    callback,
});

export const entranceTestResultEdit = (data, callback) => ({
    type: EDIT_ENTRANCE_TEST_RESULT,
    data,
    callback,
});

export const entranceTestResultDelete = (data, callback) => ({
    type: DELETE_ENTRANCE_TEST_RESULT,
    data,
    callback,
});

export const entranceTestResultExportData = (data, callback) => ({
    type: EXPORT_ENTRANCE_TEST_RESULT,
    data,
    callback,
});

export const entranceTestResultImportData = (data, callback) => ({
    type: IMPORT_ENTRANCE_TEST_RESULT,
    data,
    callback,
});

// Language Test Result
export const languageTestResultList = (data, callback) => ({
    type: LANGUAGE_TEST_RESULT_LIST,
    data,
    callback,
});

export const languageTestResultAdd = (data, callback) => ({
    type: ADD_LANGUAGE_TEST_RESULT,
    data,
    callback,
});

export const languageTestResultEdit = (data, callback) => ({
    type: EDIT_LANGUAGE_TEST_RESULT,
    data,
    callback,
});

export const languageTestResultDelete = (data, callback) => ({
    type: DELETE_LANGUAGE_TEST_RESULT,
    data,
    callback,
});

export const languageTestResultExportData = (data, callback) => ({
    type: EXPORT_LANGUAGE_TEST_RESULT,
    data,
    callback,
});

export const languageTestResultImportData = (data, callback) => ({
    type: IMPORT_LANGUAGE_TEST_RESULT,
    data,
    callback,
});








