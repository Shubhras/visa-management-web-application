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
    EDUCATION_DURATION_LIST,
    ADD_EDUCATION_DURATION,
    EDIT_EDUCATION_DURATION,
    DELETE_EDUCATION_DURATION,
    EXPORT_EDUCATION_DURATION,
    IMPORT_EDUCATION_DURATION,
    STUDY_MAJOR_AREA_LIST,
    ADD_STUDY_MAJOR_AREA,
    EDIT_STUDY_MAJOR_AREA,
    DELETE_STUDY_MAJOR_AREA,
    EXPORT_STUDY_MAJOR_AREA,
    IMPORT_STUDY_MAJOR_AREA,
    ACADEMIC_RESULT_TYPE_LIST,
    ADD_ACADEMIC_RESULT_TYPE,
    EDIT_ACADEMIC_RESULT_TYPE,
    DELETE_ACADEMIC_RESULT_TYPE,
    EXPORT_ACADEMIC_RESULT_TYPE,
    IMPORT_ACADEMIC_RESULT_TYPE,
    EDUCATION_TYPE_LIST,
    ADD_EDUCATION_TYPE,
    EDIT_EDUCATION_TYPE,
    DELETE_EDUCATION_TYPE,
    EXPORT_EDUCATION_TYPE,
    IMPORT_EDUCATION_TYPE,
    STUDY_SPECIALISATION_LIST,
    ADD_STUDY_SPECIALISATION,
    EDIT_STUDY_SPECIALISATION,
    DELETE_STUDY_SPECIALISATION,
    EXPORT_STUDY_SPECIALISATION,
    IMPORT_STUDY_SPECIALISATION,
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
    getEducationDurationListDataAPI,
    addEducationDurationDataAPI,
    editEducationDurationDataAPI,
    deleteEducationDurationDataAPI,
    exportEducationDurationDataAPI,
    importEducationDurationDataAPI,
    getStudyMajorAreaListDataAPI,
    addStudyMajorAreaDataAPI,
    editStudyMajorAreaDataAPI,
    deleteStudyMajorAreaDataAPI,
    exportStudyMajorAreaDataAPI,
    importStudyMajorAreaDataAPI,
    getAcademicResultTypeListDataAPI,
    addAcademicResultTypeDataAPI,
    editAcademicResultTypeDataAPI,
    deleteAcademicResultTypeDataAPI,
    exportAcademicResultTypeDataAPI,
    importAcademicResultTypeDataAPI,
    getEducationTypeListDataAPI,
    addEducationTypeDataAPI,
    editEducationTypeDataAPI,
    deleteEducationTypeDataAPI,
    exportEducationTypeDataAPI,
    importEducationTypeDataAPI,
    getStudySpecialisationListDataAPI,
    addStudySpecialisationDataAPI,
    editStudySpecialisationDataAPI,
    deleteStudySpecialisationDataAPI,
    exportStudySpecialisationDataAPI,
    importStudySpecialisationDataAPI,
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

//Study main area
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

