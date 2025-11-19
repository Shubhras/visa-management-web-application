import { call, takeEvery } from "redux-saga/effects";
import {
    INSTITUTE_TYPE_LIST,
    ADD_INSTITUTE_TYPE,
    EDIT_INSTITUTE_TYPE,
    DELETE_INSTITUTE_TYPE,
    EXPORT_INSTITUTE_TYPE,
    IMPORT_INSTITUTE_TYPE,
    INSTITUTE_GROUP_NAME_LIST,
    ADD_INSTITUTE_GROUP_NAME,
    EDIT_INSTITUTE_GROUP_NAME,
    DELETE_INSTITUTE_GROUP_NAME,
    EXPORT_INSTITUTE_GROUP_NAME,
    IMPORT_INSTITUTE_GROUP_NAME,
    INSTITUTE_STATUS_LIST,
    ADD_INSTITUTE_STATUS,
    EDIT_INSTITUTE_STATUS,
    DELETE_INSTITUTE_STATUS,
    EXPORT_INSTITUTE_STATUS,
    IMPORT_INSTITUTE_STATUS,
    INSTITUTE_PRIORITY_LIST,
    ADD_INSTITUTE_PRIORITY,
    EDIT_INSTITUTE_PRIORITY,
    DELETE_INSTITUTE_PRIORITY,
    EXPORT_INSTITUTE_PRIORITY,
    IMPORT_INSTITUTE_PRIORITY,
    INSTITUTE_DEPARTMENT_LIST,
    ADD_INSTITUTE_DEPARTMENT,
    EDIT_INSTITUTE_DEPARTMENT,
    DELETE_INSTITUTE_DEPARTMENT,
    EXPORT_INSTITUTE_DEPARTMENT,
    IMPORT_INSTITUTE_DEPARTMENT,
    BANK_ACCOUNT_FOR_LIST,
    ADD_BANK_ACCOUNT_FOR,
    EDIT_BANK_ACCOUNT_FOR,
    DELETE_BANK_ACCOUNT_FOR,
    EXPORT_BANK_ACCOUNT_FOR,
    IMPORT_BANK_ACCOUNT_FOR,
    WHEN_COMMISSION_ISSUE_LIST,
    ADD_WHEN_COMMISSION_ISSUE,
    EDIT_WHEN_COMMISSION_ISSUE,
    DELETE_WHEN_COMMISSION_ISSUE,
    EXPORT_WHEN_COMMISSION_ISSUE,
    IMPORT_WHEN_COMMISSION_ISSUE,
    COURSE_LEVEL_CODE_LIST,
    ADD_COURSE_LEVEL_CODE,
    EDIT_COURSE_LEVEL_CODE,
    DELETE_COURSE_LEVEL_CODE,
    EXPORT_COURSE_LEVEL_CODE,
    IMPORT_COURSE_LEVEL_CODE,
    COURSE_DIVIDED_IN_LIST,
    ADD_COURSE_DIVIDED_IN,
    EDIT_COURSE_DIVIDED_IN,
    DELETE_COURSE_DIVIDED_IN,
    EXPORT_COURSE_DIVIDED_IN,
    IMPORT_COURSE_DIVIDED_IN,
    COURSE_STATUS_LIST,
    ADD_COURSE_STATUS,
    EDIT_COURSE_STATUS,
    DELETE_COURSE_STATUS,
    EXPORT_COURSE_STATUS,
    IMPORT_COURSE_STATUS,
    INTAKE_NAME_LIST,
    ADD_INTAKE_NAME,
    EDIT_INTAKE_NAME,
    DELETE_INTAKE_NAME,
    EXPORT_INTAKE_NAME,
    IMPORT_INTAKE_NAME,
    COURSE_STATUS_INTAKE_LIST,
    ADD_COURSE_STATUS_INTAKE,
    EDIT_COURSE_STATUS_INTAKE,
    DELETE_COURSE_STATUS_INTAKE,
    EXPORT_COURSE_STATUS_INTAKE,
    IMPORT_COURSE_STATUS_INTAKE,
    SCHOLARSHIP_BASED_ON_LIST,
    ADD_SCHOLARSHIP_BASED_ON,
    EDIT_SCHOLARSHIP_BASED_ON,
    DELETE_SCHOLARSHIP_BASED_ON,
    EXPORT_SCHOLARSHIP_BASED_ON,
    IMPORT_SCHOLARSHIP_BASED_ON,
    COURSE_LEVEL_LIST,
    ADD_COURSE_LEVEL,
    EDIT_COURSE_LEVEL,
    DELETE_COURSE_LEVEL,
    EXPORT_COURSE_LEVEL,
    IMPORT_COURSE_LEVEL,
    COURSE_DURATION_LIST,
    ADD_COURSE_DURATION,
    EDIT_COURSE_DURATION,
    DELETE_COURSE_DURATION,
    EXPORT_COURSE_DURATION,
    IMPORT_COURSE_DURATION,

} from "./actionType";

