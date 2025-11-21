import { call, takeEvery } from "redux-saga/effects";
import {
    WORK_RIGHTS_LIST,
    ADD_WORK_RIGHTS,
    EDIT_WORK_RIGHTS,
    DELETE_WORK_RIGHTS,
    EXPORT_WORK_RIGHTS,
    IMPORT_WORK_RIGHTS,
    WORK_RIGHTS_DURING_STUDY_LIST,
    ADD_WORK_RIGHTS_DURING_STUDY,
    EDIT_WORK_RIGHTS_DURING_STUDY,
    DELETE_WORK_RIGHTS_DURING_STUDY,
    EXPORT_WORK_RIGHTS_DURING_STUDY,
    IMPORT_WORK_RIGHTS_DURING_STUDY,
    WORK_RIGHTS_DURING_VACATION_LIST,
    ADD_WORK_RIGHTS_DURING_VACATION,
    EDIT_WORK_RIGHTS_DURING_VACATION,
    DELETE_WORK_RIGHTS_DURING_VACATION,
    EXPORT_WORK_RIGHTS_DURING_VACATION,
    IMPORT_WORK_RIGHTS_DURING_VACATION,
    WORK_RIGHTS_AFTER_STUDY_LIST,
    ADD_WORK_RIGHTS_AFTER_STUDY,
    EDIT_WORK_RIGHTS_AFTER_STUDY,
    DELETE_WORK_RIGHTS_AFTER_STUDY,
    EXPORT_WORK_RIGHTS_AFTER_STUDY,
    IMPORT_WORK_RIGHTS_AFTER_STUDY,
    PR_POSSIBILITY_LIST,
    ADD_PR_POSSIBILITY,
    EDIT_PR_POSSIBILITY,
    DELETE_PR_POSSIBILITY,
    EXPORT_PR_POSSIBILITY,
    IMPORT_PR_POSSIBILITY,
    SPOUSE_APPLY_WITH_CANDIDATE_LIST,
    ADD_SPOUSE_APPLY_WITH_CANDIDATE,
    EDIT_SPOUSE_APPLY_WITH_CANDIDATE,
    DELETE_SPOUSE_APPLY_WITH_CANDIDATE,
    EXPORT_SPOUSE_APPLY_WITH_CANDIDATE,
    IMPORT_SPOUSE_APPLY_WITH_CANDIDATE,
    SPOUSE_VISA_CATEGORY_LIST,
    ADD_SPOUSE_VISA_CATEGORY,
    EDIT_SPOUSE_VISA_CATEGORY,
    DELETE_SPOUSE_VISA_CATEGORY,
    EXPORT_SPOUSE_VISA_CATEGORY,
    IMPORT_SPOUSE_VISA_CATEGORY,
    SPOUSE_WORK_RIGHTS_LIST,
    ADD_SPOUSE_WORK_RIGHTS,
    EDIT_SPOUSE_WORK_RIGHTS,
    DELETE_SPOUSE_WORK_RIGHTS,
    EXPORT_SPOUSE_WORK_RIGHTS,
    IMPORT_SPOUSE_WORK_RIGHTS,
    CHILDREN_APPLY_WITH_CANDIDATE_LIST,
    ADD_CHILDREN_APPLY_WITH_CANDIDATE,
    EDIT_CHILDREN_APPLY_WITH_CANDIDATE,
    DELETE_CHILDREN_APPLY_WITH_CANDIDATE,
    EXPORT_CHILDREN_APPLY_WITH_CANDIDATE,
    IMPORT_CHILDREN_APPLY_WITH_CANDIDATE,
    CHILDREN_VISA_CATEGORY_LIST,
    ADD_CHILDREN_VISA_CATEGORY,
    EDIT_CHILDREN_VISA_CATEGORY,
    DELETE_CHILDREN_VISA_CATEGORY,
    EXPORT_CHILDREN_VISA_CATEGORY,
    IMPORT_CHILDREN_VISA_CATEGORY,
    CHILDREN_STUDY_WORK_RIGHTS_LIST,
    ADD_CHILDREN_STUDY_WORK_RIGHTS,
    EDIT_CHILDREN_STUDY_WORK_RIGHTS,
    DELETE_CHILDREN_STUDY_WORK_RIGHTS,
    EXPORT_CHILDREN_STUDY_WORK_RIGHTS,
    IMPORT_CHILDREN_STUDY_WORK_RIGHTS,
    VISA_MAIN_CATEGORY_LIST,
    ADD_VISA_MAIN_CATEGORY,
    EDIT_VISA_MAIN_CATEGORY,
    DELETE_VISA_MAIN_CATEGORY,
    EXPORT_VISA_MAIN_CATEGORY,
    IMPORT_VISA_MAIN_CATEGORY,

} from "./actionType"

