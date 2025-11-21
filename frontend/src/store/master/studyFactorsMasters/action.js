import {
    ACADEMIC_RESULT_GROUP_LIST,
    ADD_ACADEMIC_RESULT_GROUP,
  ADD_AGE,
  ADD_AGE_GROUP,
  ADD_BACKLOGS_GROUP,
  ADD_ENTRANCE_TEST_ABILITY_GROUP,
  ADD_FACTOR_FOR,
  ADD_GAP_GROUP,
  ADD_LANGUAGE_ABILITY_GROUP,
  AGE_GROUP_LIST,
  AGE_LIST,
  BACKLOGS_GROUP_LIST,
  DELETE_ACADEMIC_RESULT_GROUP,
  DELETE_AGE,
  DELETE_AGE_GROUP,
  DELETE_BACKLOGS_GROUP,
  DELETE_ENTRANCE_TEST_ABILITY_GROUP,
  DELETE_FACTOR_FOR,
  DELETE_GAP_GROUP,
  DELETE_LANGUAGE_ABILITY_GROUP,
  EDIT_ACADEMIC_RESULT_GROUP,
  EDIT_AGE,
  EDIT_AGE_GROUP,
  EDIT_BACKLOGS_GROUP,
  EDIT_ENTRANCE_TEST_ABILITY_GROUP,
  EDIT_FACTOR_FOR,
  EDIT_GAP_GROUP,
  EDIT_LANGUAGE_ABILITY_GROUP,
  ENTRANCE_TEST_ABILITY_GROUP_LIST,
  EXPORT_ACADEMIC_RESULT_GROUP,
  EXPORT_AGE,
  EXPORT_AGE_GROUP,
  EXPORT_BACKLOGS_GROUP,
  EXPORT_ENTRANCE_TEST_ABILITY_GROUP,
  EXPORT_FACTOR_FOR,
  EXPORT_GAP_GROUP,
  EXPORT_LANGUAGE_ABILITY_GROUP,
  FACTOR_FOR_LIST,
  GAP_GROUP_LIST,
  IMPORT_ACADEMIC_RESULT_GROUP,
  IMPORT_AGE,
  IMPORT_AGE_GROUP,
  IMPORT_BACKLOGS_GROUP,
  IMPORT_ENTRANCE_TEST_ABILITY_GROUP,
  IMPORT_FACTOR_FOR,
  IMPORT_GAP_GROUP,
  IMPORT_LANGUAGE_ABILITY_GROUP,
  LANGUAGE_ABILITY_GROUP_LIST,
} from "./actionType";

// FACTOR_FOR
export const factorForList = (data, callback) => ({
  type: FACTOR_FOR_LIST,
  data,
  callback,
});

export const factorForAdd = (data, callback) => ({
  type: ADD_FACTOR_FOR,
  data,
  callback,
});

export const factorForEdit = (data, callback) => ({
  type: EDIT_FACTOR_FOR,
  data,
  callback,
});

export const factorForDelete = (data, callback) => ({
  type: DELETE_FACTOR_FOR,
  data,
  callback,
});

export const factorForExportData = (data, callback) => ({
  type: EXPORT_FACTOR_FOR,
  data,
  callback,
});

export const factorForImportData = (data, callback) => ({
  type: IMPORT_FACTOR_FOR,
  data,
  callback,
});

// AGE_GROUP
export const ageGroupList = (data, callback) => ({
  type: AGE_GROUP_LIST,
  data,
  callback,
});

export const ageGroupAdd = (data, callback) => ({
  type: ADD_AGE_GROUP,
  data,
  callback,
});

export const ageGroupEdit = (data, callback) => ({
  type: EDIT_AGE_GROUP,
  data,
  callback,
});

export const ageGroupDelete = (data, callback) => ({
  type: DELETE_AGE_GROUP,
  data,
  callback,
});

export const ageGroupExportData = (data, callback) => ({
  type: EXPORT_AGE_GROUP,
  data,
  callback,
});

export const ageGroupImportData = (data, callback) => ({
  type: IMPORT_AGE_GROUP,
  data,
  callback,
});

// ACADEMIC_RESULT_GROUP
export const academicResultGroupList = (data, callback) => ({
  type: ACADEMIC_RESULT_GROUP_LIST,
  data,
  callback,
});

export const academicResultGroupAdd = (data, callback) => ({
  type: ADD_ACADEMIC_RESULT_GROUP,
  data,
  callback,
});

export const academicResultGroupEdit = (data, callback) => ({
  type: EDIT_ACADEMIC_RESULT_GROUP,
  data,
  callback,
});

