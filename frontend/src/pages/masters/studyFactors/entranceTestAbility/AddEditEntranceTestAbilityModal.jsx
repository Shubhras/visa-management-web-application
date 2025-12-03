import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import Select from "react-select";
import {
  entranceTestAbilityGroupList,
  entranceTestNameList,
  entranceTestResultList,
  factorForList,
  studyFactorEntranceTestAbilityAdd,
  studyFactorEntranceTestAbilityEdit,
} from "../../../../store/actions";

const AddEditStudyFactorEntranceTestAbilityModal = ({
  show,
  handleClose,
  mode = "add",
  rowData = null,
}) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [factorForData, setFactorForData] = useState([]);
  const [entranceTestAbilityGroupData, setEntranceTestAbilityGroupData] = useState([]);
  const [entranceTestNameData, setEntranceTestNameData] = useState([]);
  const [minimumScoreRequiredData, setMinimumScoreRequiredData] = useState([]);

  // Form state
  const [formData, setFormData] = useState({
    uuid: "",
    factorForName: "",
    studyEntranceTestAbilityGroup: "",
    entranceTestName: "",
    minimumScoreRequired: "",
    description: "",
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    factorForName: "",
    studyEntranceTestAbilityGroup: "",
    entranceTestName: "",
    minimumScoreRequired: "",
  });

  // Populate form data when in edit mode
  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        uuid: rowData.uuid || "",
        factorForName: rowData.factor_for || "",
        studyEntranceTestAbilityGroup: rowData.entrance_test_ability_group || "",
        entranceTestName: rowData.entrance_test_name || "",
        minimumScoreRequired: rowData.minimum_score_required || "",
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
      entranceTestAbilityGroupList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setEntranceTestAbilityGroupData(response?.data || []);
        }
      })
    );
    dispatch(
      entranceTestNameList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setEntranceTestNameData(response?.data || []);
        }
      })
    );
    dispatch(
      entranceTestResultList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setMinimumScoreRequiredData(response?.data || []);
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

    if (!formData.factorForName) {
      newErrors.factorForName = "Factor For name is required";
      isValid = false;
    }

    if (!formData.studyEntranceTestAbilityGroup) {
      newErrors.studyEntranceTestAbilityGroup =
        "Study Entrance Test Ability Group is required";
      isValid = false;
    }

    if (!formData.entranceTestName) {
      newErrors.entranceTestName = "Entrance Test Name is required";
      isValid = false;
    }

    if (!formData.minimumScoreRequired) {
      newErrors.minimumScoreRequired = "Minimum Score is required";
      isValid = false;
    }
   
    // State name validation

    // State name validation

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
              entrance_test_ability_group:formData.studyEntranceTestAbilityGroup,
              entrance_test_name: formData.entranceTestName,
              minimum_score_required: formData.minimumScoreRequired,
              description: formData.description.trim(),
            }
          : {
              factor_for: formData.factorForName,
              entrance_test_ability_group:formData.studyEntranceTestAbilityGroup,
              entrance_test_name: formData.entranceTestName,
              minimum_score_required: formData.minimumScoreRequired,
              description: formData.description.trim(),
            };

      setLoading(true);
      const action =
        mode === "edit"
          ? studyFactorEntranceTestAbilityEdit
          : studyFactorEntranceTestAbilityAdd;

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
      studyEntranceTestAbilityGroup: "",
      entranceTestName: "",
      minimumScoreRequired: "",
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
                ? "Edit Study Factor : Entrance Test Ability"
                : "Add Study Factor : Entrance Test Ability"}
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
                <div className="col-6 mb-20">
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


                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Study Entrance Test Ability Group{" "}
                    <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={entranceTestAbilityGroupData.map((option) => ({
                      value: option.uuid,
                      label: option.name,
                    }))}
                    value={
                      formData.studyEntranceTestAbilityGroup
                        ? entranceTestAbilityGroupData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.name,
                            }))
                            .find(
                              (opt) =>
                                opt.value === formData.studyEntranceTestAbilityGroup
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "studyEntranceTestAbilityGroup",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Entrance Test Ability Group"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.studyEntranceTestAbilityGroup ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.studyEntranceTestAbilityGroup && (
                    <div className="text-danger text-sm mt-1">
                      {errors.studyEntranceTestAbilityGroup}
                    </div>
                  )}
                </div>
                
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                     Entrance Test Name {" "}
                    <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={entranceTestNameData.map((option) => ({
                      value: option.uuid,
                      label: option.fullname,
                    }))}
                    value={
                      formData.entranceTestName
                        ? entranceTestNameData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.fullname,
                            }))
                            .find(
                              (opt) =>
                                opt.value === formData.entranceTestName
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "entranceTestName",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Entrance Test Name"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.entranceTestName ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.entranceTestName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.entranceTestName}
                    </div>
                  )}
                </div>{" "}

                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Module Name{" "}
                    <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={minimumScoreRequiredData.map((option) => ({
                      value: option.uuid,
                      label: option.testresult,
                    }))}
                    value={
                      formData.minimumScoreRequired
                        ? minimumScoreRequiredData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.testresult,
                            }))
                            .find(
                              (opt) =>
                                opt.value === formData.minimumScoreRequired
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "minimumScoreRequired",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Minumum Score Required"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.minimumScoreRequired ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.minimumScoreRequired && (
                    <div className="text-danger text-sm mt-1">
                      {errors.minimumScoreRequired}
                    </div>
                  )}
                </div>{" "}

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

export default AddEditStudyFactorEntranceTestAbilityModal;
