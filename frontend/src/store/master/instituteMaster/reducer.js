import { INSTITUTE_TYPE_LIST } from "./actionType";

const initialState = {
    error: "",
    loading: false,
};
const instituteMasterReducer = (state = initialState, action) => {
    switch (action.type) {
        case INSTITUTE_TYPE_LIST:
            return {
                ...state,
            };
        default:
            return state;
    }
};

export default instituteMasterReducer;
