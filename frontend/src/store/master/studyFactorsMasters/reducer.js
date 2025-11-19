import { FACTOR_FOR_LIST } from "./actionType";

const initialState = {
    error: "",
    loading: false,
};
const studyFactorsMasterReducer = (state = initialState, action) => {
    switch (action.type) {
        case FACTOR_FOR_LIST:
            return {
                ...state,
            };
        default:
            return state;
    }
};

export default studyFactorsMasterReducer;
