import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";

const AddEditEntranceTestModal = ({
  show,
  handleClose,
  mode = "add",
  rowData = null,
}) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);

  // Form state with only specified fields
  const [formData, setFormData] = useState({
    uuid: "",
    entranceTestName: "",
    module01: "",
    module02: "",
    module03: "",
    module04: "",
    total: "",
    testDate: "",
  });

  const [errors, setErrors] = useState({
    entranceTestName: "",
    module01: "",
    module02: "",
    module03: "",
    module04: "",
    total: "",
    testDate: "",
  });

  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        uuid: rowData.uuid || "",
        entranceTestName: rowData.entranceTestName || "",
        module01: rowData.module01 || "",
        module02: rowData.module02 || "",
        module03: rowData.module03 || "",
        module04: rowData.module04 || "",
        total: rowData.total || "",
        testDate: rowData.testDate || "",
      });
    } else {
      setFormData({
        uuid: "",
        entranceTestName: "",
        module01: "",
        module02: "",
        module03: "",
        module04: "",
        total: "",
        testDate: "",
      });
    }
  }, [mode, rowData, show]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

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
    if (!formData.entranceTestName.trim()) {
      newErrors.entranceTestName = "Entrance Test Name is required";
      isValid = false;
    }

    if (!formData.module01.trim()) {
      newErrors.module01 = "Module 01 score is required";
      isValid = false;
    }

    if (!formData.module02.trim()) {
      newErrors.module02 = "Module 02 score is required";
      isValid = false;
    }

    if (!formData.module03.trim()) {
      newErrors.module03 = "Module 03 score is required";
      isValid = false;
    }

    if (!formData.module04.trim()) {
      newErrors.module04 = "Module 04 score is required";
      isValid = false;
    }

    if (!formData.total.trim()) {
      newErrors.total = "Total score is required";
      isValid = false;
    }

    if (!formData.testDate.trim()) {
      newErrors.testDate = "Test Date is required";
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
              entranceTestName: formData.entranceTestName,
              module01: formData.module01,
              module02: formData.module02,
              module03: formData.module03,
              module04: formData.module04,
              total: formData.total,
              testDate: formData.testDate,
            }
          : {
              entranceTestName: formData.entranceTestName,
              module01: formData.module01,
              module02: formData.module02,
              module03: formData.module03,
              module04: formData.module04,
              total: formData.total,
              testDate: formData.testDate,
            };

      setLoading(true);

      // For now, just close the modal
      setTimeout(() => {
        setLoading(false);
        toast.success(
          `Education ${mode === "edit" ? "updated" : "added"} successfully`
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
      entranceTestName: "",
      module01: "",
      module02: "",
      module03: "",
      module04: "",
      total: "",
      testDate: "",
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
      aria-labelledby="educationModalLabel"
      aria-hidden={!show}
    >
      <div
        className="modal-dialog modal-xl modal-dialog-centered"
        role="document"
      >
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-20 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="educationModalLabel">
              {mode === "edit" ? "Edit Education" : "Add Education"}
            </h1>
            <button
              type="button"
              className="btn-close"
              onClick={onClose}
              aria-label="Close"
            />
          </div>

          <div className="modal-body p-24 pt-10">
            <form onSubmit={handleSubmit}>
              <div className="row">
                {/* Entrance Test Name */}
                <div className="col-12">
                  <div className="row gx-2">
                    <div className="col-6 mb-3">
                      <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                        Entrance Test Name{" "}
                        <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        name="entranceTestName"
                        value={formData.entranceTestName}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.entranceTestName ? "is-invalid" : ""
                        }`}
                        placeholder="Enter entrance test name"
                      />
                      {errors.entranceTestName && (
                        <div className="text-danger text-sm mt-1">
                          {errors.entranceTestName}
                        </div>
                      )}
                    </div>

                    {/* Module 01 */}
                    <div className="col-6 mb-3">
                      <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                        Module 01 <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        name="module01"
                        value={formData.module01}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.module01 ? "is-invalid" : ""
                        }`}
                        placeholder="Enter module 01 score"
                      />
                      {errors.module01 && (
                        <div className="text-danger text-sm mt-1">
                          {errors.module01}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Module 02 + Module 03 */}
                <div className="col-12">
                  <div className="row gx-2">
                    <div className="col-6 mb-3">
                      <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                        Module 02 <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        name="module02"
                        value={formData.module02}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.module02 ? "is-invalid" : ""
                        }`}
                        placeholder="Enter module 02 score"
                      />
                      {errors.module02 && (
                        <div className="text-danger text-sm mt-1">
                          {errors.module02}
                        </div>
                      )}
                    </div>

                    <div className="col-6 mb-3">
                      <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                        Module 03 <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        name="module03"
                        value={formData.module03}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.module03 ? "is-invalid" : ""
                        }`}
                        placeholder="Enter module 03 score"
                      />
                      {errors.module03 && (
                        <div className="text-danger text-sm mt-1">
                          {errors.module03}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Module 04 + Total */}
                <div className="col-12">
                  <div className="row gx-2">
                    <div className="col-6 mb-3">
                      <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                        Module 04 <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        name="module04"
                        value={formData.module04}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.module04 ? "is-invalid" : ""
                        }`}
                        placeholder="Enter module 04 score"
                      />
                      {errors.module04 && (
                        <div className="text-danger text-sm mt-1">
                          {errors.module04}
                        </div>
                      )}
                    </div>

                    <div className="col-6 mb-3">
                      <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                        Total <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        name="total"
                        value={formData.total}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.total ? "is-invalid" : ""
                        }`}
                        placeholder="Enter total score"
                      />
                      {errors.total && (
                        <div className="text-danger text-sm mt-1">
                          {errors.total}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Test Date (ALREADY IN YOUR CODE, KEEPING SAME STYLE) */}
                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                    Test Date <span className="text-danger">*</span>
                  </label>
                  <div className="row gx-2">
                    <div className="col-6">
                      <input
                        type="date"
                        name="testDate"
                        value={formData.testDate}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.testDate ? "is-invalid" : ""
                        }`}
                        placeholder="Test Date"
                      />
                      {errors.testDate && (
                        <div className="text-danger text-sm mt-1">
                          {errors.testDate}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Buttons */}
                <div className="col-12">
                  <div className="d-flex align-items-center justify-content-center gap-3 mt-24">
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
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddEditEntranceTestModal;
