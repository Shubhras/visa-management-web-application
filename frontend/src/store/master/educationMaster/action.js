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

// Education Duration
export const educationDurationList = (data, callback) => ({
    type: EDUCATION_DURATION_LIST,
    data,
    callback,
});

export const educationDurationAdd = (data, callback) => ({
    type: ADD_EDUCATION_DURATION,
    data,
    callback,
});

export const educationDurationEdit = (data, callback) => ({
    type: EDIT_EDUCATION_DURATION,
    data,
    callback,
});

export const educationDurationDelete = (data, callback) => ({
    type: DELETE_EDUCATION_DURATION,
    data,
    callback,
});

export const educationDurationExportData = (data, callback) => ({
    type: EXPORT_EDUCATION_DURATION,
    data,
    callback,
});

export const educationDurationImportData = (data, callback) => ({
    type: IMPORT_EDUCATION_DURATION,
    data,
    callback,
});

// Study Major Area
export const studyMajorAreaList = (data, callback) => ({
    type: STUDY_MAJOR_AREA_LIST,
    data,
    callback,
});

export const studyMajorAreaAdd = (data, callback) => ({
    type: ADD_STUDY_MAJOR_AREA,
    data,
    callback,
});

export const studyMajorAreaEdit = (data, callback) => ({
    type: EDIT_STUDY_MAJOR_AREA,
    data,
    callback,
});

export const studyMajorAreaDelete = (data, callback) => ({
    type: DELETE_STUDY_MAJOR_AREA,
    data,
    callback,
});

export const studyMajorAreaExportData = (data, callback) => ({
    type: EXPORT_STUDY_MAJOR_AREA,
    data,
    callback,
});

export const studyMajorAreaImportData = (data, callback) => ({
    type: IMPORT_STUDY_MAJOR_AREA,
    data,
    callback,
});
//Academic Result Type
export const academicResultTypeList = (data, callback) => ({
    type: ACADEMIC_RESULT_TYPE_LIST,
    data,
    callback,
});

export const academicResultTypeAdd = (data, callback) => ({
    type: ADD_ACADEMIC_RESULT_TYPE,
    data,
    callback,
});

export const academicResultTypeEdit = (data, callback) => ({
    type: EDIT_ACADEMIC_RESULT_TYPE,
    data,
    callback,
});

export const academicResultTypeDelete = (data, callback) => ({
    type: DELETE_ACADEMIC_RESULT_TYPE,
    data,
    callback,
});

export const academicResultTypeExportData = (data, callback) => ({
    type: EXPORT_ACADEMIC_RESULT_TYPE,
    data,
    callback,
});

export const academicResultTypeImportData = (data, callback) => ({
    type: IMPORT_ACADEMIC_RESULT_TYPE,
    data,
    callback,
});
// Education Type
export const educationTypeList = (data, callback) => ({
    type: EDUCATION_TYPE_LIST,
    data,
    callback,
});

export const educationTypeAdd = (data, callback) => ({
    type: ADD_EDUCATION_TYPE,
    data,
    callback,
});

export const educationTypeEdit = (data, callback) => ({
    type: EDIT_EDUCATION_TYPE,
    data,
    callback,
});

export const educationTypeDelete = (data, callback) => ({
    type: DELETE_EDUCATION_TYPE,
    data,
    callback,
});

export const educationTypeExportData = (data, callback) => ({
    type: EXPORT_EDUCATION_TYPE,
    data,
    callback,
});

export const educationTypeImportData = (data, callback) => ({
    type: IMPORT_EDUCATION_TYPE,
    data,
    callback,
});
// Study Specialisation
export const studySpecialisationList = (data, callback) => ({
  type: STUDY_SPECIALISATION_LIST,
  data,
  callback,
});

export const studySpecialisationAdd = (data, callback) => ({
  type: ADD_STUDY_SPECIALISATION,
  data,
  callback,
});

export const studySpecialisationEdit = (data, callback) => ({
  type: EDIT_STUDY_SPECIALISATION,
  data,
  callback,
});

export const studySpecialisationDelete = (data, callback) => ({
  type: DELETE_STUDY_SPECIALISATION,
  data,
  callback,
});

export const studySpecialisationExportData = (data, callback) => ({
  type: EXPORT_STUDY_SPECIALISATION,
  data,
  callback,
});

export const studySpecialisationImportData = (data, callback) => ({
  type: IMPORT_STUDY_SPECIALISATION,
  data,
  callback,
});





