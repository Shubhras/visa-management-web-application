import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";

const AddEditBusinessModal = ({ show, handleClose, mode, rowData }) => {
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    country: "",
    companyName: "",
    companyType: "",
    share: "",
    startDate: "",
    endDate: "",
    turnover: "",
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        country: rowData.country || "",
        companyName: rowData.companyName || "",
        companyType: rowData.companyType || "",
        share: rowData.share || "",
        startDate: rowData.startDate || "",
        endDate: rowData.endDate || "",
        turnover: rowData.turnover || "",
      });
    }
  }, [mode, rowData]);

  const resetForm = () => {
    setFormData({
      country: "",
      companyName: "",
      companyType: "",
      share: "",
      startDate: "",
      endDate: "",
      turnover: "",
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
      "country",
      "companyName",
      "companyType",
      "share",
      "startDate",
      "endDate",
      "turnover",
    ];

    requiredFields.forEach((field) => {
      if (!formData[field]?.trim()) {
        temp[field] = `${field.replace(/([A-Z])/g, " $1")} is required`;
        valid = false;
      }
    });

    if (formData.turnover && isNaN(formData.turnover)) {
      temp.turnover = "Turnover must be a number";
      valid = false;
    }

    setErrors(temp);
    return valid;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (validateForm()) {
      const sendPayload =
        mode === "edit"
          ? {
              uuid: rowData?.uuid,
              country: formData.country,
              companyName: formData.companyName,
              companyType: formData.companyType,
              share: formData.share,
              startDate: formData.startDate,
              endDate: formData.endDate,
              turnover: formData.turnover,
            }
          : {
              country: formData.country,
              companyName: formData.companyName,
              companyType: formData.companyType,
              share: formData.share,
              startDate: formData.startDate,
              endDate: formData.endDate,
              turnover: formData.turnover,
            };

      setLoading(true);

      // Simulate API call
      setTimeout(() => {
        setLoading(false);
        toast.success(
          `Business ${mode === "edit" ? "updated" : "added"} successfully`
        );
        resetForm();
        handleClose(true);
      }, 1000);
    }
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
                ? "Edit Business Details"
                : "Add Business Details"}
            </h1>
            <button type="button" className="btn-close" onClick={onClose} />
          </div>

          {/* BODY */}
          <div className="modal-body p-24 pt-10">
            <form onSubmit={handleSubmit}>
              <div className="row gx-2">
                {/* Country */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Country <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="country"
                    value={formData.country}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.country ? "is-invalid" : ""
                    }`}
                    placeholder="Enter country"
                  />
                  {errors.country && (
                    <div className="text-danger text-sm mt-1">
                      {errors.country}
                    </div>
                  )}
                </div>

                {/* Company Name */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Company Name <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="companyName"
                    value={formData.companyName}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.companyName ? "is-invalid" : ""
                    }`}
                    placeholder="Enter company name"
                  />
                  {errors.companyName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.companyName}
                    </div>
                  )}
                </div>

                {/* Company Type */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Company Type <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="companyType"
                    value={formData.companyType}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.companyType ? "is-invalid" : ""
                    }`}
                    placeholder="Enter company type"
                  />
                  {errors.companyType && (
                    <div className="text-danger text-sm mt-1">
                      {errors.companyType}
                    </div>
                  )}
                </div>

                {/* Share */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Your Share (%) <span className="text-danger">*</span>
                  </label>
                  <input
                    type="number"
                    name="share"
                    value={formData.share}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.share ? "is-invalid" : ""
                    }`}
                    placeholder="Enter share percentage"
                  />
                  {errors.share && (
                    <div className="text-danger text-sm mt-1">
                      {errors.share}
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

                {/* Turnover */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Turnover <span className="text-danger">*</span>
                  </label>
                  <input
                    type="number"
                    name="turnover"
                    value={formData.turnover}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.turnover ? "is-invalid" : ""
                    }`}
                    placeholder="Enter turnover"
                  />
                  {errors.turnover && (
                    <div className="text-danger text-sm mt-1">
                      {errors.turnover}
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

export default AddEditBusinessModal;
