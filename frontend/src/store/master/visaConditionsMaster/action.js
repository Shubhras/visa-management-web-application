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

// Work Rights 
export const workRightsList = (data, callback) => ({
    type: WORK_RIGHTS_LIST,
    data,
    callback,
});

export const workRightsAdd = (data, callback) => ({
    type: ADD_WORK_RIGHTS,
    data,
    callback,
});

export const workRightsEdit = (data, callback) => ({
    type: EDIT_WORK_RIGHTS,
    data,
    callback,
});

export const workRightsDelete = (data, callback) => ({
    type: DELETE_WORK_RIGHTS,
    data,
    callback,
});

export const workRightsExportData = (data, callback) => ({
    type: EXPORT_WORK_RIGHTS,
    data,
    callback,
});

export const workRightsImportData = (data, callback) => ({
    type: IMPORT_WORK_RIGHTS,
    data,
    callback,
});
// Work Rights During Study
export const workRightsDuringStudyList = (data, callback) => ({
    type: WORK_RIGHTS_DURING_STUDY_LIST,
    data,
    callback,
});

export const workRightsDuringStudyAdd = (data, callback) => ({
    type: ADD_WORK_RIGHTS_DURING_STUDY,
    data,
    callback,
});

export const workRightsDuringStudyEdit = (data, callback) => ({
    type: EDIT_WORK_RIGHTS_DURING_STUDY,
    data,
    callback,
});

export const workRightsDuringStudyDelete = (data, callback) => ({
    type: DELETE_WORK_RIGHTS_DURING_STUDY,
    data,
    callback,
});

export const workRightsDuringStudyExportData = (data, callback) => ({
    type: EXPORT_WORK_RIGHTS_DURING_STUDY,
    data,
    callback,
});

export const workRightsDuringStudyImportData = (data, callback) => ({
    type: IMPORT_WORK_RIGHTS_DURING_STUDY,
    data,
    callback,
});
// Work Rights During Vacation
export const workRightsDuringVacationList = (data, callback) => ({
    type: WORK_RIGHTS_DURING_VACATION_LIST,
    data,
    callback,
});

export const workRightsDuringVacationAdd = (data, callback) => ({
    type: ADD_WORK_RIGHTS_DURING_VACATION,
    data,
    callback,
});

export const workRightsDuringVacationEdit = (data, callback) => ({
    type: EDIT_WORK_RIGHTS_DURING_VACATION,
    data,
    callback,
});

export const workRightsDuringVacationDelete = (data, callback) => ({
    type: DELETE_WORK_RIGHTS_DURING_VACATION,
    data,
    callback,
});

export const workRightsDuringVacationExportData = (data, callback) => ({
    type: EXPORT_WORK_RIGHTS_DURING_VACATION,
    data,
    callback,
});

export const workRightsDuringVacationImportData = (data, callback) => ({
    type: IMPORT_WORK_RIGHTS_DURING_VACATION,
    data,
    callback,
});
// Work Rights After Study
export const workRightsAfterStudyList = (data, callback) => ({
    type: WORK_RIGHTS_AFTER_STUDY_LIST,
    data,
    callback,
});
export const workRightsAfterStudyAdd = (data, callback) => ({
    type: ADD_WORK_RIGHTS_AFTER_STUDY,
    data,
    callback,
});
export const workRightsAfterStudyEdit = (data, callback) => ({
    type: EDIT_WORK_RIGHTS_AFTER_STUDY,
    data,
    callback,
});
export const workRightsAfterStudyDelete = (data, callback) => ({
    type: DELETE_WORK_RIGHTS_AFTER_STUDY,
    data,
    callback,
});
export const workRightsAfterStudyExportData = (data, callback) => ({
    type: EXPORT_WORK_RIGHTS_AFTER_STUDY,
    data,
    callback,
});
export const workRightsAfterStudyImportData = (data, callback) => ({
    type: IMPORT_WORK_RIGHTS_AFTER_STUDY,
    data,
    callback,
});


