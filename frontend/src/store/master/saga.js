import { call, takeEvery } from "redux-saga/effects";
import {
  DEPARTMENT_LIST,
  ADD_DEPARTMENT,
  EDIT_DEPARTMENT,
  DELETE_DEPARTMENT,
  EXPORT_DEPARTMENT,
  IMPORT_DEPARTMENT,

  COUNTRY_LIST ,
  ADD_COUNTRY ,  
  EDIT_COUNTRY,  
  DELETE_COUNTRY,
  EXPORT_COUNTRY,
  IMPORT_COUNTRY,

  STATE_LIST ,
  ADD_STATE ,  
  EDIT_STATE , 
  DELETE_STATE,
  EXPORT_STATE,
  IMPORT_STATE,




  EMPLOYEE_TYPE_LIST,
  ADD_EMPLOYEE_TYPE,
  EDIT_EMPLOYEE_TYPE,
  DELETE_EMPLOYEE_TYPE,
  EXPORT_EMPLOYEE_TYPE,
  IMPORT_EMPLOYEE_TYPE
} from "./actionTypes";

import {
  getDepartmentListDataAPI,
  addDepartmentDataAPI,
  editDepartmentDataAPI,
  deleteDepartmentDataAPI,
  exportDepartmentDataAPI,
  importDepartmentDataAPI,


  getCountryListDataAPI,
  addCountryDataAPI,
  editCountryDataAPI,
  deleteCountryDataAPI,
  exportCountryDataAPI,
  importCountryDataAPI,

  getStateListDataAPI,
  addStateDataAPI,
  editStateDataAPI,
  deleteStateDataAPI,
  exportStateDataAPI,
  importStateDataAPI,







  getEmployeeTypeListDataAPI,
  addEmployeeTypeDataAPI,
  editEmployeeTypeDataAPI,
  deleteEmployeeTypeDataAPI,
  exportEmployeeTypeDataAPI,
  importEmployeeTypeDataAPI
} from "../../service/api_helper";

function* departmentListSaga(action) {
  try {
    const response = yield call(getDepartmentListDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* departmentAddSaga(action) {
  try {
    const response = yield call(addDepartmentDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* departmentEditSaga(action) {
  try {
    const response = yield call(editDepartmentDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* departmentDeleteSaga(action) {
  try {
    const response = yield call(deleteDepartmentDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}

function* departmentExportDataSaga(action) {
  try {
    const response = yield call(exportDepartmentDataAPI, action?.data);
    if (action.callback) {

      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* departmentImportDataSaga(action) {
  try {
    const response = yield call(importDepartmentDataAPI, action?.data);
    if (action.callback) {

      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}


//COUNTRY

function* countryListSaga(action) {
  try {
    const response = yield call(getCountryListDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* countryAddSaga(action) {
  try {
    const response = yield call(addCountryDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* countryEditSaga(action) {
  try {
    const response = yield call(editCountryDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* countryDeleteSaga(action) {
  try {
    const response = yield call(deleteCountryDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}

function* countryExportDataSaga(action) {
  try {
    const response = yield call(exportCountryDataAPI, action?.data);
    if (action.callback) {

      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* countryImportDataSaga(action) {
  try {
    const response = yield call(importCountryDataAPI, action?.data);
    if (action.callback) {

      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}


//state
function* stateListSaga(action) {
  try {
    const response = yield call(getStateListDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* stateAddSaga(action) {
  try {
    const response = yield call(addStateDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* stateEditSaga(action) {
  try {
    const response = yield call(editStateDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* stateDeleteSaga(action) {
  try {
    const response = yield call(deleteStateDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}

function* stateExportDataSaga(action) {
  try {
    const response = yield call(exportStateDataAPI, action?.data);
    if (action.callback) {

      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* stateImportDataSaga(action) {
  try {
    const response = yield call(importStateDataAPI, action?.data);
    if (action.callback) {

      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}



















//EMPLOYEE_TYPE 
function* employeeTypeListSaga(action) {
  try {
    const response = yield call(getEmployeeTypeListDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* employeeTypeAddSaga(action) {
  try {
    const response = yield call(addEmployeeTypeDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* employeeTypeEditSaga(action) {
  try {
    const response = yield call(editEmployeeTypeDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* employeeTypeDeleteSaga(action) {
  try {
    const response = yield call(deleteEmployeeTypeDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}

function* employeeTypeExportDataSaga(action) {
  try {
    const response = yield call(exportEmployeeTypeDataAPI, action?.data);
    if (action.callback) {

      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* employeeTypeImportDataSaga(action) {
  try {
    const response = yield call(importEmployeeTypeDataAPI, action?.data);
    if (action.callback) {

      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}








function* masterSaga() {
  yield takeEvery(DEPARTMENT_LIST, departmentListSaga);
  yield takeEvery(ADD_DEPARTMENT, departmentAddSaga);
  yield takeEvery(EDIT_DEPARTMENT, departmentEditSaga);
  yield takeEvery(DELETE_DEPARTMENT, departmentDeleteSaga);
  yield takeEvery(EXPORT_DEPARTMENT, departmentExportDataSaga);
  yield takeEvery(IMPORT_DEPARTMENT, departmentImportDataSaga);

  //Country
  yield takeEvery(COUNTRY_LIST, countryListSaga);
  yield takeEvery(ADD_COUNTRY, countryAddSaga);
  yield takeEvery(EDIT_COUNTRY, countryEditSaga);
  yield takeEvery(DELETE_COUNTRY, countryDeleteSaga);
  yield takeEvery(EXPORT_COUNTRY, countryExportDataSaga);
  yield takeEvery(IMPORT_COUNTRY,countryImportDataSaga);






  //EMPLOYEE_TYPE 
  yield takeEvery(EMPLOYEE_TYPE_LIST, employeeTypeListSaga);
  yield takeEvery(ADD_EMPLOYEE_TYPE, employeeTypeAddSaga);
  yield takeEvery(EDIT_EMPLOYEE_TYPE, employeeTypeEditSaga);
  yield takeEvery(DELETE_EMPLOYEE_TYPE, employeeTypeDeleteSaga);
  yield takeEvery(EXPORT_EMPLOYEE_TYPE, employeeTypeExportDataSaga);
  yield takeEvery(IMPORT_EMPLOYEE_TYPE, employeeTypeImportDataSaga);
}

export default masterSaga;
