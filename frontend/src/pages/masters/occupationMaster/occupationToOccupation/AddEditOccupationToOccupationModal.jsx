import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import Select from "react-select";
import {
  occupationCodeList,
  occupationNameList,
  occupationToOccupationAdd,
  occupationToOccupationEdit,
  occupationVersionList,
  representingCountryList,
} from "../../../../store/actions";

const AddEditOccupationToOccupationModal = ({
  show,
  handleClose,
  mode = "add",
  rowData = null,
}) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);

  const [countryListData, setCountryListData] = useState([]);
  const [occupationVersionListData, setOccupationVersionListData] = useState(
    []
  );
  const [occupationNameListData, setOccupationNameListData] = useState([]);
  const [occupationCodeListData, setOccupationCodeListData] = useState([]);
  const [compareCountryListData, setCompareCountryListData] = useState([]);
  const [
    compareOccupationVersionListData,
    setCompareOccupationVersionListData,
  ] = useState([]);
  const [compareOccupationNameListData, setCompareOccupationNameListData] =
    useState([]);
  const [compareOccupationCodeListData, setCompareOccupationCodeListData] =
    useState([]);
  // Form state
  const [formData, setFormData] = useState({
    uuid: "",
    country: "",
    occupationVersion: "",
    occupationName: "",
    occupationCode: "",
    compareCountry: "",
    compareOccupationVersion: "",
    compareOccupationName: "",
    compareOccupationCode: "",
    description: "",
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    country: "",
    occupationVersion: "",
    occupationName: "",
    occupationCode: "",
    compareCountry: "",
    compareOccupationVersion: "",
    compareOccupationName: "",
    compareOccupationCode: "",
  });

  // Populate form data when in edit mode
  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        uuid: rowData.uuid || "",
        country: rowData.country || "",
        occupationVersion: rowData.occupation_version || "",
        occupationName: rowData.occupation_name || "",
        occupationCode: rowData.occupation_code || "",
        compareCountry: rowData.compare_country || "",
        compareOccupationVersion: rowData.compare_occupation_version || "",
        compareOccupationName: rowData.compare_occupation_name || "",
        compareOccupationCode: rowData.compare_occupation_code || "",
        description: rowData.description || "",
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
      search: "",
      status: "",
      sortBy: "name",
      sortOrder: "asc",
    };

    dispatch(
      representingCountryList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setCountryListData(response?.data || []);
          setCompareCountryListData(response?.data || []);
        }
      })
    );
    dispatch(
      occupationVersionList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setOccupationVersionListData(response?.data || []);
          setCompareOccupationVersionListData(response?.data || []);
        }
      })
    );
    dispatch(
      occupationNameList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setOccupationNameListData(response?.data || []);
          setCompareOccupationNameListData(response?.data || []);
        }
      })
    );
    dispatch(
      occupationCodeList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setOccupationCodeListData(response?.data || []);
          setCompareOccupationCodeListData(response?.data || []);
        }
      })
    );
  };

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: "",
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

    if (!formData.country) {
      newErrors.country = "Country is required";
      isValid = false;
    }

    if (!formData.occupationVersion) {
      newErrors.occupationVersion = "Occupation Version is required";
      isValid = false;
    }

    if (!formData.occupationName) {
      newErrors.occupationName = "Occupation Name is required";
      isValid = false;
    }

    if (!formData.occupationCode) {
      newErrors.occupationCode = "Occupation Code is required";
      isValid = false;
    }

    if (!formData.compareCountry) {
      newErrors.compareCountry = "Compare Country is required";
      isValid = false;
    }

    if (!formData.compareOccupationVersion) {
      newErrors.compareOccupationVersion =
        "Compare Occupation Version is required";
      isValid = false;
    }

    if (!formData.compareOccupationName) {
      newErrors.compareOccupationName = "Compare Occupation Name is required";
      isValid = false;
    }

    if (!formData.compareOccupationCode) {
      newErrors.compareOccupationCode = "Compare Occupation Code is required";
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();

    if (validateForm()) {
      const sendPayload =
        mode === "edit"
          ? {
              uuid: formData.uuid,
              country: formData.country,
              occupation_version: formData.occupationVersion,
              occupation_name: formData.occupationName,
              occupation_code: formData.occupationCode,
              compare_country: formData.compareCountry,
              compare_occupation_version: formData.compareOccupationVersion,
              compare_occupation_name: formData.compareOccupationName,
              compare_occupation_code: formData.compareOccupationCode,
              description: formData.description.trim(),
            }
          : {
              country: formData.country,
              occupation_version: formData.occupationVersion,
              occupation_name: formData.occupationName,
              occupation_code: formData.occupationCode,
              compare_country: formData.compareCountry,
              compare_occupation_version: formData.compareOccupationVersion,
              compare_occupation_name: formData.compareOccupationName,
              compare_occupation_code: formData.compareOccupationCode,
              description: formData.description.trim(),
            };

      setLoading(true);
      const action =
        mode === "edit"
          ? occupationToOccupationEdit
          : occupationToOccupationAdd;

      dispatch(
        action(sendPayload, (response, error) => {
          setLoading(false);
          if (error) {
            toast.error(error?.response?.data?.message || "Server error");
          } else if (
            response?.statusCode === 200 &&
            response?.status === true
          ) {
            toast.success(response?.message);
            resetForm();
            handleClose(true);
          } else {
            toast.error("Something went wrong.");
          }
        })
      );
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      uuid: "",
      country: "",
      occupationVersion: "",
      occupationName: "",
      occupationCode: "",
      compareCountry: "",
      compareOccupationVersion: "",
      compareOccupationName: "",
      compareOccupationCode: "",
      description: "",
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
      <div
        className="modal-dialog modal-lg modal-dialog-centered"
        role="document"
      >
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="AddEditStateModalLabel">
              {mode === "edit"
                ? "Edit Language Ability"
                : "Add Language Ability"}
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
              <div className="row">
                {/* Country */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Country<span className="text-danger">*</span>
                  </label>
                  <Select
                    options={countryListData.map((option) => ({
                      value: option.uuid,
                      label: option.name,
                    }))}
                    value={
                      formData.country
                        ? countryListData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.name,
                            }))
                            .find((opt) => opt.value === formData.country)
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "country",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Country"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.country ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.country && (
                    <div className="text-danger text-sm mt-1">
                      {errors.country}
                    </div>
                  )}
                </div>

                {/* Occupation Version */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Occupation Version<span className="text-danger">*</span>
                  </label>
                  <Select
                    options={occupationVersionListData.map((option) => ({
                      value: option.uuid,
                      label: option.occupation_version,
                    }))}
                    value={
                      formData.occupationVersion
                        ? occupationVersionListData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.occupation_version,
                            }))
                            .find(
                              (opt) => opt.value === formData.occupationVersion
                            )
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
                    placeholder="Select Occupation Version"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.occupationVersion ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.occupationVersion && (
                    <div className="text-danger text-sm mt-1">
                      {errors.occupationVersion}
                    </div>
                  )}
                </div>

                {/* Occupation Name */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Occupation Name<span className="text-danger">*</span>
                  </label>
                  <Select
                    options={occupationNameListData.map((option) => ({
                      value: option.uuid,
                      label: option.occupationname,
                    }))}
                    value={
                      formData.occupationName
                        ? occupationNameListData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.occupationname,
                            }))
                            .find(
                              (opt) => opt.value === formData.occupationName
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "occupationName",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Occupation Name"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.occupationName ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.occupationName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.occupationName}
                    </div>
                  )}
                </div>

                {/* Occupation Code */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Occupation Code<span className="text-danger">*</span>
                  </label>
                  <Select
                    options={occupationCodeListData.map((option) => ({
                      value: option.uuid,
                      label: option.occupationcode,
                    }))}
                    value={
                      formData.occupationCode
                        ? occupationCodeListData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.occupationcode,
                            }))
                            .find(
                              (opt) => opt.value === formData.occupationCode
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "occupationCode",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Occupation Code"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.occupationCode ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.occupationCode && (
                    <div className="text-danger text-sm mt-1">
                      {errors.occupationCode}
                    </div>
                  )}
                </div>

                {/* Compare Country */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Compare Country<span className="text-danger">*</span>
                  </label>
                  <Select
                    options={compareCountryListData.map((option) => ({
                      value: option.uuid,
                      label: option.name,
                    }))}
                    value={
                      formData.compareCountry
                        ? compareCountryListData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.name,
                            }))
                            .find(
                              (opt) => opt.value === formData.compareCountry
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "compareCountry",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Compare Country"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.compareCountry ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.compareCountry && (
                    <div className="text-danger text-sm mt-1">
                      {errors.compareCountry}
                    </div>
                  )}
                </div>

                {/* Compare Occupation Version */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Compare Occupation Version
                    <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={compareOccupationVersionListData.map((option) => ({
                      value: option.uuid,
                      label: option.occupation_version,
                    }))}
                    value={
                      formData.compareOccupationVersion
                        ? compareOccupationVersionListData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.occupation_version,
                            }))
                            .find(
                              (opt) =>
                                opt.value === formData.compareOccupationVersion
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "compareOccupationVersion",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Compare Occupation Version"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.compareOccupationVersion ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.compareOccupationVersion && (
                    <div className="text-danger text-sm mt-1">
                      {errors.compareOccupationVersion}
                    </div>
                  )}
                </div>

                {/* Compare Occupation Name */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Compare Occupation Name
                    <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={compareOccupationNameListData.map((option) => ({
                      value: option.uuid,
                      label: option.occupationname,
                    }))}
                    value={
                      formData.compareOccupationName
                        ? compareOccupationNameListData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.occupationname,
                            }))
                            .find(
                              (opt) =>
                                opt.value === formData.compareOccupationName
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "compareOccupationName",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Compare Occupation Name"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.compareOccupationName ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.compareOccupationName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.compareOccupationName}
                    </div>
                  )}
                </div>

                {/* Compare Occupation Code */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Compare Occupation Code
                    <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={compareOccupationCodeListData.map((option) => ({
                      value: option.uuid,
                      label: option.occupationcode,
                    }))}
                    value={
                      formData.compareOccupationCode
                        ? compareOccupationCodeListData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.occupationcode,
                            }))
                            .find(
                              (opt) =>
                                opt.value === formData.compareOccupationCode
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "compareOccupationCode",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Compare Occupation Code"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.compareOccupationCode ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.compareOccupationCode && (
                    <div className="text-danger text-sm mt-1">
                      {errors.compareOccupationCode}
                    </div>
                  )}
                </div>

                {/* Description */}
                <div className="col-12 mb-20">
                  <label
                    htmlFor="desc"
                    className="form-label fw-semibold text-primary-light text-sm mb-8"
                  >
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
                        <span
                          className="spinner-border spinner-border-sm me-2"
                          role="status"
                          aria-hidden="true"
                        ></span>
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

export default AddEditOccupationToOccupationModal;