// PR Possibility
export const prPossibilityList = (data, callback) => ({
    type: PR_POSSIBILITY_LIST,
    data,
    callback,
});
export const prPossibilityAdd = (data, callback) => ({
    type: ADD_PR_POSSIBILITY,
    data,
    callback,
});
export const prPossibilityEdit = (data, callback) => ({
    type: EDIT_PR_POSSIBILITY,
    data,
    callback,
});
export const prPossibilityDelete = (data, callback) => ({
    type: DELETE_PR_POSSIBILITY,
    data,
    callback,
});
export const prPossibilityExportData = (data, callback) => ({
    type: EXPORT_PR_POSSIBILITY,
    data,
    callback,
});
export const prPossibilityImportData = (data, callback) => ({
    type: IMPORT_PR_POSSIBILITY,
    data,
    callback,
});


// Spouse Can Apply with Candidate
export const spouseApplyWithCandidateList = (data, callback) => ({
    type: SPOUSE_APPLY_WITH_CANDIDATE_LIST,
    data,
    callback,
});
export const spouseApplyWithCandidateAdd = (data, callback) => ({
    type: ADD_SPOUSE_APPLY_WITH_CANDIDATE,
    data,
    callback,
});
export const spouseApplyWithCandidateEdit = (data, callback) => ({
    type: EDIT_SPOUSE_APPLY_WITH_CANDIDATE,
    data,
    callback,
});
export const spouseApplyWithCandidateDelete = (data, callback) => ({
    type: DELETE_SPOUSE_APPLY_WITH_CANDIDATE,
    data,
    callback,
});
export const spouseApplyWithCandidateExportData = (data, callback) => ({
    type: EXPORT_SPOUSE_APPLY_WITH_CANDIDATE,
    data,
    callback,
});
export const spouseApplyWithCandidateImportData = (data, callback) => ({
    type: IMPORT_SPOUSE_APPLY_WITH_CANDIDATE,
    data,
    callback,
});
// Spouse Visa Category
export const spouseVisaCategoryList = (data, callback) => ({
    type: SPOUSE_VISA_CATEGORY_LIST,
    data,
    callback,
});

export const spouseVisaCategoryAdd = (data, callback) => ({
    type: ADD_SPOUSE_VISA_CATEGORY,
    data,
    callback,
});

export const spouseVisaCategoryEdit = (data, callback) => ({
    type: EDIT_SPOUSE_VISA_CATEGORY,
    data,
    callback,
});

export const spouseVisaCategoryDelete = (data, callback) => ({
    type: DELETE_SPOUSE_VISA_CATEGORY,
    data,
    callback,
});

export const spouseVisaCategoryExportData = (data, callback) => ({
    type: EXPORT_SPOUSE_VISA_CATEGORY,
    data,
    callback,
});

export const spouseVisaCategoryImportData = (data, callback) => ({
    type: IMPORT_SPOUSE_VISA_CATEGORY,
    data,
    callback,
});

// Children Can Apply with Candidate
export const childrenApplyWithCandidateList = (data, callback) => ({
    type: CHILDREN_APPLY_WITH_CANDIDATE_LIST,
    data,
    callback,
});

export const childrenApplyWithCandidateAdd = (data, callback) => ({
    type: ADD_CHILDREN_APPLY_WITH_CANDIDATE,
    data,
    callback,
});

export const childrenApplyWithCandidateEdit = (data, callback) => ({
    type: EDIT_CHILDREN_APPLY_WITH_CANDIDATE,
    data,
    callback,
});

export const childrenApplyWithCandidateDelete = (data, callback) => ({
    type: DELETE_CHILDREN_APPLY_WITH_CANDIDATE,
    data,
    callback,
});

export const childrenApplyWithCandidateExportData = (data, callback) => ({
    type: EXPORT_CHILDREN_APPLY_WITH_CANDIDATE,
    data,
    callback,
});

export const childrenApplyWithCandidateImportData = (data, callback) => ({
    type: IMPORT_CHILDREN_APPLY_WITH_CANDIDATE,
    data,
    callback,
});


