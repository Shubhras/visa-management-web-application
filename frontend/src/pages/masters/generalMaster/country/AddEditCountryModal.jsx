// import React, { useState, useEffect } from "react";
// import { useDispatch } from "react-redux";
// import { toast } from "react-toastify";
// import {
//   countryEdit,
//   continentList,
//   countryAdd,
//   countryList,
// } from "../../../../store/master/generalMasters/actions";

// const AddEditCountryModal = ({
//   show,
//   handleClose,
//   mode = "add",
//   rowData = null,
// }) => {
//   const dispatch = useDispatch();
//   const [loading, setLoading] = useState(false);
//   const [continentListData, setContinentListData] = useState([]);
//   const [countryListData, setCountryListData] = useState([]);
 
//   const initialForm = {
//     uuid: "",
//     countryName: "",
//     continent_id: "",
//     description: "",
//     currencyFullName: "",
//     currencyShortName: "",
//     shortName: "",
//     fullName: "",
//     officialName: "",
//     capitalCity: "",
//     dialCodes: "",
//     currencyCode: "",
//   };

//   const [formData, setFormData] = useState(initialForm);
//   const [errors, setErrors] = useState({});

//   useEffect(() => {
//     fetchContinentList();
//     fetchCountryShortName();

//     if (mode === "edit" && rowData) {
//       setFormData({
//         uuid: rowData.uuid || "",
//         countryName: rowData.name || "",
//         continent_id: rowData.continent?.uuid || "",
//         description: rowData.description || "",
//         currencyFullName: rowData.currencyfullname || "",
//         currencyShortName: rowData.currencyshortname || "",
//         shortName: rowData.shortName || "",
//         fullName: rowData.fullName || "",
//         officialName: rowData.officialName || "",
//         capitalCity: rowData.capitalCity || "",
//         dialCodes: rowData.dialCodes || "",
//         currencyCode: rowData.currencyCode || "",
//       });
//     } else {
//       setFormData(initialForm);
//     }
//   }, [mode, rowData, show]);

//   const fetchContinentList = () => {
//     const params = {
//       page: 1,
//       limit: 2000,
//       search: "",
//       status: "",
//       sortBy: "updated_at",
//       sortOrder: "desc",
//     };

//     setLoading(true);
//     dispatch(
//       continentList(params, (response, error) => {
//         setLoading(false);
//         if (response?.statusCode === 200 && response?.status === true) {
//           setContinentListData(response?.data || []);
//         } else {
//           toast.error("Failed to load continent list");
//         }
//       })
//     );
//   };
//   const fetchCountryShortName = () => {
//     const params = {
//       page: 1,
//       limit: 2000,
//       search: "",
//       status: "",
//       sortBy: "updated_at",
//       sortOrder: "desc",
//     };

//     setLoading(true);
//     dispatch(
//       countryList(params, (response, error) => {
//         setLoading(false);
//         if (response?.statusCode === 200 && response?.status === true) {
//           setCountryListData(response?.data || []);
//         } else {
//           toast.error("Failed to load continent list");
//         }
//       })
//     );
//   };

//   const handleChange = (e) => {
//     const { name, value } = e.target;
//     setFormData((prev) => ({ ...prev, [name]: value }));
//     if (errors[name]) {
//       setErrors((prev) => ({ ...prev, [name]: "" }));
//     }
//   };

//   const validateForm = () => {
//     const newErrors = {};
//     if (!String(formData.countryName || "").trim()) {
//       newErrors.countryName = "Country Name is required";
//     }
//     if (!formData.continent_id) {
//       newErrors.continent_id = "Continent is required";
//     }
//     setErrors(newErrors);
//     return Object.keys(newErrors).length === 0;
//   };

//   const handleSubmit = (e) => {
//     e.preventDefault();
//     if (!validateForm()) return;