import {
    getInstituteTypeListDataAPI,
    addInstituteTypeDataAPI,
    editInstituteTypeDataAPI,
    deleteInstituteTypeDataAPI,
    exportInstituteTypeDataAPI,
    importInstituteTypeDataAPI,
    getInstituteGroupNameListDataAPI,
    addInstituteGroupNameDataAPI,
    editInstituteGroupNameDataAPI,
    deleteInstituteGroupNameDataAPI,
    exportInstituteGroupNameDataAPI,
    importInstituteGroupNameDataAPI,
    getInstituteStatusListDataAPI,
    addInstituteStatusDataAPI,
    editInstituteStatusDataAPI,
    deleteInstituteStatusDataAPI,
    exportInstituteStatusDataAPI,
    importInstituteStatusDataAPI,
    getInstitutePriorityListDataAPI,
    addInstitutePriorityDataAPI,
    editInstitutePriorityDataAPI,
    deleteInstitutePriorityDataAPI,
    exportInstitutePriorityDataAPI,
    importInstitutePriorityDataAPI,
    getInstituteDepartmentListDataAPI,
    addInstituteDepartmentDataAPI,
    editInstituteDepartmentDataAPI,
    deleteInstituteDepartmentDataAPI,
    exportInstituteDepartmentDataAPI,
    importInstituteDepartmentDataAPI,
    getBankAccountForListDataAPI,
    addBankAccountForDataAPI,
    editBankAccountForDataAPI,
    deleteBankAccountForDataAPI,
    exportBankAccountForDataAPI,
    importBankAccountForDataAPI,
    getWhenCommissionIssueListDataAPI,
    addWhenCommissionIssueDataAPI,
    editWhenCommissionIssueDataAPI,
    deleteWhenCommissionIssueDataAPI,
    exportWhenCommissionIssueDataAPI,
    importWhenCommissionIssueDataAPI,
    getCourseLevelCodeListDataAPI,
    addCourseLevelCodeDataAPI,
    editCourseLevelCodeDataAPI,
    deleteCourseLevelCodeDataAPI,
    exportCourseLevelCodeDataAPI,
    importCourseLevelCodeDataAPI,
    getCourseDividedInListDataAPI,
    addCourseDividedInDataAPI,
    editCourseDividedInDataAPI,
    deleteCourseDividedInDataAPI,
    exportCourseDividedInDataAPI,
    importCourseDividedInDataAPI,
    getCourseStatusListDataAPI,
    addCourseStatusDataAPI,
    editCourseStatusDataAPI,
    deleteCourseStatusDataAPI,
    exportCourseStatusDataAPI,
    importCourseStatusDataAPI,
    getIntakeNameListDataAPI,
    addIntakeNameDataAPI,
    editIntakeNameDataAPI,
    deleteIntakeNameDataAPI,
    exportIntakeNameDataAPI,
    importIntakeNameDataAPI,
    getCourseStatusIntakeListDataAPI,
    addCourseStatusIntakeDataAPI,
    editCourseStatusIntakeDataAPI,
    deleteCourseStatusIntakeDataAPI,
    exportCourseStatusIntakeDataAPI,
    importCourseStatusIntakeDataAPI,
    getScholarshipBasedOnListDataAPI,
    addScholarshipBasedOnDataAPI,
    editScholarshipBasedOnDataAPI,
    deleteScholarshipBasedOnDataAPI,
    exportScholarshipBasedOnDataAPI,
    importScholarshipBasedOnDataAPI,
    getCourseLevelListDataAPI,
    addCourseLevelDataAPI,
    editCourseLevelDataAPI,
    deleteCourseLevelDataAPI,
    exportCourseLevelDataAPI,
    importCourseLevelDataAPI,
    getCourseDurationListDataAPI,
    addCourseDurationDataAPI,
    editCourseDurationDataAPI,
    deleteCourseDurationDataAPI,
    exportCourseDurationDataAPI,
    importCourseDurationDataAPI,
} from "../../../service/api_helper";

