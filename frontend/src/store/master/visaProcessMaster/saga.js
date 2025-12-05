import { call, takeEvery } from "redux-saga/effects";
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
import {
    getDocumentCategoryListAPI,
    addDocumentCategoryAPI,
    editDocumentCategoryAPI,
    deleteDocumentCategoryAPI,
    exportDocumentCategoryAPI,
    importDocumentCategoryAPI,
    getDocumentNameListAPI,
    addDocumentNameAPI,
    editDocumentNameAPI,
    deleteDocumentNameAPI,
    exportDocumentNameAPI,
    importDocumentNameAPI,
    getDocumentTypeListAPI,
    addDocumentTypeAPI,
    editDocumentTypeAPI,
    deleteDocumentTypeAPI,
    exportDocumentTypeAPI,
    importDocumentTypeAPI,
    getPurposeOfVisitListAPI,
    addPurposeOfVisitAPI,
    editPurposeOfVisitAPI,
    deletePurposeOfVisitAPI,
    exportPurposeOfVisitAPI,
    importPurposeOfVisitAPI,
    getDocumentsForListAPI,
    addDocumentsForAPI,
    editDocumentsForAPI,
    deleteDocumentsForAPI,
    exportDocumentsForAPI,
    importDocumentsForAPI,
    getRequiredDocumentGeneralListAPI,
    addRequiredDocumentGeneralAPI,
    editRequiredDocumentGeneralAPI,
    deleteRequiredDocumentGeneralAPI,
    exportRequiredDocumentGeneralAPI,
    importRequiredDocumentGeneralAPI,
    getProcessStatusNameListAPI,
    addProcessStatusNameAPI,
    editProcessStatusNameAPI,
    deleteProcessStatusNameAPI,
    exportProcessStatusNameAPI,
    importProcessStatusNameAPI,
    getProcessSubStatusNameListAPI,
    addProcessSubStatusNameAPI,
    editProcessSubStatusNameAPI,
    deleteProcessSubStatusNameAPI,
    exportProcessSubStatusNameAPI,
    importProcessSubStatusNameAPI,
    getProcessTypeListAPI,
    addProcessTypeAPI,
    editProcessTypeAPI,
    deleteProcessTypeAPI,
    exportProcessTypeAPI,
    importProcessTypeAPI,
    getPaymentToListAPI,
    addPaymentToAPI,
    editPaymentToAPI,
    deletePaymentToAPI,
    exportPaymentToAPI,
    importPaymentToAPI,
    getPaymentCategoryListAPI,
    addPaymentCategoryAPI,
    editPaymentCategoryAPI,
    deletePaymentCategoryAPI,
    exportPaymentCategoryAPI,
    importPaymentCategoryAPI,
    visaMajorCategoryRCountryIdAPI,

} from "../../../service/api_helper";

