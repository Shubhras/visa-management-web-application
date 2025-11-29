import React, { useState, useEffect } from "react";
import { toast } from "react-toastify";

const AddEditRefusedModal = ({
  show,
  handleClose,
  mode = "add",
  rowData = null,
}) => {
  const [loading, setLoading] = useState(false);

  // Fields based on refusedColumns
  const [formData, setFormData] = useState({
    uuid: "",
    applicantType: "",
    country: "",
    visaCategory: "",
    refuseDate: "",
    reason: "",
  });

  const [errors, setErrors] = useState({});

  // Load data in edit mode
  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        uuid: rowData.uuid || "",
        applicantType: rowData.applicantType || "",
        country: rowData.country || "",
        visaCategory: rowData.visaCategory || "",
        refuseDate: rowData.refuseDate || "",
        reason: rowData.reason || "",
      });
    } else {
      setFormData({
        uuid: "",
        applicantType: "",
        country: "",
        visaCategory: "",
        refuseDate: "",
        reason: "",
      });
    }
  }, [mode, rowData, show]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  // Validate required fields
  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    const requiredFields = [
      "applicantType",
      "country",
      "visaCategory",
      "refuseDate",
      "reason",
    ];

    requiredFields.forEach((field) => {
      if (!formData[field]?.trim()) {
        newErrors[field] = `${field.split(/(?=[A-Z])/).join(" ")} is required`;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  };

  // Submit handler
const handleSubmit = (e) => {
  e.preventDefault();

  if (validateForm()) {
    const sendPayload =
      mode === "edit"
        ? {
            uuid: formData.uuid,
            applicantType: formData.applicantType,
            country: formData.country,
            visaCategory: formData.visaCategory,
            refuseDate: formData.refuseDate,
            reason: formData.reason,
          }
        : {
            applicantType: formData.applicantType,
            country: formData.country,
            visaCategory: formData.visaCategory,
            refuseDate: formData.refuseDate,
            reason: formData.reason,
          };

    setLoading(true);

    // Simulate API
    setTimeout(() => {
      setLoading(false);
      toast.success(
        `Refused record ${mode === "edit" ? "updated" : "added"} successfully`
      );

      resetForm();
      handleClose(true);
    }, 1000);
  }
};

  // Reset form
  const resetForm = () => {
    setFormData({
      uuid: "",
      applicantType: "",
      country: "",
      visaCategory: "",
      refuseDate: "",
      reason: "",
    });
    setErrors({});
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
      tabIndex={-1}
      role="dialog"
      aria-hidden={!show}
    >
      <div className="modal-dialog modal-xl modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-20 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5">
              {mode === "edit" ? "Edit Refused Details" : "Add Refused Details"}
            </h1>
            <button type="button" className="btn-close" onClick={onClose} />
          </div>

          <div className="modal-body p-24 pt-10">
            <form onSubmit={handleSubmit}>
              <div className="row gx-2">

                {/* Applicant Type */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Applicant Type <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="applicantType"
                    value={formData.applicantType}
                    onChange={handleChange}
                    className={`form-control radius-8 ${
                      errors.applicantType ? "is-invalid" : ""
                    }`}
                    placeholder="Enter applicant type"
                  />
                  {errors.applicantType && (
                    <div className="text-danger text-sm mt-1">{errors.applicantType}</div>
                  )}
                </div>

                {/* Country */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Country <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="country"
                    value={formData.country}
                    onChange={handleChange}
                    className={`form-control radius-8 ${
                      errors.country ? "is-invalid" : ""
                    }`}
                    placeholder="Enter country"
                  />
                  {errors.country && (
                    <div className="text-danger text-sm mt-1">{errors.country}</div>
                  )}
                </div>

                {/* Visa Category */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Visa Category <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="visaCategory"
                    value={formData.visaCategory}
                    onChange={handleChange}
                    className={`form-control radius-8 ${
                      errors.visaCategory ? "is-invalid" : ""
                    }`}
                    placeholder="Enter visa category"
                  />
                  {errors.visaCategory && (
                    <div className="text-danger text-sm mt-1">{errors.visaCategory}</div>
                  )}
                </div>

                {/* Refuse Date */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Refuse Date <span className="text-danger">*</span>
                  </label>
                  <input
                    type="date"
                    name="refuseDate"
                    value={formData.refuseDate}
                    onChange={handleChange}
                    className={`form-control radius-8 ${
                      errors.refuseDate ? "is-invalid" : ""
                    }`}
                  />
                  {errors.refuseDate && (
                    <div className="text-danger text-sm mt-1">{errors.refuseDate}</div>
                  )}
                </div>

                {/* Reason */}
                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Reason <span className="text-danger">*</span>
                  </label>
                  <textarea
                    name="reason"
                    value={formData.reason}
                    onChange={handleChange}
                    className={`form-control radius-8 ${
                      errors.reason ? "is-invalid" : ""
                    }`}
                    placeholder="Enter refusal reason"
                  />
                  {errors.reason && (
                    <div className="text-danger text-sm mt-1">{errors.reason}</div>
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

export default AddEditRefusedModal;
