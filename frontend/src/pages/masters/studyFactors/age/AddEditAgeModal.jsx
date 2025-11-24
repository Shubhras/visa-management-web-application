import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import Select from "react-select";
import { countryDemoList } from '../../../../store/master/companyMasters/actions';
import { ageAdd, ageEdit, ageGroupList, factorForList } from '../../../../store/actions';

const AddEditAgeModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [countryListData, setCountryListData] = useState([]);
  const [factorForData, setFactorForData] = useState([]);
  const [ageGroupData, setAgeGroupData] = useState([]);

  // Form state
  const [formData, setFormData] = useState({
    uuid: '',
    factorForName: '',
    studyAgeGroup:"",
    minimumAge: '',
    maximumAge: '',
    countryName: '',
    courseLevel:"",
    description: '',
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    factorForName: '',
    studyAgeGroup:"",
    minimumAge: '',
    maximumAge: '',
    countryName: '',
    courseLevel:"",
  });

  // Populate form data when in edit mode
  useEffect(() => {
    if (mode === 'edit' && rowData) {
      setFormData({
        uuid: rowData.uuid || '',
        factorForName: rowData.factorForName || '',
        studyAgeGroup: rowData.studyAgeGroup || '',
        minimumAge: rowData.minimumAge || '',
        maximumAge: rowData.maximumAge || '',//formData.state === "STATE" ? "State" : "Territory" || '',
        countryName: rowData.countryName || '',
        courseLevel: rowData.courseLevel || '',
        description: rowData.description || '',
      });
    } else {
      resetForm();
    }
    fetchCountryList();
  }, [mode, rowData, show]);

  // Fetch country list
  const fetchCountryList = () => {
    // setLoading(true);
    const params = {
      page: 1,
      limit: 2000,
      search: '',
      status: '',
      sortBy: 'name',
      sortOrder: 'asc',
    };

    dispatch(countryDemoList(params, (response, error) => {
      setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {
        setCountryListData(response?.data || []);
      }
    }));dispatch(factorForList(params, (response, error) => {
      setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {
        setFactorForData(response?.data || []);
      }
    }));dispatch(ageGroupList(params, (response, error) => {
      setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {
        setAgeGroupData(response?.data || []);
      }
    }));
  };

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  // Handle Select changes for Country
//   const handleSelectChange = (selectedOption) => {
//     setFormData((prev) => ({
//       ...prev,
//       country: selectedOption ? selectedOption.value : ""
//     }));
//     if (errors.country) {
//       setErrors((prev) => ({ ...prev, country: "" }));
//     }
//   };
  // Custom filter function for search from start
  
  const customFilterOption = (option, inputValue) => {
    if (!inputValue) return true;
    return option.label.toLowerCase().startsWith(inputValue.toLowerCase());
  };
  // Validate form
  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    // Country validation
    if (!formData.countryName.trim()) {
      newErrors.countryName = 'Country is required';
      isValid = false;
    }

    // State name validation
    if (!formData.factorForName.trim()) {
      newErrors.factorForName = 'Factor For name is required';
      isValid = false;
    }


    if (!formData.studyAgeGroup.trim()) {
      newErrors.studyAgeGroup = 'Study Age Group is required';
      isValid = false;
    }
    
    if (!formData.minimumAge.trim()) {
      newErrors.minimumAge = 'Minimum Age is required';
      isValid = false;
    }

    // State name validation
    if (!formData.maximumAge.trim()) {
      newErrors.maximumAge = 'Maximum Age is required';
      isValid = false;
    }

    if (!formData.courseLevel.trim()) {
      newErrors.courseLevel = 'Course Level is required';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();

    if (validateForm()) {
      const sendPayload = mode === 'edit'
        ? {
          uuid: formData.uuid,
          factorForName: formData.factorForName,
          studyAgeGroup: formData.studyAgeGroup,
          minimumAge: formData.minimumAge,
          maximumAge: formData.maximumAge,
          countryName: formData.countryName,
          courseLevel: formData.courseLevel,
          description: formData.description.trim(),
        }
        : {
         factor_for: formData.factorForName,
          study_age_group: formData.studyAgeGroup,
          minimum_age_months: formData.minimumAge,
          maximum_age_months: formData.maximumAge,
          countryName: formData.countryName,
          courseLevel: formData.courseLevel,
          description: formData.description.trim(),
        };

      setLoading(true);
      const action = mode === 'edit' ? ageEdit : ageAdd;

      dispatch(action(sendPayload, (response, error) => {
        setLoading(false);
        if (error) {
          toast.error(error?.response?.data?.message || "Server error");
        } else if (response?.statusCode === 200 && response?.status === true) {
          toast.success(response?.message);
          resetForm();
          handleClose(true);
        } else {
          toast.error("Something went wrong.");
        }
      }));
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
       uuid: '',
    factorForName: '',
    studyAgeGroup:"",
    minimumAge: '',
    maximumAge: '',
    countryName: '',
    courseLevel:"",
    description: '',
    });
    setErrors({});
  };

  // Handle modal close
  const onClose = () => {
    resetForm();
    setLoading(false);
    handleClose(false);
  };

  // Conditional render
  if (!show) return null;

  return (
    <div
      className="modal fade show common-ctl-popup"
      tabIndex={-1}
      role="dialog"
      aria-labelledby="AddEditStateModalLabel"
      aria-hidden={!show}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="AddEditStateModalLabel">
              {mode === 'edit' ? 'Edit Age' : 'Add Age'}
            </h1>
            <button type="button" className="btn-close" onClick={onClose} aria-label="Close" />
          </div>

          <div className="modal-body p-24">
            <form onSubmit={handleSubmit}>
              <div className="row">
                {/* Country Dropdown */}
                {/* <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Country Name <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={countryListData.map((option) => ({
                      value: option.uuid,
                      label: option.name + " (" + option?.continent?.name + ")",
                    }))}
                    value={
                      formData.country
                        ? countryListData
                          .map((option) => ({
                            value: option.uuid,
                            label: option.name + " (" + option?.continent?.name + ")",
                          }))
                          .find((opt) => opt.value === formData.country)
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "occupationVersion",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Country"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${errors.country ? "is-invalid" : ""
                      }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.country && (
                    <div className="text-danger text-sm mt-1">
                      {errors.country}
                    </div>
                  )}
                </div> */}

                 <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Factor For <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={factorForData.map((option) => ({
                      value: option.uuid,
                      label: option.name ,
                    }))}
                    value={
                      formData.factorForName
                        ? factorForData
                          .map((option) => ({
                            value: option.uuid,
                            label: option.name ,
                          }))
                          .find((opt) => opt.value === formData.factorForName)
                        : null
                    }
                   onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "factorForName",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Factor For"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${errors.factorForName ? "is-invalid" : ""
                      }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.factorForName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.factorForName}
                    </div>
                  )}
                </div>

               <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Study Age Group <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={ageGroupData.map((option) => ({
                      value: option.uuid,
                      label: option.name ,
                    }))}
                    value={
                      formData.studyAgeGroup
                        ? ageGroupData
                          .map((option) => ({
                            value: option.uuid,
                            label: option.name ,
                          }))
                          .find((opt) => opt.value === formData.studyAgeGroup)
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "studyAgeGroup",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Study Age Group"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${errors.studyAgeGroup ? "is-invalid" : ""
                      }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.studyAgeGroup && (
                    <div className="text-danger text-sm mt-1">
                      {errors.studyAgeGroup}
                    </div>
                  )}
                </div>

                {/* State Name */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Minimum Age (Months)<span className="text-danger">*</span>
                  </label>
                  <input
                    type="number"
                    name="minimumAge"
                    value={formData.minimumAge}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.minimumAge ? 'is-invalid' : ''}`}
                    placeholder="Enter Minimum Age"
                  />
                  {errors.minimumAge && (
                    <div className="text-danger text-sm mt-1">{errors.minimumAge}</div>
                  )}
                </div>
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Maximum Age (Months) <span className="text-danger">*</span>
                  </label>
                  <input
                    type="number"
                    name="maximumAge"
                    value={formData.maximumAge}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.maximumAge ? 'is-invalid' : ''}`}
                    placeholder="Enter Maximum Age"
                  />
                  {errors.maximumAge && (
                    <div className="text-danger text-sm mt-1">{errors.maximumAge}</div>
                  )}
                </div>

                {/* State Short Name */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Country Name <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="countryName"
                    value={formData.countryName}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.countryName ? 'is-invalid' : ''}`}
                    placeholder="Enter short name"
                  />
                  {errors.countryName && (
                    <div className="text-danger text-sm mt-1">{errors.countryName}</div>
                  )}
                </div>
                
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Course Level <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="courseLevel"
                    value={formData.courseLevel}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.courseLevel ? 'is-invalid' : ''}`}
                    placeholder="Enter short name"
                  />
                  {errors.courseLevel && (
                    <div className="text-danger text-sm mt-1">{errors.courseLevel}</div>
                  )}
                </div>

                {/* Description */}
                <div className="col-12 mb-20">
                  <label htmlFor="desc" className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Description
                  </label>
                  <textarea
                    className="form-control"
                    id="desc"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    rows={4}
                    placeholder="Description"
                  />
                </div>

                {/* Buttons */}
                <div className="d-flex align-items-center justify-content-center gap-3 mt-24">
                  <button
                    type="button"
                    onClick={onClose}
                    className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-16 py-4 radius-6"
                    disabled={loading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn comman-btn-color border border-primary-600 text-md px-16 py-4 radius-6"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Saving...
                      </>
                    ) : (
                      "Save"
                    )}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddEditAgeModal;