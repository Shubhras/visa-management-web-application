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