import {
  DEPARTMENT_LIST,
} from "./actionTypes"

export const departmentList = (user, history, callback) => {
  return {
    type: DEPARTMENT_LIST,
    payload: { user, history },
    callback
  }
}

