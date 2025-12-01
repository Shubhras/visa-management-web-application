import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import Select from "react-select";
import {
  academicResultGroupList,
  academicResultTypeList,
  factorForList,
  studyFactorAcademicResultAdd,
  studyFactorAcademicResultEdit,
} from "../../../../store/actions";

const AddEditStudyFactorBacklogsModal = ({
  show,
  handleClose,
  mode = "add",
  rowData = null,
}) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [factorForData, setFactorForData] = useState([]);
  const [academicResultGroupData, setAcademicResultGroupData] = useState([]);
  const [academicResultTypeData, setAcademicResultTypeData] = useState([]);

  // Form state
  const [formData, setFormData] = useState({
    uuid: "",
    factorForName: "",
    studyAcademicResultGroup: "",
    minimumAcademicResultType: "",
    minimumAcademicResult: "",
    description: "",
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    factorForName: "",
    studyAcademicResultGroup: "",
    minimumAcademicResultType: "",
    minimumAcademicResult: "",
  });

  // Populate form data when in edit mode
  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        uuid: rowData.uuid || "",
        factorForName: rowData.factor_for_uuid || "",
        studyAcademicResultGroup: rowData.studyAcademicResultGroup || "",
        minimumAcademicResultType: rowData.minimumAcademicResultType || "",
        minimumAcademicResult: rowData.minimumAcademicResult || "", //formData.state === "STATE" ? "State" : "Territory" || '',
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
      factorForList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setFactorForData(response?.data || []);
        }
      })
    );
    dispatch(
      academicResultGroupList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setAcademicResultGroupData(response?.data || []);
        }
      })
    );
    dispatch(
      academicResultTypeList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setAcademicResultTypeData(response?.data || []);
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

    // State name validation
    if (!formData.factorForName.trim()) {
      newErrors.factorForName = "Factor For name is required";
      isValid = false;
    }

    if (!formData.studyAcademicResultGroup.trim()) {
      newErrors.studyAcademicResultGroup = "Academic Result Group is required";
      isValid = false;
    }

    if (!formData.minimumAcademicResultType.trim()) {
      newErrors.minimumAcademicResultType =
        "Minimum Academic Result Type is required";
      isValid = false;
    }

    // State name validation
    if (!formData.minimumAcademicResult.trim()) {
      newErrors.minimumAcademicResult = "Minimum Academic Result is required";
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
              factor_for: formData.factorForName,
              studyAcademicResultGroup: formData.studyAcademicResultGroup,
              minimumAcademicResult: formData.minimumAcademicResult,
              minimumAcademicResultType: formData.minimumAcademicResultType,
              description: formData.description.trim(),
            }
          : {
              factor_for: formData.factorForName,
              studyAcademicResultGroup: formData.studyAcademicResultGroup,
              minimumAcademicResult: formData.minimumAcademicResult,
              minimumAcademicResultType: formData.minimumAcademicResultType,
              description: formData.description.trim(),
            };

      setLoading(true);
      const action =
        mode === "edit"
          ? studyFactorAcademicResultEdit
          : studyFactorAcademicResultAdd;

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
      factorForName: "",
      studyAcademicResultGroup: "",
      minimumAcademicResultType: "",
      minimumAcademicResult: "",
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
              {mode === "edit" ? "Edit Age" : "Add Age"}
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

                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Factor For <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={factorForData.map((option) => ({
                      value: option.uuid,
                      label: option.name,
                    }))}
                    value={
                      formData.factorForName
                        ? factorForData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.name,
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
                    className={`custom-select-container ${
                      errors.factorForName ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.factorForName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.factorForName}
                    </div>
                  )}
                </div>

                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Study : Academic Result Group{" "}
                    <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={academicResultGroupData.map((option) => ({
                      value: option.uuid,
                      label: option.name,
                    }))}
                    value={
                      formData.studyAcademicResultGroup
                        ? academicResultGroupData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.name,
                            }))
                            .find(
                              (opt) =>
                                opt.value === formData.studyAcademicResultGroup
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "studyAcademicResultGroup",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Academic Result Group"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.studyAcademicResultGroup ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.studyAcademicResultGroup && (
                    <div className="text-danger text-sm mt-1">
                      {errors.studyAcademicResultGroup}
                    </div>
                  )}
                </div>

                <div className="col-12 mb-20">
                  {/* Main Label */}
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Minimum Academic Result Required{" "}
                    <span className="text-danger">*</span>
                  </label>

                  <div className="row">
                    {/* Select Box */}
                    <div className="col-6">
                      <Select
                        options={academicResultTypeData.map((option) => ({
                          value: option.uuid,
                          label: option.name,
                        }))}
                        value={
                          formData.minimumAcademicResultType
                            ? academicResultTypeData
                                .map((option) => ({
                                  value: option.uuid,
                                  label: option.name,
                                }))
                                .find(
                                  (opt) =>
                                    opt.value ===
                                    formData.minimumAcademicResultType
                                )
                            : null
                        }
                        onChange={(selectedOption) =>
                          handleChange({
                            target: {
                              name: "minimumAcademicResultType",
                              value: selectedOption ? selectedOption.value : "",
                            },
                          })
                        }
                        filterOption={customFilterOption}
                        placeholder="Select Academic Result Type"
                        isClearable
                        isSearchable
                        className={`custom-select-container ${
                          errors.minimumAcademicResultType ? "is-invalid" : ""
                        }`}
                        classNamePrefix="custom-select"
                      />

                      {errors.minimumAcademicResultType && (
                        <div className="text-danger text-sm mt-1">
                          {errors.minimumAcademicResultType}
                        </div>
                      )}
                    </div>

                    {/* Text Input */}
                    <div className="col-6">
                      <input
                        type="text"
                        id="desc"
                        name="minimumAcademicResult"
                        value={formData.minimumAcademicResult}
                        onChange={handleChange}
                        placeholder="Minimum Academic Result"
                        className={`form-control custom-select-container ${
                          errors.minimumAcademicResult ? "is-invalid" : ""
                        }`}
                      />

                      {errors.minimumAcademicResult && (
                        <div className="text-danger text-sm mt-1">
                          {errors.minimumAcademicResult}
                        </div>
                      )}
                    </div>
                  </div>
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

export default AddEditStudyFactorBacklogsModal;
