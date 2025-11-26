import axios from "axios";

//apply base url for axios
//const API_URL = "http://192.168.0.156:8000"//import.meta.env.VITE_API_BASE_URL_USERS_MANAGEMENT_SERVICE;
//const API_URL = "https://visaadmin.digiprima.co"//import.meta.env.VITE_API_BASE_URL_USERS_MANAGEMENT_SERVICE;
 const API_URL="http://127.0.0.1:8000"
const axiosApi = axios.create({
  baseURL: API_URL,
});


// axiosApi.interceptors.request.use(
//   (config) => {
//     const authUser = localStorage.getItem('authUser');
//     const aaaaa = JSON.parse(authUser)
//     if (authUser) {
//       //console.log('authUserauthUserauthUserauthUser',authUser)
//       // const { access } = JSON.parse(authUser);
//       config.headers['Authorization'] = `Bearer ${aaaaa?.data.access}`;
//     } else {

//     }
//     // Dynamically set Content-Type based on the data type
//     if (config.data instanceof FormData) {
//       config.headers["Content-Type"] = "multipart/form-data";
//     } else {
//       config.headers["Content-Type"] = "application/json";
//     }

//     return config;
//   },
//   (error) => Promise.reject(error)
// );
axiosApi.interceptors.request.use(
  (config) => {
    const authUser = localStorage.getItem('authUser');

    // Try to parse the authUser and handle cases where the token might not exist
    let token = null;
    if (authUser) {
      try {
        const parsedUser = JSON.parse(authUser);
        token = parsedUser?.access || null;  // Safely extract token if available
      } catch (e) {
        console.error("Error parsing authUser:", e);
      }
    }

    // If token exists, add to Authorization header
    if (token) {
      
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    // Dynamically set Content-Type header based on request data
    if (config.data instanceof FormData) {
      config.headers["Content-Type"] = "multipart/form-data";
    } else {
      config.headers["Content-Type"] = "application/json";
    }

    return config;
  },
  (error) => Promise.reject(error)  // Handle error if request setup fails
);


axiosApi.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error)
);

export async function get(url, config = {}) {
  return await axiosApi
    .get(url, { ...config })
    .then((response) => response?.data);
}

export async function getExportData(url, config = {}) {
  return await axiosApi
    .get(url,{ responseType: 'blob'}, { ...config })
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
    .then((response) => response?.data);
}


export async function put(url, data, config = {}) {
  return axiosApi
    .put(url, { ...data }, { ...config })
    .then((response) => response?.data);
}

export async function del(url, config = {}) {
  return await axiosApi
    .delete(url, { ...config })
    .then((response) => response?.data);
}



export async function delWithPayload(url, data = {}, config = {}) {
  return await axiosApi
    .delete(url, { data: data, ...config })
    .then((response) => response?.data);
}