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


// Institute Type Actions
export const instituteTypeList = (data, callback) => ({
    type: INSTITUTE_TYPE_LIST,
    data,
    callback,
});

export const instituteTypeAdd = (data, callback) => ({
    type: ADD_INSTITUTE_TYPE,
    data,
    callback,
});

export const instituteTypeEdit = (data, callback) => ({
    type: EDIT_INSTITUTE_TYPE,
    data,
    callback,
});

export const instituteTypeDelete = (data, callback) => ({
    type: DELETE_INSTITUTE_TYPE,
    data,
    callback,
});

export const instituteTypeExportData = (data, callback) => ({
    type: EXPORT_INSTITUTE_TYPE,
    data,
    callback,
});

export const instituteTypeImportData = (data, callback) => ({
    type: IMPORT_INSTITUTE_TYPE,
    data,
    callback,
});

// Institute Group Name Actions
export const instituteGroupNameList = (data, callback) => ({
    type: INSTITUTE_GROUP_NAME_LIST,
    data,
    callback,
});

export const instituteGroupNameAdd = (data, callback) => ({
    type: ADD_INSTITUTE_GROUP_NAME,
    data,
    callback,
});

export const instituteGroupNameEdit = (data, callback) => ({
    type: EDIT_INSTITUTE_GROUP_NAME,
    data,
    callback,
});

export const instituteGroupNameDelete = (data, callback) => ({
    type: DELETE_INSTITUTE_GROUP_NAME,
    data,
    callback,
});

export const instituteGroupNameExportData = (data, callback) => ({
    type: EXPORT_INSTITUTE_GROUP_NAME,
    data,
    callback,
});

export const instituteGroupNameImportData = (data, callback) => ({
    type: IMPORT_INSTITUTE_GROUP_NAME,
    data,
    callback,
});

// Institute Status Actions
export const instituteStatusList = (data, callback) => ({
    type: INSTITUTE_STATUS_LIST,
    data,
    callback,
});

export const instituteStatusAdd = (data, callback) => ({
    type: ADD_INSTITUTE_STATUS,
    data,
    callback,
});

export const instituteStatusEdit = (data, callback) => ({
    type: EDIT_INSTITUTE_STATUS,
    data,
    callback,
});

export const instituteStatusDelete = (data, callback) => ({
    type: DELETE_INSTITUTE_STATUS,
    data,
    callback,
});

export const instituteStatusExportData = (data, callback) => ({
    type: EXPORT_INSTITUTE_STATUS,
    data,
    callback,
});

export const instituteStatusImportData = (data, callback) => ({
    type: IMPORT_INSTITUTE_STATUS,
    data,
    callback,
});

// Institute Priority Actions
export const institutePriorityList = (data, callback) => ({
    type: INSTITUTE_PRIORITY_LIST,
    data,
    callback,
});

export const institutePriorityAdd = (data, callback) => ({
    type: ADD_INSTITUTE_PRIORITY,
    data,
    callback,
});

export const institutePriorityEdit = (data, callback) => ({
    type: EDIT_INSTITUTE_PRIORITY,
    data,
    callback,
});

export const institutePriorityDelete = (data, callback) => ({
    type: DELETE_INSTITUTE_PRIORITY,
    data,
    callback,
});

export const institutePriorityExportData = (data, callback) => ({
    type: EXPORT_INSTITUTE_PRIORITY,
    data,
    callback,
});

export const institutePriorityImportData = (data, callback) => ({
    type: IMPORT_INSTITUTE_PRIORITY,
    data,
    callback,
});

// Institute Department Actions
export const instituteDepartmentList = (data, callback) => ({
    type: INSTITUTE_DEPARTMENT_LIST,
    data,
    callback,
});

export const instituteDepartmentAdd = (data, callback) => ({
    type: ADD_INSTITUTE_DEPARTMENT,
    data,
    callback,
});

export const instituteDepartmentEdit = (data, callback) => ({
    type: EDIT_INSTITUTE_DEPARTMENT,
    data,
    callback,
});

export const instituteDepartmentDelete = (data, callback) => ({
    type: DELETE_INSTITUTE_DEPARTMENT,
    data,
    callback,
});

export const instituteDepartmentExportData = (data, callback) => ({
    type: EXPORT_INSTITUTE_DEPARTMENT,
    data,
    callback,
});

export const instituteDepartmentImportData = (data, callback) => ({
    type: IMPORT_INSTITUTE_DEPARTMENT,
    data,
    callback,
});

