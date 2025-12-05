import {
    DOCUMENT_CATEGORY_LIST,
    ADD_DOCUMENT_CATEGORY,
    EDIT_DOCUMENT_CATEGORY,
    DELETE_DOCUMENT_CATEGORY,
    EXPORT_DOCUMENT_CATEGORY,
    IMPORT_DOCUMENT_CATEGORY,
    DOCUMENT_NAME_LIST,
    ADD_DOCUMENT_NAME,
    EDIT_DOCUMENT_NAME,
    DELETE_DOCUMENT_NAME,
    EXPORT_DOCUMENT_NAME,
    IMPORT_DOCUMENT_NAME,
    DOCUMENT_TYPE_LIST,
    ADD_DOCUMENT_TYPE,
    EDIT_DOCUMENT_TYPE,
    DELETE_DOCUMENT_TYPE,
    EXPORT_DOCUMENT_TYPE,
    IMPORT_DOCUMENT_TYPE,
    PURPOSE_OF_VISIT_LIST,
    ADD_PURPOSE_OF_VISIT,
    EDIT_PURPOSE_OF_VISIT,
    DELETE_PURPOSE_OF_VISIT,
    EXPORT_PURPOSE_OF_VISIT,
    IMPORT_PURPOSE_OF_VISIT,
    DOCUMENTS_FOR_LIST,
    ADD_DOCUMENTS_FOR,
    EDIT_DOCUMENTS_FOR,
    DELETE_DOCUMENTS_FOR,
    EXPORT_DOCUMENTS_FOR,
    IMPORT_DOCUMENTS_FOR,
    REQUIRED_DOCUMENT_GENERAL_LIST,
    ADD_REQUIRED_DOCUMENT_GENERAL,
    EDIT_REQUIRED_DOCUMENT_GENERAL,
    DELETE_REQUIRED_DOCUMENT_GENERAL,
    EXPORT_REQUIRED_DOCUMENT_GENERAL,
    IMPORT_REQUIRED_DOCUMENT_GENERAL,
    PROCESS_STATUS_NAME_LIST,
    ADD_PROCESS_STATUS_NAME,
    EDIT_PROCESS_STATUS_NAME,
    DELETE_PROCESS_STATUS_NAME,
    EXPORT_PROCESS_STATUS_NAME,
    IMPORT_PROCESS_STATUS_NAME,
    PROCESS_SUB_STATUS_NAME_LIST,
    ADD_PROCESS_SUB_STATUS_NAME,
    EDIT_PROCESS_SUB_STATUS_NAME,
    DELETE_PROCESS_SUB_STATUS_NAME,
    EXPORT_PROCESS_SUB_STATUS_NAME,
    IMPORT_PROCESS_SUB_STATUS_NAME,
    PROCESS_TYPE_LIST,
    ADD_PROCESS_TYPE,
    EDIT_PROCESS_TYPE,
    DELETE_PROCESS_TYPE,
    EXPORT_PROCESS_TYPE,
    IMPORT_PROCESS_TYPE,
    PAYMENT_TO_LIST,
    ADD_PAYMENT_TO,
    EDIT_PAYMENT_TO,
    DELETE_PAYMENT_TO,
    EXPORT_PAYMENT_TO,
    IMPORT_PAYMENT_TO,
    PAYMENT_CATEGORY_LIST,
    ADD_PAYMENT_CATEGORY,
    EDIT_PAYMENT_CATEGORY,
    DELETE_PAYMENT_CATEGORY,
    EXPORT_PAYMENT_CATEGORY,
    IMPORT_PAYMENT_CATEGORY,
    VISA_MAJOR_CATEGORY_RCOUNTRY_ID

} from "./actionType"
// Document Category
export const documentCategoryList = (data, callback) => ({
    type: DOCUMENT_CATEGORY_LIST,
    data,
    callback,
});

export const documentCategoryAdd = (data, callback) => ({
    type: ADD_DOCUMENT_CATEGORY,
    data,
    callback,
});

export const documentCategoryEdit = (data, callback) => ({
    type: EDIT_DOCUMENT_CATEGORY,
    data,
    callback,
});

export const documentCategoryDelete = (data, callback) => ({
    type: DELETE_DOCUMENT_CATEGORY,
    data,
    callback,
});

export const documentCategoryExportData = (data, callback) => ({
    type: EXPORT_DOCUMENT_CATEGORY,
    data,
    callback,
});

