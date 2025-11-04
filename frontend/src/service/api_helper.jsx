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
