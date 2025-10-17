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

export const loginUser = (user, history, callback) => {
  return {
    type: LOGIN_USER,
    payload: { user, history },
    callback
  }
}

// export const forgotpassword = (user, history, callback) => {
//   return {
//     type: FORGET_PASSWORD,
//     payload: { user, history },
//     callback
//   }
// }

// export const resetpassword = (user, history, callback) => {
//   return {
//     type: RESET_PASSWORD,
//     payload: { user, history },
//     callback
//   }
// }

// export const twoStepVerification = (data, history, callback) => {
//   return {
//     type: TWO_STEP_VERIFICATION,
//     payload: { data, history },
//     callback
//   }
// }

// export const loginSuccess = user => {
//   return {
//     type: LOGIN_SUCCESS,
//     payload: user,
//   }
// }

// export const logoutUser = (data, callback) => {
//   return {
//     type: LOGOUT_USER,
//     data,
//     callback
//   }
// }

// export const logoutUserSuccess = () => {
//   return {
//     type: LOGOUT_USER_SUCCESS,
//     payload: {},
//   }
// }

// export const apiError = error => {
//   return {
//     type: API_ERROR,
//     payload: error,
//   }
// }