import {
    getWorkRightsListAPI,
    addWorkRightsAPI,
    editWorkRightsAPI,
    deleteWorkRightsAPI,
    exportWorkRightsAPI,
    importWorkRightsAPI,
    getWorkRightsDuringStudyListAPI,
    addWorkRightsDuringStudyAPI,
    editWorkRightsDuringStudyAPI,
    deleteWorkRightsDuringStudyAPI,
    exportWorkRightsDuringStudyAPI,
    importWorkRightsDuringStudyAPI,
    getWorkRightsDuringVacationListAPI,
    addWorkRightsDuringVacationAPI,
    editWorkRightsDuringVacationAPI,
    deleteWorkRightsDuringVacationAPI,
    exportWorkRightsDuringVacationAPI,
    importWorkRightsDuringVacationAPI,
    getWorkRightsAfterStudyAPI,
    addWorkRightsAfterStudyAPI,
    editWorkRightsAfterStudyAPI,
    deleteWorkRightsAfterStudyAPI,
    exportWorkRightsAfterStudyAPI,
    importWorkRightsAfterStudyAPI,
    getPRPossibilityAPI,
    addPRPossibilityAPI,
    editPRPossibilityAPI,
    deletePRPossibilityAPI,
    exportPRPossibilityAPI,
    importPRPossibilityAPI,
    getSpouseApplyWithCandidateAPI,
    addSpouseApplyWithCandidateAPI,
    editSpouseApplyWithCandidateAPI,
    deleteSpouseApplyWithCandidateAPI,
    exportSpouseApplyWithCandidateAPI,
    importSpouseApplyWithCandidateAPI,
    getSpouseVisaCategoryListAPI,
    addSpouseVisaCategoryAPI,
    editSpouseVisaCategoryAPI,
    deleteSpouseVisaCategoryAPI,
    exportSpouseVisaCategoryAPI,
    importSpouseVisaCategoryAPI,
    getSpouseWorkRightsListAPI,
    addSpouseWorkRightsAPI,
    editSpouseWorkRightsAPI,
    deleteSpouseWorkRightsAPI,
    exportSpouseWorkRightsAPI,
    importSpouseWorkRightsAPI,
    getChildrenApplyWithCandidateListAPI,
    addChildrenApplyWithCandidateAPI,
    editChildrenApplyWithCandidateAPI,
    deleteChildrenApplyWithCandidateAPI,
    exportChildrenApplyWithCandidateAPI,
    importChildrenApplyWithCandidateAPI,
    getChildrenVisaCategoryListAPI,
    addChildrenVisaCategoryAPI,
    editChildrenVisaCategoryAPI,
    deleteChildrenVisaCategoryAPI,
    exportChildrenVisaCategoryAPI,
    importChildrenVisaCategoryAPI,
    getChildrenStudyWorkRightsListAPI,
    addChildrenStudyWorkRightsAPI,
    editChildrenStudyWorkRightsAPI,
    deleteChildrenStudyWorkRightsAPI,
    exportChildrenStudyWorkRightsAPI,
    importChildrenStudyWorkRightsAPI,
    getVisaMainCategoryListAPI,
    addVisaMainCategoryAPI,
    editVisaMainCategoryAPI,
    deleteVisaMainCategoryAPI,
    exportVisaMainCategoryAPI,
    importVisaMainCategoryAPI,

} from "../../../service/api_helper";

// --- WORK RIGHTS SAGAS ---