// Education Duration
function* educationDurationListSaga(action) {
    try {
        const response = yield call(getEducationDurationListDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationDurationAddSaga(action) {
    try {
        const response = yield call(addEducationDurationDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationDurationEditSaga(action) {
    try {
        const response = yield call(editEducationDurationDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationDurationDeleteSaga(action) {
    try {
        const response = yield call(deleteEducationDurationDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationDurationExportDataSaga(action) {
    try {
        const response = yield call(exportEducationDurationDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationDurationImportDataSaga(action) {
    try {
        const response = yield call(importEducationDurationDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Study Major Area
function* studyMajorAreaListSaga(action) {
    try {
        const response = yield call(getStudyMajorAreaListDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* studyMajorAreaAddSaga(action) {
    try {
        const response = yield call(addStudyMajorAreaDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* studyMajorAreaEditSaga(action) {
    try {
        const response = yield call(editStudyMajorAreaDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* studyMajorAreaDeleteSaga(action) {
    try {
        const response = yield call(deleteStudyMajorAreaDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* studyMajorAreaExportDataSaga(action) {
    try {
        const response = yield call(exportStudyMajorAreaDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* studyMajorAreaImportDataSaga(action) {
    try {
        const response = yield call(importStudyMajorAreaDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Academic Result Type
function* academicResultTypeListSaga(action) {
    try {
        const response = yield call(getAcademicResultTypeListDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* academicResultTypeAddSaga(action) {
    try {
        const response = yield call(addAcademicResultTypeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* academicResultTypeEditSaga(action) {
    try {
        const response = yield call(editAcademicResultTypeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* academicResultTypeDeleteSaga(action) {
    try {
        const response = yield call(deleteAcademicResultTypeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* academicResultTypeExportDataSaga(action) {
    try {
        const response = yield call(exportAcademicResultTypeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* academicResultTypeImportDataSaga(action) {
    try {
        const response = yield call(importAcademicResultTypeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
//Education  Type
function* educationTypeListSaga(action) {
    try {
        const response = yield call(getEducationTypeListDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationTypeAddSaga(action) {
    try {
        const response = yield call(addEducationTypeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationTypeEditSaga(action) {
    try {
        const response = yield call(editEducationTypeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationTypeDeleteSaga(action) {
    try {
        const response = yield call(deleteEducationTypeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationTypeExportDataSaga(action) {
    try {
        const response = yield call(exportEducationTypeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* educationTypeImportDataSaga(action) {
    try {
        const response = yield call(importEducationTypeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

// Study Specialisation
function* studySpecialisationListSaga(action) {
    try {
        const response = yield call(getStudySpecialisationListDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* studySpecialisationAddSaga(action) {
    try {
        const response = yield call(addStudySpecialisationDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* studySpecialisationEditSaga(action) {
    try {
        const response = yield call(editStudySpecialisationDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* studySpecialisationDeleteSaga(action) {
    try {
        const response = yield call(deleteStudySpecialisationDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* studySpecialisationExportDataSaga(action) {
    try {
        const response = yield call(exportStudySpecialisationDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* studySpecialisationImportDataSaga(action) {
    try {
        const response = yield call(importStudySpecialisationDataAPI, action?.data);
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
    yield takeEvery(EDUCATION_DURATION_LIST, educationDurationListSaga);
    yield takeEvery(ADD_EDUCATION_DURATION, educationDurationAddSaga);
    yield takeEvery(EDIT_EDUCATION_DURATION, educationDurationEditSaga);
    yield takeEvery(DELETE_EDUCATION_DURATION, educationDurationDeleteSaga);
    yield takeEvery(EXPORT_EDUCATION_DURATION, educationDurationExportDataSaga);
    yield takeEvery(IMPORT_EDUCATION_DURATION, educationDurationImportDataSaga);
    yield takeEvery(STUDY_MAJOR_AREA_LIST, studyMajorAreaListSaga);
    yield takeEvery(ADD_STUDY_MAJOR_AREA, studyMajorAreaAddSaga);
    yield takeEvery(EDIT_STUDY_MAJOR_AREA, studyMajorAreaEditSaga);
    yield takeEvery(DELETE_STUDY_MAJOR_AREA, studyMajorAreaDeleteSaga);
    yield takeEvery(EXPORT_STUDY_MAJOR_AREA, studyMajorAreaExportDataSaga);
    yield takeEvery(IMPORT_STUDY_MAJOR_AREA, studyMajorAreaImportDataSaga);
    yield takeEvery(ACADEMIC_RESULT_TYPE_LIST, academicResultTypeListSaga);
    yield takeEvery(ADD_ACADEMIC_RESULT_TYPE, academicResultTypeAddSaga);
    yield takeEvery(EDIT_ACADEMIC_RESULT_TYPE, academicResultTypeEditSaga);
    yield takeEvery(DELETE_ACADEMIC_RESULT_TYPE, academicResultTypeDeleteSaga);
    yield takeEvery(EXPORT_ACADEMIC_RESULT_TYPE, academicResultTypeExportDataSaga);
    yield takeEvery(IMPORT_ACADEMIC_RESULT_TYPE, academicResultTypeImportDataSaga);
    yield takeEvery(EDUCATION_TYPE_LIST, educationTypeListSaga);
    yield takeEvery(ADD_EDUCATION_TYPE, educationTypeAddSaga);
    yield takeEvery(EDIT_EDUCATION_TYPE, educationTypeEditSaga);
    yield takeEvery(DELETE_EDUCATION_TYPE, educationTypeDeleteSaga);
    yield takeEvery(EXPORT_EDUCATION_TYPE, educationTypeExportDataSaga);
    yield takeEvery(IMPORT_EDUCATION_TYPE, educationTypeImportDataSaga);
    yield takeEvery(STUDY_SPECIALISATION_LIST, studySpecialisationListSaga);
    yield takeEvery(ADD_STUDY_SPECIALISATION, studySpecialisationAddSaga);
    yield takeEvery(EDIT_STUDY_SPECIALISATION, studySpecialisationEditSaga);
    yield takeEvery(DELETE_STUDY_SPECIALISATION, studySpecialisationDeleteSaga);
    yield takeEvery(EXPORT_STUDY_SPECIALISATION, studySpecialisationExportDataSaga);
    yield takeEvery(IMPORT_STUDY_SPECIALISATION, studySpecialisationImportDataSaga);



}

export default educationmasterSaga;
