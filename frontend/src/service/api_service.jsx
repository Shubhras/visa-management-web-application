import axios from "axios";

//apply base url for axios
const API_URL = "http://103.120.178.54:7001"//import.meta.env.VITE_API_BASE_URL_USERS_MANAGEMENT_SERVICE;

const axiosApi = axios.create({
  baseURL: API_URL,
});


axiosApi.interceptors.request.use(
  (config) => {
    const authUser = localStorage.getItem('authUser');

    if (authUser) {

      const { token } = JSON.parse(authUser);
      config.headers['Authorization'] = `Bearer ${token}`;
    } else {

    }
    // Dynamically set Content-Type based on the data type
    if (config.data instanceof FormData) {
      config.headers["Content-Type"] = "multipart/form-data";
    } else {
      config.headers["Content-Type"] = "application/json";
    }

    return config;
  },
  (error) => Promise.reject(error)
);

axiosApi.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error)
);

export async function get(url, config = {}) {
  return await axiosApi
    .get(url, { ...config })
    .then((response) => response);
}

// export async function getWithData(url, data = {}, config = {}) {
//   console.log("data", data)
//   return axiosApi
//     .get(url, { ...data }, { ...config })
//     .then((response) => response);
// }


// export async function post(url, data, config = {}) {
//   return axiosApi
//     .post(url, { ...data }, { ...config })
//     .then((response) => response);
// }
export async function post(url, data, config = {}) {
  const finalData = data instanceof FormData ? data : { ...data };

  return axiosApi
    .post(url, finalData, config)
    .then((response) => response);
}


export async function put(url, data, config = {}) {
  return axiosApi
    .put(url, { ...data }, { ...config })
    .then((response) => response);
}

export async function del(url, config = {}) {
  return await axiosApi
    .delete(url, { ...config })
    .then((response) => response.data);
}

