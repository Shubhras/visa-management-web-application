import React, { useState } from 'react';
import { useDispatch } from "react-redux";
import { stakeholderCategoryAdd } from '../../../store/master/actions';
import { toast } from "react-toastify";
const AddStakeholderCategories = ({ show, handleClose }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  // IMPORTANT: All hooks must be declared BEFORE any conditional returns

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    name: '',
    description: '',
  });

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    // Name validation
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
      isValid = false;
    }
    setErrors(newErrors);
    return isValid;
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();

    if (validateForm()) {
      const sendPayload = {
        name: formData.name,
        description: formData.description,

      };
      setLoading(true);
      dispatch(stakeholderCategoryAdd(sendPayload, (response, error) => {
        setLoading(false);
        if (error) {
          toast.error(error?.response?.data?.message || "server error");
        } else {
          if (response?.statusCode === 200 && response?.status === true) {
            toast.success(response?.message);
            setFormData({
              name: '',
              description: '',
            });
            setErrors({});
            handleClose();
          } else {
            toast.error("Something went wrong.");
          }
        }
      }));
    }
  };

  // Handle modal close
  const onClose = () => {
    // Reset form and errors
    setFormData({
      name: '',
      description: '',
    });
    setErrors({});
    handleClose();
     setLoading(false);
  };
 const handleBackdropClick = (e) => {
    // Only close if clicking the backdrop itself, not the modal content
    if (e.target === e.currentTarget) {
      onClose();
    }
  };
  // NOW we can do the conditional return - AFTER all hooks
  if (!show) return null;

  return (
    <>
      <div
        className={`modal fade show common-ctl-popup`}
        tabIndex={-1}
        role="dialog"
        aria-labelledby="stakeholderModalLabel"
        aria-hidden={!show}
        onClick={handleBackdropClick}
      >
        <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
          <div className="modal-content radius-16 bg-base">
            <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
              <h1 className="modal-title fs-5" id="stakeholderModalLabel">
                Add Stakeholder Categories
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
                  {/* Name */}
                  <div className="col-12 mb-20">
                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                      Name <span className="text-danger">*</span>
                    </label>
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      className={`form-control radius-8 ${errors.name ? 'is-invalid' : ''}`}
                      placeholder="Enter name"
                    />
                    {errors.name && (
                      <div className="text-danger text-sm mt-1">
                        {errors.name}
                      </div>
                    )}
                  </div>

                  {/* Description */}
                  <div className="col-12 mb-20">
                    <label
                      htmlFor="desc"
                      className="form-label fw-semibold text-primary-light text-sm mb-8"
                    >
                      Description <span className="text-danger"></span>
                    </label>
                    <textarea
                      className={`form-control ${errors.description ? 'is-invalid' : ''}`}
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
                      className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-40 py-6 radius-8"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn comman-btn-color border border-primary-600 text-md px-40 py-6 radius-8"
                       disabled={loading}
                    >
                       {loading ? "Save" : "Save"}
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default AddStakeholderCategories;