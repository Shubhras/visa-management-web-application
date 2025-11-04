import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";

import { accreditationNameEdit, accreditationNameAdd, countryDemoList, accreditationCategoryList } from '../../../../store/master/companyMasters/actions';
import { toast } from "react-toastify";

const AddEditAccrediationNameModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [countryListData, setCountryListData] = useState([]);
  const [acccrediationCategoryListData, setAccrediationCategoryListData] = useState([]);
  // Form state
  const [formData, setFormData] = useState({
    uuid: '',
    country: '',
    category: "",
    full_name: '',
    short_name: '',
    issuing_authority: '',
    valid_upto: '',
    description: '',
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    country: '',
    category: "",
    full_name: '',
    short_name: '',
    issuing_authority: '',
    valid_upto: '',
    description: '',
  });

  // Populate form data when in edit mode
  useEffect(() => {
    if (mode === 'edit' && rowData) {
      setFormData({
        uuid: rowData.uuid || '',
        country: rowData.country || '',
        category: rowData.category || '',
        full_name: rowData.full_name || '',
        short_name: rowData.short_name || '',
        issuing_authority: rowData.issuing_authority || '',
        valid_upto: rowData.valid_upto || '',
        description: rowData.description || '',
      });
    } else {
      // Reset form when switching to add mode
      setFormData({
        uuid: '',
        country: '',
        category: "",
        full_name: '',
        short_name: '',
        issuing_authority: '',
        valid_upto: '',
        description: '',
      });
    }
    fetchCountryListDemo();
    fetchAccreditationCategoryList();
  }, [mode, rowData, show]);
  const fetchCountryListDemo = () => {
    setLoading(true);
    const params = {
      page: 1,
      limit: 2000,
      search: '',
      status: '',
      sortBy: 'updated_at', // Field to sort by
      sortOrder: 'desc', // 'asc' or 'desc'
    };

    dispatch(countryDemoList(params, (response, error) => {
      setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {

        setCountryListData(response?.data || []);

      } else {

      }
    }));
  };
  const fetchAccreditationCategoryList = () => {
    setLoading(true);
    const params = {
      page: 1,
      limit: 2000,
      search: '',
      status: '',
      sortBy: 'updated_at', // Field to sort by
      sortOrder: 'desc', // 'asc' or 'desc'
    };

    dispatch(accreditationCategoryList(params, (response, error) => {
      setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {

        setAccrediationCategoryListData(response?.data || []);

      } else {

      }
    }));
  };
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

    // // country validation
    if (!formData.country) {
      newErrors.country = 'Country is required';
      isValid = false;
    }
    if (!formData.category) {
      newErrors.category = 'Accrediation category is required';
      isValid = false;
    }
    // Full Name validation
    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required';
      isValid = false;
    }
    // short Name validation
    if (!formData.short_name.trim()) {
      newErrors.short_name = 'Short name is required';
      isValid = false;
    }
    // Issuing authority validation
    if (!formData.issuing_authority.trim()) {
      newErrors.issuing_authority = 'Issuing authority is required';
      isValid = false;
    }
    // valid_upto validation
    if (!formData.valid_upto.trim()) {
      newErrors.valid_upto = 'Valid upto is required';
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
          country: formData.country,
          category: formData.category,
          full_name: formData.full_name,
          short_name: formData.short_name,
          issuing_authority: formData.issuing_authority,
          valid_upto: formData.valid_upto,
          description: formData.description,
        }
        : {
          country: formData.country,
          category: formData.category,
          full_name: formData.full_name,
          short_name: formData.short_name,
          issuing_authority: formData.issuing_authority,
          valid_upto: formData.valid_upto,
          description: formData.description,
        };

      setLoading(true);

      const action = mode === 'edit' ? accreditationNameEdit : accreditationNameAdd;

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
      country: '',
      category: '',
      full_name: '',
      short_name: '',
      issuing_authority: '',
      valid_upto: '',
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
      aria-labelledby="AccrediationNameModalLabel"
      aria-hidden={!show}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="AccrediationNameModalLabel">
              {mode === 'edit' ? 'Edit Accrediation Name' : 'Add Accrediation Name'}
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
                  <select
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
                  </select>
                  {errors.country && (
                    <div className="text-danger text-sm mt-1">
                      {errors.country}
                    </div>
                  )}
                </div>
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Accrediation Category <span className="text-danger">*</span>
                  </label>
                  <select
                    name="category"
                    value={formData.category}
                    onChange={handleChange}
                    className={`form-control form-select radius-8 ${errors.category ? 'is-invalid' : ''}`}
                  >
                    <option value="">Select Accrediation Category</option>
                    {acccrediationCategoryListData.map((option) => (
                      <option key={option.uuid} value={option.uuid}>
                        {option.name}
                      </option>
                    ))}
                  </select>
                  {errors.category && (
                    <div className="text-danger text-sm mt-1">
                      {errors.category}
                    </div>
                  )}
                </div>
                {/* Accrediation Full Name */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Accrediation Full Name <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.full_name ? 'is-invalid' : ''}`}
                    placeholder="Enter accrediation full name"
                  />
                  {errors.full_name && (
                    <div className="text-danger text-sm mt-1">
                      {errors.full_name}
                    </div>
                  )}
                </div>
                {/* Accrediation Short Name */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Accrediation Short Name <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="short_name"
                    value={formData.short_name}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.short_name ? 'is-invalid' : ''}`}
                    placeholder="Enter accrediation short name"
                  />
                  {errors.short_name && (
                    <div className="text-danger text-sm mt-1">
                      {errors.short_name}
                    </div>
                  )}
                </div>
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Accrediation Issuing Authority Name<span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="issuing_authority"
                    value={formData.issuing_authority}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.issuing_authority ? 'is-invalid' : ''}`}
                    placeholder="Enter accrediation issuing authority"
                  />
                  {errors.issuing_authority && (
                    <div className="text-danger text-sm mt-1">
                      {errors.issuing_authority}
                    </div>
                  )}
                </div>
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Accrediation Valid Upto<span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="valid_upto"
                    value={formData.valid_upto}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.valid_upto ? 'is-invalid' : ''}`}
                    placeholder="Enter accrediation Valid Upto"
                  />
                  {errors.valid_upto && (
                    <div className="text-danger text-sm mt-1">
                      {errors.valid_upto}
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

export default AddEditAccrediationNameModal;