// Spouse Work Rights
export const spouseWorkRightsList = (data, callback) => ({
    type: SPOUSE_WORK_RIGHTS_LIST,
    data,
    callback,
});

export const spouseWorkRightsAdd = (data, callback) => ({
    type: ADD_SPOUSE_WORK_RIGHTS,
    data,
    callback,
});

export const spouseWorkRightsEdit = (data, callback) => ({
    type: EDIT_SPOUSE_WORK_RIGHTS,
    data,
    callback,
});

export const spouseWorkRightsDelete = (data, callback) => ({
    type: DELETE_SPOUSE_WORK_RIGHTS,
    data,
    callback,
});

export const spouseWorkRightsExportData = (data, callback) => ({
    type: EXPORT_SPOUSE_WORK_RIGHTS,
    data,
    callback,
});

export const spouseWorkRightsImportData = (data, callback) => ({
    type: IMPORT_SPOUSE_WORK_RIGHTS,
    data,
    callback,
});


// Children Visa Category

export const childrenVisaCategoryList = (data, callback) => ({
    type: CHILDREN_VISA_CATEGORY_LIST,
    data,
    callback,
});

export const childrenVisaCategoryAdd = (data, callback) => ({
    type: ADD_CHILDREN_VISA_CATEGORY,
    data,
    callback,
});

export const childrenVisaCategoryEdit = (data, callback) => ({
    type: EDIT_CHILDREN_VISA_CATEGORY,
    data,
    callback,
});

export const childrenVisaCategoryDelete = (data, callback) => ({
    type: DELETE_CHILDREN_VISA_CATEGORY,
    data,
    callback,
});

export const childrenVisaCategoryExportData = (data, callback) => ({
    type: EXPORT_CHILDREN_VISA_CATEGORY,
    data,
    callback,
});

export const childrenVisaCategoryImportData = (data, callback) => ({
    type: IMPORT_CHILDREN_VISA_CATEGORY,
    data,
    callback,
});

// Children Study / Work Rights
export const childrenStudyWorkRightsList = (data, callback) => ({
    type: CHILDREN_STUDY_WORK_RIGHTS_LIST,
    data,
    callback,
});

export const childrenStudyWorkRightsAdd = (data, callback) => ({
    type: ADD_CHILDREN_STUDY_WORK_RIGHTS,
    data,
    callback,
});

export const childrenStudyWorkRightsEdit = (data, callback) => ({
    type: EDIT_CHILDREN_STUDY_WORK_RIGHTS,
    data,
    callback,
});

export const childrenStudyWorkRightsDelete = (data, callback) => ({
    type: DELETE_CHILDREN_STUDY_WORK_RIGHTS,
    data,
    callback,
});

export const childrenStudyWorkRightsExportData = (data, callback) => ({
    type: EXPORT_CHILDREN_STUDY_WORK_RIGHTS,
    data,
    callback,
});

export const childrenStudyWorkRightsImportData = (data, callback) => ({
    type: IMPORT_CHILDREN_STUDY_WORK_RIGHTS,
    data,
    callback,
});

// ================================
// VISA MAIN CATEGORY - ACTIONS
// ================================
export const visaMainCategoryList = (data, callback) => ({
    type: VISA_MAIN_CATEGORY_LIST,
    data,
    callback,
});

export const visaMainCategoryAdd = (data, callback) => ({
    type: ADD_VISA_MAIN_CATEGORY,
    data,
    callback,
});

export const visaMainCategoryEdit = (data, callback) => ({
    type: EDIT_VISA_MAIN_CATEGORY,
    data,
    callback,
});

export const visaMainCategoryDelete = (data, callback) => ({
    type: DELETE_VISA_MAIN_CATEGORY,
    data,
    callback,
});

export const visaMainCategoryExportData = (data, callback) => ({
    type: EXPORT_VISA_MAIN_CATEGORY,
    data,
    callback,
});

export const visaMainCategoryImportData = (data, callback) => ({
    type: IMPORT_VISA_MAIN_CATEGORY,
    data,
    callback,
});




