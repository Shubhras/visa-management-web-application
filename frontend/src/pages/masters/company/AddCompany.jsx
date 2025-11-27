import React, { useState } from 'react';
import { useDispatch } from "react-redux";
import { companyAdd } from '../../../store/master/actions';
import { toast } from "react-toastify";
const AddCompany = ({ show, handleClose }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  // IMPORTANT: All hooks must be declared BEFORE any conditional returns

  // Form state
  const [formData, setFormData] = useState({
    departmentName: '',
    description: '',
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    departmentName: '',
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

    // Department Name validation
    if (!formData.departmentName.trim()) {
      newErrors.departmentName = 'Department Name is required';
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
        name: formData.departmentName,
        description: formData.description,

      };
      setLoading(true);
      dispatch(companyAdd(sendPayload, (response, error) => {
        setLoading(false);
        if (error) {
          toast.error(error?.response?.data?.message || "server error");
        } else {
          if (response?.statusCode === 200 && response?.status === true) {
            toast.success(response?.message);
            setFormData({
              departmentName: '',
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
      departmentName: '',
      description: '',
    });
    setErrors({});
    handleClose();
    setLoading(false);
  };

  // NOW we can do the conditional return - AFTER all hooks
  if (!show) return null;

  return (
    <>
      <div
        className={`modal fade show common-ctl-popup`}
        tabIndex={-1}
        role="dialog"
        aria-labelledby="departmentModalLabel"
        aria-hidden={!show}
      >
        <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
          <div className="modal-content radius-16 bg-base">
            <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
              <h1 className="modal-title fs-5" id="departmentModalLabel">
                Add Company Type
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
                  {/* Department Name */}
                  <div className="col-12 mb-10">
                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                      Company Type <span className="text-danger">*</span>
                    </label>
                    <input
                      type="text"
                      name="departmentName"
                      value={formData.departmentName}
                      onChange={handleChange}
                      className={`form-control radius-8 ${errors.departmentName ? 'is-invalid' : ''}`}
                      placeholder="Enter company type"
                    />
                    {errors.departmentName && (
                      <div className="text-danger text-sm mt-1">
                        {errors.departmentName}
                      </div>
                    )}
                  </div>

                  {/* Description */}
                  <div className="col-12 mb-10">
                    <label
                      htmlFor="desc"
                      className="form-label fw-semibold text-primary-light text-sm mb-0"
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
                      className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-16 py-4 radius-6"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn comman-btn-color border border-primary-600 text-md px-16 py-4 radius-6"
                      disabled={loading}
                    >
                      {loading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
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
    </>
  );
};

export default AddCompany;