export const documentCategoryImportData = (data, callback) => ({
    type: IMPORT_DOCUMENT_CATEGORY,
    data,
    callback,
});
// Document Name
export const documentNameList = (data, callback) => ({
    type: DOCUMENT_NAME_LIST,
    data,
    callback,
});

export const documentNameAdd = (data, callback) => ({
    type: ADD_DOCUMENT_NAME,
    data,
    callback,
});

export const documentNameEdit = (data, callback) => ({
    type: EDIT_DOCUMENT_NAME,
    data,
    callback,
});

export const documentNameDelete = (data, callback) => ({
    type: DELETE_DOCUMENT_NAME,
    data,
    callback,
});

export const documentNameExportData = (data, callback) => ({
    type: EXPORT_DOCUMENT_NAME,
    data,
    callback,
});

export const documentNameImportData = (data, callback) => ({
    type: IMPORT_DOCUMENT_NAME,
    data,
    callback,
});
// Document Type
export const documentTypeList = (data, callback) => ({
    type: DOCUMENT_TYPE_LIST,
    data,
    callback,
});

export const documentTypeAdd = (data, callback) => ({
    type: ADD_DOCUMENT_TYPE,
    data,
    callback,
});

export const documentTypeEdit = (data, callback) => ({
    type: EDIT_DOCUMENT_TYPE,
    data,
    callback,
});

export const documentTypeDelete = (data, callback) => ({
    type: DELETE_DOCUMENT_TYPE,
    data,
    callback,
});

export const documentTypeExportData = (data, callback) => ({
    type: EXPORT_DOCUMENT_TYPE,
    data,
    callback,
});

export const documentTypeImportData = (data, callback) => ({
    type: IMPORT_DOCUMENT_TYPE,
    data,
    callback,
});
// Purpose of Visit
export const purposeOfVisitList = (data, callback) => ({
    type: PURPOSE_OF_VISIT_LIST,
    data,
    callback,
});

export const purposeOfVisitAdd = (data, callback) => ({
    type: ADD_PURPOSE_OF_VISIT,
    data,
    callback,
});

export const purposeOfVisitEdit = (data, callback) => ({
    type: EDIT_PURPOSE_OF_VISIT,
    data,
    callback,
});

export const purposeOfVisitDelete = (data, callback) => ({
    type: DELETE_PURPOSE_OF_VISIT,
    data,
    callback,
});

export const purposeOfVisitExportData = (data, callback) => ({
    type: EXPORT_PURPOSE_OF_VISIT,
    data,
    callback,
});

export const purposeOfVisitImportData = (data, callback) => ({
    type: IMPORT_PURPOSE_OF_VISIT,
    data,
    callback,
});
// Documents For
export const documentsForList = (data, callback) => ({
    type: DOCUMENTS_FOR_LIST,
    data,
    callback,
});

export const documentsForAdd = (data, callback) => ({
    type: ADD_DOCUMENTS_FOR,
    data,
    callback,
});

export const documentsForEdit = (data, callback) => ({
    type: EDIT_DOCUMENTS_FOR,
    data,
    callback,
});

export const documentsForDelete = (data, callback) => ({
    type: DELETE_DOCUMENTS_FOR,
    data,
    callback,
});

export const documentsForExportData = (data, callback) => ({
    type: EXPORT_DOCUMENTS_FOR,
    data,
    callback,
});

export const documentsForImportData = (data, callback) => ({
    type: IMPORT_DOCUMENTS_FOR,
    data,
    callback,
});
// Required Documents (General)
export const requiredDocumentGeneralList = (data, callback) => ({
    type: REQUIRED_DOCUMENT_GENERAL_LIST,
    data,
    callback,
});

export const requiredDocumentGeneralAdd = (data, callback) => ({
    type: ADD_REQUIRED_DOCUMENT_GENERAL,
    data,
    callback,
});

export const requiredDocumentGeneralEdit = (data, callback) => ({
    type: EDIT_REQUIRED_DOCUMENT_GENERAL,
    data,
    callback,
});

export const requiredDocumentGeneralDelete = (data, callback) => ({
    type: DELETE_REQUIRED_DOCUMENT_GENERAL,
    data,
    callback,
});

export const requiredDocumentGeneralExportData = (data, callback) => ({
    type: EXPORT_REQUIRED_DOCUMENT_GENERAL,
    data,
    callback,
});

