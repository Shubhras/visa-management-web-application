import { call, takeEvery } from "redux-saga/effects";
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

import {
    getRepresentingCountryListAPI,
    addRepresentingCountryAPI,
    editRepresentingCountryAPI,
    deleteRepresentingCountryAPI,
    exportRepresentingCountryAPI,
    importRepresentingCountryAPI,
    getVisaMajorCategoryListAPI,
    addVisaMajorCategoryAPI,
    editVisaMajorCategoryAPI,
    deleteVisaMajorCategoryAPI,
    exportVisaMajorCategoryAPI,
    importVisaMajorCategoryAPI,
    getApplicantTypeListAPI,
    addApplicantTypeAPI,
    editApplicantTypeAPI,
    deleteApplicantTypeAPI,
    exportApplicantTypeAPI,
    importApplicantTypeAPI,
    getVisaEligibilityTypeListAPI,
    addVisaEligibilityTypeAPI,
    editVisaEligibilityTypeAPI,
    deleteVisaEligibilityTypeAPI,
    exportVisaEligibilityTypeAPI,
    importVisaEligibilityTypeAPI,
    getVisaStatusListAPI,
    addVisaStatusAPI,
    editVisaStatusAPI,
    deleteVisaStatusAPI,
    exportVisaStatusAPI,
    importVisaStatusAPI,
    getPossibilityLevelListAPI,
    addPossibilityLevelAPI,
    editPossibilityLevelAPI,
    deletePossibilityLevelAPI,
    exportPossibilityLevelAPI,
    importPossibilityLevelAPI,
    getVisaNameListAPI,
    addVisaNameAPI,
    editVisaNameAPI,
    deleteVisaNameAPI,
    exportVisaNameAPI,
    importVisaNameAPI,

} from "../../../service/api_helper";

