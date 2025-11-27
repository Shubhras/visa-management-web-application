import * as url from "./api_all_pages_url";
import {
  get,
  post,
  put,
  del,
  delWithPayload,
  getExportData,
} from "./api_service";

export const postDemo = (data) => post(url.POST_DEMO, data);

// ---------------- LEADS B2C ----------------

export const getLeadsB2CListAPI = (data) => {
    let customSort = "";
    if (Array.isArray(data?.sort)) {
        // Case 1: Only created_at is present → keep it
        const isOnlyCreatedAt =
            data.sort.length === 1 && data.sort[0].field === "created_at";

        // Case 2: More fields exist → remove created_at
        const finalSortArray = isOnlyCreatedAt
            ? data.sort
            : data.sort.filter(item => item.field !== "created_at");

        // Convert sorting array into a CSV string
        customSort = finalSortArray
            .map(item => `${item.field}:${item.order}`)
            .join(",");
    }

    const apiUrl = `${url.GET_LEADS_B2C_LIST}?search=${data?.search}&page=${data?.page}&limit=${data?.limit}&sortBy=${data?.sortBy}&sortOrder=${data?.sortOrder}&customSort=${customSort}`;
    return get(apiUrl);
};

export const addLeadsB2CDataAPI = (payload) => {
    const apiUrl = `${url.ADD_LEADS_B2C_API}`;
    return post(apiUrl, payload);
};

export const editLeadsB2CDataAPI = (payload) => {
    const apiUrl = `${url.EDIT_LEADS_B2C_API}${payload?.uuid}/update/`;
    return put(apiUrl, payload);
};

export const deleteLeadsB2CDataAPI = (payload) => {
    const prepareDATA = {
        id: payload,
    };
    const apiUrl = `${url.DELETE_LEADS_B2C_API}delete/`;
    return delWithPayload(apiUrl, prepareDATA);
};

export const exportLeadsB2CDataAPI = (payload) => {
    let customSort = "";
    if (Array.isArray(payload?.sort)) {
        const isOnlyCreatedAt =
            payload.sort.length === 1 && payload.sort[0].field === "created_at";

        const finalSortArray = isOnlyCreatedAt
            ? payload.sort
            : payload.sort.filter(item => item.field !== "created_at");

        customSort = finalSortArray
            .map(item => `${item.field}:${item.order}`)
            .join(",");
    }

    const apiUrl = `${url.EXPORT_LEADS_B2C_API}?search=${payload?.search}&fields=${payload?.fields}&uuids=${payload?.uuids}&customSort=${customSort}`;

    return getExportData(apiUrl, payload);
};

export const importLeadsB2CDataAPI = (payload) => {
    const apiUrl = `${url.IMPORT_LEADS_B2C_API}`;
    return post(apiUrl, payload);
};

