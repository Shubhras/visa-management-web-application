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
}
export default instituteMasterSaga;