function* workRightsListSaga(action) {
    try {
        const response = yield call(getWorkRightsListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsAddSaga(action) {
    try {
        const response = yield call(addWorkRightsAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsEditSaga(action) {
    try {
        const response = yield call(editWorkRightsAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsDeleteSaga(action) {
    try {
        const response = yield call(deleteWorkRightsAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsExportDataSaga(action) {
    try {
        const response = yield call(exportWorkRightsAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsImportDataSaga(action) {
    try {
        const response = yield call(importWorkRightsAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

// --- WORK RIGHTS DURING STUDY SAGAS ---
function* workRightsDuringStudyListSaga(action) {
    try {
        const response = yield call(getWorkRightsDuringStudyListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsDuringStudyAddSaga(action) {
    try {
        const response = yield call(addWorkRightsDuringStudyAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsDuringStudyEditSaga(action) {
    try {
        const response = yield call(editWorkRightsDuringStudyAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsDuringStudyDeleteSaga(action) {
    try {
        const response = yield call(deleteWorkRightsDuringStudyAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsDuringStudyExportDataSaga(action) {
    try {
        const response = yield call(exportWorkRightsDuringStudyAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsDuringStudyImportDataSaga(action) {
    try {
        const response = yield call(importWorkRightsDuringStudyAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// --- WORK RIGHTS DURING VACATION SAGAS ---

function* workRightsDuringVacationListSaga(action) {
    try {
        const response = yield call(getWorkRightsDuringVacationListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsDuringVacationAddSaga(action) {
    try {
        const response = yield call(addWorkRightsDuringVacationAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsDuringVacationEditSaga(action) {
    try {
        const response = yield call(editWorkRightsDuringVacationAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsDuringVacationDeleteSaga(action) {
    try {
        const response = yield call(deleteWorkRightsDuringVacationAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsDuringVacationExportDataSaga(action) {
    try {
        const response = yield call(exportWorkRightsDuringVacationAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsDuringVacationImportDataSaga(action) {
    try {
        const response = yield call(importWorkRightsDuringVacationAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

// Work Rights After Study
function* workRightsAfterStudyListSaga(action) {
    try {
        const response = yield call(getWorkRightsAfterStudyAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsAfterStudyAddSaga(action) {
    try {
        const response = yield call(addWorkRightsAfterStudyAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsAfterStudyEditSaga(action) {
    try {
        const response = yield call(editWorkRightsAfterStudyAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsAfterStudyDeleteSaga(action) {
    try {
        const response = yield call(deleteWorkRightsAfterStudyAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsAfterStudyExportSaga(action) {
    try {
        const response = yield call(exportWorkRightsAfterStudyAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* workRightsAfterStudyImportSaga(action) {
    try {
        const response = yield call(importWorkRightsAfterStudyAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

// PR Possibility
function* prPossibilityListSaga(action) {
    try {
        const response = yield call(getPRPossibilityAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* prPossibilityAddSaga(action) {
    try {
        const response = yield call(addPRPossibilityAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* prPossibilityEditSaga(action) {
    try {
        const response = yield call(editPRPossibilityAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* prPossibilityDeleteSaga(action) {
    try {
        const response = yield call(deletePRPossibilityAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* prPossibilityExportSaga(action) {
    try {
        const response = yield call(exportPRPossibilityAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* prPossibilityImportSaga(action) {
    try {
        const response = yield call(importPRPossibilityAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

// Spouse Apply With Candidate
function* spouseApplyWithCandidateListSaga(action) {
    try {
        const response = yield call(getSpouseApplyWithCandidateAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* spouseApplyWithCandidateAddSaga(action) {
    try {
        const response = yield call(addSpouseApplyWithCandidateAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* spouseApplyWithCandidateEditSaga(action) {
    try {
        const response = yield call(editSpouseApplyWithCandidateAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* spouseApplyWithCandidateDeleteSaga(action) {
    try {
        const response = yield call(deleteSpouseApplyWithCandidateAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* spouseApplyWithCandidateExportSaga(action) {
    try {
        const response = yield call(exportSpouseApplyWithCandidateAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* spouseApplyWithCandidateImportSaga(action) {
    try {
        const response = yield call(importSpouseApplyWithCandidateAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// --- SPOUSE VISA CATEGORY SAGAS ---
function* spouseVisaCategoryListSaga(action) {
    try {
        const response = yield call(getSpouseVisaCategoryListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* spouseVisaCategoryAddSaga(action) {
    try {
        const response = yield call(addSpouseVisaCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* spouseVisaCategoryEditSaga(action) {
    try {
        const response = yield call(editSpouseVisaCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* spouseVisaCategoryDeleteSaga(action) {
    try {
        const response = yield call(deleteSpouseVisaCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* spouseVisaCategoryExportDataSaga(action) {
    try {
        const response = yield call(exportSpouseVisaCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* spouseVisaCategoryImportDataSaga(action) {
    try {
        const response = yield call(importSpouseVisaCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
//  Spouse Work Rights
function* spouseWorkRightsListSaga(action) {
    try {
        const response = yield call(getSpouseWorkRightsListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* spouseWorkRightsAddSaga(action) {
    try {
        const response = yield call(addSpouseWorkRightsAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* spouseWorkRightsEditSaga(action) {
    try {
        const response = yield call(editSpouseWorkRightsAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* spouseWorkRightsDeleteSaga(action) {
    try {
        const response = yield call(deleteSpouseWorkRightsAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* spouseWorkRightsExportDataSaga(action) {
    try {
        const response = yield call(exportSpouseWorkRightsAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* spouseWorkRightsImportDataSaga(action) {
    try {
        const response = yield call(importSpouseWorkRightsAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}


//  Children Can Apply with Candidate
function* childrenApplyWithCandidateListSaga(action) {
    try {
        const response = yield call(getChildrenApplyWithCandidateListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* childrenApplyWithCandidateAddSaga(action) {
    try {
        const response = yield call(addChildrenApplyWithCandidateAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* childrenApplyWithCandidateEditSaga(action) {
    try {
        const response = yield call(editChildrenApplyWithCandidateAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* childrenApplyWithCandidateDeleteSaga(action) {
    try {
        const response = yield call(deleteChildrenApplyWithCandidateAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* childrenApplyWithCandidateExportDataSaga(action) {
    try {
        const response = yield call(exportChildrenApplyWithCandidateAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* childrenApplyWithCandidateImportDataSaga(action) {
    try {
        const response = yield call(importChildrenApplyWithCandidateAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

//  Children Visa Category
function* childrenVisaCategoryListSaga(action) {
    try {
        const response = yield call(getChildrenVisaCategoryListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* childrenVisaCategoryAddSaga(action) {
    try {
        const response = yield call(addChildrenVisaCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* childrenVisaCategoryEditSaga(action) {
    try {
        const response = yield call(editChildrenVisaCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* childrenVisaCategoryDeleteSaga(action) {
    try {
        const response = yield call(deleteChildrenVisaCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* childrenVisaCategoryExportDataSaga(action) {
    try {
        const response = yield call(exportChildrenVisaCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* childrenVisaCategoryImportDataSaga(action) {
    try {
        const response = yield call(importChildrenVisaCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

//  Children Study / Work Rights
function* childrenStudyWorkRightsListSaga(action) {
    try {
        const response = yield call(getChildrenStudyWorkRightsListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* childrenStudyWorkRightsAddSaga(action) {
    try {
        const response = yield call(addChildrenStudyWorkRightsAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* childrenStudyWorkRightsEditSaga(action) {
    try {
        const response = yield call(editChildrenStudyWorkRightsAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* childrenStudyWorkRightsDeleteSaga(action) {
    try {
        const response = yield call(deleteChildrenStudyWorkRightsAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* childrenStudyWorkRightsExportDataSaga(action) {
    try {
        const response = yield call(exportChildrenStudyWorkRightsAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* childrenStudyWorkRightsImportDataSaga(action) {
    try {
        const response = yield call(importChildrenStudyWorkRightsAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

// Visa Main Category
function* visaMainCategoryListSaga(action) {
    try {
        const response = yield call(getVisaMainCategoryListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaMainCategoryAddSaga(action) {
    try {
        const response = yield call(addVisaMainCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaMainCategoryEditSaga(action) {
    try {
        const response = yield call(editVisaMainCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaMainCategoryDeleteSaga(action) {
    try {
        const response = yield call(deleteVisaMainCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaMainCategoryExportDataSaga(action) {
    try {
        const response = yield call(exportVisaMainCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaMainCategoryImportDataSaga(action) {
    try {
        const response = yield call(importVisaMainCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}




function* visaConditionsMasterSaga() {
    yield takeEvery(WORK_RIGHTS_LIST, workRightsListSaga);
    yield takeEvery(ADD_WORK_RIGHTS, workRightsAddSaga);
    yield takeEvery(EDIT_WORK_RIGHTS, workRightsEditSaga);
    yield takeEvery(DELETE_WORK_RIGHTS, workRightsDeleteSaga);
    yield takeEvery(EXPORT_WORK_RIGHTS, workRightsExportDataSaga);
    yield takeEvery(IMPORT_WORK_RIGHTS, workRightsImportDataSaga);
    yield takeEvery(WORK_RIGHTS_DURING_STUDY_LIST, workRightsDuringStudyListSaga);
    yield takeEvery(ADD_WORK_RIGHTS_DURING_STUDY, workRightsDuringStudyAddSaga);
    yield takeEvery(EDIT_WORK_RIGHTS_DURING_STUDY, workRightsDuringStudyEditSaga);
    yield takeEvery(DELETE_WORK_RIGHTS_DURING_STUDY, workRightsDuringStudyDeleteSaga);
    yield takeEvery(EXPORT_WORK_RIGHTS_DURING_STUDY, workRightsDuringStudyExportDataSaga);
    yield takeEvery(IMPORT_WORK_RIGHTS_DURING_STUDY, workRightsDuringStudyImportDataSaga);
    yield takeEvery(WORK_RIGHTS_DURING_VACATION_LIST, workRightsDuringVacationListSaga);
    yield takeEvery(ADD_WORK_RIGHTS_DURING_VACATION, workRightsDuringVacationAddSaga);
    yield takeEvery(EDIT_WORK_RIGHTS_DURING_VACATION, workRightsDuringVacationEditSaga);
    yield takeEvery(DELETE_WORK_RIGHTS_DURING_VACATION, workRightsDuringVacationDeleteSaga);
    yield takeEvery(EXPORT_WORK_RIGHTS_DURING_VACATION, workRightsDuringVacationExportDataSaga);
    yield takeEvery(IMPORT_WORK_RIGHTS_DURING_VACATION, workRightsDuringVacationImportDataSaga);
    yield takeEvery(WORK_RIGHTS_AFTER_STUDY_LIST, workRightsAfterStudyListSaga);
    yield takeEvery(ADD_WORK_RIGHTS_AFTER_STUDY, workRightsAfterStudyAddSaga);
    yield takeEvery(EDIT_WORK_RIGHTS_AFTER_STUDY, workRightsAfterStudyEditSaga);
    yield takeEvery(DELETE_WORK_RIGHTS_AFTER_STUDY, workRightsAfterStudyDeleteSaga);
    yield takeEvery(EXPORT_WORK_RIGHTS_AFTER_STUDY, workRightsAfterStudyExportSaga);
    yield takeEvery(IMPORT_WORK_RIGHTS_AFTER_STUDY, workRightsAfterStudyImportSaga);
    yield takeEvery(PR_POSSIBILITY_LIST, prPossibilityListSaga);
    yield takeEvery(ADD_PR_POSSIBILITY, prPossibilityAddSaga);
    yield takeEvery(EDIT_PR_POSSIBILITY, prPossibilityEditSaga);
    yield takeEvery(DELETE_PR_POSSIBILITY, prPossibilityDeleteSaga);
    yield takeEvery(EXPORT_PR_POSSIBILITY, prPossibilityExportSaga);
    yield takeEvery(IMPORT_PR_POSSIBILITY, prPossibilityImportSaga);
    yield takeEvery(SPOUSE_APPLY_WITH_CANDIDATE_LIST, spouseApplyWithCandidateListSaga);
    yield takeEvery(ADD_SPOUSE_APPLY_WITH_CANDIDATE, spouseApplyWithCandidateAddSaga);
    yield takeEvery(EDIT_SPOUSE_APPLY_WITH_CANDIDATE, spouseApplyWithCandidateEditSaga);
    yield takeEvery(DELETE_SPOUSE_APPLY_WITH_CANDIDATE, spouseApplyWithCandidateDeleteSaga);
    yield takeEvery(EXPORT_SPOUSE_APPLY_WITH_CANDIDATE, spouseApplyWithCandidateExportSaga);
    yield takeEvery(IMPORT_SPOUSE_APPLY_WITH_CANDIDATE, spouseApplyWithCandidateImportSaga);
    yield takeEvery(SPOUSE_VISA_CATEGORY_LIST, spouseVisaCategoryListSaga);
    yield takeEvery(ADD_SPOUSE_VISA_CATEGORY, spouseVisaCategoryAddSaga);
    yield takeEvery(EDIT_SPOUSE_VISA_CATEGORY, spouseVisaCategoryEditSaga);
    yield takeEvery(DELETE_SPOUSE_VISA_CATEGORY, spouseVisaCategoryDeleteSaga);
    yield takeEvery(EXPORT_SPOUSE_VISA_CATEGORY, spouseVisaCategoryExportDataSaga);
    yield takeEvery(IMPORT_SPOUSE_VISA_CATEGORY, spouseVisaCategoryImportDataSaga);
    yield takeEvery(SPOUSE_WORK_RIGHTS_LIST, spouseWorkRightsListSaga);
    yield takeEvery(ADD_SPOUSE_WORK_RIGHTS, spouseWorkRightsAddSaga);
    yield takeEvery(EDIT_SPOUSE_WORK_RIGHTS, spouseWorkRightsEditSaga);
    yield takeEvery(DELETE_SPOUSE_WORK_RIGHTS, spouseWorkRightsDeleteSaga);
    yield takeEvery(EXPORT_SPOUSE_WORK_RIGHTS, spouseWorkRightsExportDataSaga);
    yield takeEvery(IMPORT_SPOUSE_WORK_RIGHTS, spouseWorkRightsImportDataSaga);
    yield takeEvery(CHILDREN_APPLY_WITH_CANDIDATE_LIST, childrenApplyWithCandidateListSaga);
    yield takeEvery(ADD_CHILDREN_APPLY_WITH_CANDIDATE, childrenApplyWithCandidateAddSaga);
    yield takeEvery(EDIT_CHILDREN_APPLY_WITH_CANDIDATE, childrenApplyWithCandidateEditSaga);
    yield takeEvery(DELETE_CHILDREN_APPLY_WITH_CANDIDATE, childrenApplyWithCandidateDeleteSaga);
    yield takeEvery(EXPORT_CHILDREN_APPLY_WITH_CANDIDATE, childrenApplyWithCandidateExportDataSaga);
    yield takeEvery(IMPORT_CHILDREN_APPLY_WITH_CANDIDATE, childrenApplyWithCandidateImportDataSaga);
    yield takeEvery(CHILDREN_VISA_CATEGORY_LIST, childrenVisaCategoryListSaga);
    yield takeEvery(ADD_CHILDREN_VISA_CATEGORY, childrenVisaCategoryAddSaga);
    yield takeEvery(EDIT_CHILDREN_VISA_CATEGORY, childrenVisaCategoryEditSaga);
    yield takeEvery(DELETE_CHILDREN_VISA_CATEGORY, childrenVisaCategoryDeleteSaga);
    yield takeEvery(EXPORT_CHILDREN_VISA_CATEGORY, childrenVisaCategoryExportDataSaga);
    yield takeEvery(IMPORT_CHILDREN_VISA_CATEGORY, childrenVisaCategoryImportDataSaga);
    yield takeEvery(CHILDREN_STUDY_WORK_RIGHTS_LIST, childrenStudyWorkRightsListSaga);
    yield takeEvery(ADD_CHILDREN_STUDY_WORK_RIGHTS, childrenStudyWorkRightsAddSaga);
    yield takeEvery(EDIT_CHILDREN_STUDY_WORK_RIGHTS, childrenStudyWorkRightsEditSaga);
    yield takeEvery(DELETE_CHILDREN_STUDY_WORK_RIGHTS, childrenStudyWorkRightsDeleteSaga);
    yield takeEvery(EXPORT_CHILDREN_STUDY_WORK_RIGHTS, childrenStudyWorkRightsExportDataSaga);
    yield takeEvery(IMPORT_CHILDREN_STUDY_WORK_RIGHTS, childrenStudyWorkRightsImportDataSaga);
    yield takeEvery(VISA_MAIN_CATEGORY_LIST, visaMainCategoryListSaga);
    yield takeEvery(ADD_VISA_MAIN_CATEGORY, visaMainCategoryAddSaga);
    yield takeEvery(EDIT_VISA_MAIN_CATEGORY, visaMainCategoryEditSaga);
    yield takeEvery(DELETE_VISA_MAIN_CATEGORY, visaMainCategoryDeleteSaga);
    yield takeEvery(EXPORT_VISA_MAIN_CATEGORY, visaMainCategoryExportDataSaga);
    yield takeEvery(IMPORT_VISA_MAIN_CATEGORY, visaMainCategoryImportDataSaga);





}

export default visaConditionsMasterSaga;
