// import axios from "axios";

import * as url from "./api_url";
import { get, post, put, del, delWithPayload, getExportData } from "./api_service";

// auth
export const postLogin = data => post(url.POST_LOGIN, data);
export const logoutUserAPI = (data) => post(url.POST_LOGOUT, data)


export const getDepartmentListDataAPI = (data) => {
    const apiUrl = `${url.GET_DEPARTMENT_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl)
};

export const addDepartmentDataAPI = (payload) => {
    const apiUrl = `${url.ADD_DEPARTMENT_API}`;
    return post(apiUrl, payload);
};

export const editDepartmentDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_DEPARTMENT_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteDepartmentDataAPI = (payload) => {
    const prapareDATA = {
        id: payload
    }
    const apiUrl = `${url.DELETE_DEPARTMENT_API}delete/`;
    return delWithPayload(apiUrl, prapareDATA);
};


export const exportDepartmentDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_DEPARTMENT_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importDepartmentDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_DEPARTMENT_API}`;
    return post(apiUrl, payload);
};



//EMPLOYEE_TYPE 
export const getEmployeeTypeListDataAPI = (data) => {
    const apiUrl = `${url.GET_EMPLOYEE_TYPE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl)
};

export const addEmployeeTypeDataAPI = (payload) => {
    const apiUrl = `${url.ADD_EMPLOYEE_TYPE_API}`;
    return post(apiUrl, payload);
};

export const editEmployeeTypeDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_EMPLOYEE_TYPE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteEmployeeTypeDataAPI = (payload) => {
    const prapareDATA = {
        id: payload
    }
    const apiUrl = `${url.DELETE_EMPLOYEE_TYPE_API}delete/`;
    return delWithPayload(apiUrl, prapareDATA);
};


export const exportEmployeeTypeDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_EMPLOYEE_TYPE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importEmployeeTypeDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_EMPLOYEE_TYPE_API}`;
    return post(apiUrl, payload);
};

//Company Type
export const getCompanyListDataAPI = (data) => {
    const apiUrl = `${url.GET_COMPANY_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl)

};

export const addCompanyDataAPI = (payload) => {
    const apiUrl = `${url.ADD_COMPANY_API}`;
    return post(apiUrl, payload);

};

export const editCompanyDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_COMPANY_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);

};

export const deleteCompanyDataAPI = (payload) => {
    const prapareDATA = {
        id: payload
    }
    const apiUrl = `${url.DELETE_COMPANY_API}delete/`;
    return delWithPayload(apiUrl, prapareDATA);
};


export const exportCompanyDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_COMPANY_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importCompanyDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_COMPANY_API}`;
    return post(apiUrl, payload);

};

// STAKEHOLDER_CATEGORY
export const getStakeholderCategoryListDataAPI = (data) => {
    const apiUrl = `${url.GET_STAKEHOLDER_CATEGORY_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addStakeholderCategoryDataAPI = (payload) => {
    const apiUrl = `${url.ADD_STAKEHOLDER_CATEGORY_API}`;
    return post(apiUrl, payload);
};

export const editStakeholderCategoryDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_STAKEHOLDER_CATEGORY_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteStakeholderCategoryDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_STAKEHOLDER_CATEGORY_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportStakeholderCategoryDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_STAKEHOLDER_CATEGORY_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importStakeholderCategoryDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_STAKEHOLDER_CATEGORY_API}`;
    return post(apiUrl, payload);
};

// PRIORITY_TYPE
export const getPriorityTypeListDataAPI = (data) => {
    const apiUrl = `${url.GET_PRIORITY_TYPE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addPriorityTypeDataAPI = (payload) => {
    const apiUrl = `${url.ADD_PRIORITY_TYPE_API}`;
    return post(apiUrl, payload);
};

export const editPriorityTypeDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_PRIORITY_TYPE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deletePriorityTypeDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_PRIORITY_TYPE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportPriorityTypeDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_PRIORITY_TYPE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importPriorityTypeDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_PRIORITY_TYPE_API}`;
    return post(apiUrl, payload);
};

// TAGS_TYPE
export const getTagsTypeListDataAPI = (data) => {
    const apiUrl = `${url.GET_TAGS_TYPE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addTagsTypeDataAPI = (payload) => {
    const apiUrl = `${url.ADD_TAGS_TYPE_API}`;
    return post(apiUrl, payload);
};

export const editTagsTypeDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_TAGS_TYPE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteTagsTypeDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_TAGS_TYPE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportTagsTypeDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_TAGS_TYPE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importTagsTypeDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_TAGS_TYPE_API}`;
    return post(apiUrl, payload);
};

// ACTIVITY_TYPE
export const getActivityTypeListDataAPI = (data) => {
    const apiUrl = `${url.GET_ACTIVITY_TYPE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addActivityTypeDataAPI = (payload) => {
    const apiUrl = `${url.ADD_ACTIVITY_TYPE_API}`;
    return post(apiUrl, payload);
};

export const editActivityTypeDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_ACTIVITY_TYPE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteActivityTypeDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_ACTIVITY_TYPE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportActivityTypeDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_ACTIVITY_TYPE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importActivityTypeDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_ACTIVITY_TYPE_API}`;
    return post(apiUrl, payload);
};


// LOST_REASON_B2C
export const getLostReasonB2CListDataAPI = (data) => {
    const apiUrl = `${url.GET_LOST_REASON_B2C_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addLostReasonB2CDataAPI = (payload) => {
    const apiUrl = `${url.ADD_LOST_REASON_B2C_API}`;
    return post(apiUrl, payload);
};

export const editLostReasonB2CDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_LOST_REASON_B2C_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteLostReasonB2CDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_LOST_REASON_B2C_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportLostReasonB2CDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_LOST_REASON_B2C_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importLostReasonB2CDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_LOST_REASON_B2C_API}`;
    return post(apiUrl, payload);
};

// LOST_REASON_B2B
export const getLostReasonB2BListDataAPI = (data) => {
    const apiUrl = `${url.GET_LOST_REASON_B2B_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addLostReasonB2BDataAPI = (payload) => {
    const apiUrl = `${url.ADD_LOST_REASON_B2B_API}`;
    return post(apiUrl, payload);
};

export const editLostReasonB2BDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_LOST_REASON_B2B_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteLostReasonB2BDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_LOST_REASON_B2B_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportLostReasonB2BDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_LOST_REASON_B2B_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importLostReasonB2BDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_LOST_REASON_B2B_API}`;
    return post(apiUrl, payload);
};
// LEAD_SOURCE
export const getLeadSourceListDataAPI = (data) => {
    const apiUrl = `${url.GET_LEAD_SOURCE_LIST_API}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addLeadSourceDataAPI = (payload) => {
    const apiUrl = `${url.ADD_LEAD_SOURCE_API}`;
    return post(apiUrl, payload);
};

export const editLeadSourceDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_LEAD_SOURCE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteLeadSourceDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_LEAD_SOURCE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportLeadSourceDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_LEAD_SOURCE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importLeadSourceDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_LEAD_SOURCE_API}`;
    return post(apiUrl, payload);
};

