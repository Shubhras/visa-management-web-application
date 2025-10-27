import { call, takeEvery } from "redux-saga/effects";
import {
  DEPARTMENT_LIST,
  ADD_DEPARTMENT,
  EDIT_DEPARTMENT,
  DELETE_DEPARTMENT,
  EXPORT_DEPARTMENT,
  IMPORT_DEPARTMENT,

  EMPLOYEE_TYPE_LIST,
  ADD_EMPLOYEE_TYPE,
  EDIT_EMPLOYEE_TYPE,
  DELETE_EMPLOYEE_TYPE,
  EXPORT_EMPLOYEE_TYPE,
  IMPORT_EMPLOYEE_TYPE,

  COMPANY_LIST,
  ADD_COMPANY,
  EDIT_COMPANY,
  DELETE_COMPANY,
  EXPORT_COMPANY,
  IMPORT_COMPANY,
} from "./actionTypes";

import {
  getDepartmentListDataAPI,
  addDepartmentDataAPI,
  editDepartmentDataAPI,
  deleteDepartmentDataAPI,
  exportDepartmentDataAPI,
  importDepartmentDataAPI,

  getEmployeeTypeListDataAPI,
  addEmployeeTypeDataAPI,
  editEmployeeTypeDataAPI,
  deleteEmployeeTypeDataAPI,
  exportEmployeeTypeDataAPI,
  importEmployeeTypeDataAPI,

  getCompanyListDataAPI,
  addCompanyDataAPI,
  editCompanyDataAPI,
  deleteCompanyDataAPI,
  exportCompanyDataAPI,
  importCompanyDataAPI
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

//Company Type 
function* companyListSaga(action) {
  try {
    const response = yield call(getCompanyListDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* companyAddSaga(action) {
  try {
    const response = yield call(addCompanyDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* companyEditSaga(action) {
  try {
    const response = yield call(editCompanyDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* companyDeleteSaga(action) {
  try {
    const response = yield call(deleteCompanyDataAPI, action?.data);
    if (action.callback) {
      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}

function* companyExportDataSaga(action) {
  try {
    const response = yield call(exportCompanyDataAPI, action?.data);
    if (action.callback) {

      action.callback(response);
    }
  } catch (error) {
    if (action.callback) {
      action.callback(null, error);
    }
  }
}
function* companyImportDataSaga(action) {
  try {
    const response = yield call(importCompanyDataAPI, action?.data);
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


  //EMPLOYEE_TYPE 
  yield takeEvery(EMPLOYEE_TYPE_LIST, employeeTypeListSaga);
  yield takeEvery(ADD_EMPLOYEE_TYPE, employeeTypeAddSaga);
  yield takeEvery(EDIT_EMPLOYEE_TYPE, employeeTypeEditSaga);
  yield takeEvery(DELETE_EMPLOYEE_TYPE, employeeTypeDeleteSaga);
  yield takeEvery(EXPORT_EMPLOYEE_TYPE, employeeTypeExportDataSaga);
  yield takeEvery(IMPORT_EMPLOYEE_TYPE, employeeTypeImportDataSaga);

  //Company Type
  yield takeEvery(COMPANY_LIST, companyListSaga);
  yield takeEvery(ADD_COMPANY, companyAddSaga);
  yield takeEvery(EDIT_COMPANY, companyEditSaga);
  yield takeEvery(DELETE_COMPANY, companyDeleteSaga);
  yield takeEvery(EXPORT_COMPANY, companyExportDataSaga);
  yield takeEvery(IMPORT_COMPANY, companyImportDataSaga);

}

export default masterSaga;