// Bank Account For
export const bankAccountForList = (data, callback) => ({
    type: BANK_ACCOUNT_FOR_LIST,
    data,
    callback,
});

export const bankAccountForAdd = (data, callback) => ({
    type: ADD_BANK_ACCOUNT_FOR,
    data,
    callback,
});

export const bankAccountForEdit = (data, callback) => ({
    type: EDIT_BANK_ACCOUNT_FOR,
    data,
    callback,
});

export const bankAccountForDelete = (data, callback) => ({
    type: DELETE_BANK_ACCOUNT_FOR,
    data,
    callback,
});

export const bankAccountForExportData = (data, callback) => ({
    type: EXPORT_BANK_ACCOUNT_FOR,
    data,
    callback,
});

export const bankAccountForImportData = (data, callback) => ({
    type: IMPORT_BANK_ACCOUNT_FOR,
    data,
    callback,
});
// When Commission Issue Actions
export const whenCommissionIssueList = (data, callback) => ({
    type: WHEN_COMMISSION_ISSUE_LIST,
    data,
    callback,
});

export const whenCommissionIssueAdd = (data, callback) => ({
    type: ADD_WHEN_COMMISSION_ISSUE,
    data,
    callback,
});

export const whenCommissionIssueEdit = (data, callback) => ({
    type: EDIT_WHEN_COMMISSION_ISSUE,
    data,
    callback,
});

export const whenCommissionIssueDelete = (data, callback) => ({
    type: DELETE_WHEN_COMMISSION_ISSUE,
    data,
    callback,
});

export const whenCommissionIssueExportData = (data, callback) => ({
    type: EXPORT_WHEN_COMMISSION_ISSUE,
    data,
    callback,
});

export const whenCommissionIssueImportData = (data, callback) => ({
    type: IMPORT_WHEN_COMMISSION_ISSUE,
    data,
    callback,
});
// Course Level Code Actions
export const courseLevelCodeList = (data, callback) => ({
    type: COURSE_LEVEL_CODE_LIST,
    data,
    callback,
});

export const courseLevelCodeAdd = (data, callback) => ({
    type: ADD_COURSE_LEVEL_CODE,
    data,
    callback,
});

export const courseLevelCodeEdit = (data, callback) => ({
    type: EDIT_COURSE_LEVEL_CODE,
    data,
    callback,
});

export const courseLevelCodeDelete = (data, callback) => ({
    type: DELETE_COURSE_LEVEL_CODE,
    data,
    callback,
});

export const courseLevelCodeExportData = (data, callback) => ({
    type: EXPORT_COURSE_LEVEL_CODE,
    data,
    callback,
});

export const courseLevelCodeImportData = (data, callback) => ({
    type: IMPORT_COURSE_LEVEL_CODE,
    data,
    callback,
});
// Course Divided In Actions
export const courseDividedInList = (data, callback) => ({
    type: COURSE_DIVIDED_IN_LIST,
    data,
    callback,
});

export const courseDividedInAdd = (data, callback) => ({
    type: ADD_COURSE_DIVIDED_IN,
    data,
    callback,
});

export const courseDividedInEdit = (data, callback) => ({
    type: EDIT_COURSE_DIVIDED_IN,
    data,
    callback,
});

export const courseDividedInDelete = (data, callback) => ({
    type: DELETE_COURSE_DIVIDED_IN,
    data,
    callback,
});

export const courseDividedInExportData = (data, callback) => ({
    type: EXPORT_COURSE_DIVIDED_IN,
    data,
    callback,
});

export const courseDividedInImportData = (data, callback) => ({
    type: IMPORT_COURSE_DIVIDED_IN,
    data,
    callback,
});
// Course Status Actions
export const courseStatusList = (data, callback) => ({
    type: COURSE_STATUS_LIST,
    data,
    callback,
});

export const courseStatusAdd = (data, callback) => ({
    type: ADD_COURSE_STATUS,
    data,
    callback,
});

export const courseStatusEdit = (data, callback) => ({
    type: EDIT_COURSE_STATUS,
    data,
    callback,
});

export const courseStatusDelete = (data, callback) => ({
    type: DELETE_COURSE_STATUS,
    data,
    callback,
});

export const courseStatusExportData = (data, callback) => ({
    type: EXPORT_COURSE_STATUS,
    data,
    callback,
});

