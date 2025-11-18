import { WORK_RIGHTS_LIST } from "./actionType";

const initialState = {
    error: "",
    loading: false,
};
const visaConditionsMasterReducer = (state = initialState, action) => {
    switch (action.type) {
        case WORK_RIGHTS_LIST:
            return {
                ...state,
            };
        default:
            return state;
    }
};

export default visaConditionsMasterReducer;
