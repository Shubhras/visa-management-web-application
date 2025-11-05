import { IMPORT_ACCREDITATION_NAME_API } from "../../../service/api_url";
import {
  BANK_ACCOUNT_TYPE_LIST,
  ADD_BANK_ACCOUNT_TYPE,
  EDIT_BANK_ACCOUNT_TYPE,
  DELETE_BANK_ACCOUNT_TYPE,
  IMPORT_BANK_ACCOUNT_TYPE,
  EXPORT_BANK_ACCOUNT_TYPE,
    STAKEHOLDER_TYPE_LIST,
  ADD_STAKEHOLDER_TYPE,
  EDIT_STAKEHOLDER_TYPE,
  DELETE_STAKEHOLDER_TYPE,
  IMPORT_STAKEHOLDER_TYPE,
  EXPORT_STAKEHOLDER_TYPE,
  OWNERSHIP_TYPE_LIST,
  ADD_OWNERSHIP_TYPE,
  EDIT_OWNERSHIP_TYPE,
  DELETE_OWNERSHIP_TYPE,
  EXPORT_OWNERSHIP_TYPE,
  IMPORT_OWNERSHIP_TYPE,
  ACCREDITATION_CATEGORY_LIST,
  ADD_ACCREDITATION_CATEGORY,
  EDIT_ACCREDITATION_CATEGORY,
  DELETE_ACCREDITATION_CATEGORY,
  EXPORT_ACCREDITATION_CATEGORY,
  IMPORT_ACCREDITATION_CATEGORY,
  DELETE_LICENCE_NAME,
  EXPORT_LICENCE_NAME,
  IMPORT_LICENCE_NAME,
  EDIT_LICENCE_NAME,
  ADD_LICENCE_NAME,
  LICENCE_NAME_LIST,
  ACCREDITATION_NAME_LIST,
  ADD_ACCREDITATION_NAME,
  EDIT_ACCREDITATION_NAME,
  DELETE_ACCREDITATION_NAME,
  EXPORT_ACCREDITATION_NAME,
  COUNTRY_LIST_DEMO,
} from "./actionTypes"

// BANK_ACCOUNT_TYPE
export const bankAccountTypeList = (data, callback) => ({
    type: BANK_ACCOUNT_TYPE_LIST,
    data,
    callback,
});

export const bankAccountTypeAdd = (data, callback) => ({
    type: ADD_BANK_ACCOUNT_TYPE,
    data,
    callback,
});

export const bankAccountTypeEdit = (data, callback) => ({
    type: EDIT_BANK_ACCOUNT_TYPE,
    data,
    callback,
});

export const bankAccountTypeDelete = (data, callback) => ({
    type: DELETE_BANK_ACCOUNT_TYPE,
    data,
    callback,
});

export const bankAccountTypeExportData = (data, callback) => ({
    type: EXPORT_BANK_ACCOUNT_TYPE,
    data,
    callback,
});

export const bankAccountTypeImportData = (data, callback) => ({
    type: IMPORT_BANK_ACCOUNT_TYPE,
    data,
    callback,
});

// STAKEHOLDER_TYPE
export const stakeholderTypeList = (data, callback) => ({
    type: STAKEHOLDER_TYPE_LIST,
    data,
    callback,
});

export const stakeholderTypeAdd = (data, callback) => ({
    type: ADD_STAKEHOLDER_TYPE,
    data,
    callback,
});

export const stakeholderTypeEdit = (data, callback) => ({
    type: EDIT_STAKEHOLDER_TYPE,
    data,
    callback,
});

export const stakeholderTypeDelete = (data, callback) => ({
    type: DELETE_STAKEHOLDER_TYPE,
    data,
    callback,
});

export const stakeholderTypeExportData = (data, callback) => ({
    type: EXPORT_STAKEHOLDER_TYPE,
    data,
    callback,
});

export const stakeholderTypeImportData = (data, callback) => ({
    type: IMPORT_STAKEHOLDER_TYPE,
    data,
    callback,
});

// OWNERSHIP_TYPE
export const ownershipTypeList = (data, callback) => ({
    type: OWNERSHIP_TYPE_LIST,
    data,
    callback,
});

export const ownershipTypeAdd = (data, callback) => ({
    type: ADD_OWNERSHIP_TYPE,
    data,
    callback,
});

export const ownershipTypeEdit = (data, callback) => ({
    type: EDIT_OWNERSHIP_TYPE,
    data,
    callback,
});

export const ownershipTypeDelete = (data, callback) => ({
    type: DELETE_OWNERSHIP_TYPE,
    data,
    callback,
});

export const ownershipTypeExportData = (data, callback) => ({
    type: EXPORT_OWNERSHIP_TYPE,
    data,
    callback,
});

export const ownershipTypeImportData = (data, callback) => ({
    type: IMPORT_OWNERSHIP_TYPE,
    data,
    callback,
});

// ACCREDITATION_CATEGORY
export const accreditationCategoryList = (data, callback) => ({
    type: ACCREDITATION_CATEGORY_LIST,
    data,
    callback,
});

export const accreditationCategoryAdd = (data, callback) => ({
    type: ADD_ACCREDITATION_CATEGORY,
    data,
    callback,
});

export const accreditationCategoryEdit = (data, callback) => ({
    type: EDIT_ACCREDITATION_CATEGORY,
    data,
    callback,
});

export const accreditationCategoryDelete = (data, callback) => ({
    type: DELETE_ACCREDITATION_CATEGORY,
    data,
    callback,
});

export const accreditationCategoryExportData = (data, callback) => ({
    type: EXPORT_ACCREDITATION_CATEGORY,
    data,
    callback,
});

export const accreditationCategoryImportData = (data, callback) => ({
    type: IMPORT_ACCREDITATION_CATEGORY,
    data,
    callback,
})

// LICENCE_NAME
export const licenceNameList = (data, callback) => ({
    type: LICENCE_NAME_LIST,
    data,
    callback,
});

export const licenceNameAdd = (data, callback) => ({
    type: ADD_LICENCE_NAME,
    data,
    callback,
});

export const licenceNameEdit = (data, callback) => ({
    type: EDIT_LICENCE_NAME,
    data,
    callback,
});

export const licenceNameDelete = (data, callback) => ({
    type: DELETE_LICENCE_NAME,
    data,
    callback,
});

export const licenceNameExportData = (data, callback) => ({
    type: EXPORT_LICENCE_NAME,
    data,
    callback,
});

export const licenceNameImportData = (data, callback) => ({
    type: IMPORT_LICENCE_NAME,
    data,
    callback,
});

// ACCREDITATION_NAME
export const accreditationNameList = (data, callback) => ({
    type: ACCREDITATION_NAME_LIST,
    data,
    callback,
});

export const accreditationNameAdd = (data, callback) => ({
    type: ADD_ACCREDITATION_NAME,
    data,
    callback,
});

export const accreditationNameEdit = (data, callback) => ({
    type: EDIT_ACCREDITATION_NAME,
    data,
    callback,
});

export const accreditationNameDelete = (data, callback) => ({
    type: DELETE_ACCREDITATION_NAME,
    data,
    callback,
});

export const accreditationNameExportData = (data, callback) => ({
    type: EXPORT_ACCREDITATION_NAME,
    data,
    callback,
});

export const accreditationNameImportData = (data, callback) => ({
    type: IMPORT_ACCREDITATION_NAME_API,
    data,
    callback,
});

export const countryDemoList = (data, callback) => ({
    type: COUNTRY_LIST_DEMO,
    data,
    callback,
});