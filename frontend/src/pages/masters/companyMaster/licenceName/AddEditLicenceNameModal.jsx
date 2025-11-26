import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { licenceNameEdit, licenceNameAdd, countryDemoList } from '../../../../store/master/companyMasters/actions';
import { toast } from "react-toastify";
import Select from "react-select";
const AddEditLicenceNameModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [countryListData, setCountryListData] = useState([]);

  // Form state
  const [formData, setFormData] = useState({
    uuid: '',
    country: '',
    full_name: '',
    short_name: '',
    issuing_authority: '',
    valid_upto: '',
    valid_upto_type: '', // Permanent/Date/Valid Upto
    valid_upto_numeric: '',
    valid_upto_unit: '', // Weeks/Months/Year
    description: '',
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    country: '',
    full_name: '',
    short_name: '',
    issuing_authority: '',
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
        country: rowData.country || '',
        full_name: rowData.full_name || '',
        short_name: rowData.short_name || '',
        issuing_authority: rowData.issuing_authority || '',
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
        country: '',
        full_name: '',
        short_name: '',
        issuing_authority: '',
        valid_upto: '',
        valid_upto_type: '',
        valid_upto_numeric: '',
        valid_upto_unit: '',
        description: '',
      });
    }
    fetchCountryList();
  }, [mode, rowData, show]);


  const fetchCountryList = () => {
    //setLoading(true);
    const params = {
      page: 1,
      limit: 2000,
      search: '',
      status: '',
      sortBy: 'name',
      sortOrder: 'asc',
    };

    dispatch(countryDemoList(params, (response, error) => {
      setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {
        setCountryListData(response?.data || []);
      } else {

      }
    }));
  };

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
   // Handle Select changes for Country
  const handleSelectChange = (selectedOption) => {
    setFormData((prev) => ({
      ...prev,
      country: selectedOption ? selectedOption.value : ""
    }));
    if (errors.country) {
      setErrors((prev) => ({ ...prev, country: "" }));
    }
  };

    const customFilterOption = (option, inputValue) => {
    if (!inputValue) return true;
    return option.label.toLowerCase().startsWith(inputValue.toLowerCase());
  };


  // Validate form
  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    // country validation
    if (!formData.country) {
      newErrors.country = 'Country is required';
      isValid = false;
    }

    // Full Name validation
    if (!formData.full_name.trim()) {
      newErrors.full_name = 'License full name is required';
      isValid = false;
    }

    // short Name validation
    if (!formData.short_name.trim()) {
      newErrors.short_name = 'License short name is required';
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
      const sendPayload = mode === 'edit'
        ? {
          uuid: formData.uuid,
          country: formData.country,
          full_name: formData.full_name,
          short_name: formData.short_name,
          issuing_authority: formData.issuing_authority,

          valid_date: formData.valid_upto || null,
          valid_type: formData.valid_upto_type || "",
          valid_duration_value: formData.valid_upto_numeric || null,
          valid_duration_unit: formData.valid_upto_unit ? formData.valid_upto_unit : null,
          description: formData.description,
        }
        : {
          country: formData.country,
          full_name: formData.full_name,
          short_name: formData.short_name,
          issuing_authority: formData.issuing_authority,
          valid_date: formData.valid_upto || null,
          valid_type: formData.valid_upto_type || "",
          valid_duration_value: formData.valid_upto_numeric || null,
          valid_duration_unit: formData.valid_upto_unit ? formData.valid_upto_unit : null,
          description: formData.description,
        };

      setLoading(true);

      const action = mode === 'edit' ? licenceNameEdit : licenceNameAdd;

      dispatch(action(sendPayload, (response, error) => {
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
      }));
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      uuid: '',
      country: '',
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
    handleClose(false);
  };

  // Conditional return after all hooks
  if (!show) return null;

  return (
    <div
      className="modal fade show common-ctl-popup"
      tabIndex={-1}
      role="dialog"
      aria-labelledby="LicenceNameModalLabel"
      aria-hidden={!show}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="LicenceNameModalLabel">
              {mode === 'edit' ? 'Edit Licence Name' : 'Add Licence Name'}
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
                {/* Country */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Country <span className="text-danger">*</span>
                  </label>
                  {/* <select
                    name="country"
                    value={formData.country}
                    onChange={handleChange}
                    className={`form-control form-select radius-8 ${errors.country ? 'is-invalid' : ''}`}
                  >
                    <option value="">Select Country</option>
                    {countryListData.map((option) => (
                      <option key={option.uuid} value={option.uuid}>
                        {option.name}
                      </option>
                    ))}
                  </select> */}
                  <Select
                    options={countryListData.map((option) => ({
                      value: option.uuid,
                      label: option.name,
                    }))}
                    value={
                      formData.country
                        ? countryListData
                          .map((option) => ({ value: option.uuid, label: option.name }))
                          .find((opt) => opt.value === formData.country)
                        : null
                    }
                    onChange={handleSelectChange}
                    filterOption={customFilterOption} // Custom search from start
                    placeholder="Select Country"
                    isClearable
                    isSearchable
                  />
                  {errors.country && (
                    <div className="text-danger text-sm mt-1">
                      {errors.country}
                    </div>
                  )}
                </div>

                {/* LicenceName */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    License Full Name<span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.full_name ? 'is-invalid' : ''}`}
                    placeholder="Enter licence full name"
                  />
                  {errors.full_name && (
                    <div className="text-danger text-sm mt-1">
                      {errors.full_name}
                    </div>
                  )}
                </div>

                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    License Short Name<span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="short_name"
                    value={formData.short_name}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.short_name ? 'is-invalid' : ''}`}
                    placeholder="Enter licence short name"
                  />
                  {errors.short_name && (
                    <div className="text-danger text-sm mt-1">
                      {errors.short_name}
                    </div>
                  )}
                </div>
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    License Issuing Authority Name
                  </label>
                  <input
                    type="text"
                    name="issuing_authority"
                    value={formData.issuing_authority}
                    onChange={handleChange}
                    className={`form-control radius-8`}
                    placeholder="Enter licence issuing authority name"
                  />
                </div>
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    License Valid Upto
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
                    {(formData.valid_upto_type === 'Valid Upto') && (
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
  );
};

export default AddEditLicenceNameModal;