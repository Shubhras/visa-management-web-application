import { JOB_TYPE_LIST } from "./actionType";

const initialState = {
    error: "",
    loading: false,
};
const occupationMasterReducer = (state = initialState, action) => {
    switch (action.type) {
        case JOB_TYPE_LIST:
            return {
                ...state,
            };
        default:
            return state;
    }
};

export default occupationMasterReducer;
