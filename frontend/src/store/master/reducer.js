import {
  DEPARTMENT_LIST,
} from "./actionTypes"

const initialState = {
  error: "",
  loading: false,
}

const departmentListReduser = (state = initialState, action) => {
  switch (action.type) {
    case DEPARTMENT_LIST:
      state = {
        ...state,
        loading: true,
      }
       break
    default:
      state = { ...state }
      break
  }
  return state
}

export default departmentListReduser
