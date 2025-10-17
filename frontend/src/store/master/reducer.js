import {
  DEPARTMENT_LIST,
} from "./actionTypes"

const initialState = {
  error: "",
  loading: false,
}

const MastertReducer = (state = initialState, action) => {
  switch (action.type) {
    case DEPARTMENT_LIST:
      return {
        ...state,
      };
    default:
      return state;
  }
}

export default MastertReducer



