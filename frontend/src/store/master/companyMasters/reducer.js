import {
  BANK_ACCOUNT_TYPE_LIST,
} from "./actionTypes"

const initialState = {
  error: "",
  loading: false,
}

const CompanyMastertReducer = (state = initialState, action) => {
  switch (action.type) {
    case BANK_ACCOUNT_TYPE_LIST:
      return {
        ...state,
      };
    default:
      return state;
  }
}

export default CompanyMastertReducer



