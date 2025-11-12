import { call, takeEvery } from "redux-saga/effects";
import {
    JOB_TYPE_LIST,
    ADD_JOB_TYPE,
    EDIT_JOB_TYPE,
    DELETE_JOB_TYPE,
    EXPORT_JOB_TYPE,
    IMPORT_JOB_TYPE,
    MODE_OF_SALARY_LIST,
    ADD_MODE_OF_SALARY,
    EDIT_MODE_OF_SALARY,
    DELETE_MODE_OF_SALARY,
    EXPORT_MODE_OF_SALARY,
    IMPORT_MODE_OF_SALARY,
    IT_RETURN_STATUS_LIST,
    ADD_IT_RETURN_STATUS,
    EDIT_IT_RETURN_STATUS,
    DELETE_IT_RETURN_STATUS,
    EXPORT_IT_RETURN_STATUS,
    IMPORT_IT_RETURN_STATUS,
    OCCUPATION_TYPE_LIST,
    ADD_OCCUPATION_TYPE,
    EDIT_OCCUPATION_TYPE,
    DELETE_OCCUPATION_TYPE,
    EXPORT_OCCUPATION_TYPE,
    IMPORT_OCCUPATION_TYPE,
    OCCUPATION_PROSPECT_LIST,
    ADD_OCCUPATION_PROSPECT,
    EDIT_OCCUPATION_PROSPECT,
    DELETE_OCCUPATION_PROSPECT,
    EXPORT_OCCUPATION_PROSPECT,
    IMPORT_OCCUPATION_PROSPECT,
} from "./actionType";

import {
    getJobTypeListDataAPI,
    addJobTypeDataAPI,
    editJobTypeDataAPI,
    deleteJobTypeDataAPI,
    exportJobTypeDataAPI,
    importJobTypeDataAPI,
    getModeOfSalaryDataAPI,
    addModeOfSalaryDataAPI,
    editModeOfSalaryDataAPI,
    deleteModeOfSalaryDataAPI,
    exportModeOfSalaryDataAPI,
    importModeOfSalaryDataAPI,
    getItReturnStatusListDataAPI,
    addItReturnStatusDataAPI,
    editItReturnStatusDataAPI,
    deleteItReturnStatusDataAPI,
    exportItReturnStatusDataAPI,
    importItReturnStatusDataAPI,
    getOccupationTypeListDataAPI,
    addOccupationTypeDataAPI,
    editOccupationTypeDataAPI,
    deleteOccupationTypeDataAPI,
    exportOccupationTypeDataAPI,
    importOccupationTypeDataAPI,
    getOccupationProspectListDataAPI,
    addOccupationProspectDataAPI,
    editOccupationProspectDataAPI,
    deleteOccupationProspectDataAPI,
    exportOccupationProspectDataAPI,
    importOccupationProspectDataAPI,
} from "../../../service/api_helper";

