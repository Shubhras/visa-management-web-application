import axios from "axios";

import * as url from "./api_url";
import { get, post, put } from "./api_service";

// auth
export const postLogin = data => post(url.POST_LOGIN, data);
export const logoutUserAPI = (data) => post(url.POST_LOGOUT, data)

// export const forgetPasswordAPI = data => put(url.FORGET_PASSWORD_URL, data);
// export const resetPasswordAPI = data => put(url.RESET_PASSWORD_URL, data);
// export const twoStepVerificationAPI = data => post(url.TWO_STEP_VERIFICATION, data);


// //international admin
// export const getUsersDetailsById = (payload) => {
//   const apiUrl = `${url.GET_USERS_DETAILS_BY_ID}`;
//   return post(apiUrl, payload);
// };

// export const getUsersListData = ({ roleId, search }) => {
//   const apiUrl = `${url.GET_ALL_NATIONALADMIN}/?searchkeyword=${search}`;
//   return get(apiUrl);
// };

// export const getCountryListData = ({ continentId, search = '' }) => {
//   if (continentId === null || continentId.length === 0) {
//     return get(url.GET_COUNTRY_LIST);
//   } else {
//     const continentIds = continentId.map(item => item.id).join(',');
//     const apiUrl = `${url.GET_COUNTRY_LIST}?continentIds=${continentIds}${search ? `&search=${search}` : ''}`;
//     return get(apiUrl);
//   }
// };


// export const getLanguageListData = () => get(url.GET_LANGUAGE_LIST);
// export const getCurrenciesListData = () => get(url.GET_CURRENCIES_LIST);
// export const getContinentListData = () => get(url.GET_CONTINENT_LIST);

// export const add_national_api = (data) => post(url.ADD_NATIONAL_ADMIN, data)
// export const get_countryCode = ({ countryIds }) => {
//   console.log("countryIds",countryIds)
//   const findCountryIds = countryIds.map(item => item.id).join(',');
//   const payload = {
//     countryIds: findCountryIds
//   }
//   return post(url.GETCOUNTRYCODE, payload)
// }
// export const get_countryCode = ({ countryIds }) => {
//   console.log("countryIds", countryIds);
//   let findCountryIds;
//   if (Array.isArray(countryIds)) {
//     findCountryIds = countryIds.map(item => item.id).join(',');
//   } else {
//     findCountryIds = countryIds;
//   }
//   const payload = {
//     countryIds: findCountryIds
//   };
//   return post(url.GETCOUNTRYCODE, payload);
// };

// export const check_validate_phone = (data) => post(url.CHECK_VALIDATE_PHONE, data)
// export const check_validate_postalCode = (data) => post(url.CHECK_VALIDATE_POSTAL_CODE, data)

// export const getAdminStaticAPI = (data) => {
//   const apiUrl = `${url.GET_ADMINSTATIC}/${data?.id}`
//   return get(apiUrl)
// }

// export const getAllTableDataSuperAdmin = (data) => {
//   let urls = {};
//   if (data?.data?.authority === "users") {
//     urls = {
//       "1": `${url.SUPER_ADMINS_INTERNATIONAL}/${data?.data?.id}`,
//       "2": `${url.ADMIN_INTERNATIONAL}/${data?.data?.id}`,
//       "3": `${url.CUSTOMERS_INTERNATIONAL}/${data?.data?.id}`
//     };
//   } else {
//     urls = {
//       "1": `${url.MAIN_TABLE_INTERNATIONAL}/${data?.data?.id}`,
//       "2": `${url.SUPER_ADMINS_INTERNATIONAL}/${data?.data?.id}`,
//       "3": `${url.ADMIN_INTERNATIONAL}/${data?.data?.id}`,
//       "4": `${url.CUSTOMERS_INTERNATIONAL}/${data?.data?.id}`
//     };
//   }

//   const apiUrl = urls[data?.activeTab] || urls["4"];
//   return get(apiUrl);
// };


// export const getAllCountryListAPI = (data) => {
//   const apiUrl = `${url.GET_ALL_COUNTRY_LIST_URL}`
//   return get(apiUrl)
// }

// export const getCityListAPI = (data) => {
//   const apiUrl = `${url.GET_ALL_CITY_LIST_URL}?countriesId=${data?.countriesId}`
//   return get(apiUrl)
// }

// export const getCountriesStateWiseAPI = (data) => {
//   const apiUrl = `${url.GET_ALL_COUNTIES_LIST_URL}?countriesId=${data?.countriesId}`
//   return get(apiUrl)
// }

// export const addSuperaAdminAPINationalAdminAPI = (data) => {
//   const apiUrl = `${url.ADD_SUPERADMIN_IN_NATIONAL_ADMIN_URL}`;
//   return post(apiUrl, data);
// };
// export const addAdminAPINationalAdminAPI = (data) => {
//   const apiUrl = `${url.ADD_ADMIN_IN_NATIONAL_ADMIN_URL}`;
//   return post(apiUrl, data);
// };
// export const addCustomerAPINationalAdminAPI = (data) => {
//   const apiUrl = `${url.ADD_CUSTOMER_IN_NATIONAL_ADMIN_URL}`;
//   return post(apiUrl, data);
// };




