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
    DEGREE_AWARDED_BY_LIST,
    ADD_DEGREE_AWARDED_BY,
    EDIT_DEGREE_AWARDED_BY,
    DELETE_DEGREE_AWARDED_BY,
    EXPORT_DEGREE_AWARDED_BY,
    IMPORT_DEGREE_AWARDED_BY,
    ACADEMIC_RESULT_LIST,
    ADD_ACADEMIC_RESULT,
    EDIT_ACADEMIC_RESULT,
    DELETE_ACADEMIC_RESULT,
    EXPORT_ACADEMIC_RESULT,
    IMPORT_ACADEMIC_RESULT,
    DEGREE_AWARDED_INSTITUTE_LIST,
    ADD_DEGREE_AWARDED_INSTITUTE,
    EDIT_DEGREE_AWARDED_INSTITUTE,
    DELETE_DEGREE_AWARDED_INSTITUTE,
    EXPORT_DEGREE_AWARDED_INSTITUTE,
    IMPORT_DEGREE_AWARDED_INSTITUTE,
    ACADEMIC_RESULT_TO_RESULT_LIST,
    ADD_ACADEMIC_RESULT_TO_RESULT,
    EDIT_ACADEMIC_RESULT_TO_RESULT,
    DELETE_ACADEMIC_RESULT_TO_RESULT,
    EXPORT_ACADEMIC_RESULT_TO_RESULT,
    IMPORT_ACADEMIC_RESULT_TO_RESULT,
    ECA_AWARDING_BODY_LIST,
    ADD_ECA_AWARDING_BODY,
    EDIT_ECA_AWARDING_BODY,
    DELETE_ECA_AWARDING_BODY,
    EXPORT_ECA_AWARDING_BODY,
    IMPORT_ECA_AWARDING_BODY,
    MEDIUM_OF_EDUCATION_LIST,
    ADD_MEDIUM_OF_EDUCATION,
    EDIT_MEDIUM_OF_EDUCATION,
    DELETE_MEDIUM_OF_EDUCATION,
    EXPORT_MEDIUM_OF_EDUCATION,
    IMPORT_MEDIUM_OF_EDUCATION
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
    getDegreeAwardedByListDataAPI,
    addDegreeAwardedByDataAPI,
    editDegreeAwardedByDataAPI,
    deleteDegreeAwardedByDataAPI,
    exportDegreeAwardedByDataAPI,
    importDegreeAwardedByDataAPI,
    getAcademicResultListDataAPI,
    addAcademicResultDataAPI,
    editAcademicResultDataAPI,
    deleteAcademicResultDataAPI,
    exportAcademicResultDataAPI,
    importAcademicResultDataAPI,
    getDegreeAwardedInstituteListDataAPI,
    addDegreeAwardedInstituteDataAPI,
    editDegreeAwardedInstituteDataAPI,
    deleteDegreeAwardedInstituteDataAPI,
    exportDegreeAwardedInstituteDataAPI,
    importDegreeAwardedInstituteDataAPI,
    getAcademicResultToResultListAPI,
    addAcademicResultToResultAPI,
    editAcademicResultToResultAPI,
    deleteAcademicResultToResultAPI,
    exportAcademicResultToResultAPI,
    importAcademicResultToResultAPI,
    getEcaAwardingBodyListAPI,
    addEcaAwardingBodyAPI,
    editEcaAwardingBodyAPI,
    deleteEcaAwardingBodyAPI,
    exportEcaAwardingBodyAPI,
    importEcaAwardingBodyAPI,
    getMediumOfEducationListAPI,
    addMediumOfEducationAPI,
    editMediumOfEducationAPI,
    deleteMediumOfEducationAPI,
    exportMediumOfEducationAPI,
    importMediumOfEducationAPI

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
// Degree Awarded By
function* degreeAwardedByListSaga(action) {
    try {
        const response = yield call(getDegreeAwardedByListDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* degreeAwardedByAddSaga(action) {
    try {
        const response = yield call(addDegreeAwardedByDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* degreeAwardedByEditSaga(action) {
    try {
        const response = yield call(editDegreeAwardedByDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* degreeAwardedByDeleteSaga(action) {
    try {
        const response = yield call(deleteDegreeAwardedByDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* degreeAwardedByExportDataSaga(action) {
    try {
        const response = yield call(exportDegreeAwardedByDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* degreeAwardedByImportDataSaga(action) {
    try {
        const response = yield call(importDegreeAwardedByDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Academic Result
function* academicResultListSaga(action) {
    try {
        const response = yield call(getAcademicResultListDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* academicResultAddSaga(action) {
    try {
        const response = yield call(addAcademicResultDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* academicResultEditSaga(action) {
    try {
        const response = yield call(editAcademicResultDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* academicResultDeleteSaga(action) {
    try {
        const response = yield call(deleteAcademicResultDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* academicResultExportDataSaga(action) {
    try {
        const response = yield call(exportAcademicResultDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* academicResultImportDataSaga(action) {
    try {
        const response = yield call(importAcademicResultDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Degree Awarded Institute
function* degreeAwardedInstituteListSaga(action) {
    try {
        const response = yield call(getDegreeAwardedInstituteListDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* degreeAwardedInstituteAddSaga(action) {
    try {
        const response = yield call(addDegreeAwardedInstituteDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* degreeAwardedInstituteEditSaga(action) {
    try {
        const response = yield call(editDegreeAwardedInstituteDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* degreeAwardedInstituteDeleteSaga(action) {
    try {
        const response = yield call(deleteDegreeAwardedInstituteDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* degreeAwardedInstituteExportDataSaga(action) {
    try {
        const response = yield call(exportDegreeAwardedInstituteDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* degreeAwardedInstituteImportDataSaga(action) {
    try {
        const response = yield call(importDegreeAwardedInstituteDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Academic Result To Result (Compare Mapping)
function* academicResultToResultListSaga(action) {
    try {
        const response = yield call(getAcademicResultToResultListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* academicResultToResultAddSaga(action) {
    try {
        const response = yield call(addAcademicResultToResultAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* academicResultToResultEditSaga(action) {
    try {
        const response = yield call(editAcademicResultToResultAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* academicResultToResultDeleteSaga(action) {
    try {
        const response = yield call(deleteAcademicResultToResultAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* academicResultToResultExportDataSaga(action) {
    try {
        const response = yield call(exportAcademicResultToResultAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* academicResultToResultImportDataSaga(action) {
    try {
        const response = yield call(importAcademicResultToResultAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// ECA Awarding Body 
function* ecaAwardingBodyListSaga(action) {
    try {
        const response = yield call(getEcaAwardingBodyListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* ecaAwardingBodyAddSaga(action) {
    try {
        const response = yield call(addEcaAwardingBodyAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* ecaAwardingBodyEditSaga(action) {
    try {
        const response = yield call(editEcaAwardingBodyAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* ecaAwardingBodyDeleteSaga(action) {
    try {
        const response = yield call(deleteEcaAwardingBodyAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* ecaAwardingBodyExportDataSaga(action) {
    try {
        const response = yield call(exportEcaAwardingBodyAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* ecaAwardingBodyImportDataSaga(action) {
    try {
        const response = yield call(importEcaAwardingBodyAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Medium of Education
function* mediumOfEducationListSaga(action) {
    try {
        const response = yield call(getMediumOfEducationListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* mediumOfEducationAddSaga(action) {
    try {
        const response = yield call(addMediumOfEducationAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* mediumOfEducationEditSaga(action) {
    try {
        const response = yield call(editMediumOfEducationAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* mediumOfEducationDeleteSaga(action) {
    try {
        const response = yield call(deleteMediumOfEducationAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* mediumOfEducationExportDataSaga(action) {
    try {
        const response = yield call(exportMediumOfEducationAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* mediumOfEducationImportDataSaga(action) {
    try {
        const response = yield call(importMediumOfEducationAPI, action?.data);
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
    yield takeEvery(DEGREE_AWARDED_BY_LIST, degreeAwardedByListSaga);
    yield takeEvery(ADD_DEGREE_AWARDED_BY, degreeAwardedByAddSaga);
    yield takeEvery(EDIT_DEGREE_AWARDED_BY, degreeAwardedByEditSaga);
    yield takeEvery(DELETE_DEGREE_AWARDED_BY, degreeAwardedByDeleteSaga);
    yield takeEvery(EXPORT_DEGREE_AWARDED_BY, degreeAwardedByExportDataSaga);
    yield takeEvery(IMPORT_DEGREE_AWARDED_BY, degreeAwardedByImportDataSaga);
    yield takeEvery(ACADEMIC_RESULT_LIST, academicResultListSaga);
    yield takeEvery(ADD_ACADEMIC_RESULT, academicResultAddSaga);
    yield takeEvery(EDIT_ACADEMIC_RESULT, academicResultEditSaga);
    yield takeEvery(DELETE_ACADEMIC_RESULT, academicResultDeleteSaga);
    yield takeEvery(EXPORT_ACADEMIC_RESULT, academicResultExportDataSaga);
    yield takeEvery(IMPORT_ACADEMIC_RESULT, academicResultImportDataSaga);
    yield takeEvery(DEGREE_AWARDED_INSTITUTE_LIST, degreeAwardedInstituteListSaga);
    yield takeEvery(ADD_DEGREE_AWARDED_INSTITUTE, degreeAwardedInstituteAddSaga);
    yield takeEvery(EDIT_DEGREE_AWARDED_INSTITUTE, degreeAwardedInstituteEditSaga);
    yield takeEvery(DELETE_DEGREE_AWARDED_INSTITUTE, degreeAwardedInstituteDeleteSaga);
    yield takeEvery(EXPORT_DEGREE_AWARDED_INSTITUTE, degreeAwardedInstituteExportDataSaga);
    yield takeEvery(IMPORT_DEGREE_AWARDED_INSTITUTE, degreeAwardedInstituteImportDataSaga);
    yield takeEvery(ACADEMIC_RESULT_TO_RESULT_LIST, academicResultToResultListSaga);
    yield takeEvery(ADD_ACADEMIC_RESULT_TO_RESULT, academicResultToResultAddSaga);
    yield takeEvery(EDIT_ACADEMIC_RESULT_TO_RESULT, academicResultToResultEditSaga);
    yield takeEvery(DELETE_ACADEMIC_RESULT_TO_RESULT, academicResultToResultDeleteSaga);
    yield takeEvery(EXPORT_ACADEMIC_RESULT_TO_RESULT, academicResultToResultExportDataSaga);
    yield takeEvery(IMPORT_ACADEMIC_RESULT_TO_RESULT, academicResultToResultImportDataSaga);
    yield takeEvery(ECA_AWARDING_BODY_LIST, ecaAwardingBodyListSaga);
    yield takeEvery(ADD_ECA_AWARDING_BODY, ecaAwardingBodyAddSaga);
    yield takeEvery(EDIT_ECA_AWARDING_BODY, ecaAwardingBodyEditSaga);
    yield takeEvery(DELETE_ECA_AWARDING_BODY, ecaAwardingBodyDeleteSaga);
    yield takeEvery(EXPORT_ECA_AWARDING_BODY, ecaAwardingBodyExportDataSaga);
    yield takeEvery(IMPORT_ECA_AWARDING_BODY, ecaAwardingBodyImportDataSaga);
    yield takeEvery(MEDIUM_OF_EDUCATION_LIST, mediumOfEducationListSaga);
    yield takeEvery(ADD_MEDIUM_OF_EDUCATION, mediumOfEducationAddSaga);
    yield takeEvery(EDIT_MEDIUM_OF_EDUCATION, mediumOfEducationEditSaga);
    yield takeEvery(DELETE_MEDIUM_OF_EDUCATION, mediumOfEducationDeleteSaga);
    yield takeEvery(EXPORT_MEDIUM_OF_EDUCATION, mediumOfEducationExportDataSaga);
    yield takeEvery(IMPORT_MEDIUM_OF_EDUCATION, mediumOfEducationImportDataSaga);



}

export default educationmasterSaga;
