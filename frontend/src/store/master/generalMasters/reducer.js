import {
  GENDER_LIST,
} from "./actionTypes"

const initialState = {
  error: "",
  loading: false,
}

const GeneralMastertReducer = (state = initialState, action) => {
  switch (action.type) {
    case GENDER_LIST:
      return {
        ...state,
      };
    default:
      return state;
  }
}

export default GeneralMastertReducer



