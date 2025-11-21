import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import { civilIdNameEdit, civilIdNameAdd } from '../../../../store/master/generalMasters/actions';

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
        name: rowData.civil_id_name || '',
        full_name: rowData.authority_full_name || '',
        short_name: rowData.authority_short_name || '',
        valid_upto_type: rowData.valid_type || '',
        valid_upto: rowData.valid_date || '',
        valid_upto_numeric: rowData.valid_duration_value || '',
        valid_upto_unit: rowData.valid_duration_unit || '',
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

    // If valid_upto_type changes, reset related fields
    if (name === 'valid_upto_type') {
      setFormData(prev => ({
        ...prev,
        [name]: value,
        valid_upto: '',
        valid_upto_numeric: '',
        valid_upto_unit: ''
      }));
      // Clear related errors when type changes
      setErrors(prev => ({
        ...prev,
        valid_upto: '',
        valid_upto_numeric: '',
        valid_upto_unit: ''
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }

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
    // Valid Upto Type specific validations
    if (formData.valid_upto_type === 'Date') {
      if (!formData.valid_upto) {
        newErrors.valid_upto = 'Date is required';
        isValid = false;
      }
    }

    if (formData.valid_upto_type === 'Valid Upto') {
      if (!formData.valid_upto_numeric) {
        newErrors.valid_upto_numeric = 'Numeric value is required';
        isValid = false;
      }
      if (!formData.valid_upto_unit) {
        newErrors.valid_upto_unit = 'Period is required';
        isValid = false;
      }
    }

    setErrors(newErrors);
    return isValid;
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();

    if (validateForm()) {
      // const sendPayload = mode === 'edit'
      //   ? {
      //     uuid: formData.uuid,
      //     civil_id_name: formData.name,
      //     authority_full_name: formData.full_name || null,
      //     authority_short_name: formData.short_name || null,
      //     valid_date: formData.valid_upto || null,
      //     valid_type: formData.valid_upto_type || null,
      //     valid_duration_value: formData.valid_upto_numeric || null,
      //     valid_duration_unit: formData.valid_upto_unit ? formData.valid_upto_unit : null,
      //     description: formData.description || null,
      //   }
      //   : {
      //     civil_id_name: formData.name,
      //     authority_full_name: formData.full_name || null,
      //     authority_short_name: formData.short_name || null,
      //     valid_date: formData.valid_upto || null,
      //     valid_type: formData.valid_upto_type || null,
      //     valid_duration_value: formData.valid_upto_numeric || null,
      //     valid_duration_unit: formData.valid_upto_unit ? formData.valid_upto_unit : null,
      //     description: formData.description || null,
      //   };

       const sendPayload = mode === 'edit'
        ? {
          uuid: formData.uuid,
          civil_id_name: formData.name,
          authority_full_name: formData.full_name || "",
          authority_short_name: formData.short_name || "",
          valid_date: formData.valid_upto || "",
          valid_type: formData.valid_upto_type || "",
          valid_duration_value: formData.valid_upto_numeric || null,
          valid_duration_unit: formData.valid_upto_unit ? formData.valid_upto_unit : "",
          description: formData.description || null,
        }
        : {
          civil_id_name: formData.name,
          authority_full_name: formData.full_name || "",
          authority_short_name: formData.short_name || "",
          valid_date: formData.valid_upto || "",
          valid_type: formData.valid_upto_type || "",
          valid_duration_value: formData.valid_upto_numeric || null,
          valid_duration_unit: formData.valid_upto_unit ? formData.valid_upto_unit : "",
          description: formData.description || "",
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
                {/* Valid Upto */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Civil ID Valid Upto
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
                        <option value="Permanent">Permanent</option>
                        <option value="Date">Date</option>
                        <option value="Valid Upto">Valid Upto</option>
                      </select>
                    </div>

                    {/* Show Date Picker if Date is selected */}
                    {formData.valid_upto_type === 'Date' && (
                      <div className="col-md-8">
                        <input
                          type="date"
                          name="valid_upto"
                          value={formData.valid_upto}
                          onChange={handleChange}
                          className={`form-control radius-8 ${errors.valid_upto ? 'is-invalid' : ''}`}
                        />
                        {errors.valid_upto && (
                          <div className="text-danger text-sm mt-1">
                            {errors.valid_upto}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Show Numeric and Unit fields if Valid Upto is selected */}
                    {formData.valid_upto_type === 'Valid Upto' && (
                      <>
                        <div className="col-md-4">
                          <input
                            type="number"
                            name="valid_upto_numeric"
                            value={formData.valid_upto_numeric}
                            onChange={handleChange}
                            className={`form-control radius-8 ${errors.valid_upto_numeric ? 'is-invalid' : ''}`}
                            placeholder="Enter number"
                          />
                          {errors.valid_upto_numeric && (
                            <div className="text-danger text-sm mt-1">
                              {errors.valid_upto_numeric}
                            </div>
                          )}
                        </div>
                        <div className="col-md-4">
                          <select
                            name="valid_upto_unit"
                            value={formData.valid_upto_unit}
                            onChange={handleChange}
                            className={`form-control form-select radius-8 ${errors.valid_upto_unit ? 'is-invalid' : ''}`}
                          >
                            <option value="">Select Period</option>
                            <option value="Weeks">Weeks</option>
                            <option value="Months">Months</option>
                            <option value="Years">Years</option>
                          </select>
                          {errors.valid_upto_unit && (
                            <div className="text-danger text-sm mt-1">
                              {errors.valid_upto_unit}
                            </div>
                          )}
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
                    className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-16 py-4 radius-6"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn comman-btn-color border border-primary-600 text-md px-16 py-4 radius-6"
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