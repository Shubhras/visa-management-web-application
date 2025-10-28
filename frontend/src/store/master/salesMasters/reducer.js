import {
  ACTIVITY_TYPE_LIST,
} from "./actionTypes"

const initialState = {
  error: "",
  loading: false,
}

const SalesMastertReducer = (state = initialState, action) => {
  switch (action.type) {
    case ACTIVITY_TYPE_LIST:
      return {
        ...state,
      };
    default:
      return state;
  }
}

export default SalesMastertReducer