// --- Representing Country SAGAS ---
function* representingCountryListSaga(action) {
    try {
        const response = yield call(getRepresentingCountryListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* representingCountryAddSaga(action) {
    try {
        const response = yield call(addRepresentingCountryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* representingCountryEditSaga(action) {
    try {
        const response = yield call(editRepresentingCountryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* representingCountryDeleteSaga(action) {
    try {
        const response = yield call(deleteRepresentingCountryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* representingCountryExportDataSaga(action) {
    try {
        const response = yield call(exportRepresentingCountryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* representingCountryImportDataSaga(action) {
    try {
        const response = yield call(importRepresentingCountryAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

// Visa Majore Category
function* visaMajorCategoryListSaga(action) {
    try {
        const response = yield call(getVisaMajorCategoryListAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaMajorCategoryAddSaga(action) {
    try {
        const response = yield call(addVisaMajorCategoryAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaMajorCategoryEditSaga(action) {
    try {
        const response = yield call(editVisaMajorCategoryAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaMajorCategoryDeleteSaga(action) {
    try {
        const response = yield call(deleteVisaMajorCategoryAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaMajorCategoryExportSaga(action) {
    try {
        const response = yield call(exportVisaMajorCategoryAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
function* visaMajorCategoryImportSaga(action) {
    try {
        const response = yield call(importVisaMajorCategoryAPI, action.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// Applicant Type Sagas
function* applicantTypeListSaga(action) {
    try {
        const response = yield call(getApplicantTypeListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* applicantTypeAddSaga(action) {
    try {
        const response = yield call(addApplicantTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* applicantTypeEditSaga(action) {
    try {
        const response = yield call(editApplicantTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* applicantTypeDeleteSaga(action) {
    try {
        const response = yield call(deleteApplicantTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* applicantTypeExportSaga(action) {
    try {
        const response = yield call(exportApplicantTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* applicantTypeImportSaga(action) {
    try {
        const response = yield call(importApplicantTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

// VISA ELIGIBILITY TYPE SAGAS
function* visaEligibilityTypeListSaga(action) {
    try {
        const response = yield call(getVisaEligibilityTypeListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaEligibilityTypeAddSaga(action) {
    try {
        const response = yield call(addVisaEligibilityTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaEligibilityTypeEditSaga(action) {
    try {
        const response = yield call(editVisaEligibilityTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaEligibilityTypeDeleteSaga(action) {
    try {
        const response = yield call(deleteVisaEligibilityTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaEligibilityTypeExportDataSaga(action) {
    try {
        const response = yield call(exportVisaEligibilityTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaEligibilityTypeImportDataSaga(action) {
    try {
        const response = yield call(importVisaEligibilityTypeAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// --- VISA STATUS SAGAS ---
function* visaStatusListSaga(action) {
    try {
        const response = yield call(getVisaStatusListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaStatusAddSaga(action) {
    try {
        const response = yield call(addVisaStatusAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaStatusEditSaga(action) {
    try {
        const response = yield call(editVisaStatusAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaStatusDeleteSaga(action) {
    try {
        const response = yield call(deleteVisaStatusAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaStatusExportDataSaga(action) {
    try {
        const response = yield call(exportVisaStatusAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaStatusImportDataSaga(action) {
    try {
        const response = yield call(importVisaStatusAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// --- POSSIBILITY LEVEL SAGAS ---
function* possibilityLevelListSaga(action) {
    try {
        const response = yield call(getPossibilityLevelListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* possibilityLevelAddSaga(action) {
    try {
        const response = yield call(addPossibilityLevelAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* possibilityLevelEditSaga(action) {
    try {
        const response = yield call(editPossibilityLevelAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* possibilityLevelDeleteSaga(action) {
    try {
        const response = yield call(deletePossibilityLevelAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* possibilityLevelExportDataSaga(action) {
    try {
        const response = yield call(exportPossibilityLevelAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* possibilityLevelImportDataSaga(action) {
    try {
        const response = yield call(importPossibilityLevelAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
// ---------------- VISA NAME SAGAS ----------------
function* visaNameListSaga(action) {
    try {
        const response = yield call(getVisaNameListAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaNameAddSaga(action) {
    try {
        const response = yield call(addVisaNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaNameEditSaga(action) {
    try {
        const response = yield call(editVisaNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaNameDeleteSaga(action) {
    try {
        const response = yield call(deleteVisaNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaNameExportDataSaga(action) {
    try {
        const response = yield call(exportVisaNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* visaNameImportDataSaga(action) {
    try {
        const response = yield call(importVisaNameAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}





function* visaMasterSaga() {

    yield takeEvery(REPRESENTING_COUNTRY_LIST, representingCountryListSaga);
    yield takeEvery(ADD_REPRESENTING_COUNTRY, representingCountryAddSaga);
    yield takeEvery(EDIT_REPRESENTING_COUNTRY, representingCountryEditSaga);
    yield takeEvery(DELETE_REPRESENTING_COUNTRY, representingCountryDeleteSaga);
    yield takeEvery(EXPORT_REPRESENTING_COUNTRY, representingCountryExportDataSaga);
    yield takeEvery(IMPORT_REPRESENTING_COUNTRY, representingCountryImportDataSaga);
    yield takeEvery(VISA_MAJOR_CATEGORY_LIST, visaMajorCategoryListSaga);
    yield takeEvery(ADD_VISA_MAJOR_CATEGORY, visaMajorCategoryAddSaga);
    yield takeEvery(EDIT_VISA_MAJOR_CATEGORY, visaMajorCategoryEditSaga);
    yield takeEvery(DELETE_VISA_MAJOR_CATEGORY, visaMajorCategoryDeleteSaga);
    yield takeEvery(EXPORT_VISA_MAJOR_CATEGORY, visaMajorCategoryExportSaga);
    yield takeEvery(IMPORT_VISA_MAJOR_CATEGORY, visaMajorCategoryImportSaga);
    yield takeEvery(APPLICANT_TYPE_LIST, applicantTypeListSaga);
    yield takeEvery(ADD_APPLICANT_TYPE, applicantTypeAddSaga);
    yield takeEvery(EDIT_APPLICANT_TYPE, applicantTypeEditSaga);
    yield takeEvery(DELETE_APPLICANT_TYPE, applicantTypeDeleteSaga);
    yield takeEvery(EXPORT_APPLICANT_TYPE, applicantTypeExportSaga);
    yield takeEvery(IMPORT_APPLICANT_TYPE, applicantTypeImportSaga);
    yield takeEvery(VISA_ELIGIBILITY_TYPE_LIST, visaEligibilityTypeListSaga);
    yield takeEvery(ADD_VISA_ELIGIBILITY_TYPE, visaEligibilityTypeAddSaga);
    yield takeEvery(EDIT_VISA_ELIGIBILITY_TYPE, visaEligibilityTypeEditSaga);
    yield takeEvery(DELETE_VISA_ELIGIBILITY_TYPE, visaEligibilityTypeDeleteSaga);
    yield takeEvery(EXPORT_VISA_ELIGIBILITY_TYPE, visaEligibilityTypeExportDataSaga);
    yield takeEvery(IMPORT_VISA_ELIGIBILITY_TYPE, visaEligibilityTypeImportDataSaga);
    yield takeEvery(VISA_STATUS_LIST, visaStatusListSaga);
    yield takeEvery(ADD_VISA_STATUS, visaStatusAddSaga);
    yield takeEvery(EDIT_VISA_STATUS, visaStatusEditSaga);
    yield takeEvery(DELETE_VISA_STATUS, visaStatusDeleteSaga);
    yield takeEvery(EXPORT_VISA_STATUS, visaStatusExportDataSaga);
    yield takeEvery(IMPORT_VISA_STATUS, visaStatusImportDataSaga);
    yield takeEvery(POSSIBILITY_LEVEL_LIST, possibilityLevelListSaga);
    yield takeEvery(ADD_POSSIBILITY_LEVEL, possibilityLevelAddSaga);
    yield takeEvery(EDIT_POSSIBILITY_LEVEL, possibilityLevelEditSaga);
    yield takeEvery(DELETE_POSSIBILITY_LEVEL, possibilityLevelDeleteSaga);
    yield takeEvery(EXPORT_POSSIBILITY_LEVEL, possibilityLevelExportDataSaga);
    yield takeEvery(IMPORT_POSSIBILITY_LEVEL, possibilityLevelImportDataSaga);
    yield takeEvery(VISA_NAME_LIST, visaNameListSaga);
    yield takeEvery(ADD_VISA_NAME, visaNameAddSaga);
    yield takeEvery(EDIT_VISA_NAME, visaNameEditSaga);
    yield takeEvery(DELETE_VISA_NAME, visaNameDeleteSaga);
    yield takeEvery(EXPORT_VISA_NAME, visaNameExportDataSaga);
    yield takeEvery(IMPORT_VISA_NAME, visaNameImportDataSaga);








}
export default visaMasterSaga;