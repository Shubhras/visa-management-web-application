import {
    REPRESENTING_COUNTRY_LIST,
    ADD_REPRESENTING_COUNTRY,
    EDIT_REPRESENTING_COUNTRY,
    DELETE_REPRESENTING_COUNTRY,
    EXPORT_REPRESENTING_COUNTRY,
    IMPORT_REPRESENTING_COUNTRY,
    VISA_MAJOR_CATEGORY_LIST,
    ADD_VISA_MAJOR_CATEGORY,
    EDIT_VISA_MAJOR_CATEGORY,
    DELETE_VISA_MAJOR_CATEGORY,
    EXPORT_VISA_MAJOR_CATEGORY,
    IMPORT_VISA_MAJOR_CATEGORY,
    APPLICANT_TYPE_LIST,
    ADD_APPLICANT_TYPE,
    EDIT_APPLICANT_TYPE,
    DELETE_APPLICANT_TYPE,
    EXPORT_APPLICANT_TYPE,
    IMPORT_APPLICANT_TYPE,
    VISA_ELIGIBILITY_TYPE_LIST,
    ADD_VISA_ELIGIBILITY_TYPE,
    EDIT_VISA_ELIGIBILITY_TYPE,
    DELETE_VISA_ELIGIBILITY_TYPE,
    EXPORT_VISA_ELIGIBILITY_TYPE,
    IMPORT_VISA_ELIGIBILITY_TYPE,
    VISA_STATUS_LIST,
    ADD_VISA_STATUS,
    EDIT_VISA_STATUS,
    DELETE_VISA_STATUS,
    EXPORT_VISA_STATUS,
    IMPORT_VISA_STATUS,
    POSSIBILITY_LEVEL_LIST,
    ADD_POSSIBILITY_LEVEL,
    EDIT_POSSIBILITY_LEVEL,
    DELETE_POSSIBILITY_LEVEL,
    EXPORT_POSSIBILITY_LEVEL,
    IMPORT_POSSIBILITY_LEVEL,
    VISA_NAME_LIST,
    ADD_VISA_NAME,
    EDIT_VISA_NAME,
    DELETE_VISA_NAME,
    EXPORT_VISA_NAME,
    IMPORT_VISA_NAME,

} from "./actionType";


// Representing Country Actions
export const representingCountryData = (data, callback) => ({
    type: REPRESENTING_COUNTRY_LIST,
    data,
    callback,
});

export const representingCountryAdd = (data, callback) => ({
    type: ADD_REPRESENTING_COUNTRY,
    data,
    callback,
});

export const representingCountryEdit = (data, callback) => ({
    type: EDIT_REPRESENTING_COUNTRY,
    data,
    callback,
});

export const representingCountryDelete = (data, callback) => ({
    type: DELETE_REPRESENTING_COUNTRY,
    data,
    callback,
});

export const representingCountryExportData = (data, callback) => ({
    type: EXPORT_REPRESENTING_COUNTRY,
    data,
    callback,
});

export const representingCountryImportData = (data, callback) => ({
    type: IMPORT_REPRESENTING_COUNTRY,
    data,
    callback,
});
export const visaMajorCategoryList = (data, callback) => ({
    type: VISA_MAJOR_CATEGORY_LIST,
    data,
    callback,
});

export const visaMajorCategoryAdd = (data, callback) => ({
    type: ADD_VISA_MAJOR_CATEGORY,
    data,
    callback,
});

export const visaMajorCategoryEdit = (data, callback) => ({
    type: EDIT_VISA_MAJOR_CATEGORY,
    data,
    callback,
});

export const visaMajorCategoryDelete = (data, callback) => ({
    type: DELETE_VISA_MAJOR_CATEGORY,
    data,
    callback,
});

export const visaMajorCategoryExportData = (data, callback) => ({
    type: EXPORT_VISA_MAJOR_CATEGORY,
    data,
    callback,
});

export const visaMajorCategoryImportData = (data, callback) => ({
    type: IMPORT_VISA_MAJOR_CATEGORY,
    data,
    callback,
});
// Applicant Type
export const applicantTypeList = (data, callback) => ({
    type: APPLICANT_TYPE_LIST,
    data,
    callback,
});