// --- DOCUMENT CATEGORY SAGAS ---
function* documentCategoryListSaga(action) {
    try {
        const response = yield call(getDocumentCategoryListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentCategoryAddSaga(action) {
    try {
        const response = yield call(addDocumentCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentCategoryEditSaga(action) {
    try {
        const response = yield call(editDocumentCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentCategoryDeleteSaga(action) {
    try {
        const response = yield call(deleteDocumentCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentCategoryExportDataSaga(action) {
    try {
        const response = yield call(exportDocumentCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentCategoryImportDataSaga(action) {
    try {
        const response = yield call(importDocumentCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Document Name
function* documentNameListSaga(action) {
    try {
        const response = yield call(getDocumentNameListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentNameAddSaga(action) {
    try {
        const response = yield call(addDocumentNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentNameEditSaga(action) {
    try {
        const response = yield call(editDocumentNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentNameDeleteSaga(action) {
    try {
        const response = yield call(deleteDocumentNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentNameExportDataSaga(action) {
    try {
        const response = yield call(exportDocumentNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentNameImportDataSaga(action) {
    try {
        const response = yield call(importDocumentNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

// Document Type
function* documentTypeListSaga(action) {
    try {
        const response = yield call(getDocumentTypeListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentTypeAddSaga(action) {
    try {
        const response = yield call(addDocumentTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentTypeEditSaga(action) {
    try {
        const response = yield call(editDocumentTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentTypeDeleteSaga(action) {
    try {
        const response = yield call(deleteDocumentTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentTypeExportDataSaga(action) {
    try {
        const response = yield call(exportDocumentTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentTypeImportDataSaga(action) {
    try {
        const response = yield call(importDocumentTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

// Purpose of Visit
function* purposeOfVisitListSaga(action) {
    try {
        const response = yield call(getPurposeOfVisitListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* purposeOfVisitAddSaga(action) {
    try {
        const response = yield call(addPurposeOfVisitAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* purposeOfVisitEditSaga(action) {
    try {
        const response = yield call(editPurposeOfVisitAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* purposeOfVisitDeleteSaga(action) {
    try {
        const response = yield call(deletePurposeOfVisitAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* purposeOfVisitExportDataSaga(action) {
    try {
        const response = yield call(exportPurposeOfVisitAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* purposeOfVisitImportDataSaga(action) {
    try {
        const response = yield call(importPurposeOfVisitAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Documents For
function* documentsForListSaga(action) {
    try {
        const response = yield call(getDocumentsForListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentsForAddSaga(action) {
    try {
        const response = yield call(addDocumentsForAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentsForEditSaga(action) {
    try {
        const response = yield call(editDocumentsForAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentsForDeleteSaga(action) {
    try {
        const response = yield call(deleteDocumentsForAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentsForExportDataSaga(action) {
    try {
        const response = yield call(exportDocumentsForAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* documentsForImportDataSaga(action) {
    try {
        const response = yield call(importDocumentsForAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Required document general
function* requiredDocumentGeneralListSaga(action) {
    try {
        const response = yield call(getRequiredDocumentGeneralListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* requiredDocumentGeneralAddSaga(action) {
    try {
        const response = yield call(addRequiredDocumentGeneralAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* requiredDocumentGeneralEditSaga(action) {
    try {
        const response = yield call(editRequiredDocumentGeneralAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* requiredDocumentGeneralDeleteSaga(action) {
    try {
        const response = yield call(deleteRequiredDocumentGeneralAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* requiredDocumentGeneralExportDataSaga(action) {
    try {
        const response = yield call(exportRequiredDocumentGeneralAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* requiredDocumentGeneralImportDataSaga(action) {
    try {
        const response = yield call(importRequiredDocumentGeneralAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Process status Name
function* processStatusNameListSaga(action) {
    try {
        const response = yield call(getProcessStatusNameListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* processStatusNameAddSaga(action) {
    try {
        const response = yield call(addProcessStatusNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* processStatusNameEditSaga(action) {
    try {
        const response = yield call(editProcessStatusNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* processStatusNameDeleteSaga(action) {
    try {
        const response = yield call(deleteProcessStatusNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* processStatusNameExportDataSaga(action) {
    try {
        const response = yield call(exportProcessStatusNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* processStatusNameImportDataSaga(action) {
    try {
        const response = yield call(importProcessStatusNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Process sub status name
function* processSubStatusNameListSaga(action) {
    try {
        const response = yield call(getProcessSubStatusNameListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* processSubStatusNameAddSaga(action) {
    try {
        const response = yield call(addProcessSubStatusNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* processSubStatusNameEditSaga(action) {
    try {
        const response = yield call(editProcessSubStatusNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* processSubStatusNameDeleteSaga(action) {
    try {
        const response = yield call(deleteProcessSubStatusNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* processSubStatusNameExportDataSaga(action) {
    try {
        const response = yield call(exportProcessSubStatusNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* processSubStatusNameImportDataSaga(action) {
    try {
        const response = yield call(importProcessSubStatusNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Process Type
function* processTypeListSaga(action) {
    try {
        const response = yield call(getProcessTypeListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* processTypeAddSaga(action) {
    try {
        const response = yield call(addProcessTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* processTypeEditSaga(action) {
    try {
        const response = yield call(editProcessTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* processTypeDeleteSaga(action) {
    try {
        const response = yield call(deleteProcessTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* processTypeExportDataSaga(action) {
    try {
        const response = yield call(exportProcessTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* processTypeImportDataSaga(action) {
    try {
        const response = yield call(importProcessTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Process To
function* paymentToListSaga(action) {
    try {
        const response = yield call(getPaymentToListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* paymentToAddSaga(action) {
    try {
        const response = yield call(addPaymentToAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* paymentToEditSaga(action) {
    try {
        const response = yield call(editPaymentToAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* paymentToDeleteSaga(action) {
    try {
        const response = yield call(deletePaymentToAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* paymentToExportDataSaga(action) {
    try {
        const response = yield call(exportPaymentToAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* paymentToImportDataSaga(action) {
    try {
        const response = yield call(importPaymentToAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Payment Category
function* paymentCategoryListSaga(action) {
    try {
        const response = yield call(getPaymentCategoryListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* paymentCategoryAddSaga(action) {
    try {
        const response = yield call(addPaymentCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* paymentCategoryEditSaga(action) {
    try {
        const response = yield call(editPaymentCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* paymentCategoryDeleteSaga(action) {
    try {
        const response = yield call(deletePaymentCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* paymentCategoryExportDataSaga(action) {
    try {
        const response = yield call(exportPaymentCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* paymentCategoryImportDataSaga(action) {
    try {
        const response = yield call(importPaymentCategoryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}


function* visaMajorCategoryRCountryIdSaga(action) {
    try {
        const response = yield call(visaMajorCategoryRCountryIdAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}



function* visaProcessMasterSaga() {
    yield takeEvery(DOCUMENT_CATEGORY_LIST, documentCategoryListSaga);
    yield takeEvery(ADD_DOCUMENT_CATEGORY, documentCategoryAddSaga);
    yield takeEvery(EDIT_DOCUMENT_CATEGORY, documentCategoryEditSaga);
    yield takeEvery(DELETE_DOCUMENT_CATEGORY, documentCategoryDeleteSaga);
    yield takeEvery(EXPORT_DOCUMENT_CATEGORY, documentCategoryExportDataSaga);
    yield takeEvery(IMPORT_DOCUMENT_CATEGORY, documentCategoryImportDataSaga);
    yield takeEvery(DOCUMENT_NAME_LIST, documentNameListSaga);
    yield takeEvery(ADD_DOCUMENT_NAME, documentNameAddSaga);
    yield takeEvery(EDIT_DOCUMENT_NAME, documentNameEditSaga);
    yield takeEvery(DELETE_DOCUMENT_NAME, documentNameDeleteSaga);
    yield takeEvery(EXPORT_DOCUMENT_NAME, documentNameExportDataSaga);
    yield takeEvery(IMPORT_DOCUMENT_NAME, documentNameImportDataSaga);
    yield takeEvery(DOCUMENT_TYPE_LIST, documentTypeListSaga);
    yield takeEvery(ADD_DOCUMENT_TYPE, documentTypeAddSaga);
    yield takeEvery(EDIT_DOCUMENT_TYPE, documentTypeEditSaga);
    yield takeEvery(DELETE_DOCUMENT_TYPE, documentTypeDeleteSaga);
    yield takeEvery(EXPORT_DOCUMENT_TYPE, documentTypeExportDataSaga);
    yield takeEvery(IMPORT_DOCUMENT_TYPE, documentTypeImportDataSaga);
    yield takeEvery(PURPOSE_OF_VISIT_LIST, purposeOfVisitListSaga);
    yield takeEvery(ADD_PURPOSE_OF_VISIT, purposeOfVisitAddSaga);
    yield takeEvery(EDIT_PURPOSE_OF_VISIT, purposeOfVisitEditSaga);
    yield takeEvery(DELETE_PURPOSE_OF_VISIT, purposeOfVisitDeleteSaga);
    yield takeEvery(EXPORT_PURPOSE_OF_VISIT, purposeOfVisitExportDataSaga);
    yield takeEvery(IMPORT_PURPOSE_OF_VISIT, purposeOfVisitImportDataSaga);
    yield takeEvery(DOCUMENTS_FOR_LIST, documentsForListSaga);
    yield takeEvery(ADD_DOCUMENTS_FOR, documentsForAddSaga);
    yield takeEvery(EDIT_DOCUMENTS_FOR, documentsForEditSaga);
    yield takeEvery(DELETE_DOCUMENTS_FOR, documentsForDeleteSaga);
    yield takeEvery(EXPORT_DOCUMENTS_FOR, documentsForExportDataSaga);
    yield takeEvery(IMPORT_DOCUMENTS_FOR, documentsForImportDataSaga);
    yield takeEvery(REQUIRED_DOCUMENT_GENERAL_LIST, requiredDocumentGeneralListSaga);
    yield takeEvery(ADD_REQUIRED_DOCUMENT_GENERAL, requiredDocumentGeneralAddSaga);
    yield takeEvery(EDIT_REQUIRED_DOCUMENT_GENERAL, requiredDocumentGeneralEditSaga);
    yield takeEvery(DELETE_REQUIRED_DOCUMENT_GENERAL, requiredDocumentGeneralDeleteSaga);
    yield takeEvery(EXPORT_REQUIRED_DOCUMENT_GENERAL, requiredDocumentGeneralExportDataSaga);
    yield takeEvery(IMPORT_REQUIRED_DOCUMENT_GENERAL, requiredDocumentGeneralImportDataSaga);
    yield takeEvery(PROCESS_STATUS_NAME_LIST, processStatusNameListSaga);
    yield takeEvery(ADD_PROCESS_STATUS_NAME, processStatusNameAddSaga);
    yield takeEvery(EDIT_PROCESS_STATUS_NAME, processStatusNameEditSaga);
    yield takeEvery(DELETE_PROCESS_STATUS_NAME, processStatusNameDeleteSaga);
    yield takeEvery(EXPORT_PROCESS_STATUS_NAME, processStatusNameExportDataSaga);
    yield takeEvery(IMPORT_PROCESS_STATUS_NAME, processStatusNameImportDataSaga);
    yield takeEvery(PROCESS_SUB_STATUS_NAME_LIST, processSubStatusNameListSaga);
    yield takeEvery(ADD_PROCESS_SUB_STATUS_NAME, processSubStatusNameAddSaga);
    yield takeEvery(EDIT_PROCESS_SUB_STATUS_NAME, processSubStatusNameEditSaga);
    yield takeEvery(DELETE_PROCESS_SUB_STATUS_NAME, processSubStatusNameDeleteSaga);
    yield takeEvery(EXPORT_PROCESS_SUB_STATUS_NAME, processSubStatusNameExportDataSaga);
    yield takeEvery(IMPORT_PROCESS_SUB_STATUS_NAME, processSubStatusNameImportDataSaga);
    yield takeEvery(PROCESS_TYPE_LIST, processTypeListSaga);
    yield takeEvery(ADD_PROCESS_TYPE, processTypeAddSaga);
    yield takeEvery(EDIT_PROCESS_TYPE, processTypeEditSaga);
    yield takeEvery(DELETE_PROCESS_TYPE, processTypeDeleteSaga);
    yield takeEvery(EXPORT_PROCESS_TYPE, processTypeExportDataSaga);
    yield takeEvery(IMPORT_PROCESS_TYPE, processTypeImportDataSaga);
    yield takeEvery(PAYMENT_TO_LIST, paymentToListSaga);
    yield takeEvery(ADD_PAYMENT_TO, paymentToAddSaga);
    yield takeEvery(EDIT_PAYMENT_TO, paymentToEditSaga);
    yield takeEvery(DELETE_PAYMENT_TO, paymentToDeleteSaga);
    yield takeEvery(EXPORT_PAYMENT_TO, paymentToExportDataSaga);
    yield takeEvery(IMPORT_PAYMENT_TO, paymentToImportDataSaga);
    yield takeEvery(PAYMENT_CATEGORY_LIST, paymentCategoryListSaga);
    yield takeEvery(ADD_PAYMENT_CATEGORY, paymentCategoryAddSaga);
    yield takeEvery(EDIT_PAYMENT_CATEGORY, paymentCategoryEditSaga);
    yield takeEvery(DELETE_PAYMENT_CATEGORY, paymentCategoryDeleteSaga);
    yield takeEvery(EXPORT_PAYMENT_CATEGORY, paymentCategoryExportDataSaga);
    yield takeEvery(IMPORT_PAYMENT_CATEGORY, paymentCategoryImportDataSaga);
    yield takeEvery(VISA_MAJOR_CATEGORY_RCOUNTRY_ID,visaMajorCategoryRCountryIdSaga);

}

export default visaProcessMasterSaga;