//     const payload = {
//       name: formData.countryName,
//       continent_id: formData.continent_id,
//       officialName: formData.officialName,
//       capitalCity: formData.capitalCity,
//       currencyshortname: formData.currencyShortName,
//       shortName: formData.shortName,
//       currencyfullname: formData.currencyFullName,
//       //   fullName: formData.fullName,
//       dialCodes: formData.dialCodes,
//       currencyCode: formData.currencyCode,
//       description: formData.description,
//     };

//     if (mode === "edit") payload.uuid = formData.uuid;

//     const action = mode === "edit" ? countryEdit : countryAdd;

//     setLoading(true);
//     dispatch(
//       action(payload, (response, error) => {
//         setLoading(false);
//         if (error) {
//           toast.error(error?.response?.data?.message || "Server error");
//         } else if (response?.statusCode === 200 && response?.status === true) {
//           toast.success(response?.message || "Country saved successfully");
//           resetForm();
//           handleClose();
//         } else {
//           toast.error("Something went wrong while saving.");
//         }
//       })
//     );
//   };

//   const resetForm = () => {
//     setFormData(initialForm);
//     setErrors({});
//   };

//   const onClose = () => {
//     resetForm();
//     setLoading(false);
//     handleClose();
//   };

//   if (!show) return null;

//   return (
//     <div
//       className="modal fade show common-ctl-popup"
//       tabIndex={-1}
//       role="dialog"
//       aria-labelledby="countryModalLabel"
//       aria-hidden={!show}
//       style={{ display: show ? "block" : "none" }}
//     >
//       <div
//         className="modal-dialog modal-lg modal-dialog-centered"
//         role="document"
//       >
//         <div className="modal-content radius-16 bg-base">
//           <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
//             <h1 className="modal-title fs-5" id="countryModalLabel">
//               {mode === "edit" ? "Edit Country" : "Add Country"}
//             </h1>
//             <button
//               type="button"
//               className="btn-close"
//               onClick={onClose}
//               aria-label="Close"
//             />
//           </div>

//           <div className="modal-body p-24">
//             <form onSubmit={handleSubmit}>
//               {/* Row 1 */}
//               <div className="row">
//                 <div className="col-md-6 mb-20">
//                   <label className="form-label fw-semibold text-primary-light text-sm mb-8">
//                     Country Name <span className="text-danger">*</span>
//                   </label>
//                   <input
//                     type="text"
//                     name="countryName"
//                     value={formData.countryName}
//                     onChange={handleChange}
//                     className={`form-control radius-8 ${
//                       errors.countryName ? "is-invalid" : ""
//                     }`}
//                     placeholder="Enter country name"
//                   />
//                   {errors.countryName && (
//                     <div className="text-danger text-sm mt-1">
//                       {errors.countryName}
//                     </div>
//                   )}
//                 </div>

//                 <div className="col-md-6 mb-20">
//                   <label className="form-label fw-semibold text-primary-light text-sm mb-8">
//                     Continent <span className="text-danger">*</span>
//                   </label>
//                   <select
//                     name="continent_id"
//                     value={formData.continent_id}
//                     onChange={handleChange}
//                     className={`form-control form-select radius-8 ${
//                       errors.continent_id ? "is-invalid" : ""
//                     }`}
//                   >
//                     <option value="">Select Continent</option>
//                     {continentListData.map((option) => (
//                       <option key={option.uuid} value={option.uuid}>
//                         {option.name}
//                       </option>
//                     ))}
//                   </select>
//                   {errors.continent_id && (
//                     <div className="text-danger text-sm mt-1">
//                       {errors.continent_id}
//                     </div>
//                   )}
//                 </div>
//               </div>

//               {/* Row 2 */}
//               <div className="row">
//                 <div className="col-md-6 mb-20">
//                   <label className="form-label fw-semibold text-primary-light text-sm mb-8">
//                     Country Official Name
//                   </label>
//                   <input
//                     type="text"
//                     name="officialName"
//                     value={formData.officialName}
//                     onChange={handleChange}
//                     className="form-control radius-8"
//                     placeholder="Enter official name"
//                   />
//                 </div>