export const applicantTypeAdd = (data, callback) => ({
    type: ADD_APPLICANT_TYPE,
    data,
    callback,
});

export const applicantTypeEdit = (data, callback) => ({
    type: EDIT_APPLICANT_TYPE,
    data,
    callback,
});

export const applicantTypeDelete = (data, callback) => ({
    type: DELETE_APPLICANT_TYPE,
    data,
    callback,
});

export const applicantTypeExportData = (data, callback) => ({
    type: EXPORT_APPLICANT_TYPE,
    data,
    callback,
});

export const applicantTypeImportData = (data, callback) => ({
    type: IMPORT_APPLICANT_TYPE,
    data,
    callback,
});
// VISA ELIGIBILITY TYPE
export const visaEligibilityTypeList = (data, callback) => ({
    type: VISA_ELIGIBILITY_TYPE_LIST,
    data,
    callback,
});

export const visaEligibilityTypeAdd = (data, callback) => ({
    type: ADD_VISA_ELIGIBILITY_TYPE,
    data,
    callback,
});

export const visaEligibilityTypeEdit = (data, callback) => ({
    type: EDIT_VISA_ELIGIBILITY_TYPE,
    data,
    callback,
});

export const visaEligibilityTypeDelete = (data, callback) => ({
    type: DELETE_VISA_ELIGIBILITY_TYPE,
    data,
    callback,
});

export const visaEligibilityTypeExportData = (data, callback) => ({
    type: EXPORT_VISA_ELIGIBILITY_TYPE,
    data,
    callback,
});

export const visaEligibilityTypeImportData = (data, callback) => ({
    type: IMPORT_VISA_ELIGIBILITY_TYPE,
    data,
    callback,
});
// VISA STATUS
export const visaStatusList = (data, callback) => ({
    type: VISA_STATUS_LIST,
    data,
    callback,
});

export const visaStatusAdd = (data, callback) => ({
    type: ADD_VISA_STATUS,
    data,
    callback,
});

export const visaStatusEdit = (data, callback) => ({
    type: EDIT_VISA_STATUS,
    data,
    callback,
});

export const visaStatusDelete = (data, callback) => ({
    type: DELETE_VISA_STATUS,
    data,
    callback,
});

export const visaStatusExportData = (data, callback) => ({
    type: EXPORT_VISA_STATUS,
    data,
    callback,
});

export const visaStatusImportData = (data, callback) => ({
    type: IMPORT_VISA_STATUS,
    data,
    callback,
});
// POSSIBILITY LEVEL
export const possibilityLevelList = (data, callback) => ({
    type: POSSIBILITY_LEVEL_LIST,
    data,
    callback,
});

export const possibilityLevelAdd = (data, callback) => ({
    type: ADD_POSSIBILITY_LEVEL,
    data,
    callback,
});

export const possibilityLevelEdit = (data, callback) => ({
    type: EDIT_POSSIBILITY_LEVEL,
    data,
    callback,
});

export const possibilityLevelDelete = (data, callback) => ({
    type: DELETE_POSSIBILITY_LEVEL,
    data,
    callback,
});

export const possibilityLevelExportData = (data, callback) => ({
    type: EXPORT_POSSIBILITY_LEVEL,
    data,
    callback,
});

export const possibilityLevelImportData = (data, callback) => ({
    type: IMPORT_POSSIBILITY_LEVEL,
    data,
    callback,
});
// ---------------- VISA NAME ----------------
export const visaNameList = (data, callback) => ({
    type: VISA_NAME_LIST,
    data,
    callback,
});

export const visaNameAdd = (data, callback) => ({
    type: ADD_VISA_NAME,
    data,
    callback,
});

export const visaNameEdit = (data, callback) => ({
    type: EDIT_VISA_NAME,
    data,
    callback,
});

export const visaNameDelete = (data, callback) => ({
    type: DELETE_VISA_NAME,
    data,
    callback,
});

export const visaNameExportData = (data, callback) => ({
    type: EXPORT_VISA_NAME,
    data,
    callback,
});

export const visaNameImportData = (data, callback) => ({
    type: IMPORT_VISA_NAME,
    data,
    callback,
});




