import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";

const AddEditSpouseEducationModal = ({ show, handleClose, mode, rowData }) => {
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    educationLevel: "",
    duration: "",
    studyMainArea: "",
    eduType: "",
    startDate: "",
    endDate: "",
    result: "",
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        educationLevel: rowData.educationLevel || "",
        duration: rowData.duration || "",
        studyMainArea: rowData.studyMainArea || "",
        eduType: rowData.eduType || "",
        startDate: rowData.startDate || "",
        endDate: rowData.endDate || "",
        result: rowData.result || "",
      });
    }
  }, [mode, rowData]);

  const resetForm = () => {
    setFormData({
      educationLevel: "",
      duration: "",
      studyMainArea: "",
      eduType: "",
      startDate: "",
      endDate: "",
      result: "",
    });
    setErrors({});
  };

  const handleInput = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (errors[e.target.name]) {
      setErrors({ ...errors, [e.target.name]: "" });
    }
  };

  const validateForm = () => {
    let temp = {};
    let valid = true;

    const requiredFields = [
      "educationLevel",
      "duration",
      "studyMainArea",
      "eduType",
      "startDate",
      "endDate",
      "result",
    ];

    requiredFields.forEach((field) => {
      if (!formData[field]?.trim()) {
        temp[field] = `${field.replace(/([A-Z])/g, " $1")} is required`;
        valid = false;
      }
    });

    if (formData.result && isNaN(parseFloat(formData.result))) {
      temp.result = "Result must be numeric";
      valid = false;
    }

    setErrors(temp);
    return valid;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    const payload =
      mode === "edit"
        ? { uuid: rowData?.uuid, ...formData }
        : { ...formData };

    setLoading(true);

    setTimeout(() => {
      setLoading(false);
      toast.success(
        `Spouse Education ${
          mode === "edit" ? "updated" : "added"
        } successfully`
      );
      resetForm();
      handleClose(true);
    }, 1000);
  };

  const onClose = () => {
    resetForm();
    setLoading(false);
    handleClose(false);
  };

  if (!show) return null;

  return (
    <div
      className="modal fade show common-ctl-popup"
      tabIndex="-1"
      role="dialog"
      aria-hidden={!show}
    >
      <div
        className="modal-dialog modal-xl modal-dialog-centered"
        role="document"
      >
        <div className="modal-content radius-16 bg-base">
          {/* HEADER */}
          <div className="modal-header py-16 px-20 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5">
              {mode === "edit"
                ? "Edit Spouse Education Details"
                : "Add Spouse Education Details"}
            </h1>
            <button type="button" className="btn-close" onClick={onClose} />
          </div>

          {/* BODY */}
          <div className="modal-body p-24 pt-10">
            <form onSubmit={handleSubmit}>
              <div className="row gx-2">

                {/* Education Level */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Education Level <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="educationLevel"
                    value={formData.educationLevel}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.educationLevel ? "is-invalid" : ""
                    }`}
                    placeholder="Enter education level"
                  />
                  {errors.educationLevel && (
                    <div className="text-danger text-sm mt-1">
                      {errors.educationLevel}
                    </div>
                  )}
                </div>

                {/* Duration */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Duration (Months) <span className="text-danger">*</span>
                  </label>
                  <input
                    type="number"
                    name="duration"
                    value={formData.duration}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.duration ? "is-invalid" : ""
                    }`}
                    placeholder="Enter duration"
                  />
                  {errors.duration && (
                    <div className="text-danger text-sm mt-1">
                      {errors.duration}
                    </div>
                  )}
                </div>

                {/* Study Main Area */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Study Main Area <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="studyMainArea"
                    value={formData.studyMainArea}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.studyMainArea ? "is-invalid" : ""
                    }`}
                    placeholder="Enter study main area"
                  />
                  {errors.studyMainArea && (
                    <div className="text-danger text-sm mt-1">
                      {errors.studyMainArea}
                    </div>
                  )}
                </div>

                {/* Edu Type */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Education Type <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="eduType"
                    value={formData.eduType}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.eduType ? "is-invalid" : ""
                    }`}
                    placeholder="Enter education type"
                  />
                  {errors.eduType && (
                    <div className="text-danger text-sm mt-1">
                      {errors.eduType}
                    </div>
                  )}
                </div>

                {/* Start Date */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Start Date <span className="text-danger">*</span>
                  </label>
                  <input
                    type="date"
                    name="startDate"
                    value={formData.startDate}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.startDate ? "is-invalid" : ""
                    }`}
                  />
                  {errors.startDate && (
                    <div className="text-danger text-sm mt-1">
                      {errors.startDate}
                    </div>
                  )}
                </div>

                {/* End Date */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    End Date <span className="text-danger">*</span>
                  </label>
                  <input
                    type="date"
                    name="endDate"
                    value={formData.endDate}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.endDate ? "is-invalid" : ""
                    }`}
                  />
                  {errors.endDate && (
                    <div className="text-danger text-sm mt-1">
                      {errors.endDate}
                    </div>
                  )}
                </div>

                {/* Result */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Result (%) <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="result"
                    value={formData.result}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.result ? "is-invalid" : ""
                    }`}
                    placeholder="Enter result percentage"
                  />
                  {errors.result && (
                    <div className="text-danger text-sm mt-1">
                      {errors.result}
                    </div>
                  )}
                </div>

                {/* BUTTONS */}
                <div className="col-12 d-flex justify-content-center gap-3 mt-24">
                  <button
                    type="button"
                    onClick={onClose}
                    className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-16 py-6 radius-6"
                  >
                    Cancel
                  </button>

                  <button
                    type="submit"
                    className="btn comman-btn-color border border-primary-600 text-md px-16 py-6 radius-6"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Saving...
                      </>
                    ) : mode === "edit" ? (
                      "Update"
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

export default AddEditSpouseEducationModal;
