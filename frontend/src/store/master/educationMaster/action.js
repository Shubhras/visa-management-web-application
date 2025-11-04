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

//Education level Code
export const educationLevelCodeList = (data, callback) => ({
    type: EDUCATION_LEVEL_CODE_LIST,
    data,
    callback,
});

export const educationLevelCodeAdd = (data, callback) => ({
    type: ADD_EDUCATION_LEVEL_CODE,
    data,
    callback,
});

export const educationLevelCodeEdit = (data, callback) => ({
    type: EDIT_EDUCATION_LEVEL_CODE,
    data,
    callback,
});

export const educationLevelCodeDelete = (data, callback) => ({
    type: DELETE_EDUCATION_LEVEL_CODE,
    data,
    callback,
});

export const educationLevelCodeExportData = (data, callback) => ({
    type: EXPORT_EDUCATION_LEVEL_CODE,
    data,
    callback,
});

export const educationLevelCodeImportData = (data, callback) => ({
    type: IMPORT_EDUCATION_LEVEL_CODE,
    data,
    callback,
});

// Education Level
export const educationLevelList = (data, callback) => ({
    type: EDUCATION_LEVEL_LIST,
    data,
    callback,
});

export const educationLevelAdd = (data, callback) => ({
    type: ADD_EDUCATION_LEVEL,
    data,
    callback,
});

export const educationLevelEdit = (data, callback) => ({
    type: EDIT_EDUCATION_LEVEL,
    data,
    callback,
});

export const educationLevelDelete = (data, callback) => ({
    type: DELETE_EDUCATION_LEVEL,
    data,
    callback,
});

export const educationLevelExportData = (data, callback) => ({
    type: EXPORT_EDUCATION_LEVEL,
    data,
    callback,
});
export const educationLevelImportData = (data, callback) => ({
    type: IMPORT_EDUCATION_LEVEL,
    data,
    callback,
});

//Study main area
export const studyMainAreaList = (data, callback) => ({
    type: STUDY_MAIN_AREA_LIST,
    data,
    callback,
});

export const studyMainAreaAdd = (data, callback) => ({
    type: ADD_STUDY_MAIN_AREA,
    data,
    callback,
});

export const studyMainAreaEdit = (data, callback) => ({
    type: EDIT_STUDY_MAIN_AREA,
    data,
    callback,
});

export const studyMainAreaDelete = (data, callback) => ({
    type: DELETE_STUDY_MAIN_AREA,
    data,
    callback,
});

export const studyMainAreaExportData = (data, callback) => ({
    type: EXPORT_STUDY_MAIN_AREA,
    data,
    callback,
});

export const studyMainAreaImportData = (data, callback) => ({
    type: IMPORT_STUDY_MAIN_AREA,
    data,
    callback,
});