// INTEREST_LEVEL
export const getInterestLevelListDataAPI = (data) => {
    const apiUrl = `${url.GET_INTEREST_LEVEL_LIST_API}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addInterestLevelDataAPI = (payload) => {
    const apiUrl = `${url.ADD_INTEREST_LEVEL_API}`;
    return post(apiUrl, payload);
};

export const editInterestLevelDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_INTEREST_LEVEL_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteInterestLevelDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_INTEREST_LEVEL_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportInterestLevelDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_INTEREST_LEVEL_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importInterestLevelDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_INTEREST_LEVEL_API}`;
    return post(apiUrl, payload);
};
// BANK_ACCOUNT_TYPE
export const getBankAccountTypeListDataAPI = (data) => {
    const apiUrl = `${url.GET_BANK_ACCOUNT_TYPE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addBankAccountTypeDataAPI = (payload) => {
    const apiUrl = `${url.ADD_BANK_ACCOUNT_TYPE_API}`;
    return post(apiUrl, payload);
};

export const editBankAccountTypeDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_BANK_ACCOUNT_TYPE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteBankAccountTypeDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_BANK_ACCOUNT_TYPE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportBankAccountTypeDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_BANK_ACCOUNT_TYPE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importBankAccountTypeDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_BANK_ACCOUNT_TYPE_API}`;
    return post(apiUrl, payload);
};

// GENDER
export const getGenderListDataAPI = (data) => {
    const apiUrl = `${url.GET_GENDER_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addGenderDataAPI = (payload) => {
    const apiUrl = `${url.ADD_GENDER_API}`;
    return post(apiUrl, payload);
};

export const editGenderDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_GENDER_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteGenderDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_GENDER_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportGenderDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_GENDER_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importGenderDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_GENDER_API}`;
    return post(apiUrl, payload);
};


// MARITAL STATUS
export const getMaritalStatusListDataAPI = (data) => {
    const apiUrl = `${url.GET_MARITAL_STATUS_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addMaritalStatusDataAPI = (payload) => {
    const apiUrl = `${url.ADD_MARITAL_STATUS_API}`;
    return post(apiUrl, payload);
};

export const editMaritalStatusDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_MARITAL_STATUS_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteMaritalStatusDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_MARITAL_STATUS_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportMaritalStatusDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_MARITAL_STATUS_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importMaritalStatusDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_MARITAL_STATUS_API}`;
    return post(apiUrl, payload);
};

// STAKEHOLDER_TYPE
export const getStakeholderTypeListDataAPI = (data) => {
    const apiUrl = `${url.GET_STAKEHOLDER_TYPE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addStakeholderTypeDataAPI = (payload) => {
    const apiUrl = `${url.ADD_STAKEHOLDER_TYPE_API}`;
    return post(apiUrl, payload);
};

export const editStakeholderTypeDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_STAKEHOLDER_TYPE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteStakeholderTypeDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_STAKEHOLDER_TYPE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportStakeholderTypeDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_STAKEHOLDER_TYPE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importStakeholderTypeDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_STAKEHOLDER_TYPE_API}`;
    return post(apiUrl, payload);
};

// OWNERSHIP_TYPE
export const getOwnershipTypeListDataAPI = (data) => {
    const apiUrl = `${url.GET_OWNERSHIP_TYPE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addOwnershipTypeDataAPI = (payload) => {
    const apiUrl = `${url.ADD_OWNERSHIP_TYPE_API}`;
    return post(apiUrl, payload);
};

export const editOwnershipTypeDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_OWNERSHIP_TYPE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteOwnershipTypeDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_OWNERSHIP_TYPE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportOwnershipTypeDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_OWNERSHIP_TYPE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importOwnershipTypeDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_OWNERSHIP_TYPE_API}`;
    return post(apiUrl, payload);
};

// ACCREDITATION_CATEGORY
export const getAccreditationCategoryListDataAPI = (data) => {
    const apiUrl = `${url.GET_ACCREDITATION_CATEGORY_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addAccreditationCategoryDataAPI = (payload) => {
    const apiUrl = `${url.ADD_ACCREDITATION_CATEGORY_API}`;
    return post(apiUrl, payload);
};

export const editAccreditationCategoryDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_ACCREDITATION_CATEGORY_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteAccreditationCategoryDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_ACCREDITATION_CATEGORY_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportAccreditationCategoryDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_ACCREDITATION_CATEGORY_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importAccreditationCategoryDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_ACCREDITATION_CATEGORY_API}`;
    return post(apiUrl, payload);
};

// LICENCE_NAME
export const getLicenceNameListDataAPI = (data) => {
    const apiUrl = `${url.GET_LICENCE_NAME_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addLicenceNameDataAPI = (payload) => {
    const apiUrl = `${url.ADD_LICENCE_NAME_API}`;
    return post(apiUrl, payload);
};

export const editLicenceNameDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_LICENCE_NAME_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteLicenceNameDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_LICENCE_NAME_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportLicenceNameDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_LICENCE_NAME_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importLicenceNameDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_LICENCE_NAME_API}`;
    return post(apiUrl, payload);
};

// ACCREDITATION_NAME
export const getAccreditationNameListDataAPI = (data) => {
    const apiUrl = `${url.GET_ACCREDITATION_NAME_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addAccreditationNameDataAPI = (payload) => {
    const apiUrl = `${url.ADD_ACCREDITATION_NAME_API}`;
    return post(apiUrl, payload);
};

export const editAccreditationNameDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_ACCREDITATION_NAME_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteAccreditationNameDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_ACCREDITATION_NAME_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportAccreditationNameDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_ACCREDITATION_NAME_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importAccreditationNameDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_ACCREDITATION_NAME_API}`;
    return post(apiUrl, payload);
};

// export const getCountryListDataAPI = (data) => {
//     const apiUrl = `${url.GET_COUNTRY_LIST_DEMO}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
//     return get(apiUrl);
// };

//education level code
export const getEducationLevelCodeListDataAPI = (data) => {
    const apiUrl = `${url.GET_EDUCATION_LEVEL_CODE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addEducationLevelCodeDataAPI = (payload) => {
    const apiUrl = `${url.ADD_EDUCATION_LEVEL_CODE_API}`;
    return post(apiUrl, payload);
};

export const editEducationLevelCodeDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_EDUCATION_LEVEL_CODE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteEducationLevelCodeDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_EDUCATION_LEVEL_CODE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportEducationLevelCodeDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_EDUCATION_LEVEL_CODE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importEducationLevelCodeDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_EDUCATION_LEVEL_CODE_API}`;
    return post(apiUrl, payload);
};

