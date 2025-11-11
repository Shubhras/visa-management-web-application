import {
    LANGUAGE_NAME_TEST_LIST,
} from "./actionType";

const initialState = {
    error: "",
    loading: false,
};

const TestMasterReducer = (state = initialState, action) => {
    switch (action.type) {
        case LANGUAGE_NAME_TEST_LIST:
            return {
                ...state,
            };
        default:
            return state;
    }
};

export default TestMasterReducer;