export const courseStatusImportData = (data, callback) => ({
    type: IMPORT_COURSE_STATUS,
    data,
    callback,
});

// Intake Name Actions
export const intakeNameList = (data, callback) => ({
    type: INTAKE_NAME_LIST,
    data,
    callback,
});

export const intakeNameAdd = (data, callback) => ({
    type: ADD_INTAKE_NAME,
    data,
    callback,
});

export const intakeNameEdit = (data, callback) => ({
    type: EDIT_INTAKE_NAME,
    data,
    callback,
});

export const intakeNameDelete = (data, callback) => ({
    type: DELETE_INTAKE_NAME,
    data,
    callback,
});

export const intakeNameExportData = (data, callback) => ({
    type: EXPORT_INTAKE_NAME,
    data,
    callback,
});

export const intakeNameImportData = (data, callback) => ({
    type: IMPORT_INTAKE_NAME,
    data,
    callback,
});
// Course Status for Intake Actions
export const courseStatusIntakeList = (data, callback) => ({
    type: COURSE_STATUS_INTAKE_LIST,
    data,
    callback,
});

export const courseStatusIntakeAdd = (data, callback) => ({
    type: ADD_COURSE_STATUS_INTAKE,
    data,
    callback,
});

export const courseStatusIntakeEdit = (data, callback) => ({
    type: EDIT_COURSE_STATUS_INTAKE,
    data,
    callback,
});

export const courseStatusIntakeDelete = (data, callback) => ({
    type: DELETE_COURSE_STATUS_INTAKE,
    data,
    callback,
});

export const courseStatusIntakeExportData = (data, callback) => ({
    type: EXPORT_COURSE_STATUS_INTAKE,
    data,
    callback,
});

export const courseStatusIntakeImportData = (data, callback) => ({
    type: IMPORT_COURSE_STATUS_INTAKE,
    data,
    callback,
});
// Scholarship Based On Actions
export const scholarshipBasedOnList = (data, callback) => ({
    type: SCHOLARSHIP_BASED_ON_LIST,
    data,
    callback,
});

export const scholarshipBasedOnAdd = (data, callback) => ({
    type: ADD_SCHOLARSHIP_BASED_ON,
    data,
    callback,
});

export const scholarshipBasedOnEdit = (data, callback) => ({
    type: EDIT_SCHOLARSHIP_BASED_ON,
    data,
    callback,
});

export const scholarshipBasedOnDelete = (data, callback) => ({
    type: DELETE_SCHOLARSHIP_BASED_ON,
    data,
    callback,
});

export const scholarshipBasedOnExportData = (data, callback) => ({
    type: EXPORT_SCHOLARSHIP_BASED_ON,
    data,
    callback,
});

export const scholarshipBasedOnImportData = (data, callback) => ({
    type: IMPORT_SCHOLARSHIP_BASED_ON,
    data,
    callback,
});
// Course Level Actions
export const courseLevelList = (data, callback) => ({
    type: COURSE_LEVEL_LIST,
    data,
    callback,
});

export const courseLevelAdd = (data, callback) => ({
    type: ADD_COURSE_LEVEL,
    data,
    callback,
});

export const courseLevelEdit = (data, callback) => ({
    type: EDIT_COURSE_LEVEL,
    data,
    callback,
});

export const courseLevelDelete = (data, callback) => ({
    type: DELETE_COURSE_LEVEL,
    data,
    callback,
});

export const courseLevelExportData = (data, callback) => ({
    type: EXPORT_COURSE_LEVEL,
    data,
    callback,
});

export const courseLevelImportData = (data, callback) => ({
    type: IMPORT_COURSE_LEVEL,
    data,
    callback,
});
// Course Duration Actions
export const courseDurationList = (data, callback) => ({
    type: COURSE_DURATION_LIST,
    data,
    callback,
});

export const courseDurationAdd = (data, callback) => ({
    type: ADD_COURSE_DURATION,
    data,
    callback,
});

export const courseDurationEdit = (data, callback) => ({
    type: EDIT_COURSE_DURATION,
    data,
    callback,
});

export const courseDurationDelete = (data, callback) => ({
    type: DELETE_COURSE_DURATION,
    data,
    callback,
});

export const courseDurationExportData = (data, callback) => ({
    type: EXPORT_COURSE_DURATION,
    data,
    callback,
});

export const courseDurationImportData = (data, callback) => ({
    type: IMPORT_COURSE_DURATION,
    data,
    callback,
});












