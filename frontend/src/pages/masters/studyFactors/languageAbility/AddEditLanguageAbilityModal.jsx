import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import Select from "react-select";
import { countryDemoList } from "../../../../store/master/companyMasters/actions";
import {
  factorForList,
  languageAbilityGroupList,
  languageTestModuleNameList,
  languageTestNameList,
  languageTestResultList,
  representingCountryList,
  studyFactorLanguageAbilityAdd,
  studyFactorLanguageAbilityEdit,
} from "../../../../store/actions";
import LanguageTestModuleNameList from "../../testMaster/languageTestModuleName/LanguageTestModuleNameList";

const AddEditStudyFactorLanguageAbilityModal = ({
  show,
  handleClose,
  mode = "add",
  rowData = null,
}) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [factorForData, setFactorForData] = useState([]);
  const [languageAbilityGroupData, setLanguageAbilityGroupData] = useState([]);
  const [moduleNameData, setModuleNameData] = useState([]);
  const [minimumOverallScoreData, setMinimumOverallScoreData] = useState([]);
  const [notLessThanData, setNotLessThanData] = useState([]);
  const [languageTestNameData, setLanguageTextNameData] = useState([]);

  // Form state
  const [formData, setFormData] = useState({
    uuid: "",
    factorForName: "",
    studyLanguageAbilityGroup: "",
    languageTestName: "",
    moduleName: "",
    minimumOverallScore: "",
    notMoreThan: "",
    inNoOfModules: "",
    description: "",
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    factorForName: "",
    studyLanguageAbilityGroup: "",
    languageTestName: "",
    moduleName: "",
    minimumOverallScore: "",
    notMoreThan: "",
    inNoOfModules: "",
  });

  // Populate form data when in edit mode
  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        uuid: rowData.uuid || "",
        factorForName: rowData.factor_for_uuid || "",
        studyLanguageAbilityGroup: rowData.studyLanguageAbilityGroup || "",
        languageTestName: rowData.languageTestName || "",
        moduleName: rowData.moduleName || "",
        minimumOverallScore: rowData.minimumOverallScore || "",
        notMoreThan: rowData.notMoreThan || "", //formData.state === "STATE" ? "State" : "Territory" || '',
        inNoOfModules: rowData.inNoOfModules || "",
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
      languageAbilityGroupList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setLanguageAbilityGroupData(response?.data || []);
        }
      })
    );
    dispatch(
      languageTestModuleNameList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setModuleNameData(response?.data || []);
        }
      })
    );
    dispatch(
      languageTestResultList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setMinimumOverallScoreData(response?.data || []);
          setNotLessThanData(response?.data || []);
        }
      })
    );
    dispatch(
      languageTestNameList(params, (response, error) => {
        setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setLanguageTextNameData(response?.data || []);
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

    if (!formData.factorForName.trim()) {
      newErrors.factorForName = "Factor For name is required";
      isValid = false;
    }

    if (!formData.studyLanguageAbilityGroup.trim()) {
      newErrors.studyLanguageAbilityGroup =
        "Study Language Ability Group is required";
      isValid = false;
    }

    if (!formData.languageTestName.trim()) {
      newErrors.languageTestName = "Language Test Name is required";
      isValid = false;
    }
    if (!formData.moduleName.trim()) {
      newErrors.moduleName = "Modules Name is required";
      isValid = false;
    }
    if (!formData.minimumOverallScore.trim()) {
      newErrors.minimumOverallScore = "Minimum Overall Score is required";
      isValid = false;
    }
    

    // State name validation

    // State name validation

    setErrors(newErrors);
    return isValid;
  };

  // Handle form submission
  const handleSubmit = (e) => {
    console.log("clcik clcik")
    e.preventDefault();

    if (validateForm()) {
      const sendPayload =
        mode === "edit"
          ? {
              uuid: formData.uuid,
              factor_for: formData.factorForName.trim(),
              language_ability_group:
                formData.studyLanguageAbilityGroup.trim(),
              language_test_name: formData.languageTestName.trim(),
              module_name: formData.moduleName.trim(),
              minimum_overall_score: formData.minimumOverallScore.trim(),
              not_less_than: formData.notMoreThan.trim(),
              in_no_of_modules: formData.inNoOfModules.trim(),
              description: formData.description.trim(),
            }
          : {
            factor_for: formData.factorForName.trim(),
              language_ability_group:
                formData.studyLanguageAbilityGroup.trim(),
              language_test_name: formData.languageTestName.trim(),
              module_name: formData.moduleName.trim(),
              minimum_overall_score: formData.minimumOverallScore.trim(),
              not_less_than: formData.notMoreThan.trim(),
              in_no_of_modules: formData.inNoOfModules.trim(),
              description: formData.description.trim(),
            };

      setLoading(true);
      const action =
        mode === "edit"
          ? studyFactorLanguageAbilityEdit
          : studyFactorLanguageAbilityAdd;

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
      studyLanguageAbilityGroup: "",
      languageTestName: "",
      moduleName: "",
      minimumOverallScore: "",
      notMoreThan: "",
      inNoOfModules: "",
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
                    Study Factor Language Ability{" "}
                    <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={languageAbilityGroupData.map((option) => ({
                      value: option.uuid,
                      label: option.name,
                    }))}
                    value={
                      formData.studyLanguageAbilityGroup
                        ? languageAbilityGroupData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.name,
                            }))
                            .find(
                              (opt) =>
                                opt.value === formData.studyLanguageAbilityGroup
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "studyLanguageAbilityGroup",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select language Ability Group"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.studyLanguageAbilityGroup ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.studyLanguageAbilityGroup && (
                    <div className="text-danger text-sm mt-1">
                      {errors.studyLanguageAbilityGroup}
                    </div>
                  )}
                </div>
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Language Test Name {" "}
                    <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={languageTestNameData.map((option) => ({
                      value: option.uuid,
                      label: option.name,
                    }))}
                    value={
                      formData.languageTestName
                        ? languageTestNameData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.name,
                            }))
                            .find(
                              (opt) =>
                                opt.value === formData.languageTestName
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "languageTestName",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select language Test Name"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.languageTestName ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.languageTestName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.languageTestName}
                    </div>
                  )}
                </div>{" "}

                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Module Name{" "}
                    <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={moduleNameData.map((option) => ({
                      value: option.uuid,
                      label: option.name,
                    }))}
                    value={
                      formData.moduleName
                        ? moduleNameData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.name,
                            }))
                            .find(
                              (opt) =>
                                opt.value === formData.moduleName
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "moduleName",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Module Name"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.moduleName ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.moduleName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.moduleName}
                    </div>
                  )}
                </div>{" "}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Minimum Overall Score{" "}
                    <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={minimumOverallScoreData.map((option) => ({
                      value: option.uuid,
                      label: option.numeric_score,
                    }))}
                    value={
                      formData.minimumOverallScore
                        ? minimumOverallScoreData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.numeric_score,
                            }))
                            .find(
                              (opt) =>
                                opt.value === formData.minimumOverallScore
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "minimumOverallScore",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Minimum Overall Score"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.minimumOverallScore ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.minimumOverallScore && (
                    <div className="text-danger text-sm mt-1">
                      {errors.minimumOverallScore}
                    </div>
                  )}
                </div>{" "}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Not Less Than{" "}
                  </label>
                  <Select
                    options={notLessThanData.map((option) => ({
                      value: option.uuid,
                      label: option.numeric_score,
                    }))}
                    value={
                      formData.notMoreThan
                        ? notLessThanData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.numeric_score,
                            }))
                            .find(
                              (opt) =>
                                opt.value === formData.notMoreThan
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "notMoreThan",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Not less Than"
                    isClearable
                    isSearchable
                    className={`custom-select-container`}
                    classNamePrefix="custom-select"
                  />
                 
                </div>

                 <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    In No. of Modules 
                  </label>
                  <input
                    type="number"
                    name="inNoOfModules"
                    value={formData.inNoOfModules}
                    onChange={handleChange}
                    className={`form-control radius-8`}
                    placeholder="Enter Factor For"
                  />
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

export default AddEditStudyFactorLanguageAbilityModal;
