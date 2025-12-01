import { call, takeEvery } from "redux-saga/effects";
import {
  addAcademicResultGroupAPI,
  addAgeAPI,
  addAgeGroupAPI,
  addBacklogsGroupAPI,
  addEntranceTestAbilityGroupAPI,
  addFactorForAPI,
  addGapGroupAPI,
  addLanguageAbilityGroupAPI,
  addStudyFactorAcademicResultAPI,
  addStudyFactorBacklogsAPI,
  addStudyFactorEntranceTestAbilityAPI,
  addStudyFactorGapAPI,
  addStudyFactorLanguageAbilityAPI,
  deleteAcademicResultGroupAPI,
  deleteAgeAPI,
  deleteAgeGroupAPI,
  deleteBacklogsGroupAPI,
  deleteEntranceTestAbilityGroupAPI,
  deleteFactorForAPI,
  deleteGapGroupAPI,
  deleteLanguageAbilityGroupAPI,
  deleteStudyFactorAcademicResultAPI,
  deleteStudyFactorBacklogsAPI,
  deleteStudyFactorEntranceTestAbilityAPI,
  deleteStudyFactorGapAPI,
  deleteStudyFactorLanguageAbilityAPI,
  editAcademicResultGroupAPI,
  editAgeAPI,
  editAgeGroupAPI,
  editBacklogsGroupAPI,
  editEntranceTestAbilityGroupAPI,
  editFactorForAPI,
  editGapGroupAPI,
  editLanguageAbilityGroupAPI,
  editStudyFactorAcademicResultAPI,
  editStudyFactorBacklogsAPI,
  editStudyFactorEntranceTestAbilityAPI,
  editStudyFactorGapAPI,
  editStudyFactorLanguageAbilityAPI,
  exportAcademicResultGroupAPI,
  exportAgeAPI,
  exportAgeGroupAPI,
  exportBacklogsGroupAPI,
  exportEntranceTestAbilityGroupAPI,
  exportFactorForAPI,
  exportGapGroupAPI,
  exportLanguageAbilityGroupAPI,
  exportStudyFactorAcademicResultAPI,
  exportStudyFactorBacklogsAPI,
  exportStudyFactorEntranceTestAbilityAPI,
  exportStudyFactorGapAPI,
  exportStudyFactorLanguageAbilityAPI,
  getAcademicResultGroupListAPI,
  getAgeGroupListAPI,
  getAgeListAPI,
  getBacklogsGroupListAPI,
  getEntranceTestAbilityGroupListAPI,
  getFactorForListAPI,
  getGapGroupListAPI,
  getLanguageAbilityGroupListAPI,
  getStudyFactorAcademicResultListAPI,
  getStudyFactorBacklogsListAPI,
  getStudyFactorEntranceTestAbilityListAPI,
  getStudyFactorGapListAPI,
  getStudyFactorLanguageAbilityListAPI,
  importAcademicResultGroupAPI,
  importAgeAPI,
  importAgeGroupAPI,
  importBacklogsGroupAPI,
  importEntranceTestAbilityGroupAPI,
  importFactorForAPI,
  importGapGroupAPI,
  importLanguageAbilityGroupAPI,
  importStudyFactorAcademicResultAPI,
  importStudyFactorBacklogsAPI,
  importStudyFactorEntranceTestAbilityAPI,
  importStudyFactorGapAPI,
  importStudyFactorLanguageAbilityAPI,
} from "../../../service/api_helper";
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
  ADD_STUDY_FACTOR_ACADEMIC_RESULT,
  ADD_STUDY_FACTOR_BACKLOGS,
  ADD_STUDY_FACTOR_ENTRANCE_TEST_ABILITY,
  ADD_STUDY_FACTOR_GAP,
  ADD_STUDY_FACTOR_LANGUAGE_ABILITY,
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
  DELETE_STUDY_FACTOR_ACADEMIC_RESULT,
  DELETE_STUDY_FACTOR_BACKLOGS,
  DELETE_STUDY_FACTOR_ENTRANCE_TEST_ABILITY,
  DELETE_STUDY_FACTOR_GAP,
  DELETE_STUDY_FACTOR_LANGUAGE_ABILITY,
  EDIT_ACADEMIC_RESULT_GROUP,
  EDIT_AGE,
  EDIT_AGE_GROUP,
  EDIT_BACKLOGS_GROUP,
  EDIT_ENTRANCE_TEST_ABILITY_GROUP,
  EDIT_FACTOR_FOR,
  EDIT_GAP_GROUP,
  EDIT_LANGUAGE_ABILITY_GROUP,
  EDIT_STUDY_FACTOR_ACADEMIC_RESULT,
  EDIT_STUDY_FACTOR_BACKLOGS,
  EDIT_STUDY_FACTOR_ENTRANCE_TEST_ABILITY,
  EDIT_STUDY_FACTOR_GAP,
  EDIT_STUDY_FACTOR_LANGUAGE_ABILITY,
  ENTRANCE_TEST_ABILITY_GROUP_LIST,
  EXPORT_ACADEMIC_RESULT_GROUP,
  EXPORT_AGE,
  EXPORT_AGE_GROUP,
  EXPORT_BACKLOGS_GROUP,
  EXPORT_ENTRANCE_TEST_ABILITY_GROUP,
  EXPORT_FACTOR_FOR,
  EXPORT_GAP_GROUP,
  EXPORT_LANGUAGE_ABILITY_GROUP,
  EXPORT_STUDY_FACTOR_ACADEMIC_RESULT,
  EXPORT_STUDY_FACTOR_BACKLOGS,
  EXPORT_STUDY_FACTOR_ENTRANCE_TEST_ABILITY,
  EXPORT_STUDY_FACTOR_GAP,
  EXPORT_STUDY_FACTOR_LANGUAGE_ABILITY,
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
  IMPORT_STUDY_FACTOR_ACADEMIC_RESULT,
  IMPORT_STUDY_FACTOR_BACKLOGS,
  IMPORT_STUDY_FACTOR_ENTRANCE_TEST_ABILITY,
  IMPORT_STUDY_FACTOR_GAP,
  IMPORT_STUDY_FACTOR_LANGUAGE_ABILITY,
  LANGUAGE_ABILITY_GROUP_LIST,
  STUDY_FACTOR_ACADEMIC_RESULT_LIST,
  STUDY_FACTOR_BACKLOGS_LIST,
  STUDY_FACTOR_ENTRANCE_TEST_ABILITY_LIST,
  STUDY_FACTOR_GAP_LIST,
  STUDY_FACTOR_LANGUAGE_ABILITY_LIST,
} from "./actionType";