//                 <div className="col-md-6 mb-20">
//                   <label className="form-label fw-semibold text-primary-light text-sm mb-8">
//                     Country Short Name
//                   </label>
//                   <input
//                     type="text"
//                     name="shortName"
//                     value={formData.shortName}
//                     onChange={handleChange}
//                     className="form-control radius-8"
//                     placeholder="Enter Short name"
//                   />
//                 </div>
//               </div>

//               {/* Row 3 */}
//               <div className="row">
//                 <div className="col-md-6 mb-20">
//                   <label className="form-label fw-semibold text-primary-light text-sm mb-8">
//                     Capital City
//                   </label>
//                   <input
//                     type="text"
//                     name="capitalCity"
//                     value={formData.capitalCity}
//                     onChange={handleChange}
//                     className="form-control radius-8"
//                     placeholder="Enter capital city"
//                   />
//                 </div>

//                 <div className="col-md-6 mb-20">
//                   <label className="form-label fw-semibold text-primary-light text-sm mb-8">
//                     Currency Full Name
//                   </label>
//                   <input
//                     type="text"
//                     name="currencyFullName"
//                     value={formData.currencyFullName}
//                     onChange={handleChange}
//                     className="form-control radius-8"
//                     placeholder="Enter currency full name"
//                   />
//                 </div>
//               </div>

//               {/* Row 4 */}
//               <div className="row">
//                 <div className="col-md-6 mb-20">
//                   <label className="form-label fw-semibold text-primary-light text-sm mb-8">
//                     Currency Short Name
//                   </label>
//                   <input
//                     type="text"
//                     name="currencyShortName"
//                     value={formData.currencyShortName}
//                     onChange={handleChange}
//                     className="form-control radius-8"
//                     placeholder="Enter currency short name"
//                   />
//                 </div>

//                 <div className="col-md-6 mb-20">
//                   <label className="form-label fw-semibold text-primary-light text-sm mb-8">
//                     Currency Code
//                   </label>
//                   <input
//                     type="text"
//                     name="currencyCode"
//                     value={formData.currencyCode}
//                     onChange={handleChange}
//                     className="form-control radius-8"
//                     placeholder="Enter currency code"
//                   />
//                 </div>
//               </div>

//               {/* Row 5 */}
//               <div className="row">
//                 <div className="col-md-6 mb-20">
//                   <label className="form-label fw-semibold text-primary-light text-sm mb-8">
//                     Country Calling Code
//                   </label>
//                   <input
//                     type="text"
//                     name="dialCodes"
//                     value={formData.dialCodes}
//                     onChange={handleChange}
//                     className="form-control radius-8"
//                     placeholder="Enter calling code"
//                   />
//                 </div>

//                 <div className="col-md-6 mb-20">
//                   <label className="form-label fw-semibold text-primary-light text-sm mb-8">
//                     Description
//                   </label>
//                   <textarea
//                     className="form-control radius-8"
//                     name="description"
//                     value={formData.description}
//                     onChange={handleChange}
//                     rows={1}
//                     placeholder="Enter description"
//                   />
//                 </div>
//               </div>

//               {/* Buttons */}
//               <div className="d-flex align-items-center justify-content-center gap-3 mt-24">
//                 <button
//                   type="button"
//                   onClick={onClose}
//                   className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-16 py-4 radius-6"
//                 >
//                   Cancel
//                 </button>
//                 <button
//                   type="submit"
//                   className="btn comman-btn-color border border-primary-600 text-md px-16 py-4 radius-6"
//                   disabled={loading}
//                 >
//                   {loading ? "Saving..." : "Save"}
//                 </button>
//               </div>
//             </form>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default AddEditCountryModal;
import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import Select from "react-select";
import {
  countryEdit,
  continentList,
  countryAdd,
  countryList,
} from "../../../../store/master/generalMasters/actions";

