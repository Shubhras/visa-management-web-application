import {
  LOGIN_USER,
  // LOGIN_SUCCESS,
  // LOGOUT_USER,
  // LOGOUT_USER_SUCCESS,
  // API_ERROR,
  // TWO_STEP_VERIFICATION,
  // FORGET_PASSWORD,
  // RESET_PASSWORD,
} from "./actionTypes"

const initialState = {
  error: "",
  loading: false,
}

const login = (state = initialState, action) => {
  switch (action.type) {
    case LOGIN_USER:
      state = {
        ...state,
        loading: true,
      }
       break
    // case LOGIN_SUCCESS:
    //   state = {
    //     ...state,
    //     loading: false,
    //   }
    //   break
    // case LOGOUT_USER:
    //   state = { ...state }
    //   break
    // case TWO_STEP_VERIFICATION:
    //   state = { ...state }
    //   break
    // case LOGOUT_USER_SUCCESS:
    //   state = { ...state }
    //   break
    // case API_ERROR:
    //   state = { ...state, error: action.payload, loading: false }
    //   break
    // case FORGET_PASSWORD:
    //   state = { ...state }
    //   break
    // case RESET_PASSWORD:
    //   state = { ...state }
    //   break

    default:
      state = { ...state }
      break
  }
  return state
}

export default login