export const requiredDocumentGeneralImportData = (data, callback) => ({
    type: IMPORT_REQUIRED_DOCUMENT_GENERAL,
    data,
    callback,
});
// Process Status Name
export const processStatusNameList = (data, callback) => ({
    type: PROCESS_STATUS_NAME_LIST,
    data,
    callback,
});

export const processStatusNameAdd = (data, callback) => ({
    type: ADD_PROCESS_STATUS_NAME,
    data,
    callback,
});

export const processStatusNameEdit = (data, callback) => ({
    type: EDIT_PROCESS_STATUS_NAME,
    data,
    callback,
});

export const processStatusNameDelete = (data, callback) => ({
    type: DELETE_PROCESS_STATUS_NAME,
    data,
    callback,
});

export const processStatusNameExportData = (data, callback) => ({
    type: EXPORT_PROCESS_STATUS_NAME,
    data,
    callback,
});

export const processStatusNameImportData = (data, callback) => ({
    type: IMPORT_PROCESS_STATUS_NAME,
    data,
    callback,
});
// Process Sub-Status Name
export const processSubStatusNameList = (data, callback) => ({
    type: PROCESS_SUB_STATUS_NAME_LIST,
    data,
    callback,
});

export const processSubStatusNameAdd = (data, callback) => ({
    type: ADD_PROCESS_SUB_STATUS_NAME,
    data,
    callback,
});

export const processSubStatusNameEdit = (data, callback) => ({
    type: EDIT_PROCESS_SUB_STATUS_NAME,
    data,
    callback,
});

export const processSubStatusNameDelete = (data, callback) => ({
    type: DELETE_PROCESS_SUB_STATUS_NAME,
    data,
    callback,
});

export const processSubStatusNameExportData = (data, callback) => ({
    type: EXPORT_PROCESS_SUB_STATUS_NAME,
    data,
    callback,
});

export const processSubStatusNameImportData = (data, callback) => ({
    type: IMPORT_PROCESS_SUB_STATUS_NAME,
    data,
    callback,
});
// Process Type
export const processTypeList = (data, callback) => ({
    type: PROCESS_TYPE_LIST,
    data,
    callback,
});

export const processTypeAdd = (data, callback) => ({
    type: ADD_PROCESS_TYPE,
    data,
    callback,
});

export const processTypeEdit = (data, callback) => ({
    type: EDIT_PROCESS_TYPE,
    data,
    callback,
});

export const processTypeDelete = (data, callback) => ({
    type: DELETE_PROCESS_TYPE,
    data,
    callback,
});

export const processTypeExportData = (data, callback) => ({
    type: EXPORT_PROCESS_TYPE,
    data,
    callback,
});

export const processTypeImportData = (data, callback) => ({
    type: IMPORT_PROCESS_TYPE,
    data,
    callback,
});
// Payment To
export const paymentToList = (data, callback) => ({
    type: PAYMENT_TO_LIST,
    data,
    callback,
});

export const paymentToAdd = (data, callback) => ({
    type: ADD_PAYMENT_TO,
    data,
    callback,
});

export const paymentToEdit = (data, callback) => ({
    type: EDIT_PAYMENT_TO,
    data,
    callback,
});

export const paymentToDelete = (data, callback) => ({
    type: DELETE_PAYMENT_TO,
    data,
    callback,
});

export const paymentToExportData = (data, callback) => ({
    type: EXPORT_PAYMENT_TO,
    data,
    callback,
});

export const paymentToImportData = (data, callback) => ({
    type: IMPORT_PAYMENT_TO,
    data,
    callback,
});
// Payment Category
export const paymentCategoryList = (data, callback) => ({
    type: PAYMENT_CATEGORY_LIST,
    data,
    callback,
});

export const paymentCategoryAdd = (data, callback) => ({
    type: ADD_PAYMENT_CATEGORY,
    data,
    callback,
});

export const paymentCategoryEdit = (data, callback) => ({
    type: EDIT_PAYMENT_CATEGORY,
    data,
    callback,
});

export const paymentCategoryDelete = (data, callback) => ({
    type: DELETE_PAYMENT_CATEGORY,
    data,
    callback,
});

export const paymentCategoryExportData = (data, callback) => ({
    type: EXPORT_PAYMENT_CATEGORY,
    data,
    callback,
});

export const paymentCategoryImportData = (data, callback) => ({
    type: IMPORT_PAYMENT_CATEGORY,
    data,
    callback,
});

export const visamajorCategoryRCountryIdList = (data, callback) => ({
    type: VISA_MAJOR_CATEGORY_RCOUNTRY_ID,
    data,
    callback,
});