const AddEditCountryModal = ({
  show,
  handleClose,
  mode = "add",
  rowData = null,
}) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [continentListData, setContinentListData] = useState([]);
  const [countryListData, setCountryListData] = useState([]);
 
  const initialForm = {
    uuid: "",
    countryName: "",
    continent_id: "",
    description: "",
    currencyFullName: "",
    currencyShortName: "",
    shortName: "",
    fullName: "",
    officialName: "",
    capitalCity: "",
    dialCodes: "",
    currencyCode: "",
  };

  const [formData, setFormData] = useState(initialForm);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    fetchContinentList();
    fetchCountryShortName();

    if (mode === "edit" && rowData) {
      setFormData({
        uuid: rowData.uuid || "",
        countryName: rowData.name || "",
        continent_id: rowData.continent?.uuid || "",
        description: rowData.description || "",
        currencyFullName: rowData.currencyfullname || "",
        currencyShortName: rowData.currencyshortname || "",
        shortName: rowData.shortName || "",
        fullName: rowData.fullName || "",
        officialName: rowData.officialName || "",
        capitalCity: rowData.capitalCity || "",
        dialCodes: rowData.dialCodes || "",
        currencyCode: rowData.currencyCode || "",
      });
    } else {
      setFormData(initialForm);
    }
  }, [mode, rowData, show]);

  const fetchContinentList = () => {
    const params = {
      page: 1,
      limit: 2000,
      search: "",
      status: "",
      sortBy: "updated_at",
      sortOrder: "desc",
    };

    setLoading(true);
    dispatch(
      continentList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setContinentListData(response?.data || []);
        } else {
          toast.error("Failed to load continent list");
        }
      })
    );
  };
  const fetchCountryShortName = () => {
    const params = {
      page: 1,
      limit: 2000,
      search: "",
      status: "",
      sortBy: "updated_at",
      sortOrder: "desc",
    };

    setLoading(true);
    dispatch(
      countryList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setCountryListData(response?.data || []);
        } else {
          toast.error("Failed to load continent list");
        }
      })
    );
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const handleSelectChange = (selectedOption) => {
    setFormData((prev) => ({ 
      ...prev, 
      continent_id: selectedOption ? selectedOption.value : "" 
    }));
    if (errors.continent_id) {
      setErrors((prev) => ({ ...prev, continent_id: "" }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!String(formData.countryName || "").trim()) {
      newErrors.countryName = "Country Name is required";
    }
    if (!formData.continent_id) {
      newErrors.continent_id = "Continent is required";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    const payload = {
      name: formData.countryName,
      continent_id: formData.continent_id,
      officialName: formData.officialName,
      capitalCity: formData.capitalCity,
      currencyshortname: formData.currencyShortName,
      shortName: formData.shortName,
      currencyfullname: formData.currencyFullName,
      //   fullName: formData.fullName,
      dialCodes: formData.dialCodes,
      currencyCode: formData.currencyCode,
      description: formData.description,
    };

    if (mode === "edit") payload.uuid = formData.uuid;

    const action = mode === "edit" ? countryEdit : countryAdd;

    setLoading(true);
    dispatch(
      action(payload, (response, error) => {
        setLoading(false);
        if (error) {
          toast.error(error?.response?.data?.message || "Server error");
        } else if (response?.statusCode === 200 && response?.status === true) {
          toast.success(response?.message || "Country saved successfully");
          resetForm();
          handleClose();
        } else {
          toast.error("Something went wrong while saving.");
        }
      })
    );
  };

  const resetForm = () => {
    setFormData(initialForm);
    setErrors({});
  };

  const onClose = () => {
    resetForm();
    setLoading(false);
    handleClose();
  };

  if (!show) return null;

  return (
    <div
      className="modal fade show common-ctl-popup"
      tabIndex={-1}
      role="dialog"
      aria-labelledby="countryModalLabel"
      aria-hidden={!show}
      style={{ display: show ? "block" : "none" }}
    >
      <div
        className="modal-dialog modal-lg modal-dialog-centered"
        role="document"
      >
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="countryModalLabel">
              {mode === "edit" ? "Edit Country" : "Add Country"}
            </h1>
            <button
              type="button"
              className="btn-close"
              onClick={onClose}
              aria-label="Close"
            />
          </div>

          <div className="modal-body p-24">
            <form onSubmit={handleSubmit}>
              {/* Row 1 */}
              <div className="row">
                <div className="col-md-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Country Name <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="countryName"
                    value={formData.countryName}
                    onChange={handleChange}
                    className={`form-control radius-8 ${
                      errors.countryName ? "is-invalid" : ""
                    }`}
                    placeholder="Enter country name"
                  />
                  {errors.countryName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.countryName}
                    </div>
                  )}
                </div>

                <div className="col-md-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Continent <span className="text-danger">*</span>
                  </label>

                   <Select
                    options={continentListData.map((option) => ({
                      value: option.uuid,
                      label: option.name,
                    }))}
                    value={
                      formData.continent_id
                        ? continentListData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.name,
                            }))
                            .find((opt) => opt.value === formData.continent_id)
                        : null
                    }
                    onChange={handleSelectChange}
                    placeholder="Select Continent"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.continent_id ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.continent_id && (
                    <div className="text-danger text-sm mt-1">
                      {errors.continent_id}
                    </div>
                  )}
                </div>
              </div>

              {/* Row 2 */}
              <div className="row">
                <div className="col-md-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Country Official Name
                  </label>
                  <input
                    type="text"
                    name="officialName"
                    value={formData.officialName}
                    onChange={handleChange}
                    className="form-control radius-8"
                    placeholder="Enter official name"
                  />
                </div>

                <div className="col-md-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Country Short Name
                  </label>
                  <input
                    type="text"
                    name="shortName"
                    value={formData.shortName}
                    onChange={handleChange}
                    className="form-control radius-8"
                    placeholder="Enter Short name"
                  />
                </div>
              </div>

              {/* Row 3 */}
              <div className="row">
                <div className="col-md-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Capital City
                  </label>
                  <input
                    type="text"
                    name="capitalCity"
                    value={formData.capitalCity}
                    onChange={handleChange}
                    className="form-control radius-8"
                    placeholder="Enter capital city"
                  />
                </div>

                <div className="col-md-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Currency Full Name
                  </label>
                  <input
                    type="text"
                    name="currencyFullName"
                    value={formData.currencyFullName}
                    onChange={handleChange}
                    className="form-control radius-8"
                    placeholder="Enter currency full name"
                  />
                </div>
              </div>

              {/* Row 4 */}
              <div className="row">
                <div className="col-md-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Currency Short Name
                  </label>
                  <input
                    type="text"
                    name="currencyShortName"
                    value={formData.currencyShortName}
                    onChange={handleChange}
                    className="form-control radius-8"
                    placeholder="Enter currency short name"
                  />
                </div>

                <div className="col-md-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Currency Code
                  </label>
                  <input
                    type="text"
                    name="currencyCode"
                    value={formData.currencyCode}
                    onChange={handleChange}
                    className="form-control radius-8"
                    placeholder="Enter currency code"
                  />
                </div>
              </div>

              {/* Row 5 */}
              <div className="row">
                <div className="col-md-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Country Calling Code
                  </label>
                  <input
                    type="text"
                    name="dialCodes"
                    value={formData.dialCodes}
                    onChange={handleChange}
                    className="form-control radius-8"
                    placeholder="Enter calling code"
                  />
                </div>

                <div className="col-md-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Description
                  </label>
                  <textarea
                    className="form-control radius-8"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    rows={1}
                    placeholder="Enter description"
                  />
                </div>
              </div>

              {/* Buttons */}
              <div className="d-flex align-items-center justify-content-center gap-3 mt-24">
                <button
                  type="button"
                  onClick={onClose}
                  className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-16 py-4 radius-6"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn comman-btn-color border border-primary-600 text-md px-16 py-4 radius-6"
                  disabled={loading}
                >
                  {loading ? "Saving..." : "Save"}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddEditCountryModal;