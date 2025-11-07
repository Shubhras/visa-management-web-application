import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import {civilIdNameEdit, civilIdNameAdd } from '../../../../store/master/generalMasters/actions';

const AddEditCivilIDNameModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    uuid: '',
    name: '',
    full_name: '',
    short_name: '',
    valid_upto: '',
    valid_upto_type: '', // Permanent/Date/Valid Upto
    valid_upto_numeric: '',
    valid_upto_unit: '', // Weeks/Months/Year
    description: '',
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    name: '',
    full_name: '',
    short_name: '',
    valid_upto: '',
    valid_upto_type: '',
    valid_upto_numeric: '',
    valid_upto_unit: '',
    description: '',
  });

  // Populate form data when in edit mode
  useEffect(() => {
    if (mode === 'edit' && rowData) {
      setFormData({
        uuid: rowData.uuid || '',
        name: rowData.name || '',
        full_name: rowData.full_name || '',
        short_name: rowData.short_name || '',
        valid_upto: rowData.valid_upto || '',
        valid_upto_type: rowData.valid_upto_type || '',
        valid_upto_numeric: rowData.valid_upto_numeric || '',
        valid_upto_unit: rowData.valid_upto_unit || '',
        description: rowData.description || '',
      });
    } else {
      // Reset form when switching to add mode
      setFormData({
        uuid: '',
        name: '',
        full_name: '',
        short_name: '',
        valid_upto: '',
        valid_upto_type: '',
        valid_upto_numeric: '',
        valid_upto_unit: '',
        description: '',
      });
    }
  }, [mode, rowData, show]);

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

    // country validation
    if (!formData.name) {
      newErrors.name = 'Civil ID name is required';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();

    if (validateForm()) {
      const sendPayload = mode === 'edit'
        ? {
          uuid: formData.uuid,
          civil_id_name: formData.civil_id_name,
          authority_full_name: formData.authority_full_name,
          authority_short_name: formData.authority_short_name,
          valid_upto: formData.valid_upto,
          valid_type: formData.valid_upto_type?.toUpperCase() || '',
          valid_duration_value: formData.valid_upto_numeric,
          valid_duration_unit: formData.valid_upto_unit,
          description: formData.description,
        }
        : {
          civil_id_name: formData.name,
          authority_full_name: formData.full_name,
          authority_short_name: formData.short_name,
          valid_upto: formData.valid_upto,
          valid_type: formData.valid_upto_type?.toUpperCase() || '',
          valid_duration_value: formData.valid_upto_numeric,
          valid_duration_unit: formData.valid_upto_unit,
          description: formData.description,
        };

      setLoading(true);

      const action = mode === 'edit' ? civilIdNameEdit : civilIdNameAdd;

      dispatch(action(sendPayload, (response, error) => {
        setLoading(false);
        if (error) {
          toast.error(error?.response?.data?.message || "Server error");
        } else {
          if (response?.statusCode === 200 && response?.status === true) {
            toast.success(response?.message);
            resetForm();
            handleClose();
          } else {
            toast.error("Something went wrong.");
          }
        }
      }));
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      uuid: '',
      name: '',
      full_name: '',
      short_name: '',
      issuing_authority: '',
      valid_upto: '',
      valid_upto_type: '',
      valid_upto_numeric: '',
      valid_upto_unit: '',
      description: '',
    });
    setErrors({});
  };

  // Handle modal close
  const onClose = () => {
    resetForm();
    setLoading(false);
    handleClose();
  };

  // Conditional return after all hooks
  if (!show) return null;

  return (
    <div
      className="modal fade show common-ctl-popup"
      tabIndex={-1}
      role="dialog"
      aria-labelledby="CivilIDNameModalLabel"
      aria-hidden={!show}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="CivilIDNameModalLabel">
              {mode === 'edit' ? 'Edit Civil ID Name' : 'Add Civil ID Name'}
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

                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Civil ID Name<span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.name ? 'is-invalid' : ''}`}
                    placeholder="Enter civil ID name"
                  />
                  {errors.name && (
                    <div className="text-danger text-sm mt-1">
                      {errors.name}
                    </div>
                  )}
                </div>
            
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Authority Full Name
                  </label>
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    className={`form-control radius-8`}
                    placeholder="Enter authority full name"
                  />
                </div>

                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                   Authority Short Name
                  </label>
                  <input
                    type="text"
                    name="short_name"
                    value={formData.short_name}
                    onChange={handleChange}
                    className={`form-control radius-8`}
                    placeholder="Enter authority short name"
                  />
                </div>
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                   ID Valid Duration
                  </label>
                  <div className="row g-2">
                    {/* Type Dropdown */}
                    <div className="col-md-4">
                      <select
                        name="valid_upto_type"
                        value={formData.valid_upto_type}
                        onChange={handleChange}
                        className="form-control form-select radius-8"
                      >
                        <option value="">Select Type</option>
                        <option value="permanent">Permanent</option>
                        <option value="date">Date</option>
                        <option value="valid_upto">Valid Upto</option>
                      </select>
                    </div>
                    {/* Show Date Picker if Date is selected */}
                    {formData.valid_upto_type === 'date' && (
                      <div className="col-md-8">
                        <input
                          type="date"
                          name="valid_upto"
                          value={formData.valid_upto}
                          onChange={handleChange}
                          className="form-control radius-8"
                        />
                      </div>
                    )}
                    {/* Show Numeric and Unit fields if Permanent or Valid Upto is selected */}
                    {(formData.valid_upto_type === 'valid_upto') && (
                      <>
                        <div className="col-md-4">
                          <input
                            type="number"
                            name="valid_upto_numeric"
                            value={formData.valid_upto_numeric}
                            onChange={handleChange}
                            className="form-control radius-8"
                            placeholder="Enter number"
                          />
                        </div>
                        <div className="col-md-4">
                          <select
                            name="valid_upto_unit"
                            value={formData.valid_upto_unit}
                            onChange={handleChange}
                            className="form-control form-select radius-8"
                          >
                            <option value="">Select Period</option>
                            <option value="weeks">Weeks</option>
                            <option value="months">Months</option>
                            <option value="years">Years</option>
                          </select>
                        </div>
                      </>
                    )}
                  </div>
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
                    {loading ? 'Saving...' : 'Save'}
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

export default AddEditCivilIDNameModal;