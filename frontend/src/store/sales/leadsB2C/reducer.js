import {
    LEADS_B2C_LIST,
} from "./actionType";

const initialState = {
    error: "",
    loading: false,
};

const salesReducer = (state = initialState, action) => {
    switch (action.type) {
        case LEADS_B2C_LIST:
            return {
                ...state,
            };
        default:
            return state;
    }
};

export default salesReducer;