export const academicResultGroupDelete = (data, callback) => ({
  type: DELETE_ACADEMIC_RESULT_GROUP,
  data,
  callback,
});

export const academicResultGroupExportData = (data, callback) => ({
  type: EXPORT_ACADEMIC_RESULT_GROUP,
  data,
  callback,
});

export const academicResultGroupImportData = (data, callback) => ({
  type: IMPORT_ACADEMIC_RESULT_GROUP,
  data,
  callback,
});

export const backlogsGroupList = (data, callback) => ({
  type: BACKLOGS_GROUP_LIST,
  data,
  callback,
});

export const backlogsGroupAdd = (data, callback) => ({
  type: ADD_BACKLOGS_GROUP,
  data,
  callback,
});

export const backlogsGroupEdit = (data, callback) => ({
  type: EDIT_BACKLOGS_GROUP,
  data,
  callback,
});

export const backlogsGroupDelete = (data, callback) => ({
  type: DELETE_BACKLOGS_GROUP,
  data,
  callback,
});

export const backlogsGroupExportData = (data, callback) => ({
  type: EXPORT_BACKLOGS_GROUP,
  data,
 callback,
});

export const backlogsGroupImportData = (data, callback) => ({
  type: IMPORT_BACKLOGS_GROUP,
  data,
  callback,
});

export const gapGroupList = (data, callback) => ({
  type: GAP_GROUP_LIST,
  data,
  callback,
});

export const gapGroupAdd = (data, callback) => ({
  type: ADD_GAP_GROUP,
  data,
  callback,
});

export const gapGroupEdit = (data, callback) => ({
  type: EDIT_GAP_GROUP,
  data,
  callback,
});

export const gapGroupDelete = (data, callback) => ({
  type: DELETE_GAP_GROUP,
  data,
  callback,
});

export const gapGroupExportData = (data, callback) => ({
  type: EXPORT_GAP_GROUP,
  data,
  callback,
});

export const gapGroupImportData = (data, callback) => ({
  type: IMPORT_GAP_GROUP,
  data,
  callback,
});

export const languageAbilityGroupList = (data, callback) => ({
  type: LANGUAGE_ABILITY_GROUP_LIST,
  data,
  callback,
});

export const languageAbilityGroupAdd = (data, callback) => ({
  type: ADD_LANGUAGE_ABILITY_GROUP,
  data,
  callback,
});

export const languageAbilityGroupEdit = (data, callback) => ({
  type: EDIT_LANGUAGE_ABILITY_GROUP,
  data,
  callback,
});

export const languageAbilityGroupDelete = (data, callback) => ({
  type: DELETE_LANGUAGE_ABILITY_GROUP,
  data,
  callback,
});

export const languageAbilityGroupExportData = (data, callback) => ({
  type: EXPORT_LANGUAGE_ABILITY_GROUP,
  data,
  callback,
});

export const languageAbilityGroupImportData = (data, callback) => ({
  type: IMPORT_LANGUAGE_ABILITY_GROUP,
  data,
  callback,
});

export const entranceTestAbilityGroupList = (data, callback) => ({
  type: ENTRANCE_TEST_ABILITY_GROUP_LIST,
  data,
  callback,
});

export const entranceTestAbilityGroupAdd = (data, callback) => ({
  type: ADD_ENTRANCE_TEST_ABILITY_GROUP,
  data,
  callback,
});

export const entranceTestAbilityGroupEdit = (data, callback) => ({
  type: EDIT_ENTRANCE_TEST_ABILITY_GROUP,
  data,
  callback,
});

export const entranceTestAbilityGroupDelete = (data, callback) => ({
  type: DELETE_ENTRANCE_TEST_ABILITY_GROUP,
  data,
  callback,
});

export const entranceTestAbilityGroupExportData = (data, callback) => ({
  type: EXPORT_ENTRANCE_TEST_ABILITY_GROUP,
  data,
  callback,
});

export const entranceTestAbilityGroupImportData = (data, callback) => ({
  type: IMPORT_ENTRANCE_TEST_ABILITY_GROUP,
  data,
  callback,
});

export const ageList = (data, callback) => ({
  type: AGE_LIST,
  data,
  callback,
});

export const ageAdd = (data, callback) => ({
  type: ADD_AGE,
  data,
  callback,
});

export const ageEdit = (data, callback) => ({
  type: EDIT_AGE,
  data,
  callback,
});

export const ageDelete = (data, callback) => ({
  type: DELETE_AGE,
  data,
  callback,
});

export const ageExportData = (data, callback) => ({
  type: EXPORT_AGE,
  data,
  callback,
});

export const ageImportData = (data, callback) => ({
  type: IMPORT_AGE,
  data,
  callback,
});



