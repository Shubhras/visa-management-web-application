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

const AddEditStudyFactorAcademicResultModal = ({
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
  const [selectedDatatype, setSelectedDatatype] = useState("");

  // Form state
  const [formData, setFormData] = useState({
    uuid: "",
    factorForName: "",
    studyAcademicResultGroup: "",
    minimumAcademicResultType: "",
    minimumAcademicResult: "",
    description: "",
  });

  // Validation errors
  const [errors, setErrors] = useState({
    factorForName: "",
    studyAcademicResultGroup: "",
    minimumAcademicResultType: "",
    minimumAcademicResult: "",
  });

  // Datatype options for the dropdown
  const datatypeOptions = [
    { value: "Numeric", label: "Numeric" },
    { value: "Text", label: "Text" },
  ];

  // ========= EDIT MODE: POPULATE DATA =========
  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        uuid: rowData.uuid || "",
        factorForName: rowData.factor_for_uuid || "",
        studyAcademicResultGroup: rowData.studyAcademicResultGroup || "",
        minimumAcademicResultType: rowData.minimum_academic_result_type || "",
        minimumAcademicResult: rowData.minimumAcademicResult || "",
        description: rowData.description || "",
      });
    } else {
      resetForm();
    }

    fetchDropdowns();
  }, [mode, rowData, show]);

  // ========= SET DATATYPE WHEN TYPE IS SELECTED =========
  useEffect(() => {
    if (formData.minimumAcademicResultType && academicResultTypeData.length > 0) {
      const selectedType = academicResultTypeData.find(
        (type) => type.uuid === formData.minimumAcademicResultType
      );
      if (selectedType) {
        setSelectedDatatype(selectedType.datatype);
      }
    }
  }, [formData.minimumAcademicResultType, academicResultTypeData]);

  // ========= FETCH DROPDOWNS =========
  const fetchDropdowns = () => {
    const params = {
      page: 1,
      limit: 2000,
      search: "",
      status: "",
      sortBy: "name",
      sortOrder: "asc",
    };

    dispatch(
      factorForList(params, (response) => {
        if (response?.statusCode === 200 && response?.status === true) {
          setFactorForData(response?.data || []);
        }
      })
    );

    dispatch(
      academicResultGroupList(params, (response) => {
        if (response?.statusCode === 200 && response?.status === true) {
          setAcademicResultGroupData(response?.data || []);
        }
      })
    );

    dispatch(
      academicResultTypeList(params, (response) => {
        if (response?.statusCode === 200 && response?.status === true) {
          setAcademicResultTypeData(response?.data || []);
        }
      })
    );
  };

  // ========= INPUT CHANGE =========
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  // ========= HANDLE ACADEMIC RESULT TYPE CHANGE =========
  const handleAcademicResultTypeChange = (selectedOption) => {
    const newValue = selectedOption ? selectedOption.value : "";
    
    setFormData((prev) => ({
      ...prev,
      minimumAcademicResultType: newValue,
      minimumAcademicResult: "", // Clear the datatype value when type changes
    }));

    if (errors.minimumAcademicResultType) {
      setErrors((prev) => ({ ...prev, minimumAcademicResultType: "" }));
    }

    // Find the selected type to get its datatype
    if (selectedOption) {
      const selectedType = academicResultTypeData.find(
        (type) => type.uuid === selectedOption.value
      );
      if (selectedType) {
        setSelectedDatatype(selectedType.datatype);
        // Auto-select the datatype in the dropdown
        setFormData(prev => ({ ...prev, minimumAcademicResult: selectedType.datatype }));
      }
    } else {
      setSelectedDatatype("");
      setFormData(prev => ({ ...prev, minimumAcademicResult: "" }));
    }
  };

  // ========= HANDLE DATATYPE CHANGE =========
  const handleDatatypeChange = (selectedOption) => {
    const newValue = selectedOption ? selectedOption.value : "";
    setFormData((prev) => ({
      ...prev,
      minimumAcademicResult: newValue,
    }));
    if (errors.minimumAcademicResult) {
      setErrors((prev) => ({ ...prev, minimumAcademicResult: "" }));
    }
  };

  const customFilterOption = (option, inputValue) => {
    if (!inputValue) return true;
    return option.label.toLowerCase().startsWith(inputValue.toLowerCase());
  };

  // ========= VALIDATION =========
  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    if (!formData.factorForName.trim()) {
      newErrors.factorForName = "Factor For name is required";
      isValid = false;
    }

    if (!formData.studyAcademicResultGroup.trim()) {
      newErrors.studyAcademicResultGroup = "Academic Result Group is required";
      isValid = false;
    }

    if (!formData.minimumAcademicResultType.trim()) {
      newErrors.minimumAcademicResultType = "Minimum Academic Result Type is required";
      isValid = false;
    }

    if (!formData.minimumAcademicResult.trim()) {
      newErrors.minimumAcademicResult = "Minimum Academic Result is required";
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  // ========= SAVE =========
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validateForm()) return;

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
    const action = mode === "edit" ? studyFactorAcademicResultEdit : studyFactorAcademicResultAdd;

    dispatch(
      action(sendPayload, (response, error) => {
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
      })
    );
  };

  // ========= RESET =========
  const resetForm = () => {
    setFormData({
      uuid: "",
      factorForName: "",
      studyAcademicResultGroup: "",
      minimumAcademicResultType: "",
      minimumAcademicResult: "",
      description: "",
    });
    setSelectedDatatype("");
    setErrors({});
  };

  const onClose = () => {
    resetForm();
    setLoading(false);
    handleClose(false);
  };

  if (!show) return null;

  return (
    <div className="modal fade show common-ctl-popup" tabIndex={-1}>
      <div className="modal-dialog modal-lg modal-dialog-centered">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border-0 border-bottom">
            <h1 className="modal-title fs-5">
              {mode === "edit" ? "Edit Academic Result" : "Add Academic Result"}
            </h1>
            <button type="button" className="btn-close" onClick={onClose} />
          </div>

          <div className="modal-body ">
            <form onSubmit={handleSubmit}>
              <div className="row">
                {/* FACTOR FOR */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-sm">
                    Factor For <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={factorForData.map((o) => ({
                      value: o.uuid,
                      label: o.name,
                    }))}
                    value={
                      formData.factorForName
                        ? factorForData
                            .map((o) => ({ value: o.uuid, label: o.name }))
                            .find((opt) => opt.value === formData.factorForName)
                        : null
                    }
                    onChange={(selected) =>
                      handleChange({
                        target: {
                          name: "factorForName",
                          value: selected ? selected.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Factor For"
                    isClearable
                    className={`custom-select-container ${errors.factorForName ? "is-invalid" : ""}`}
                  />
                  {errors.factorForName && (
                    <div className="text-danger">{errors.factorForName}</div>
                  )}
                </div>

                {/* Academic Result Group */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-sm">
                    Study : Academic Result Group <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={academicResultGroupData.map((o) => ({
                      value: o.uuid,
                      label: o.name,
                    }))}
                    value={
                      formData.studyAcademicResultGroup
                        ? academicResultGroupData
                            .map((o) => ({ value: o.uuid, label: o.name }))
                            .find((opt) => opt.value === formData.studyAcademicResultGroup)
                        : null
                    }
                    onChange={(selected) =>
                      handleChange({
                        target: {
                          name: "studyAcademicResultGroup",
                          value: selected ? selected.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Academic Result Group"
                    isClearable
                    className={`custom-select-container ${errors.studyAcademicResultGroup ? "is-invalid" : ""}`}
                  />
                  {errors.studyAcademicResultGroup && (
                    <div className="text-danger">{errors.studyAcademicResultGroup}</div>
                  )}
                </div>

                {/* Minimum Academic Result */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-sm">
                    Minimum Academic Result Required <span className="text-danger">*</span>
                  </label>
                  <div className="row">
                    {/* Type Select */}
                    <div className="col-6">
                      <Select
                        options={academicResultTypeData.map((o) => ({
                          value: o.uuid,
                          label: o.name,
                          datatype: o.datatype,
                        }))}
                        value={
                          formData.minimumAcademicResultType
                            ? academicResultTypeData
                                .map((o) => ({
                                  value: o.uuid,
                                  label: o.name,
                                  datatype: o.datatype,
                                }))
                                .find((opt) => opt.value === formData.minimumAcademicResultType)
                            : null
                        }
                        onChange={handleAcademicResultTypeChange}
                        filterOption={customFilterOption}
                        placeholder="Select Academic Result Type"
                        isClearable
                        className={`custom-select-container ${errors.minimumAcademicResultType ? "is-invalid" : ""}`}
                      />
                      {errors.minimumAcademicResultType && (
                        <div className="text-danger">{errors.minimumAcademicResultType}</div>
                      )}
                    </div>

                    {/* Datatype Select */}
                    <div className="col-6">
                      <Select
                        options={datatypeOptions}
                        value={
                          formData.minimumAcademicResult
                            ? datatypeOptions.find(
                                (opt) => opt.value === formData.minimumAcademicResult
                              )
                            : null
                        }
                        onChange={handleDatatypeChange}
                        placeholder={selectedDatatype ? `Select datatype` : "Select type first"}
                        isClearable
                        isSearchable
                        isDisabled={!formData.minimumAcademicResultType}
                        className={`custom-select-container ${errors.minimumAcademicResult ? "is-invalid" : ""}`}
                        classNamePrefix="custom-select"
                      />
                      {formData.minimumAcademicResultType && !formData.minimumAcademicResult && (
                        <small className="text-muted mt-1 d-block">
                          Expected datatype from selected type: <strong>{selectedDatatype}</strong>
                        </small>
                      )}
                      {errors.minimumAcademicResult && (
                        <div className="text-danger">{errors.minimumAcademicResult}</div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Description */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-sm">Description</label>
                  <textarea
                    className="form-control"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    rows={4}
                    placeholder="Description"
                  />
                </div>

                {/* Buttons */}
                <div className="d-flex justify-content-center gap-3 mt-24">
                  <button
                    type="button"
                    onClick={onClose}
                    className="border border-danger-600 text-danger-600 px-16 py-4 radius-6"
                    disabled={loading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn comman-btn-color border border-primary-600 px-16 py-4 radius-6"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
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

export default AddEditStudyFactorAcademicResultModal;