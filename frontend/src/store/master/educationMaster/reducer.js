import {
    EDUCATION_LEVEL_CODE_LIST,
} from "./actionType";

const initialState = {
    error: "",
    loading: false,
};

const EducationMasterReducer = (state = initialState, action) => {
    switch (action.type) {
        case EDUCATION_LEVEL_CODE_LIST:
            return {
                ...state,
            };
        default:
            return state;
    }
};

export default EducationMasterReducer;