//Factor For
function* factorForListSaga(action) {
  try {
    const response = yield call(getFactorForListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* factorForAddSaga(action) {
  try {
    const response = yield call(addFactorForAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* factorForEditSaga(action) {
  try {
    const response = yield call(editFactorForAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* factorForDeleteSaga(action) {
  try {
    const response = yield call(deleteFactorForAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* factorForExportSaga(action) {
  try {
    const response = yield call(exportFactorForAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* factorForImportSaga(action) {
  try {
    const response = yield call(importFactorForAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

//Age Group
function* ageGroupListSaga(action) {
  try {
    const response = yield call(getAgeGroupListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* ageGroupAddSaga(action) {
  try {
    const response = yield call(addAgeGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* ageGroupEditSaga(action) {
  try {
    const response = yield call(editAgeGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* ageGroupDeleteSaga(action) {
  try {
    const response = yield call(deleteAgeGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* ageGroupExportSaga(action) {
  try {
    const response = yield call(exportAgeGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* ageGroupImportSaga(action) {
  try {
    const response = yield call(importAgeGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}
// Academic Result Group
function* academicResultGroupListSaga(action) {
  try {
    const response = yield call(getAcademicResultGroupListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* academicResultGroupAddSaga(action) {
  try {
    const response = yield call(addAcademicResultGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* academicResultGroupEditSaga(action) {
  try {
    const response = yield call(editAcademicResultGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* academicResultGroupDeleteSaga(action) {
  try {
    const response = yield call(deleteAcademicResultGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* academicResultGroupExportSaga(action) {
  try {
    const response = yield call(exportAcademicResultGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* academicResultGroupImportSaga(action) {
  try {
    const response = yield call(importAcademicResultGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}
//BACKLOGS GROUP
function* backlogsGroupListSaga(action) {
  try {
    const response = yield call(getBacklogsGroupListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* backlogsGroupAddSaga(action) {
  try {
    const response = yield call(addBacklogsGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* backlogsGroupEditSaga(action) {
  try {
    const response = yield call(editBacklogsGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* backlogsGroupDeleteSaga(action) {
  try {
    const response = yield call(deleteBacklogsGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* backlogsGroupExportSaga(action) {
  try {
    const response = yield call(exportBacklogsGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* backlogsGroupImportSaga(action) {
  try {
    const response = yield call(importBacklogsGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}
//GAP GROUP
function* gapGroupListSaga(action) {
  try {
    const response = yield call(getGapGroupListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* gapGroupAddSaga(action) {
  try {
    const response = yield call(addGapGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* gapGroupEditSaga(action) {
  try {
    const response = yield call(editGapGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* gapGroupDeleteSaga(action) {
  try {
    const response = yield call(deleteGapGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* gapGroupExportSaga(action) {
  try {
    const response = yield call(exportGapGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* gapGroupImportSaga(action) {
  try {
    const response = yield call(importGapGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// Language Ability Group Sagas
function* languageAbilityGroupListSaga(action) {
  try {
    const response = yield call(getLanguageAbilityGroupListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* languageAbilityGroupAddSaga(action) {
  try {
    const response = yield call(addLanguageAbilityGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* languageAbilityGroupEditSaga(action) {
  try {
    const response = yield call(editLanguageAbilityGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* languageAbilityGroupDeleteSaga(action) {
  try {
    const response = yield call(deleteLanguageAbilityGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* languageAbilityGroupExportSaga(action) {
  try {
    const response = yield call(exportLanguageAbilityGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* languageAbilityGroupImportSaga(action) {
  try {
    const response = yield call(importLanguageAbilityGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// Entrance Test Ability Group Sagas
function* entranceTestAbilityGroupListSaga(action) {
  try {
    const response = yield call(
      getEntranceTestAbilityGroupListAPI,
      action?.data
    );
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* entranceTestAbilityGroupAddSaga(action) {
  try {
    const response = yield call(addEntranceTestAbilityGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* entranceTestAbilityGroupEditSaga(action) {
  try {
    const response = yield call(editEntranceTestAbilityGroupAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* entranceTestAbilityGroupDeleteSaga(action) {
  try {
    const response = yield call(
      deleteEntranceTestAbilityGroupAPI,
      action?.data
    );
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* entranceTestAbilityGroupExportSaga(action) {
  try {
    const response = yield call(
      exportEntranceTestAbilityGroupAPI,
      action?.data
    );
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* entranceTestAbilityGroupImportSaga(action) {
  try {
    const response = yield call(
      importEntranceTestAbilityGroupAPI,
      action?.data
    );
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// Age – Sagas
function* ageListSaga(action) {
  try {
    const response = yield call(getAgeListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* ageAddSaga(action) {
  try {
    const response = yield call(addAgeAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* ageEditSaga(action) {
  try {
    const response = yield call(editAgeAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* ageDeleteSaga(action) {
  try {
    const response = yield call(deleteAgeAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* ageExportSaga(action) {
  try {
    const response = yield call(exportAgeAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* ageImportSaga(action) {
  try {
    const response = yield call(importAgeAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// Study Factor – Academic Result Sagas
function* studyFactorAcademicResultListSaga(action) {
  try {
    const response = yield call(
      getStudyFactorAcademicResultListAPI,
      action?.data
    );
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorAcademicResultAddSaga(action) {
  try {
    const response = yield call(addStudyFactorAcademicResultAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorAcademicResultEditSaga(action) {
  try {
    const response = yield call(editStudyFactorAcademicResultAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorAcademicResultDeleteSaga(action) {
  try {
    const response = yield call(
      deleteStudyFactorAcademicResultAPI,
      action?.data
    );
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorAcademicResultExportSaga(action) {
  try {
    const response = yield call(
      exportStudyFactorAcademicResultAPI,
      action?.data
    );
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorAcademicResultImportSaga(action) {
  try {
    const response = yield call(
      importStudyFactorAcademicResultAPI,
      action?.data
    );
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// Study Factor – Backlogs Sagas
function* studyFactorBacklogsListSaga(action) {
  try {
    const response = yield call(getStudyFactorBacklogsListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorBacklogsAddSaga(action) {
  try {
    const response = yield call(addStudyFactorBacklogsAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorBacklogsEditSaga(action) {
  try {
    const response = yield call(editStudyFactorBacklogsAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorBacklogsDeleteSaga(action) {
  try {
    const response = yield call(deleteStudyFactorBacklogsAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorBacklogsExportSaga(action) {
  try {
    const response = yield call(exportStudyFactorBacklogsAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorBacklogsImportSaga(action) {
  try {
    const response = yield call(importStudyFactorBacklogsAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// Study Factor – GAP Sagas
function* studyFactorGapListSaga(action) {
  try {
    const response = yield call(getStudyFactorGapListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorGapAddSaga(action) {
  try {
    const response = yield call(addStudyFactorGapAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorGapEditSaga(action) {
  try {
    const response = yield call(editStudyFactorGapAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorGapDeleteSaga(action) {
  try {
    const response = yield call(deleteStudyFactorGapAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorGapExportSaga(action) {
  try {
    const response = yield call(exportStudyFactorGapAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorGapImportSaga(action) {
  try {
    const response = yield call(importStudyFactorGapAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// Study Factor – Language Ability Sagas
function* studyFactorLanguageAbilityListSaga(action) {
  try {
    const response = yield call(getStudyFactorLanguageAbilityListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorLanguageAbilityAddSaga(action) {
  try {
    const response = yield call(addStudyFactorLanguageAbilityAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorLanguageAbilityEditSaga(action) {
  try {
    const response = yield call(editStudyFactorLanguageAbilityAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorLanguageAbilityDeleteSaga(action) {
  try {
    const response = yield call(deleteStudyFactorLanguageAbilityAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorLanguageAbilityExportSaga(action) {
  try {
    const response = yield call(exportStudyFactorLanguageAbilityAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorLanguageAbilityImportSaga(action) {
  try {
    const response = yield call(importStudyFactorLanguageAbilityAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

// Study Factor – Entrance Test Ability Sagas
function* studyFactorEntranceTestAbilityListSaga(action) {
  try {
    const response = yield call(getStudyFactorEntranceTestAbilityListAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorEntranceTestAbilityAddSaga(action) {
  try {
    const response = yield call(addStudyFactorEntranceTestAbilityAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorEntranceTestAbilityEditSaga(action) {
  try {
    const response = yield call(editStudyFactorEntranceTestAbilityAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorEntranceTestAbilityDeleteSaga(action) {
  try {
    const response = yield call(deleteStudyFactorEntranceTestAbilityAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorEntranceTestAbilityExportSaga(action) {
  try {
    const response = yield call(exportStudyFactorEntranceTestAbilityAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}

function* studyFactorEntranceTestAbilityImportSaga(action) {
  try {
    const response = yield call(importStudyFactorEntranceTestAbilityAPI, action?.data);
    action.callback?.(response);
  } catch (error) {
    action.callback?.(null, error);
  }
}


function* studyFactorsMasterSaga() {
  yield takeEvery(FACTOR_FOR_LIST, factorForListSaga);
  yield takeEvery(ADD_FACTOR_FOR, factorForAddSaga);
  yield takeEvery(EDIT_FACTOR_FOR, factorForEditSaga);
  yield takeEvery(DELETE_FACTOR_FOR, factorForDeleteSaga);
  yield takeEvery(EXPORT_FACTOR_FOR, factorForExportSaga);
  yield takeEvery(IMPORT_FACTOR_FOR, factorForImportSaga);
  yield takeEvery(AGE_GROUP_LIST, ageGroupListSaga);
  yield takeEvery(ADD_AGE_GROUP, ageGroupAddSaga);
  yield takeEvery(EDIT_AGE_GROUP, ageGroupEditSaga);
  yield takeEvery(DELETE_AGE_GROUP, ageGroupDeleteSaga);
  yield takeEvery(EXPORT_AGE_GROUP, ageGroupExportSaga);
  yield takeEvery(IMPORT_AGE_GROUP, ageGroupImportSaga);
  yield takeEvery(ACADEMIC_RESULT_GROUP_LIST, academicResultGroupListSaga);
  yield takeEvery(ADD_ACADEMIC_RESULT_GROUP, academicResultGroupAddSaga);
  yield takeEvery(EDIT_ACADEMIC_RESULT_GROUP, academicResultGroupEditSaga);
  yield takeEvery(DELETE_ACADEMIC_RESULT_GROUP, academicResultGroupDeleteSaga);
  yield takeEvery(EXPORT_ACADEMIC_RESULT_GROUP, academicResultGroupExportSaga);
  yield takeEvery(IMPORT_ACADEMIC_RESULT_GROUP, academicResultGroupImportSaga);
  yield takeEvery(BACKLOGS_GROUP_LIST, backlogsGroupListSaga);
  yield takeEvery(ADD_BACKLOGS_GROUP, backlogsGroupAddSaga);
  yield takeEvery(EDIT_BACKLOGS_GROUP, backlogsGroupEditSaga);
  yield takeEvery(DELETE_BACKLOGS_GROUP, backlogsGroupDeleteSaga);
  yield takeEvery(EXPORT_BACKLOGS_GROUP, backlogsGroupExportSaga);
  yield takeEvery(IMPORT_BACKLOGS_GROUP, backlogsGroupImportSaga);
  yield takeEvery(GAP_GROUP_LIST, gapGroupListSaga);
  yield takeEvery(ADD_GAP_GROUP, gapGroupAddSaga);
  yield takeEvery(EDIT_GAP_GROUP, gapGroupEditSaga);
  yield takeEvery(DELETE_GAP_GROUP, gapGroupDeleteSaga);
  yield takeEvery(EXPORT_GAP_GROUP, gapGroupExportSaga);
  yield takeEvery(IMPORT_GAP_GROUP, gapGroupImportSaga);
  yield takeEvery(LANGUAGE_ABILITY_GROUP_LIST, languageAbilityGroupListSaga);
  yield takeEvery(ADD_LANGUAGE_ABILITY_GROUP, languageAbilityGroupAddSaga);
  yield takeEvery(EDIT_LANGUAGE_ABILITY_GROUP, languageAbilityGroupEditSaga);
  yield takeEvery(
    DELETE_LANGUAGE_ABILITY_GROUP,
    languageAbilityGroupDeleteSaga
  );
  yield takeEvery(
    EXPORT_LANGUAGE_ABILITY_GROUP,
    languageAbilityGroupExportSaga
  );
  yield takeEvery(
    IMPORT_LANGUAGE_ABILITY_GROUP,
    languageAbilityGroupImportSaga
  );
  yield takeEvery(
    ENTRANCE_TEST_ABILITY_GROUP_LIST,
    entranceTestAbilityGroupListSaga
  );
  yield takeEvery(
    ADD_ENTRANCE_TEST_ABILITY_GROUP,
    entranceTestAbilityGroupAddSaga
  );
  yield takeEvery(
    EDIT_ENTRANCE_TEST_ABILITY_GROUP,
    entranceTestAbilityGroupEditSaga
  );
  yield takeEvery(
    DELETE_ENTRANCE_TEST_ABILITY_GROUP,
    entranceTestAbilityGroupDeleteSaga
  );
  yield takeEvery(
    EXPORT_ENTRANCE_TEST_ABILITY_GROUP,
    entranceTestAbilityGroupExportSaga
  );
  yield takeEvery(
    IMPORT_ENTRANCE_TEST_ABILITY_GROUP,
    entranceTestAbilityGroupImportSaga
  );
  yield takeEvery(AGE_LIST, ageListSaga);
  yield takeEvery(ADD_AGE, ageAddSaga);
  yield takeEvery(EDIT_AGE, ageEditSaga);
  yield takeEvery(DELETE_AGE, ageDeleteSaga);
  yield takeEvery(EXPORT_AGE, ageExportSaga);
  yield takeEvery(IMPORT_AGE, ageImportSaga);
  yield takeEvery(
    STUDY_FACTOR_ACADEMIC_RESULT_LIST,
    studyFactorAcademicResultListSaga
  );

  yield takeEvery(
    ADD_STUDY_FACTOR_ACADEMIC_RESULT,
    studyFactorAcademicResultAddSaga
  );

  yield takeEvery(
    EDIT_STUDY_FACTOR_ACADEMIC_RESULT,
    studyFactorAcademicResultEditSaga
  );

  yield takeEvery(
    DELETE_STUDY_FACTOR_ACADEMIC_RESULT,
    studyFactorAcademicResultDeleteSaga
  );

  yield takeEvery(
    EXPORT_STUDY_FACTOR_ACADEMIC_RESULT,
    studyFactorAcademicResultExportSaga
  );

  yield takeEvery(
    IMPORT_STUDY_FACTOR_ACADEMIC_RESULT,
    studyFactorAcademicResultImportSaga
  );
  yield takeEvery(STUDY_FACTOR_BACKLOGS_LIST, studyFactorBacklogsListSaga);
  yield takeEvery(ADD_STUDY_FACTOR_BACKLOGS, studyFactorBacklogsAddSaga);
  yield takeEvery(EDIT_STUDY_FACTOR_BACKLOGS, studyFactorBacklogsEditSaga);
  yield takeEvery(DELETE_STUDY_FACTOR_BACKLOGS, studyFactorBacklogsDeleteSaga);
  yield takeEvery(EXPORT_STUDY_FACTOR_BACKLOGS, studyFactorBacklogsExportSaga);
  yield takeEvery(IMPORT_STUDY_FACTOR_BACKLOGS, studyFactorBacklogsImportSaga);
  yield takeEvery(STUDY_FACTOR_GAP_LIST, studyFactorGapListSaga);
  yield takeEvery(ADD_STUDY_FACTOR_GAP, studyFactorGapAddSaga);
  yield takeEvery(EDIT_STUDY_FACTOR_GAP, studyFactorGapEditSaga);
  yield takeEvery(DELETE_STUDY_FACTOR_GAP, studyFactorGapDeleteSaga);
  yield takeEvery(EXPORT_STUDY_FACTOR_GAP, studyFactorGapExportSaga);
  yield takeEvery(IMPORT_STUDY_FACTOR_GAP, studyFactorGapImportSaga);
yield takeEvery(
  STUDY_FACTOR_LANGUAGE_ABILITY_LIST,
  studyFactorLanguageAbilityListSaga
);
yield takeEvery(
  ADD_STUDY_FACTOR_LANGUAGE_ABILITY,
  studyFactorLanguageAbilityAddSaga
);
yield takeEvery(
  EDIT_STUDY_FACTOR_LANGUAGE_ABILITY,
  studyFactorLanguageAbilityEditSaga
);
yield takeEvery(
  DELETE_STUDY_FACTOR_LANGUAGE_ABILITY,
  studyFactorLanguageAbilityDeleteSaga
);
yield takeEvery(
  EXPORT_STUDY_FACTOR_LANGUAGE_ABILITY,
  studyFactorLanguageAbilityExportSaga
);
yield takeEvery(
  IMPORT_STUDY_FACTOR_LANGUAGE_ABILITY,
  studyFactorLanguageAbilityImportSaga
);
yield takeEvery(
  STUDY_FACTOR_ENTRANCE_TEST_ABILITY_LIST,
  studyFactorEntranceTestAbilityListSaga
);
yield takeEvery(
  ADD_STUDY_FACTOR_ENTRANCE_TEST_ABILITY,
  studyFactorEntranceTestAbilityAddSaga
);
yield takeEvery(
  EDIT_STUDY_FACTOR_ENTRANCE_TEST_ABILITY,
  studyFactorEntranceTestAbilityEditSaga
);
yield takeEvery(
  DELETE_STUDY_FACTOR_ENTRANCE_TEST_ABILITY,
  studyFactorEntranceTestAbilityDeleteSaga
);
yield takeEvery(
  EXPORT_STUDY_FACTOR_ENTRANCE_TEST_ABILITY,
  studyFactorEntranceTestAbilityExportSaga
);
yield takeEvery(
  IMPORT_STUDY_FACTOR_ENTRANCE_TEST_ABILITY,
  studyFactorEntranceTestAbilityImportSaga
);

}
export default studyFactorsMasterSaga;
