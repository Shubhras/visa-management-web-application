import React, { useState } from 'react'
import { Icon } from '@iconify/react/dist/iconify.js';
import { Link } from 'react-router-dom';

const AddLeads = ({ show, handleClose }) => {
  // IMPORTANT: All hooks must be declared BEFORE any conditional returns
  
  // Form state
  const [formData, setFormData] = useState({
    leadName: '',
    description: '',
    // status: 'active'
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    leadName: '',
    description: '',
    // status: ''
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
    if (!formData.leadName.trim()) {
      newErrors.leadName = 'Lead Name is required';
      isValid = false;
    }

    // Description validation
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
      isValid = false;
    }

    // Status validation
    // if (!formData.status) {
    //   newErrors.status = 'Please select a status';
    //   isValid = false;
    // }

    setErrors(newErrors);
    return isValid;
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      // Form is valid, proceed with submission
      console.log('Form submitted:', formData);
      
      // Add your API call or form submission logic here
      // Example: await api.AddLeads(formData);
      
      // Reset form and close modal
      setFormData({
        leadName: '',
        description: '',
        // status: 'active'
      });
      setErrors({});
      handleClose();
    }
  };

  // Handle modal close
  const onClose = () => {
    // Reset form and errors
    setFormData({
      leadName: '',
      description: '',
      // status: 'active'
    });
    setErrors({});
    handleClose();
  };

  // NOW we can do the conditional return - AFTER all hooks
  if (!show) return null;

  return (
    <>
      <div
        className={`modal fade show`}
        style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}
        tabIndex={-1}
        role="dialog"
        aria-labelledby="departmentModalLabel"
        aria-hidden={!show}
      >
        <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
          <div className="modal-content radius-16 bg-base">
            <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
              <h1 className="modal-title fs-5" id="departmentModalLabel">
                Add New Lead
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
                  {/*  Name */}
                  <div className="col-12 mb-20">
                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                       Name <span className="text-danger">*</span>
                    </label>
                    <input
                      type="text"
                      name="leadName"
                      value={formData.leadName}
                      onChange={handleChange}
                      className={`form-control radius-8 ${errors.leadName ? 'is-invalid' : ''}`}
                      placeholder="Enter Name"
                    />
                    {errors.leadName && (
                      <div className="text-danger text-sm mt-1">
                        {errors.leadName}
                      </div>
                    )}
                  </div>

                  {/* Description */}
                  <div className="col-12 mb-20">
                    <label
                      htmlFor="desc"
                      className="form-label fw-semibold text-primary-light text-sm mb-8"
                    >
                      Description <span className="text-danger">*</span>
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
                    {errors.description && (
                      <div className="text-danger text-sm mt-1">
                        {errors.description}
                      </div>
                    )}
                  </div>

                  {/* Status */}
                  {/* <div className="col-12 mb-20">
                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                      Status <span className="text-danger">*</span>
                    </label>
                    <div className="d-flex align-items-center flex-wrap gap-28">
                      <div className="form-check checked-success d-flex align-items-center gap-2">
                        <input
                          className="form-check-input"
                          type="radio"
                          name="status"
                          id="active"
                          value="active"
                          checked={formData.status === 'active'}
                          onChange={handleChange}
                        />
                        <label
                          className="form-check-label fw-medium text-secondary-light text-sm d-flex align-items-center gap-1"
                          htmlFor="active"
                        >
                          <span className="w-8-px h-8-px bg-success-600 rounded-circle" />
                          Active
                        </label>
                      </div>

                      <div className="form-check checked-danger d-flex align-items-center gap-2">
                        <input
                          className="form-check-input"
                          type="radio"
                          name="status"
                          id="inactive"
                          value="inactive"
                          checked={formData.status === 'inactive'}
                          onChange={handleChange}
                        />
                        <label
                          className="form-check-label fw-medium text-secondary-light text-sm d-flex align-items-center gap-1"
                          htmlFor="inactive"
                        >
                          <span className="w-8-px h-8-px bg-danger-600 rounded-circle" />
                          Inactive
                        </label>
                      </div>
                    </div>
                    {errors.status && (
                      <div className="text-danger text-sm mt-1">
                        {errors.status}
                      </div>
                    )}
                  </div> */}

                  {/* Buttons */}
                  <div className="d-flex align-items-center justify-content-center gap-3 mt-24">
                    <button
                      type="button"
                      onClick={onClose}
                      className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-40 py-11 radius-8"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn btn-primary border border-primary-600 text-md px-48 py-12 radius-8"
                    >
                      Save
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

export default AddLeads;