// --- JOB TYPE SAGAS ---
function* jobTypeListSaga(action) {
    try {
        const response = yield call(getJobTypeListDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* jobTypeAddSaga(action) {
    try {
        const response = yield call(addJobTypeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* jobTypeEditSaga(action) {
    try {
        const response = yield call(editJobTypeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* jobTypeDeleteSaga(action) {
    try {
        const response = yield call(deleteJobTypeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* jobTypeExportDataSaga(action) {
    try {
        const response = yield call(exportJobTypeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* jobTypeImportDataSaga(action) {
    try {
        const response = yield call(importJobTypeDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}


// Mode of Salary 
function* modeOfSalaryListSaga(action) {
    try {
        const response = yield call(getModeOfSalaryDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

function* modeOfSalaryAddSaga(action) {
    try {
        const response = yield call(addModeOfSalaryDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
function* modeOfSalaryEditSaga(action) {
    try {
        const response = yield call(editModeOfSalaryDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
function* modeOfSalaryDeleteSaga(action) {
    try {
        const response = yield call(deleteModeOfSalaryDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
function* modeOfSalaryExportDataSaga(action) {
    try {
        const response = yield call(exportModeOfSalaryDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}
function* modeOfSalaryImportDataSaga(action) {
    try {
        const response = yield call(importModeOfSalaryDataAPI, action?.data);
        if (action.callback) action.callback(response);
    } catch (error) {
        if (action.callback) action.callback(null, error);
    }
}

// --- IT RETURN STATUS SAGAS ---
function* itReturnStatusListSaga(action) {
    try {
        const response = yield call(getItReturnStatusListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* itReturnStatusAddSaga(action) {
    try {
        const response = yield call(addItReturnStatusDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* itReturnStatusEditSaga(action) {
    try {
        const response = yield call(editItReturnStatusDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* itReturnStatusDeleteSaga(action) {
    try {
        const response = yield call(deleteItReturnStatusDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* itReturnStatusExportDataSaga(action) {
    try {
        const response = yield call(exportItReturnStatusDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* itReturnStatusImportDataSaga(action) {
    try {
        const response = yield call(importItReturnStatusDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

// --- OCCUPATION TYPE SAGAS ---
function* occupationTypeListSaga(action) {
    try {
        const response = yield call(getOccupationTypeListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* occupationTypeAddSaga(action) {
    try {
        const response = yield call(addOccupationTypeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* occupationTypeEditSaga(action) {
    try {
        const response = yield call(editOccupationTypeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* occupationTypeDeleteSaga(action) {
    try {
        const response = yield call(deleteOccupationTypeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* occupationTypeExportDataSaga(action) {
    try {
        const response = yield call(exportOccupationTypeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* occupationTypeImportDataSaga(action) {
    try {
        const response = yield call(importOccupationTypeDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

// --- OCCUPATION PROSPECT SAGAS ---
function* occupationProspectListSaga(action) {
    try {
        const response = yield call(getOccupationProspectListDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* occupationProspectAddSaga(action) {
    try {
        const response = yield call(addOccupationProspectDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* occupationProspectEditSaga(action) {
    try {
        const response = yield call(editOccupationProspectDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* occupationProspectDeleteSaga(action) {
    try {
        const response = yield call(deleteOccupationProspectDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* occupationProspectExportDataSaga(action) {
    try {
        const response = yield call(exportOccupationProspectDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}

function* occupationProspectImportDataSaga(action) {
    try {
        const response = yield call(importOccupationProspectDataAPI, action?.data);
        action.callback?.(response);
    } catch (error) {
        action.callback?.(null, error);
    }
}






// Root Saga
function* occupationMasterSaga() {
    yield takeEvery(JOB_TYPE_LIST, jobTypeListSaga);
    yield takeEvery(ADD_JOB_TYPE, jobTypeAddSaga);
    yield takeEvery(EDIT_JOB_TYPE, jobTypeEditSaga);
    yield takeEvery(DELETE_JOB_TYPE, jobTypeDeleteSaga);
    yield takeEvery(EXPORT_JOB_TYPE, jobTypeExportDataSaga);
    yield takeEvery(IMPORT_JOB_TYPE, jobTypeImportDataSaga);
    yield takeEvery(MODE_OF_SALARY_LIST, modeOfSalaryListSaga);
    yield takeEvery(ADD_MODE_OF_SALARY, modeOfSalaryAddSaga);
    yield takeEvery(EDIT_MODE_OF_SALARY, modeOfSalaryEditSaga);
    yield takeEvery(DELETE_MODE_OF_SALARY, modeOfSalaryDeleteSaga);
    yield takeEvery(EXPORT_MODE_OF_SALARY, modeOfSalaryExportDataSaga);
    yield takeEvery(IMPORT_MODE_OF_SALARY, modeOfSalaryImportDataSaga);
    yield takeEvery(IT_RETURN_STATUS_LIST, itReturnStatusListSaga);
    yield takeEvery(ADD_IT_RETURN_STATUS, itReturnStatusAddSaga);
    yield takeEvery(EDIT_IT_RETURN_STATUS, itReturnStatusEditSaga);
    yield takeEvery(DELETE_IT_RETURN_STATUS, itReturnStatusDeleteSaga);
    yield takeEvery(EXPORT_IT_RETURN_STATUS, itReturnStatusExportDataSaga);
    yield takeEvery(IMPORT_IT_RETURN_STATUS, itReturnStatusImportDataSaga);
    yield takeEvery(OCCUPATION_TYPE_LIST, occupationTypeListSaga);
    yield takeEvery(ADD_OCCUPATION_TYPE, occupationTypeAddSaga);
    yield takeEvery(EDIT_OCCUPATION_TYPE, occupationTypeEditSaga);
    yield takeEvery(DELETE_OCCUPATION_TYPE, occupationTypeDeleteSaga);
    yield takeEvery(EXPORT_OCCUPATION_TYPE, occupationTypeExportDataSaga);
    yield takeEvery(IMPORT_OCCUPATION_TYPE, occupationTypeImportDataSaga);
    yield takeEvery(OCCUPATION_PROSPECT_LIST, occupationProspectListSaga);
    yield takeEvery(ADD_OCCUPATION_PROSPECT, occupationProspectAddSaga);
    yield takeEvery(EDIT_OCCUPATION_PROSPECT, occupationProspectEditSaga);
    yield takeEvery(DELETE_OCCUPATION_PROSPECT, occupationProspectDeleteSaga);
    yield takeEvery(EXPORT_OCCUPATION_PROSPECT, occupationProspectExportDataSaga);
    yield takeEvery(IMPORT_OCCUPATION_PROSPECT, occupationProspectImportDataSaga);



}
export default occupationMasterSaga;