// --- INSTITUTE TYPE SAGAS ---
function* instituteTypeListSaga(action) {
    try {
        const response = yield call(getInstituteTypeListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteTypeAddSaga(action) {
    try {
        const response = yield call(addInstituteTypeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteTypeEditSaga(action) {
    try {
        const response = yield call(editInstituteTypeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteTypeDeleteSaga(action) {
    try {
        const response = yield call(deleteInstituteTypeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteTypeExportDataSaga(action) {
    try {
        const response = yield call(exportInstituteTypeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteTypeImportDataSaga(action) {
    try {
        const response = yield call(importInstituteTypeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

// --- INSTITUTE GROUP NAME SAGAS ---
function* instituteGroupNameListSaga(action) {
    try {
        const response = yield call(getInstituteGroupNameListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteGroupNameAddSaga(action) {
    try {
        const response = yield call(addInstituteGroupNameDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteGroupNameEditSaga(action) {
    try {
        const response = yield call(editInstituteGroupNameDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteGroupNameDeleteSaga(action) {
    try {
        const response = yield call(deleteInstituteGroupNameDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteGroupNameExportDataSaga(action) {
    try {
        const response = yield call(exportInstituteGroupNameDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteGroupNameImportDataSaga(action) {
    try {
        const response = yield call(importInstituteGroupNameDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

// --- INSTITUTE STATUS SAGAS ---
function* instituteStatusListSaga(action) {
    try {
        const response = yield call(getInstituteStatusListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteStatusAddSaga(action) {
    try {
        const response = yield call(addInstituteStatusDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteStatusEditSaga(action) {
    try {
        const response = yield call(editInstituteStatusDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteStatusDeleteSaga(action) {
    try {
        const response = yield call(deleteInstituteStatusDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteStatusExportDataSaga(action) {
    try {
        const response = yield call(exportInstituteStatusDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteStatusImportDataSaga(action) {
    try {
        const response = yield call(importInstituteStatusDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

// --- INSTITUTE PRIORITY SAGAS ---
function* institutePriorityListSaga(action) {
    try {
        const response = yield call(getInstitutePriorityListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* institutePriorityAddSaga(action) {
    try {
        const response = yield call(addInstitutePriorityDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* institutePriorityEditSaga(action) {
    try {
        const response = yield call(editInstitutePriorityDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* institutePriorityDeleteSaga(action) {
    try {
        const response = yield call(deleteInstitutePriorityDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* institutePriorityExportDataSaga(action) {
    try {
        const response = yield call(exportInstitutePriorityDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* institutePriorityImportDataSaga(action) {
    try {
        const response = yield call(importInstitutePriorityDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

// --- INSTITUTE DEPARTMENT SAGAS ---
function* instituteDepartmentListSaga(action) {
    try {
        const response = yield call(getInstituteDepartmentListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteDepartmentAddSaga(action) {
    try {
        const response = yield call(addInstituteDepartmentDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteDepartmentEditSaga(action) {
    try {
        const response = yield call(editInstituteDepartmentDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteDepartmentDeleteSaga(action) {
    try {
        const response = yield call(deleteInstituteDepartmentDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteDepartmentExportDataSaga(action) {
    try {
        const response = yield call(exportInstituteDepartmentDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* instituteDepartmentImportDataSaga(action) {
    try {
        const response = yield call(importInstituteDepartmentDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}
// Bank Account For
function* bankAccountForListSaga(action) {
    try {
        const response = yield call(getBankAccountForListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* bankAccountForAddSaga(action) {
    try {
        const response = yield call(addBankAccountForDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* bankAccountForEditSaga(action) {
    try {
        const response = yield call(editBankAccountForDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* bankAccountForDeleteSaga(action) {
    try {
        const response = yield call(deleteBankAccountForDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* bankAccountForExportDataSaga(action) {
    try {
        const response = yield call(exportBankAccountForDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* bankAccountForImportDataSaga(action) {
    try {
        const response = yield call(importBankAccountForDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}
// --- WHEN COMMISSION ISSUE SAGAS ---
function* whenCommissionIssueListSaga(action) {
    try {
        const response = yield call(getWhenCommissionIssueListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* whenCommissionIssueAddSaga(action) {
    try {
        const response = yield call(addWhenCommissionIssueDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* whenCommissionIssueEditSaga(action) {
    try {
        const response = yield call(editWhenCommissionIssueDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* whenCommissionIssueDeleteSaga(action) {
    try {
        const response = yield call(deleteWhenCommissionIssueDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* whenCommissionIssueExportDataSaga(action) {
    try {
        const response = yield call(exportWhenCommissionIssueDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* whenCommissionIssueImportDataSaga(action) {
    try {
        const response = yield call(importWhenCommissionIssueDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}
// --- COURSE LEVEL CODE SAGAS ---
function* courseLevelCodeListSaga(action) {
    try {
        const response = yield call(getCourseLevelCodeListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseLevelCodeAddSaga(action) {
    try {
        const response = yield call(addCourseLevelCodeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseLevelCodeEditSaga(action) {
    try {
        const response = yield call(editCourseLevelCodeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseLevelCodeDeleteSaga(action) {
    try {
        const response = yield call(deleteCourseLevelCodeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseLevelCodeExportDataSaga(action) {
    try {
        const response = yield call(exportCourseLevelCodeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseLevelCodeImportDataSaga(action) {
    try {
        const response = yield call(importCourseLevelCodeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}
// --- COURSE DIVIDED IN SAGAS ---
function* courseDividedInListSaga(action) {
    try {
        const response = yield call(getCourseDividedInListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseDividedInAddSaga(action) {
    try {
        const response = yield call(addCourseDividedInDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseDividedInEditSaga(action) {
    try {
        const response = yield call(editCourseDividedInDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseDividedInDeleteSaga(action) {
    try {
        const response = yield call(deleteCourseDividedInDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseDividedInExportDataSaga(action) {
    try {
        const response = yield call(exportCourseDividedInDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseDividedInImportDataSaga(action) {
    try {
        const response = yield call(importCourseDividedInDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}
// --- COURSE STATUS SAGAS ---
function* courseStatusListSaga(action) {
    try {
        const response = yield call(getCourseStatusListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseStatusAddSaga(action) {
    try {
        const response = yield call(addCourseStatusDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseStatusEditSaga(action) {
    try {
        const response = yield call(editCourseStatusDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseStatusDeleteSaga(action) {
    try {
        const response = yield call(deleteCourseStatusDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseStatusExportDataSaga(action) {
    try {
        const response = yield call(exportCourseStatusDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseStatusImportDataSaga(action) {
    try {
        const response = yield call(importCourseStatusDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}
// Intake Name Sagas
function* intakeNameListSaga(action) {
    try {
        const response = yield call(getIntakeNameListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* intakeNameAddSaga(action) {
    try {
        const response = yield call(addIntakeNameDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* intakeNameEditSaga(action) {
    try {
        const response = yield call(editIntakeNameDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* intakeNameDeleteSaga(action) {
    try {
        const response = yield call(deleteIntakeNameDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* intakeNameExportDataSaga(action) {
    try {
        const response = yield call(exportIntakeNameDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* intakeNameImportDataSaga(action) {
    try {
        const response = yield call(importIntakeNameDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

// Course Status for Intake Sagas
function* courseStatusIntakeListSaga(action) {
    try {
        const response = yield call(getCourseStatusIntakeListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseStatusIntakeAddSaga(action) {
    try {
        const response = yield call(addCourseStatusIntakeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseStatusIntakeEditSaga(action) {
    try {
        const response = yield call(editCourseStatusIntakeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseStatusIntakeDeleteSaga(action) {
    try {
        const response = yield call(deleteCourseStatusIntakeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseStatusIntakeExportDataSaga(action) {
    try {
        const response = yield call(exportCourseStatusIntakeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseStatusIntakeImportDataSaga(action) {
    try {
        const response = yield call(importCourseStatusIntakeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}
// Scholarship Based On Sagas
function* scholarshipBasedOnListSaga(action) {
    try {
        const response = yield call(getScholarshipBasedOnListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* scholarshipBasedOnAddSaga(action) {
    try {
        const response = yield call(addScholarshipBasedOnDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* scholarshipBasedOnEditSaga(action) {
    try {
        const response = yield call(editScholarshipBasedOnDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* scholarshipBasedOnDeleteSaga(action) {
    try {
        const response = yield call(deleteScholarshipBasedOnDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* scholarshipBasedOnExportDataSaga(action) {
    try {
        const response = yield call(exportScholarshipBasedOnDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* scholarshipBasedOnImportDataSaga(action) {
    try {
        const response = yield call(importScholarshipBasedOnDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

// Course Level Sagas
function* courseLevelListSaga(action) {
    try {
        const response = yield call(getCourseLevelListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseLevelAddSaga(action) {
    try {
        const response = yield call(addCourseLevelDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseLevelEditSaga(action) {
    try {
        const response = yield call(editCourseLevelDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseLevelDeleteSaga(action) {
    try {
        const response = yield call(deleteCourseLevelDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseLevelExportDataSaga(action) {
    try {
        const response = yield call(exportCourseLevelDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseLevelImportDataSaga(action) {
    try {
        const response = yield call(importCourseLevelDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}
// Course Duration Sagas
function* courseDurationListSaga(action) {
    try {
        const response = yield call(getCourseDurationListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseDurationAddSaga(action) {
    try {
        const response = yield call(addCourseDurationDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseDurationEditSaga(action) {
    try {
        const response = yield call(editCourseDurationDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseDurationDeleteSaga(action) {
    try {
        const response = yield call(deleteCourseDurationDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseDurationExportDataSaga(action) {
    try {
        const response = yield call(exportCourseDurationDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* courseDurationImportDataSaga(action) {
    try {
        const response = yield call(importCourseDurationDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}


// Root Saga
function* instituteMasterSaga() {
    yield takeEvery(INSTITUTE_TYPE_LIST, instituteTypeListSaga);
    yield takeEvery(ADD_INSTITUTE_TYPE, instituteTypeAddSaga);
    yield takeEvery(EDIT_INSTITUTE_TYPE, instituteTypeEditSaga);
    yield takeEvery(DELETE_INSTITUTE_TYPE, instituteTypeDeleteSaga);
    yield takeEvery(EXPORT_INSTITUTE_TYPE, instituteTypeExportDataSaga);
    yield takeEvery(IMPORT_INSTITUTE_TYPE, instituteTypeImportDataSaga);
    yield takeEvery(INSTITUTE_GROUP_NAME_LIST, instituteGroupNameListSaga);
    yield takeEvery(ADD_INSTITUTE_GROUP_NAME, instituteGroupNameAddSaga);
    yield takeEvery(EDIT_INSTITUTE_GROUP_NAME, instituteGroupNameEditSaga);
    yield takeEvery(DELETE_INSTITUTE_GROUP_NAME, instituteGroupNameDeleteSaga);
    yield takeEvery(EXPORT_INSTITUTE_GROUP_NAME, instituteGroupNameExportDataSaga);
    yield takeEvery(IMPORT_INSTITUTE_GROUP_NAME, instituteGroupNameImportDataSaga);
    yield takeEvery(INSTITUTE_STATUS_LIST, instituteStatusListSaga);
    yield takeEvery(ADD_INSTITUTE_STATUS, instituteStatusAddSaga);
    yield takeEvery(EDIT_INSTITUTE_STATUS, instituteStatusEditSaga);
    yield takeEvery(DELETE_INSTITUTE_STATUS, instituteStatusDeleteSaga);
    yield takeEvery(EXPORT_INSTITUTE_STATUS, instituteStatusExportDataSaga);
    yield takeEvery(IMPORT_INSTITUTE_STATUS, instituteStatusImportDataSaga);
    yield takeEvery(INSTITUTE_PRIORITY_LIST, institutePriorityListSaga);
    yield takeEvery(ADD_INSTITUTE_PRIORITY, institutePriorityAddSaga);
    yield takeEvery(EDIT_INSTITUTE_PRIORITY, institutePriorityEditSaga);
    yield takeEvery(DELETE_INSTITUTE_PRIORITY, institutePriorityDeleteSaga);
    yield takeEvery(EXPORT_INSTITUTE_PRIORITY, institutePriorityExportDataSaga);
    yield takeEvery(IMPORT_INSTITUTE_PRIORITY, institutePriorityImportDataSaga);
    yield takeEvery(INSTITUTE_DEPARTMENT_LIST, instituteDepartmentListSaga);
    yield takeEvery(ADD_INSTITUTE_DEPARTMENT, instituteDepartmentAddSaga);
    yield takeEvery(EDIT_INSTITUTE_DEPARTMENT, instituteDepartmentEditSaga);
    yield takeEvery(DELETE_INSTITUTE_DEPARTMENT, instituteDepartmentDeleteSaga);
    yield takeEvery(EXPORT_INSTITUTE_DEPARTMENT, instituteDepartmentExportDataSaga);
    yield takeEvery(IMPORT_INSTITUTE_DEPARTMENT, instituteDepartmentImportDataSaga);
    yield takeEvery(BANK_ACCOUNT_FOR_LIST, bankAccountForListSaga);
    yield takeEvery(ADD_BANK_ACCOUNT_FOR, bankAccountForAddSaga);
    yield takeEvery(EDIT_BANK_ACCOUNT_FOR, bankAccountForEditSaga);
    yield takeEvery(DELETE_BANK_ACCOUNT_FOR, bankAccountForDeleteSaga);
    yield takeEvery(EXPORT_BANK_ACCOUNT_FOR, bankAccountForExportDataSaga);
    yield takeEvery(IMPORT_BANK_ACCOUNT_FOR, bankAccountForImportDataSaga);
    yield takeEvery(WHEN_COMMISSION_ISSUE_LIST, whenCommissionIssueListSaga);
    yield takeEvery(ADD_WHEN_COMMISSION_ISSUE, whenCommissionIssueAddSaga);
    yield takeEvery(EDIT_WHEN_COMMISSION_ISSUE, whenCommissionIssueEditSaga);
    yield takeEvery(DELETE_WHEN_COMMISSION_ISSUE, whenCommissionIssueDeleteSaga);
    yield takeEvery(EXPORT_WHEN_COMMISSION_ISSUE, whenCommissionIssueExportDataSaga);
    yield takeEvery(IMPORT_WHEN_COMMISSION_ISSUE, whenCommissionIssueImportDataSaga);
    yield takeEvery(COURSE_LEVEL_CODE_LIST, courseLevelCodeListSaga);
    yield takeEvery(ADD_COURSE_LEVEL_CODE, courseLevelCodeAddSaga);
    yield takeEvery(EDIT_COURSE_LEVEL_CODE, courseLevelCodeEditSaga);
    yield takeEvery(DELETE_COURSE_LEVEL_CODE, courseLevelCodeDeleteSaga);
    yield takeEvery(EXPORT_COURSE_LEVEL_CODE, courseLevelCodeExportDataSaga);
    yield takeEvery(IMPORT_COURSE_LEVEL_CODE, courseLevelCodeImportDataSaga);
    yield takeEvery(COURSE_DIVIDED_IN_LIST, courseDividedInListSaga);
    yield takeEvery(ADD_COURSE_DIVIDED_IN, courseDividedInAddSaga);
    yield takeEvery(EDIT_COURSE_DIVIDED_IN, courseDividedInEditSaga);
    yield takeEvery(DELETE_COURSE_DIVIDED_IN, courseDividedInDeleteSaga);
    yield takeEvery(EXPORT_COURSE_DIVIDED_IN, courseDividedInExportDataSaga);
    yield takeEvery(IMPORT_COURSE_DIVIDED_IN, courseDividedInImportDataSaga);
    yield takeEvery(COURSE_STATUS_LIST, courseStatusListSaga);
    yield takeEvery(ADD_COURSE_STATUS, courseStatusAddSaga);
    yield takeEvery(EDIT_COURSE_STATUS, courseStatusEditSaga);
    yield takeEvery(DELETE_COURSE_STATUS, courseStatusDeleteSaga);
    yield takeEvery(EXPORT_COURSE_STATUS, courseStatusExportDataSaga);
    yield takeEvery(IMPORT_COURSE_STATUS, courseStatusImportDataSaga);
    yield takeEvery(INTAKE_NAME_LIST, intakeNameListSaga);
    yield takeEvery(ADD_INTAKE_NAME, intakeNameAddSaga);
    yield takeEvery(EDIT_INTAKE_NAME, intakeNameEditSaga);
    yield takeEvery(DELETE_INTAKE_NAME, intakeNameDeleteSaga);
    yield takeEvery(EXPORT_INTAKE_NAME, intakeNameExportDataSaga);
    yield takeEvery(IMPORT_INTAKE_NAME, intakeNameImportDataSaga);
    yield takeEvery(COURSE_STATUS_INTAKE_LIST, courseStatusIntakeListSaga);
    yield takeEvery(ADD_COURSE_STATUS_INTAKE, courseStatusIntakeAddSaga);
    yield takeEvery(EDIT_COURSE_STATUS_INTAKE, courseStatusIntakeEditSaga);
    yield takeEvery(DELETE_COURSE_STATUS_INTAKE, courseStatusIntakeDeleteSaga);
    yield takeEvery(EXPORT_COURSE_STATUS_INTAKE, courseStatusIntakeExportDataSaga);
    yield takeEvery(IMPORT_COURSE_STATUS_INTAKE, courseStatusIntakeImportDataSaga);
    yield takeEvery(SCHOLARSHIP_BASED_ON_LIST, scholarshipBasedOnListSaga);
    yield takeEvery(ADD_SCHOLARSHIP_BASED_ON, scholarshipBasedOnAddSaga);
    yield takeEvery(EDIT_SCHOLARSHIP_BASED_ON, scholarshipBasedOnEditSaga);
    yield takeEvery(DELETE_SCHOLARSHIP_BASED_ON, scholarshipBasedOnDeleteSaga);
    yield takeEvery(EXPORT_SCHOLARSHIP_BASED_ON, scholarshipBasedOnExportDataSaga);
    yield takeEvery(IMPORT_SCHOLARSHIP_BASED_ON, scholarshipBasedOnImportDataSaga);
    yield takeEvery(COURSE_LEVEL_LIST, courseLevelListSaga);
    yield takeEvery(ADD_COURSE_LEVEL, courseLevelAddSaga);
    yield takeEvery(EDIT_COURSE_LEVEL, courseLevelEditSaga);
    yield takeEvery(DELETE_COURSE_LEVEL, courseLevelDeleteSaga);
    yield takeEvery(EXPORT_COURSE_LEVEL, courseLevelExportDataSaga);
    yield takeEvery(IMPORT_COURSE_LEVEL, courseLevelImportDataSaga);
    yield takeEvery(COURSE_DURATION_LIST, courseDurationListSaga);
    yield takeEvery(ADD_COURSE_DURATION, courseDurationAddSaga);
    yield takeEvery(EDIT_COURSE_DURATION, courseDurationEditSaga);
    yield takeEvery(DELETE_COURSE_DURATION, courseDurationDeleteSaga);
    yield takeEvery(EXPORT_COURSE_DURATION, courseDurationExportDataSaga);
    yield takeEvery(IMPORT_COURSE_DURATION, courseDurationImportDataSaga);


}
export default instituteMasterSaga;