import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import {
  occupationCategoryList,
  occupationLevelAdd,
  occupationLevelCodeList,
  occupationLevelEdit,
  occupationVersionList,
  representingCountryList,
} from "../../../../store/master/occupationMaster/action";
import Select from "react-select";

const AddEditOccupationLevel = ({
  show,
  handleClose,
  mode = "add",
  rowData = null,
}) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [countryData, setCountryData] = useState([]);
  const [occupationversiondata, setOccupationVersionData] = useState([]);
  const [occupationCategoryData, setOccupationCategoryData] = useState([]);
  const [occupationLevelCodeData, setOccupationLevelCodeData] = useState([]);

  // Form state
  const [formData, setFormData] = useState({
    uuid: "",
    country: "",
    occupationVersion: "",
    occupationLevelCode: "",
    occupationLevelName: "",
    occupationCategory: "",
    description: "",
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    country: "",
    occupationVersion: "",
    occupationLevelCode: "",
    occupationCategory: "",
    occupationLevelName: "",
  });

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
        // setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setCountryData(response?.data || []);
        }
      })
    );
    dispatch(
      occupationVersionList(params, (response, error) => {
        // setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setOccupationVersionData(response?.data || []);
        }
      })
    );
    dispatch(
      occupationCategoryList(params, (response, error) => {
        // setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setOccupationCategoryData(response?.data || []);
        }
      })
    );
    dispatch(
      occupationLevelCodeList(params, (response, error) => {
        // setLoading(false);
        if (response?.statusCode === 200 && response?.status === true) {
          setOccupationLevelCodeData(response?.data || []);
        }
      })
    );
  };
  const customFilterOptionCountry = (option, inputValue) => {
    if (!inputValue) return true;
    return option.label.toLowerCase().startsWith(inputValue.toLowerCase());
  };
  // Populate form data when in edit mode
  useEffect(() => {
    if (show) {
      if (mode === "edit" && rowData) {
        setFormData({
          uuid: rowData.uuid || "",
          country: rowData.country_uuid || "",
          occupationVersion: rowData.occupationversion_uuid || "",
          occupationLevelCode: rowData.occupationlevelcode_uuid || "",
          occupationCategory: rowData.occupationcategory_uuid || "",
          occupationLevelName: rowData.occupationlevel || "",
          description: rowData.description || "",
        });
      } else {
        // Reset form when switching to add mode
        setFormData({
          uuid: "",
          country: "",
          occupationVersion: "",
          occupationLevelCode: "",
          occupationCategory: "",
          occupationLevelName: "",
          description: "",
        });
      }
      fetchCountryList();
    }
  }, [mode, rowData, show]);

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

  // Validate form
  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    // Department Name validation
    if (!formData.occupationLevelCode.trim()) {
      newErrors.occupationLevelCode = "Occupation Level Code Name is required";
      isValid = false;
    }
    if (!formData.country.trim()) {
      newErrors.country = "Country is required";
      isValid = false;
    }
    if (!formData.occupationVersion.trim()) {
      newErrors.occupationVersion = "Occupation Version is required";
      isValid = false;
    }
    if (!formData.occupationLevelName.trim()) {
      newErrors.occupationLevelName = "Occupation Level is required";
      isValid = false;
    }
    if (!formData.occupationCategory.trim()) {
      newErrors.occupationCategory = "Occupation Category is required";
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
              country_id: formData.country,
              occupationversion_id: formData.occupationVersion,
              occupationlevelcode_id: formData.occupationLevelCode,
              occupationcategory_id: formData.occupationCategory,
              occupationlevel: formData.occupationLevelName,
              description: formData.description,
            }
          : {
              country_id: formData.country,
              occupationversion_id: formData.occupationVersion,
              occupationlevelcode_id: formData.occupationLevelCode,
              occupationcategory_id: formData.occupationCategory,
              occupationlevel: formData.occupationLevelName,
              description: formData.description,
            };

      setLoading(true);

      const action = mode === "edit" ? occupationLevelEdit : occupationLevelAdd;

      dispatch(
        action(sendPayload, (response, error) => {
          setLoading(false);
          if (error) {
            toast.error(error?.response?.data?.message || "Server error");
          } else {
            if (response?.statusCode === 200 && response?.status === true) {
              toast.success(response?.message);
              resetForm();
              handleClose(true);
            } else {
              toast.error("Something went wrong.");
            }
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
      occupationLevelCode: "",
      occupationCategory: "",
      occupationLevelName: "",
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

  // Conditional return after all hooks
  if (!show) return null;

  return (
    <div
      className="modal fade show common-ctl-popup"
      tabIndex={-1}
      role="dialog"
      aria-labelledby="departmentModalLabel"
      aria-hidden={!show}
    >
      <div
        className="modal-dialog modal-lg modal-dialog-centered"
        role="document"
      >
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="departmentModalLabel">
              {mode === "edit"
                ? "Edit Occupation Level"
                : "Add Occupation Level"}
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
                {/* Department Name */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Country<span className="text-danger">*</span>
                  </label>
                  <Select
                    options={countryData.map((option) => ({
                      value: option.uuid,
                      label: option.name + " (" + option?.continent?.name + ")",
                    }))}
                    value={
                      formData.country
                        ? countryData
                            .map((option) => ({
                              value: option.uuid,
                              label:
                                option.name +
                                " (" +
                                option?.continent?.name +
                                ")",
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
                    placeholder="Select country"
                    filterOption={customFilterOptionCountry}
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
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Occupation Version<span className="text-danger">*</span>
                  </label>
                  <Select
                    options={occupationversiondata.map((option) => ({
                      value: option.uuid,
                      label: option.occupation_version,
                    }))}
                    value={
                      formData.occupationVersion
                        ? occupationversiondata
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
                    placeholder="Select Occupation Version"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.country ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.occupationVersion && (
                    <div className="text-danger text-sm mt-1">
                      {errors.occupationVersion}
                    </div>
                  )}
                </div>
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Occupation Category<span className="text-danger">*</span>
                  </label>
                  <Select
                    options={occupationCategoryData.map((option) => ({
                      value: option.uuid,
                      label: option.occupationcategory,
                    }))}
                    value={
                      formData.occupationCategory
                        ? occupationCategoryData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.occupationcategory,
                            }))
                            .find(
                              (opt) => opt.value === formData.occupationCategory
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "occupationCategory",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    placeholder="Select Occupation Category"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.country ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.occupationCategory && (
                    <div className="text-danger text-sm mt-1">
                      {errors.occupationCategory}
                    </div>
                  )}
                </div>{" "}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Occupation Level Code<span className="text-danger">*</span>
                  </label>
                  <Select
                    options={occupationLevelCodeData.map((option) => ({
                      value: option.uuid,
                      label: option.occupationlevelcode,
                    }))}
                    value={
                      formData.occupationLevelCode
                        ? occupationLevelCodeData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.occupationlevelcode,
                            }))
                            .find(
                              (opt) =>
                                opt.value === formData.occupationLevelCode
                            )
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "occupationLevelCode",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    placeholder="Select Occupation Level Code"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.country ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.occupationLevelCode && (
                    <div className="text-danger text-sm mt-1">
                      {errors.occupationLevelCode}
                    </div>
                  )}
                </div>{" "}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Occupation Level <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="occupationLevelName"
                    value={formData.occupationLevelName}
                    onChange={handleChange}
                    className={`form-control radius-8 ${
                      errors.occupationLevelName ? "is-invalid" : ""
                    }`}
                    placeholder="Enter Occupation Level Name"
                  />
                  {errors.occupationLevelName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.occupationLevelName}
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
                    className={`form-control ${
                      errors.description ? "is-invalid" : ""
                    }`}
                    id="desc"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    rows={4}
                    cols={50}
                    placeholder="Description"
                  />
                </div>
                {/* Buttons */}
                <div className="d-flex align-items-center justify-content-center gap-3 mt-24">
                  <button
                    type="button"
                    onClick={onClose}
                    className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-16 py-6 radius-8"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn comman-btn-color border border-primary-600 text-md px-16 py-6 radius-8"
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

export default AddEditOccupationLevel;
