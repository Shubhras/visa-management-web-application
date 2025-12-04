import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";
import Select from "react-select";

const AddEditActionModal = ({ show, handleClose, mode, rowData }) => {
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    action: null, // React Select value
    dueDate: "",
    time: "",
  });

  const [errors, setErrors] = useState({});

  const actionOptions = [
    { value: "call", label: "Call" },
    { value: "email", label: "Email" },
    { value: "sms", label: "SMS" },
    { value: "meeting", label: "Scheduled Meeting" },
  ];

  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        action:
          actionOptions.find((opt) => opt.value === rowData.action) || null,
        dueDate: rowData.dueDate || "",
        time: rowData.time || "",
      });
    }
  }, [mode, rowData]);

  const resetForm = () => {
    setFormData({ action: null, dueDate: "", time: "" });
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

    if (!formData.action) {
      temp.action = "Action is required";
      valid = false;
    }
    if (!formData.dueDate) {
      temp.dueDate = "Due Date is required";
      valid = false;
    }
    if (!formData.time) {
      temp.time = "Time is required";
      valid = false;
    }

    setErrors(temp);
    return valid;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (validateForm()) {
      const sendPayload = {
        action: formData.action?.value,
        dueDate: formData.dueDate,
        time: formData.time,
        ...(mode === "edit" && rowData?.uuid ? { uuid: rowData.uuid } : {}),
      };

      setLoading(true);

      // Simulate API call
      setTimeout(() => {
        setLoading(false);
        toast.success(
          `Action ${mode === "edit" ? "updated" : "added"} successfully`
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
        className="modal-dialog modal-lg modal-dialog-centered"
        role="document"
      >
        <div className="modal-content radius-16 bg-base">
          {/* HEADER */}
          <div className="modal-header py-16 px-20 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5">
              {mode === "edit" ? "Edit Action" : "Add Action"}
            </h1>
            <button type="button" className="btn-close" onClick={onClose} />
          </div>

          {/* BODY */}
          <div className="modal-body p-24 pt-10">
            <form onSubmit={handleSubmit}>
              <div className="row gx-2">
                {/* Action */}
                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Action <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={actionOptions}
                    value={formData.action}
                    onChange={(selected) =>
                      setFormData({ ...formData, action: selected })
                    }
                    placeholder="Select Action"
                  />
                  {errors.action && (
                    <div className="text-danger text-sm mt-1">
                      {errors.action}
                    </div>
                  )}
                </div>

                {/* Due Date */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Due Date <span className="text-danger">*</span>
                  </label>
                  <input
                    type="date"
                    name="dueDate"
                    value={formData.dueDate}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.dueDate ? "is-invalid" : ""
                    }`}
                  />
                  {errors.dueDate && (
                    <div className="text-danger text-sm mt-1">
                      {errors.dueDate}
                    </div>
                  )}
                </div>

                {/* Time */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Time <span className="text-danger">*</span>
                  </label>
                  <input
                    type="time"
                    name="time"
                    value={formData.time}
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.time ? "is-invalid" : ""
                    }`}
                  />
                  {errors.time && (
                    <div className="text-danger text-sm mt-1">
                      {errors.time}
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

export default AddEditActionModal;
