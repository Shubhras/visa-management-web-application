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

  STAKEHOLDER_CATEGORY_LIST,
  ADD_STAKEHOLDER_CATEGORY,
  EDIT_STAKEHOLDER_CATEGORY,
  DELETE_STAKEHOLDER_CATEGORY,
  EXPORT_STAKEHOLDER_CATEGORY,
  IMPORT_STAKEHOLDER_CATEGORY,

  PRIORITY_TYPE_LIST,
  ADD_PRIORITY_TYPE,
  EDIT_PRIORITY_TYPE,
  DELETE_PRIORITY_TYPE,
  EXPORT_PRIORITY_TYPE,
  IMPORT_PRIORITY_TYPE,
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
  importCompanyDataAPI,

  getStakeholderCategoryListDataAPI,
  addStakeholderCategoryDataAPI,
  editStakeholderCategoryDataAPI,
  deleteStakeholderCategoryDataAPI,
  exportStakeholderCategoryDataAPI,
  importStakeholderCategoryDataAPI,

  getPriorityTypeListDataAPI,
  addPriorityTypeDataAPI,
  editPriorityTypeDataAPI,
  deletePriorityTypeDataAPI,
  exportPriorityTypeDataAPI,
  importPriorityTypeDataAPI,
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

//stakeholder Category
function* stakeholderCategoryListSaga(action) {
  try {
    const response = yield call(getStakeholderCategoryListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* stakeholderCategoryAddSaga(action) {
  try {
    const response = yield call(addStakeholderCategoryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* stakeholderCategoryEditSaga(action) {
  try {
    const response = yield call(editStakeholderCategoryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* stakeholderCategoryDeleteSaga(action) {
  try {
    const response = yield call(deleteStakeholderCategoryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* stakeholderCategoryExportDataSaga(action) {
  try {
    const response = yield call(exportStakeholderCategoryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* stakeholderCategoryImportDataSaga(action) {
  try {
    const response = yield call(importStakeholderCategoryDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

//Priority type
function* priorityTypeListSaga(action) {
  try {
    const response = yield call(getPriorityTypeListDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* priorityTypeAddSaga(action) {
  try {
    const response = yield call(addPriorityTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* priorityTypeEditSaga(action) {
  try {
    const response = yield call(editPriorityTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* priorityTypeDeleteSaga(action) {
  try {
    const response = yield call(deletePriorityTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* priorityTypeExportDataSaga(action) {
  try {
    const response = yield call(exportPriorityTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
  }
}

function* priorityTypeImportDataSaga(action) {
  try {
    const response = yield call(importPriorityTypeDataAPI, action?.data);
    if (action.callback) action.callback(response);
  } catch (error) {
    if (action.callback) action.callback(null, error);
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

   //stakeholder Category
  yield takeEvery(STAKEHOLDER_CATEGORY_LIST, stakeholderCategoryListSaga);
  yield takeEvery(ADD_STAKEHOLDER_CATEGORY, stakeholderCategoryAddSaga);
  yield takeEvery(EDIT_STAKEHOLDER_CATEGORY, stakeholderCategoryEditSaga);
  yield takeEvery(DELETE_STAKEHOLDER_CATEGORY, stakeholderCategoryDeleteSaga);
  yield takeEvery(EXPORT_STAKEHOLDER_CATEGORY, stakeholderCategoryExportDataSaga);
  yield takeEvery(IMPORT_STAKEHOLDER_CATEGORY, stakeholderCategoryImportDataSaga);

  //Priority type
  yield takeEvery(PRIORITY_TYPE_LIST, priorityTypeListSaga);
  yield takeEvery(ADD_PRIORITY_TYPE, priorityTypeAddSaga);
  yield takeEvery(EDIT_PRIORITY_TYPE, priorityTypeEditSaga);
  yield takeEvery(DELETE_PRIORITY_TYPE, priorityTypeDeleteSaga);
  yield takeEvery(EXPORT_PRIORITY_TYPE, priorityTypeExportDataSaga);
  yield takeEvery(IMPORT_PRIORITY_TYPE, priorityTypeImportDataSaga);

}

export default masterSaga;
