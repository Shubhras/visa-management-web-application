import { REPRESENTING_COUNTRY_LIST } from "./actionType";

const initialState = {
    error: "",
    loading: false,
};
const visaMasterReducer = (state = initialState, action) => {
    switch (action.type) {
        case REPRESENTING_COUNTRY_LIST:
            return {
                ...state,
            };
        default:
            return state;
    }
};

export default visaMasterReducer;
