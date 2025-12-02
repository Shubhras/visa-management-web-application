import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";

const AddEditRelativesDetailsModal = ({
  show,
  handleClose,
  mode = "add",
  rowData = null,
}) => {
  const [loading, setLoading] = useState(false);

  // Form state according to Relatives Details table
  const [formData, setFormData] = useState({
    uuid: "",
    applicantType: "",
    country: "",
    state: "",
    city: "",
    relation: "",
    visaCategory: "",
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
  if (mode === "edit" && rowData) {
    setFormData({
      uuid: rowData.uuid || "",      // <-- use uuid, not id
      applicantType: rowData.applicantType || "",
      country: rowData.country || "",
      state: rowData.state || "",
      city: rowData.city || "",
      relation: rowData.relation || "",
      visaCategory: rowData.visaCategory || "",
    });
  } else {
    setFormData({
      uuid: "",
      applicantType: "",
      country: "",
      state: "",
      city: "",
      relation: "",
      visaCategory: "",
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

  // Validate form
  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    // Applicant Type
    if (!formData.applicantType.trim()) {
      newErrors.applicantType = "Applicant Type is required";
      isValid = false;
    }

    // Country
    if (!formData.country.trim()) {
      newErrors.country = "Country is required";
      isValid = false;
    }

    // State
    if (!formData.state.trim()) {
      newErrors.state = "State is required";
      isValid = false;
    }

    // City
    if (!formData.city.trim()) {
      newErrors.city = "City is required";
      isValid = false;
    }

    // Relation
    if (!formData.relation.trim()) {
      newErrors.relation = "Relation is required";
      isValid = false;
    }

    // Visa Category
    if (!formData.visaCategory.trim()) {
      newErrors.visaCategory = "Visa Category is required";
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
              applicantType: formData.applicantType,
              country: formData.country,
              state: formData.state,
              city: formData.city,
              relation: formData.relation,
              visaCategory: formData.visaCategory,
            }
          : {
              applicantType: formData.applicantType,
              country: formData.country,
              state: formData.state,
              city: formData.city,
              relation: formData.relation,
              visaCategory: formData.visaCategory,
            };

      setLoading(true);

      // Simulate API call
      setTimeout(() => {
        setLoading(false);
        toast.success(
          `Relative ${mode === "edit" ? "updated" : "added"} successfully`
        );
        resetForm();
        handleClose(true);
      }, 1000);
    }
  };

  const resetForm = () => {
    setFormData({
      uuid: "",
      applicantType: "",
      country: "",
      state: "",
      city: "",
      relation: "",
      visaCategory: "",
    });
    setErrors({});
  };

   // Handle modal close
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
      <div
        className="modal-dialog modal-xl modal-dialog-centered"
        role="document"
      >
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-20 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5">
              {mode === "edit" ? "Edit Relative" : "Add Relative"}
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
                    <div className="text-danger text-sm mt-1">
                      {errors.applicantType}
                    </div>
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
                    <div className="text-danger text-sm mt-1">
                      {errors.country}
                    </div>
                  )}
                </div>

                {/* State */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    State <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="state"
                    value={formData.state}
                    onChange={handleChange}
                    className={`form-control radius-8 ${
                      errors.state ? "is-invalid" : ""
                    }`}
                    placeholder="Enter state"
                  />
                  {errors.state && (
                    <div className="text-danger text-sm mt-1">
                      {errors.state}
                    </div>
                  )}
                </div>

                {/* City */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    City <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="city"
                    value={formData.city}
                    onChange={handleChange}
                    className={`form-control radius-8 ${
                      errors.city ? "is-invalid" : ""
                    }`}
                    placeholder="Enter city"
                  />
                  {errors.city && (
                    <div className="text-danger text-sm mt-1">
                      {errors.city}
                    </div>
                  )}
                </div>

                {/* Relation */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Relation <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="relation"
                    value={formData.relation}
                    onChange={handleChange}
                    className={`form-control radius-8 ${
                      errors.relation ? "is-invalid" : ""
                    }`}
                    placeholder="Enter relation"
                  />
                  {errors.relation && (
                    <div className="text-danger text-sm mt-1">
                      {errors.relation}
                    </div>
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
                    <div className="text-danger text-sm mt-1">
                      {errors.visaCategory}
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

export default AddEditRelativesDetailsModal;
