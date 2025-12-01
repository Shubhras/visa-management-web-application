import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";

const AddEditSpouseExperienceModal = ({ show, handleClose, mode, rowData }) => {
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    employerName: "",
    occupation: "",
    jobType: "",
    startDate: "",
    endDate: "",
    salary: "",
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        employerName: rowData.employerName || "",
        occupation: rowData.occupation || "",
        jobType: rowData.jobType || "",
        startDate: rowData.startDate || "",
        endDate: rowData.endDate || "",
        salary: rowData.salary || "",
      });
    }
  }, [mode, rowData]);

  const resetForm = () => {
    setFormData({
      employerName: "",
      occupation: "",
      jobType: "",
      startDate: "",
      endDate: "",
      salary: "",
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

    const required = [
      "employerName",
      "occupation",
      "jobType",
      "startDate",
      "endDate",
      "salary",
    ];

    required.forEach((field) => {
      if (!formData[field]?.trim()) {
        temp[field] = `${field.replace(/([A-Z])/g, " $1")} is required`;
        valid = false;
      }
    });

    if (formData.salary && isNaN(Number(formData.salary))) {
      temp.salary = "Salary must be a number";
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
        `Spouse Experience ${
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
                ? "Edit Spouse Experience Details"
                : "Add Spouse Experience Details"}
            </h1>
            <button type="button" className="btn-close" onClick={onClose} />
          </div>

          {/* BODY */}
          <div className="modal-body p-24 pt-10">
            <form onSubmit={handleSubmit}>
              <div className="row gx-2">

                {/* Employer Name */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Employer Name <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="employerName"
                    value={formData.employerName}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.employerName ? "is-invalid" : ""
                    }`}
                    placeholder="Enter employer name"
                  />
                  {errors.employerName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.employerName}
                    </div>
                  )}
                </div>

                {/* Occupation */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Occupation <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="occupation"
                    value={formData.occupation}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.occupation ? "is-invalid" : ""
                    }`}
                    placeholder="Enter occupation"
                  />
                  {errors.occupation && (
                    <div className="text-danger text-sm mt-1">
                      {errors.occupation}
                    </div>
                  )}
                </div>

                {/* Job Type */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Job Type <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="jobType"
                    value={formData.jobType}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.jobType ? "is-invalid" : ""
                    }`}
                    placeholder="Enter job type (Full-Time, Part-Time)"
                  />
                  {errors.jobType && (
                    <div className="text-danger text-sm mt-1">
                      {errors.jobType}
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

                {/* Salary */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Salary <span className="text-danger">*</span>
                  </label>
                  <input
                    type="number"
                    name="salary"
                    value={formData.salary}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.salary ? "is-invalid" : ""
                    }`}
                    placeholder="Enter salary"
                  />
                  {errors.salary && (
                    <div className="text-danger text-sm mt-1">
                      {errors.salary}
                    </div>
                  )}
                </div>

                {/* Buttons */}
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

export default AddEditSpouseExperienceModal;
