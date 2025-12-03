import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";

const AddEditDocumentsModal = ({ show, handleClose, mode, rowData }) => {
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    documentCategory: "",
    documentName: "",
    attachments: [], // Use array for multi-file
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        documentCategory: rowData.documentCategory || "",
        documentName: rowData.documentName || "",
        attachment: rowData.attachment || null,
      });
    }
  }, [mode, rowData]);

  const resetForm = () => {
    setFormData({
      documentCategory: "",
      documentName: "",
      attachment: null,
    });
    setErrors({});
  };

  const handleInput = (e) => {
    const { name, value, files } = e.target;

    if (files) {
      // If it's a file input
      setFormData((prev) => ({
        ...prev,
        [name]: Array.from(files), // Convert FileList to array
      }));
    } else {
      // If it's a text input
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }

    // Clear errors if any
    setErrors((prev) => ({
      ...prev,
      [name]: "",
    }));
  };

  const validateForm = () => {
    let temp = {};
    let valid = true;

    if (!formData.documentCategory.trim()) {
      temp.documentCategory = "Document Category is required";
      valid = false;
    }
    if (!formData.documentName.trim()) {
      temp.documentName = "Document Name is required";
      valid = false;
    }

    if (!formData.attachments || formData.attachments.length === 0) {
      temp.attachments = "Attachments are required";
      valid = false;
    }

    setErrors(temp);
    return valid;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    const payload =
      mode === "edit" ? { uuid: rowData?.uuid, ...formData } : { ...formData };

    setLoading(true);

    setTimeout(() => {
      setLoading(false);
      toast.success(
        `Spouse Document ${mode === "edit" ? "updated" : "added"} successfully`
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
              {mode === "edit" ? "Edit Spouse Document" : "Add Spouse Document"}
            </h1>
            <button type="button" className="btn-close" onClick={onClose} />
          </div>

          {/* BODY */}
          <div className="modal-body p-24 pt-10">
            <form onSubmit={handleSubmit}>
              <div className="row gx-2">
                {/* Document Category */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Document Category <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="documentCategory"
                    value={formData.documentCategory}
                    onChange={handleInput}
                    placeholder="Enter document category"
                    className={`form-control radius-8 ${
                      errors.documentCategory ? "is-invalid" : ""
                    }`}
                  />
                  {errors.documentCategory && (
                    <div className="text-danger text-sm mt-1">
                      {errors.documentCategory}
                    </div>
                  )}
                </div>

                {/* Document Name */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Document Name <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="documentName"
                    value={formData.documentName}
                    onChange={handleInput}
                    placeholder="Enter document name"
                    className={`form-control radius-8 ${
                      errors.documentName ? "is-invalid" : ""
                    }`}
                  />
                  {errors.documentName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.documentName}
                    </div>
                  )}
                </div>

                {/* Attachment */}
                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Attachments <span className="text-danger">*</span>
                  </label>
                  <input
                    type="file"
                    name="attachments"
                    accept="image/*,application/pdf"
                    multiple
                    onChange={handleInput}
                    className={`form-control radius-8 ${
                      errors.attachments ? "is-invalid" : ""
                    }`}
                  />
                  {errors.attachments && (
                    <div className="text-danger text-sm mt-1">
                      {errors.attachments}
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

export default AddEditDocumentsModal;
