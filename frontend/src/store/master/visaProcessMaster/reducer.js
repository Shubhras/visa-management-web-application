import { DOCUMENT_CATEGORY_LIST } from "./actionType";

const initialState = {
    error: "",
    loading: false,
};
const visaProcessMasterReducer = (state = initialState, action) => {
    switch (action.type) {
        case DOCUMENT_CATEGORY_LIST:
            return {
                ...state,
            };
        default:
            return state;
    }
};

export default visaProcessMasterReducer;
