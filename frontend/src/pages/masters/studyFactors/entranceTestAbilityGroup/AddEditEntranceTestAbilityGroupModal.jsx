import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import { gapGroupAdd, gapGroupEdit } from "../../../../store/actions";

const AddEditEntranceTestAbilityGroupModal = ({
  show,
  handleClose,
  mode = "add",
  rowData = null,
}) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    uuid: "",
    gapGroupName: "",
    description: "",
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    gapGroupName: "",
    description: "",
  });

  // Populate form data when in edit mode
  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        uuid: rowData.uuid || "",
        gapGroupName: rowData.name || "",
        description: rowData.description || "",
      });
    } else {
      // Reset form when switching to add mode
      setFormData({
        uuid: "",
        gapGroupName: "",
        description: "",
      });
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
    if (!formData.gapGroupName.trim()) {
      newErrors.gapGroupName = "Name is required";
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
              name: formData.gapGroupName,
              description: formData.description,
            }
          : {
              name: formData.gapGroupName,
              description: formData.description,
            };

      setLoading(true);

      const action = mode === "edit" ? gapGroupEdit : gapGroupAdd;

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
      gapGroupName: "",
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
      aria-labelledby="factorForModalLabel"
      aria-hidden={!show}
    >
      <div
        className="modal-dialog modal-lg modal-dialog-centered"
        role="document"
      >
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="departmentModalLabel">
              {mode === "edit" ? "Edit Gap Group" : "Add Gap Group"}
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
                    Gap Group <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="gapGroupName"
                    value={formData.gapGroupName}
                    onChange={handleChange}
                    className={`form-control radius-8 ${
                      errors.gapGroupName ? "is-invalid" : ""
                    }`}
                    placeholder="Enter Factor For"
                  />
                  {errors.gapGroupName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.gapGroupName}
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

export default AddEditEntranceTestAbilityGroupModal;