// EDUCATION_LEVEL
export const getEducationLevelListDataAPI = (data) => {
    const apiUrl = `${url.GET_EDUCATION_LEVEL_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addEducationLevelDataAPI = (payload) => {
    const apiUrl = `${url.ADD_EDUCATION_LEVEL_API}`;
    return post(apiUrl, payload);
};

export const editEducationLevelDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_EDUCATION_LEVEL_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteEducationLevelDataAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_EDUCATION_LEVEL_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportEducationLevelDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_EDUCATION_LEVEL_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importEducationLevelDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_EDUCATION_LEVEL_API}`;
    return post(apiUrl, payload);
};

//Study main area
export const getStudyMainAreaListDataAPI = (data) => {
    const apiUrl = `${url.GET_STUDY_MAIN_AREA_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addStudyMainAreaDataAPI = (payload) => {
    const apiUrl = `${url.ADD_STUDY_MAIN_AREA_API}`;
    return post(apiUrl, payload);
};

export const editStudyMainAreaDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_STUDY_MAIN_AREA_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteStudyMainAreaDataAPI = (payload) => {
    const prepareDATA = {
        id: payload,
    };
    const apiUrl = `${url.DELETE_STUDY_MAIN_AREA_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportStudyMainAreaDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_STUDY_MAIN_AREA_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importStudyMainAreaDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_STUDY_MAIN_AREA_API}`;
    return post(apiUrl, payload);
};

// CONTINENT
export const getContinentListDataAPI = (data) => {
    const apiUrl = `${url.GET_CONTINENT_LIST_API}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addContinentDataAPI = (payload) => {
    const apiUrl = `${url.Add_CONTINENT_LIST_API}`;
    return post(apiUrl, payload);
};

export const editContinentDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_CONTINENT_LIST_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteContinentDataAPI = (payload) => {
    const prepareDATA = {
        id: payload,
    };
    const apiUrl = `${url.DELETE_CONTINENT_LIST_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportContinentDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_CONTINENT_LIST_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importContinentDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_CONTINENT_LIST_API}`;
    return post(apiUrl, payload);
};

//COUNTRY
export const getCountryListDataAPI = (data) => {
    const apiUrl = `${url.GET_COUNTRY_LIST_API}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addCountryDataAPI = (payload) => {
    const apiUrl = `${url.ADD_COUNTRY_LIST_API}`;
    return post(apiUrl, payload);
};

export const editCountryDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_COUNTRY_LIST_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteCountryDataAPI = (payload) => {
    const prepareDATA = {
        id: payload,
    };
    const apiUrl = `${url.DELETE_COUNTRY_LIST_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportCountryDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_COUNTRY_LIST_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importCountryDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_COUNTRY_LIST_API}`;
    return post(apiUrl, payload);
};

// STATE
export const getStateListDataAPI = (data) => {
    const apiUrl = `${url.GET_STATE_LIST_API}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addStateDataAPI = (payload) => {
    const apiUrl = `${url.ADD_STATE_LIST_API}`;
    return post(apiUrl, payload);
};

export const editStateDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_STATE_LIST_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteStateDataAPI = (payload) => {
    const prepareDATA = {
        id: payload,
    };
    const apiUrl = `${url.DELETE_STATE_LIST_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportStateDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_STATE_LIST_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importStateDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_STATE_LIST_API}`;
    return post(apiUrl, payload);
};
export const getStateDataByCountryAPI = (payload) => {
    const apiUrl = `${url.GET_STATE_LIST_BY_COUNTRY_API}?country_id=${payload.countryId}`;
    return get(apiUrl);
};


// CIVIL_ID_NAME
export const getCivilIdNameListDataAPI = (data) => {
    const apiUrl = `${url.GET_CIVIL_ID_NAME_LIST_API}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addCivilIdNameDataAPI = (payload) => {
    const apiUrl = `${url.ADD_CIVIL_ID_NAME_LIST_API}`;
    return post(apiUrl, payload);
};

export const editCivilIdNameDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_CIVIL_ID_NAME_LIST_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteCivilIdNameDataAPI = (payload) => {
    const prepareDATA = {
        id: payload,
    };
    const apiUrl = `${url.DELETE_CIVIL_ID_NAME_LIST_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportCivilIdNameDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_CIVIL_ID_NAME_LIST_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importCivilIdNameDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_CIVIL_ID_NAME_LIST_API}`;
    return post(apiUrl, payload);
};

// RELATION
export const getRelationListDataAPI = (data) => {
    const apiUrl = `${url.GET_RELATION_LIST_API}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addRelationDataAPI = (payload) => {
    const apiUrl = `${url.ADD_RELATION_LIST_API}`;
    return post(apiUrl, payload);
};

export const editRelationDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_RELATION_LIST_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteRelationDataAPI = (payload) => {
    const prepareDATA = {
        id: payload,
    };
    const apiUrl = `${url.DELETE_RELATION_LIST_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportRelationDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_RELATION_LIST_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importRelationDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_RELATION_LIST_API}`;
    return post(apiUrl, payload);
};

// TIME_ZONE
export const getTimeZoneListDataAPI = (data) => {
    const apiUrl = `${url.GET_TIME_ZONE_LIST_API}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addTimeZoneDataAPI = (payload) => {
    const apiUrl = `${url.ADD_TIME_ZONE_LIST_API}`;
    return post(apiUrl, payload);
};

export const editTimeZoneDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_TIME_ZONE_LIST_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteTimeZoneDataAPI = (payload) => {
    const prepareDATA = {
        id: payload,
    };
    const apiUrl = `${url.DELETE_TIME_ZONE_LIST_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportTimeZoneDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_TIME_ZONE_LIST_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importTimeZoneDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_TIME_ZONE_LIST_API}`;
    return post(apiUrl, payload);
};
//Education Duration
export const getEducationDurationListDataAPI = (data) => {
    const apiUrl = `${url.GET_EDUCATION_DURATION_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addEducationDurationDataAPI = (payload) => {
    const apiUrl = `${url.ADD_EDUCATION_DURATION_API}`;
    return post(apiUrl, payload);
};

export const editEducationDurationDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_EDUCATION_DURATION_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteEducationDurationDataAPI = (payload) => {
    const prepareDATA = {
        id: payload,
    };
    const apiUrl = `${url.DELETE_EDUCATION_DURATION_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportEducationDurationDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_EDUCATION_DURATION_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importEducationDurationDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_EDUCATION_DURATION_API}`;
    return post(apiUrl, payload);
};

// Study Major Area
export const getStudyMajorAreaListDataAPI = (data) => {
    const apiUrl = `${url.GET_STUDY_MAJOR_AREA_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addStudyMajorAreaDataAPI = (payload) => {
    const apiUrl = `${url.ADD_STUDY_MAJOR_AREA_API}`;
    return post(apiUrl, payload);
};

export const editStudyMajorAreaDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_STUDY_MAJOR_AREA_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteStudyMajorAreaDataAPI = (payload) => {
    const prepareDATA = {
        id: payload,
    };
    const apiUrl = `${url.DELETE_STUDY_MAJOR_AREA_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportStudyMajorAreaDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_STUDY_MAJOR_AREA_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importStudyMajorAreaDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_STUDY_MAJOR_AREA_API}`;
    return post(apiUrl, payload);
};

export const studyMajorAreaListByMainAreaAPI = (payload) => {
    const apiUrl = `${url.STUDY_MAJOR_AREA_LIST_BY_MAIN_AREA_API}?main_uuid=${payload.mainarea_id}`;
    return get(apiUrl, payload);
};

// Academic Result Type
export const getAcademicResultTypeListDataAPI = (data) => {
    const apiUrl = `${url.GET_ACADEMIC_RESULT_TYPE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addAcademicResultTypeDataAPI = (payload) => {
    const apiUrl = `${url.ADD_ACADEMIC_RESULT_TYPE_API}`;
    return post(apiUrl, payload);
};

export const editAcademicResultTypeDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_ACADEMIC_RESULT_TYPE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteAcademicResultTypeDataAPI = (payload) => {
    const prepareDATA = {
        id: payload,
    };
    const apiUrl = `${url.DELETE_ACADEMIC_RESULT_TYPE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportAcademicResultTypeDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_ACADEMIC_RESULT_TYPE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importAcademicResultTypeDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_ACADEMIC_RESULT_TYPE_API}`;
    return post(apiUrl, payload);
};

// Education Type
export const getEducationTypeListDataAPI = (data) => {
    const apiUrl = `${url.GET_EDUCATION_TYPE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addEducationTypeDataAPI = (payload) => {
    const apiUrl = `${url.ADD_EDUCATION_TYPE_API}`;
    return post(apiUrl, payload);
};

export const editEducationTypeDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_EDUCATION_TYPE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteEducationTypeDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_EDUCATION_TYPE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportEducationTypeDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_EDUCATION_TYPE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importEducationTypeDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_EDUCATION_TYPE_API}`;
    return post(apiUrl, payload);
};

// Study Specialisation

export const getStudySpecialisationListDataAPI = (data) => {
    const apiUrl = `${url.GET_STUDY_SPECIALISATION_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addStudySpecialisationDataAPI = (payload) => {
    const apiUrl = `${url.ADD_STUDY_SPECIALISATION_API}`;
    return post(apiUrl, payload);
};

export const editStudySpecialisationDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_STUDY_SPECIALISATION_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteStudySpecialisationDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_STUDY_SPECIALISATION_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportStudySpecialisationDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_STUDY_SPECIALISATION_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importStudySpecialisationDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_STUDY_SPECIALISATION_API}`;
    return post(apiUrl, payload);
};

// Degree Awarede By
export const getDegreeAwardedByListDataAPI = (data) => {
    const apiUrl = `${url.GET_DEGREE_AWARDED_BY_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addDegreeAwardedByDataAPI = (payload) => {
    const apiUrl = `${url.ADD_DEGREE_AWARDED_BY_API}`;
    return post(apiUrl, payload);
};

export const editDegreeAwardedByDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_DEGREE_AWARDED_BY_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteDegreeAwardedByDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_DEGREE_AWARDED_BY_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportDegreeAwardedByDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_DEGREE_AWARDED_BY_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importDegreeAwardedByDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_DEGREE_AWARDED_BY_API}`;
    return post(apiUrl, payload);
};
// Academin result
export const getAcademicResultListDataAPI = (data) => {
    const apiUrl = `${url.GET_ACADEMIC_RESULT_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const getAcademicResultListByAcademicTypeDataAPI = (payload) => {
    const apiUrl = `${url.GET_ACADEMIC_RESULT_LIST_BY_ACADEMIC_TYPE}?uuid=${payload?.educationLevelId}`;
    return get(apiUrl);
};


export const addAcademicResultDataAPI = (payload) => {
    const apiUrl = `${url.ADD_ACADEMIC_RESULT_API}`;
    return post(apiUrl, payload);
};

export const editAcademicResultDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_ACADEMIC_RESULT_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteAcademicResultDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_ACADEMIC_RESULT_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportAcademicResultDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_ACADEMIC_RESULT_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importAcademicResultDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_ACADEMIC_RESULT_API}`;
    return post(apiUrl, payload);
};

// Degree Awarded Institute
export const getDegreeAwardedInstituteListDataAPI = (data) => {
    const apiUrl = `${url.GET_DEGREE_AWARDED_INSTITUTE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addDegreeAwardedInstituteDataAPI = (payload) => {
    const apiUrl = `${url.ADD_DEGREE_AWARDED_INSTITUTE_API}`;
    return post(apiUrl, payload);
};

export const editDegreeAwardedInstituteDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_DEGREE_AWARDED_INSTITUTE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteDegreeAwardedInstituteDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_DEGREE_AWARDED_INSTITUTE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportDegreeAwardedInstituteDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_DEGREE_AWARDED_INSTITUTE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importDegreeAwardedInstituteDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_DEGREE_AWARDED_INSTITUTE_API}`;
    return post(apiUrl, payload);
};

// Academic Result To Result (Compare Mapping)
export const getAcademicResultToResultListAPI = (data) => {
    const apiUrl = `${url.GET_ACADEMIC_RESULT_TO_RESULT_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addAcademicResultToResultAPI = (payload) => {
    const apiUrl = `${url.ADD_ACADEMIC_RESULT_TO_RESULT_API}`;
    return post(apiUrl, payload);
};

export const editAcademicResultToResultAPI = (payload) => {
    const apiUrl = `${url.EDIT_ACADEMIC_RESULT_TO_RESULT_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteAcademicResultToResultAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_ACADEMIC_RESULT_TO_RESULT_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportAcademicResultToResultAPI = (payload) => {
    const apiUrl = `${url.EXPORT_ACADEMIC_RESULT_TO_RESULT_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importAcademicResultToResultAPI = (payload) => {
    const apiUrl = `${url.IMPORT_ACADEMIC_RESULT_TO_RESULT_API}`;
    return post(apiUrl, payload);
};

// DISTRICT
export const getDistrictListDataAPI = (data) => {
    const apiUrl = `${url.GET_DISTRICT_LIST_API}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addDistrictDataAPI = (payload) => {
    const apiUrl = `${url.ADD_DISTRICT_LIST_API}`;
    return post(apiUrl, payload);
};

export const editDistrictDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_DISTRICT_LIST_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteDistrictDataAPI = (payload) => {
    const prepareDATA = {
        id: payload,
    };
    const apiUrl = `${url.DELETE_DISTRICT_LIST_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportDistrictDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_DISTRICT_LIST_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importDistrictDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_DISTRICT_LIST_API}`;
    return post(apiUrl, payload);
};
export const getDistrictDataByStateAPI = (payload) => {
    const apiUrl = `${url.GET_DISTRICT_LIST_BY_STATE_API}?country_id=${payload.countryId}&state_id=${payload.stateId}`;
    return get(apiUrl);
};

// CITY
export const getCityListDataAPI = (data) => {
    const apiUrl = `${url.GET_CITY_LIST_API}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addCityDataAPI = (payload) => {
    const apiUrl = `${url.ADD_CITY_LIST_API}`;
    return post(apiUrl, payload);
};

export const editCityDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_CITY_LIST_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteCityDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_CITY_LIST_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportCityDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_CITY_LIST_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importCityDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_CITY_LIST_API}`;
    return post(apiUrl, payload);
};

// ECA Awarding Body API Services

export const getEcaAwardingBodyListAPI = (data) => {
    const apiUrl = `${url.GET_ECA_AWARDING_BODY_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addEcaAwardingBodyAPI = (payload) => {
    const apiUrl = `${url.ADD_ECA_AWARDING_BODY_API}`;
    return post(apiUrl, payload);
};

export const editEcaAwardingBodyAPI = (payload) => {
    const apiUrl = `${url.EDIT_ECA_AWARDING_BODY_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteEcaAwardingBodyAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_ECA_AWARDING_BODY_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportEcaAwardingBodyAPI = (payload) => {
    const apiUrl = `${url.EXPORT_ECA_AWARDING_BODY_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importEcaAwardingBodyAPI = (payload) => {
    const apiUrl = `${url.IMPORT_ECA_AWARDING_BODY_API}`;
    return post(apiUrl, payload);
};
// Medium of Education API Services

export const getMediumOfEducationListAPI = (data) => {
    const apiUrl = `${url.GET_MEDIUM_OF_EDUCATION_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addMediumOfEducationAPI = (payload) => {
    const apiUrl = `${url.ADD_MEDIUM_OF_EDUCATION_API}`;
    return post(apiUrl, payload);
};
export const editMediumOfEducationAPI = (payload) => {
    const apiUrl = `${url.EDIT_MEDIUM_OF_EDUCATION_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteMediumOfEducationAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_MEDIUM_OF_EDUCATION_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportMediumOfEducationAPI = (payload) => {
    const apiUrl = `${url.EXPORT_MEDIUM_OF_EDUCATION_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importMediumOfEducationAPI = (payload) => {
    const apiUrl = `${url.IMPORT_MEDIUM_OF_EDUCATION_API}`;
    return post(apiUrl, payload);
};

// ECA For API Services
export const getEcaForListAPI = (data) => {
    const apiUrl = `${url.GET_ECA_FOR_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addEcaForAPI = (payload) => {
    const apiUrl = `${url.ADD_ECA_FOR_API}`;
    return post(apiUrl, payload);
};

export const editEcaForAPI = (payload) => {
    const apiUrl = `${url.EDIT_ECA_FOR_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteEcaForAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_ECA_FOR_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportEcaForAPI = (payload) => {
    const apiUrl = `${url.EXPORT_ECA_FOR_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importEcaForAPI = (payload) => {
    const apiUrl = `${url.IMPORT_ECA_FOR_API}`;
    return post(apiUrl, payload);
};

// Language Name(Test)
export const getLanguageNameTestListAPI = (data) => {
    const apiUrl = `${url.GET_LANGUAGE_NAME_TEST_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addLanguageNameTestAPI = (payload) => {
    const apiUrl = `${url.ADD_LANGUAGE_NAME_TEST_API}`;
    return post(apiUrl, payload);
};

export const editLanguageNameTestAPI = (payload) => {
    const apiUrl = `${url.EDIT_LANGUAGE_NAME_TEST_API}${payload?.uuid}/update`;
    return put(apiUrl, payload);
};

export const deleteLanguageNameTestAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_LANGUAGE_NAME_TEST_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportLanguageNameTestAPI = (payload) => {
    const apiUrl = `${url.EXPORT_LANGUAGE_NAME_TEST_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importLanguageNameTestAPI = (payload) => {
    const apiUrl = `${url.IMPORT_LANGUAGE_NAME_TEST_API}`;
    return post(apiUrl, payload);
};

// Language Test Name
export const getLanguageTestNameListAPI = (data) => {
    const apiUrl = `${url.GET_LANGUAGE_TEST_NAME_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addLanguageTestNameAPI = (payload) => {
    const apiUrl = `${url.ADD_LANGUAGE_TEST_NAME_API}`;
    return post(apiUrl, payload);
};

export const editLanguageTestNameAPI = (payload) => {
    const apiUrl = `${url.EDIT_LANGUAGE_TEST_NAME_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteLanguageTestNameAPI = (payload) => {
    const prepareDATA = {
        id: payload
    };
    const apiUrl = `${url.DELETE_LANGUAGE_TEST_NAME_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportLanguageTestNameAPI = (payload) => {
    const apiUrl = `${url.EXPORT_LANGUAGE_TEST_NAME_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importLanguageTestNameAPI = (payload) => {
    const apiUrl = `${url.IMPORT_LANGUAGE_TEST_NAME_API}`;
    return post(apiUrl, payload);
};

// Language Test Module Name
export const getLanguageTestModuleNameListAPI = (data) => {
    const apiUrl = `${url.GET_LANGUAGE_TEST_MODULE_NAME_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addLanguageTestModuleNameAPI = (payload) => {
    const apiUrl = `${url.ADD_LANGUAGE_TEST_MODULE_NAME_API}`;
    return post(apiUrl, payload);
};

export const editLanguageTestModuleNameAPI = (payload) => {
    const apiUrl = `${url.EDIT_LANGUAGE_TEST_MODULE_NAME_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteLanguageTestModuleNameAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_LANGUAGE_TEST_MODULE_NAME_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportLanguageTestModuleNameAPI = (payload) => {
    const apiUrl = `${url.EXPORT_LANGUAGE_TEST_MODULE_NAME_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importLanguageTestModuleNameAPI = (payload) => {
    const apiUrl = `${url.IMPORT_LANGUAGE_TEST_MODULE_NAME_API}`;
    return post(apiUrl, payload);
};

// Language Benchmark Level
export const getLanguageBenchmarkLevelListAPI = (data) => {
    const apiUrl = `${url.GET_LANGUAGE_BENCHMARK_LEVEL_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addLanguageBenchmarkLevelAPI = (payload) => {
    const apiUrl = `${url.ADD_LANGUAGE_BENCHMARK_LEVEL_API}`;
    return post(apiUrl, payload);
};

export const editLanguageBenchmarkLevelAPI = (payload) => {
    const apiUrl = `${url.EDIT_LANGUAGE_BENCHMARK_LEVEL_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteLanguageBenchmarkLevelAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_LANGUAGE_BENCHMARK_LEVEL_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportLanguageBenchmarkLevelAPI = (payload) => {
    const apiUrl = `${url.EXPORT_LANGUAGE_BENCHMARK_LEVEL_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importLanguageBenchmarkLevelAPI = (payload) => {
    const apiUrl = `${url.IMPORT_LANGUAGE_BENCHMARK_LEVEL_API}`;
    return post(apiUrl, payload);
};

// CLB Level
export const getClbLevelListAPI = (data) => {
    const apiUrl = `${url.GET_CLB_LEVEL_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addClbLevelAPI = (payload) => {
    const apiUrl = `${url.ADD_CLB_LEVEL_API}`;
    return post(apiUrl, payload);
};

export const editClbLevelAPI = (payload) => {
    const apiUrl = `${url.EDIT_CLB_LEVEL_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteClbLevelAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_CLB_LEVEL_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportClbLevelAPI = (payload) => {
    const apiUrl = `${url.EXPORT_CLB_LEVEL_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importClbLevelAPI = (payload) => {
    const apiUrl = `${url.IMPORT_CLB_LEVEL_API}`;
    return post(apiUrl, payload);
};
// Entrance Test Name
export const getEntranceTestNameListAPI = (data) => {
    const apiUrl = `${url.GET_ENTRANCE_TEST_NAME_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addEntranceTestNameAPI = (payload) => {
    const apiUrl = `${url.ADD_ENTRANCE_TEST_NAME_API}`;
    return post(apiUrl, payload);
};

export const editEntranceTestNameAPI = (payload) => {
    const apiUrl = `${url.EDIT_ENTRANCE_TEST_NAME_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteEntranceTestNameAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_ENTRANCE_TEST_NAME_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportEntranceTestNameAPI = (payload) => {
    const apiUrl = `${url.EXPORT_ENTRANCE_TEST_NAME_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importEntranceTestNameAPI = (payload) => {
    const apiUrl = `${url.IMPORT_ENTRANCE_TEST_NAME_API}`;
    return post(apiUrl, payload);
};
// Entrance Test Module Name
export const getEntranceTestModuleNameListAPI = (data) => {
    const apiUrl = `${url.GET_ENTRANCE_TEST_MODULE_NAME_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addEntranceTestModuleNameAPI = (payload) => {
    const apiUrl = `${url.ADD_ENTRANCE_TEST_MODULE_NAME_API}`;
    return post(apiUrl, payload);
};

export const editEntranceTestModuleNameAPI = (payload) => {
    const apiUrl = `${url.EDIT_ENTRANCE_TEST_MODULE_NAME_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteEntranceTestModuleNameAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_ENTRANCE_TEST_MODULE_NAME_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportEntranceTestModuleNameAPI = (payload) => {
    const apiUrl = `${url.EXPORT_ENTRANCE_TEST_MODULE_NAME_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importEntranceTestModuleNameAPI = (payload) => {
    const apiUrl = `${url.IMPORT_ENTRANCE_TEST_MODULE_NAME_API}`;
    return post(apiUrl, payload);
};


// Entrance Test Result
export const getEntranceTestResultListAPI = (data) => {
    const apiUrl = `${url.GET_ENTRANCE_TEST_RESULT_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addEntranceTestResultAPI = (payload) => {
    const apiUrl = `${url.ADD_ENTRANCE_TEST_RESULT_API}`;
    return post(apiUrl, payload);
};

export const editEntranceTestResultAPI = (payload) => {
    const apiUrl = `${url.EDIT_ENTRANCE_TEST_RESULT_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteEntranceTestResultAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_ENTRANCE_TEST_RESULT_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportEntranceTestResultAPI = (payload) => {
    const apiUrl = `${url.EXPORT_ENTRANCE_TEST_RESULT_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importEntranceTestResultAPI = (payload) => {
    const apiUrl = `${url.IMPORT_ENTRANCE_TEST_RESULT_API}`;
    return post(apiUrl, payload);
};

// Language Test Result
export const getLanguageTestResultListAPI = (data) => {
    const apiUrl = `${url.GET_LANGUAGE_TEST_RESULT_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addLanguageTestResultAPI = (payload) => {
    const apiUrl = `${url.ADD_LANGUAGE_TEST_RESULT_API}`;
    return post(apiUrl, payload);
};

export const editLanguageTestResultAPI = (payload) => {
    const apiUrl = `${url.EDIT_LANGUAGE_TEST_RESULT_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteLanguageTestResultAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_LANGUAGE_TEST_RESULT_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportLanguageTestResultAPI = (payload) => {
    const apiUrl = `${url.EXPORT_LANGUAGE_TEST_RESULT_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importLanguageTestResultAPI = (payload) => {
    const apiUrl = `${url.IMPORT_LANGUAGE_TEST_RESULT_API}`;
    return post(apiUrl, payload);
};

// Job Type
export const getJobTypeListDataAPI = (data) => {
    const apiUrl = `${url.GET_JOB_TYPE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addJobTypeDataAPI = (payload) => {
    const apiUrl = `${url.ADD_JOB_TYPE_API}`;
    return post(apiUrl, payload);
};

export const editJobTypeDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_JOB_TYPE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteJobTypeDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_JOB_TYPE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportJobTypeDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_JOB_TYPE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importJobTypeDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_JOB_TYPE_API}`;
    return post(apiUrl, payload);
};
// Mode of Salary
export const getModeOfSalaryDataAPI = (data) => {
    const apiUrl = `${url.GET_MODE_OF_SALARY_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addModeOfSalaryDataAPI = (payload) => {
    const apiUrl = `${url.ADD_MODE_OF_SALARY_API}`;
    return post(apiUrl, payload);
};

export const editModeOfSalaryDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_MODE_OF_SALARY_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteModeOfSalaryDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_MODE_OF_SALARY_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportModeOfSalaryDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_MODE_OF_SALARY_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importModeOfSalaryDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_MODE_OF_SALARY_API}`;
    return post(apiUrl, payload);
};

// IT Return Status
export const getItReturnStatusListDataAPI = (data) => {
    const apiUrl = `${url.GET_IT_RETURN_STATUS_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addItReturnStatusDataAPI = (payload) => {
    const apiUrl = `${url.ADD_IT_RETURN_STATUS_API}`;
    return post(apiUrl, payload);
};

export const editItReturnStatusDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_IT_RETURN_STATUS_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteItReturnStatusDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_IT_RETURN_STATUS_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportItReturnStatusDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_IT_RETURN_STATUS_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importItReturnStatusDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_IT_RETURN_STATUS_API}`;
    return post(apiUrl, payload);
};
// Occupation Type
export const getOccupationTypeListDataAPI = (data) => {
    const apiUrl = `${url.GET_OCCUPATION_TYPE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addOccupationTypeDataAPI = (payload) => {
    const apiUrl = `${url.ADD_OCCUPATION_TYPE_API}`;
    return post(apiUrl, payload);
};

export const editOccupationTypeDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_OCCUPATION_TYPE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteOccupationTypeDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_OCCUPATION_TYPE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportOccupationTypeDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_OCCUPATION_TYPE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importOccupationTypeDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_OCCUPATION_TYPE_API}`;
    return post(apiUrl, payload);
};

// Occupation Prospect
export const getOccupationProspectListDataAPI = (data) => {
    const apiUrl = `${url.GET_OCCUPATION_PROSPECT_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addOccupationProspectDataAPI = (payload) => {
    const apiUrl = `${url.ADD_OCCUPATION_PROSPECT_API}`;
    return post(apiUrl, payload);
};

export const editOccupationProspectDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_OCCUPATION_PROSPECT_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteOccupationProspectDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_OCCUPATION_PROSPECT_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportOccupationProspectDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_OCCUPATION_PROSPECT_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importOccupationProspectDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_OCCUPATION_PROSPECT_API}`;
    return post(apiUrl, payload);
};

// --- OCCUPATION CATEGORY API FUNCTIONS ---
export const getOccupationCategoryListDataAPI = (data) => {
    const apiUrl = `${url.GET_OCCUPATION_CATEGORY_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addOccupationCategoryDataAPI = (payload) => {
    const apiUrl = `${url.ADD_OCCUPATION_CATEGORY_API}`;
    return post(apiUrl, payload);
};

export const editOccupationCategoryDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_OCCUPATION_CATEGORY_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteOccupationCategoryDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_OCCUPATION_CATEGORY_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportOccupationCategoryDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_OCCUPATION_CATEGORY_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importOccupationCategoryDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_OCCUPATION_CATEGORY_API}`;
    return post(apiUrl, payload);
};

// Occupation Version
export const getOccupationVersionListDataAPI = (data) => {
    const apiUrl = `${url.GET_OCCUPATION_VERSION_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addOccupationVersionDataAPI = (payload) => {
    const apiUrl = `${url.ADD_OCCUPATION_VERSION_API}`;
    return post(apiUrl, payload);
};

export const editOccupationVersionDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_OCCUPATION_VERSION_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteOccupationVersionDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_OCCUPATION_VERSION_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportOccupationVersionDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_OCCUPATION_VERSION_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importOccupationVersionDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_OCCUPATION_VERSION_API}`;
    return post(apiUrl, payload);
};



// Institute Type
export const getInstituteTypeListDataAPI = (data) => {
    const apiUrl = `${url.GET_INSTITUTE_TYPE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addInstituteTypeDataAPI = (payload) => {
    const apiUrl = `${url.ADD_INSTITUTE_TYPE_API}`;
    return post(apiUrl, payload);
};

export const editInstituteTypeDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_INSTITUTE_TYPE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteInstituteTypeDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_INSTITUTE_TYPE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportInstituteTypeDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_INSTITUTE_TYPE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importInstituteTypeDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_INSTITUTE_TYPE_API}`;
    return post(apiUrl, payload);
};
// Institute Group Name 
export const getInstituteGroupNameListDataAPI = (data) => {
    const apiUrl = `${url.GET_INSTITUTE_GROUP_NAME_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addInstituteGroupNameDataAPI = (payload) => {
    const apiUrl = `${url.ADD_INSTITUTE_GROUP_NAME_API}`;
    return post(apiUrl, payload);
};

export const editInstituteGroupNameDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_INSTITUTE_GROUP_NAME_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteInstituteGroupNameDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_INSTITUTE_GROUP_NAME_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportInstituteGroupNameDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_INSTITUTE_GROUP_NAME_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importInstituteGroupNameDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_INSTITUTE_GROUP_NAME_API}`;
    return post(apiUrl, payload);
};

// Institute Status API Calls
export const getInstituteStatusListDataAPI = (data) => {
    const apiUrl = `${url.GET_INSTITUTE_STATUS_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addInstituteStatusDataAPI = (payload) => {
    const apiUrl = `${url.ADD_INSTITUTE_STATUS_API}`;
    return post(apiUrl, payload);
};

export const editInstituteStatusDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_INSTITUTE_STATUS_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteInstituteStatusDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_INSTITUTE_STATUS_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportInstituteStatusDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_INSTITUTE_STATUS_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importInstituteStatusDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_INSTITUTE_STATUS_API}`;
    return post(apiUrl, payload);
};

// Institute Priority API Calls
export const getInstitutePriorityListDataAPI = (data) => {
    const apiUrl = `${url.GET_INSTITUTE_PRIORITY_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addInstitutePriorityDataAPI = (payload) => {
    const apiUrl = `${url.ADD_INSTITUTE_PRIORITY_API}`;
    return post(apiUrl, payload);
};

export const editInstitutePriorityDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_INSTITUTE_PRIORITY_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteInstitutePriorityDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_INSTITUTE_PRIORITY_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportInstitutePriorityDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_INSTITUTE_PRIORITY_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importInstitutePriorityDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_INSTITUTE_PRIORITY_API}`;
    return post(apiUrl, payload);
};

// Institute Department API Calls
export const getInstituteDepartmentListDataAPI = (data) => {
    const apiUrl = `${url.GET_INSTITUTE_DEPARTMENT_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addInstituteDepartmentDataAPI = (payload) => {
    const apiUrl = `${url.ADD_INSTITUTE_DEPARTMENT_API}`;
    return post(apiUrl, payload);
};

export const editInstituteDepartmentDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_INSTITUTE_DEPARTMENT_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteInstituteDepartmentDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_INSTITUTE_DEPARTMENT_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportInstituteDepartmentDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_INSTITUTE_DEPARTMENT_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importInstituteDepartmentDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_INSTITUTE_DEPARTMENT_API}`;
    return post(apiUrl, payload);
};

// Bank Account For API Calls
export const getBankAccountForListDataAPI = (data) => {
    const apiUrl = `${url.GET_BANK_ACCOUNT_FOR_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addBankAccountForDataAPI = (payload) => {
    const apiUrl = `${url.ADD_BANK_ACCOUNT_FOR_API}`;
    return post(apiUrl, payload);
};

export const editBankAccountForDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_BANK_ACCOUNT_FOR_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteBankAccountForDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_BANK_ACCOUNT_FOR_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportBankAccountForDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_BANK_ACCOUNT_FOR_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importBankAccountForDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_BANK_ACCOUNT_FOR_API}`;
    return post(apiUrl, payload);
};

// When Commission Issue API Calls
export const getWhenCommissionIssueListDataAPI = (data) => {
    const apiUrl = `${url.GET_WHEN_COMMISSION_ISSUE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addWhenCommissionIssueDataAPI = (payload) => {
    const apiUrl = `${url.ADD_WHEN_COMMISSION_ISSUE_API}`;
    return post(apiUrl, payload);
};

export const editWhenCommissionIssueDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_WHEN_COMMISSION_ISSUE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteWhenCommissionIssueDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_WHEN_COMMISSION_ISSUE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportWhenCommissionIssueDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_WHEN_COMMISSION_ISSUE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importWhenCommissionIssueDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_WHEN_COMMISSION_ISSUE_API}`;
    return post(apiUrl, payload);
};
// Course Level Code API Calls
export const getCourseLevelCodeListDataAPI = (data) => {
    const apiUrl = `${url.GET_COURSE_LEVEL_CODE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addCourseLevelCodeDataAPI = (payload) => {
    const apiUrl = `${url.ADD_COURSE_LEVEL_CODE_API}`;
    return post(apiUrl, payload);
};

export const editCourseLevelCodeDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_COURSE_LEVEL_CODE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteCourseLevelCodeDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_COURSE_LEVEL_CODE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportCourseLevelCodeDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_COURSE_LEVEL_CODE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importCourseLevelCodeDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_COURSE_LEVEL_CODE_API}`;
    return post(apiUrl, payload);
};
// Course Divided In API Calls
export const getCourseDividedInListDataAPI = (data) => {
    const apiUrl = `${url.GET_COURSE_DIVIDED_IN_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addCourseDividedInDataAPI = (payload) => {
    const apiUrl = `${url.ADD_COURSE_DIVIDED_IN_API}`;
    return post(apiUrl, payload);
};

export const editCourseDividedInDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_COURSE_DIVIDED_IN_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteCourseDividedInDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_COURSE_DIVIDED_IN_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportCourseDividedInDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_COURSE_DIVIDED_IN_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importCourseDividedInDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_COURSE_DIVIDED_IN_API}`;
    return post(apiUrl, payload);
};
// Course Status API Calls
export const getCourseStatusListDataAPI = (data) => {
    const apiUrl = `${url.GET_COURSE_STATUS_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addCourseStatusDataAPI = (payload) => {
    const apiUrl = `${url.ADD_COURSE_STATUS_API}`;
    return post(apiUrl, payload);
};

export const editCourseStatusDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_COURSE_STATUS_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteCourseStatusDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_COURSE_STATUS_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportCourseStatusDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_COURSE_STATUS_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importCourseStatusDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_COURSE_STATUS_API}`;
    return post(apiUrl, payload);
};
// Intake Name API
export const getIntakeNameListDataAPI = (data) => {
    const apiUrl = `${url.GET_INTAKE_NAME_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addIntakeNameDataAPI = (payload) => {
    const apiUrl = `${url.ADD_INTAKE_NAME_API}`;
    return post(apiUrl, payload);
};

export const editIntakeNameDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_INTAKE_NAME_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteIntakeNameDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_INTAKE_NAME_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportIntakeNameDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_INTAKE_NAME_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importIntakeNameDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_INTAKE_NAME_API}`;
    return post(apiUrl, payload);
};

// Course Status for Intake API
export const getCourseStatusIntakeListDataAPI = (data) => {
    const apiUrl = `${url.GET_COURSE_STATUS_INTAKE_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addCourseStatusIntakeDataAPI = (payload) => {
    const apiUrl = `${url.ADD_COURSE_STATUS_INTAKE_API}`;
    return post(apiUrl, payload);
};

export const editCourseStatusIntakeDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_COURSE_STATUS_INTAKE_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteCourseStatusIntakeDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_COURSE_STATUS_INTAKE_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportCourseStatusIntakeDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_COURSE_STATUS_INTAKE_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importCourseStatusIntakeDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_COURSE_STATUS_INTAKE_API}`;
    return post(apiUrl, payload);
};
// Scholarship Based On API
export const getScholarshipBasedOnListDataAPI = (data) => {
    const apiUrl = `${url.GET_SCHOLARSHIP_BASED_ON_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addScholarshipBasedOnDataAPI = (payload) => {
    const apiUrl = `${url.ADD_SCHOLARSHIP_BASED_ON_API}`;
    return post(apiUrl, payload);
};

export const editScholarshipBasedOnDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_SCHOLARSHIP_BASED_ON_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteScholarshipBasedOnDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_SCHOLARSHIP_BASED_ON_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportScholarshipBasedOnDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_SCHOLARSHIP_BASED_ON_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importScholarshipBasedOnDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_SCHOLARSHIP_BASED_ON_API}`;
    return post(apiUrl, payload);
};
// Course Level API
export const getCourseLevelListDataAPI = (data) => {
    const apiUrl = `${url.GET_COURSE_LEVEL_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addCourseLevelDataAPI = (payload) => {
    const apiUrl = `${url.ADD_COURSE_LEVEL_API}`;
    return post(apiUrl, payload);
};

export const editCourseLevelDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_COURSE_LEVEL_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteCourseLevelDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_COURSE_LEVEL_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportCourseLevelDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_COURSE_LEVEL_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importCourseLevelDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_COURSE_LEVEL_API}`;
    return post(apiUrl, payload);
};
// Course Duration API
export const getCourseDurationListDataAPI = (data) => {
    const apiUrl = `${url.GET_COURSE_DURATION_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}`;
    return get(apiUrl);
};

export const addCourseDurationDataAPI = (payload) => {
    const apiUrl = `${url.ADD_COURSE_DURATION_API}`;
    return post(apiUrl, payload);
};

export const editCourseDurationDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_COURSE_DURATION_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteCourseDurationDataAPI = (payload) => {
    const prepareDATA = { id: payload };
    const apiUrl = `${url.DELETE_COURSE_DURATION_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportCourseDurationDataAPI = (payload) => {
    const apiUrl = `${url.EXPORT_COURSE_DURATION_API}?fields=${payload?.fields}&uuids=${payload?.uuids}`;
    return getExportData(apiUrl, payload);
};

export const importCourseDurationDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_COURSE_DURATION_API}`;
    return post(apiUrl, payload);
};














