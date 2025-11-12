import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import Select from "react-select";
import { stateAdd, stateEdit } from '../../../../store/master/generalMasters/actions';
import { countryDemoList } from '../../../../store/master/companyMasters/actions';

const AddEditStateModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [countryListData, setCountryListData] = useState([]);

  // Form state
  const [formData, setFormData] = useState({
    uuid: '',
    country: '',
    name: '',
    short_name: '',
    stateTerritory: '',
    description: '',
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    country: '',
    name: '',
    short_name: '',
    stateTerritory: '',
    description: '',
  });

  // Populate form data when in edit mode
  useEffect(() => {
    if (mode === 'edit' && rowData) {
      setFormData({
        uuid: rowData.uuid || '',
        country: rowData.country_id || '',
        name: rowData.stateName || '',
        short_name: rowData.stateshortName || '',
        stateTerritory: rowData.state_display || '',//formData.state === "STATE" ? "State" : "Territory" || '',
        description: rowData.description || '',
      });
    } else {
      resetForm();
    }
    fetchCountryList();
  }, [mode, rowData, show]);

  // Fetch country list
  const fetchCountryList = () => {
    setLoading(true);
    const params = {
      page: 1,
      limit: 2000,
      search: '',
      status: '',
      sortBy: 'updated_at',
      sortOrder: 'desc',
    };

    dispatch(countryDemoList(params, (response, error) => {
      setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {
        setCountryListData(response?.data || []);
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

  // Validate form
  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    // Country validation
    if (!formData.country.trim()) {
      newErrors.country = 'Country is required';
      isValid = false;
    }

    // State name validation
    if (!formData.name.trim()) {
      newErrors.name = 'State name is required';
      isValid = false;
    }


    if (!formData.stateTerritory.trim()) {
      newErrors.stateTerritory = 'State/Territory is required';
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
          country_id: formData.country,
          stateName: formData.name.trim(),
          stateshortName: formData.short_name.trim(),
          //state: formData.stateTerritory.trim() === "State" ? "STATE" : "TERRITORY",
          state: formData.stateTerritory?.toUpperCase() || '',
          description: formData.description.trim(),
        }
        : {
          country_id: formData.country,
          stateName: formData.name.trim(),
          stateshortName: formData.short_name.trim(),
          state: formData.stateTerritory?.toUpperCase() || '',
          description: formData.description.trim(),
        };

      setLoading(true);
      const action = mode === 'edit' ? stateEdit : stateAdd;

      dispatch(action(sendPayload, (response, error) => {
        setLoading(false);
        if (error) {
          toast.error(error?.response?.data?.message || "Server error");
        } else if (response?.statusCode === 200 && response?.status === true) {
          toast.success(response?.message);
          resetForm();
          handleClose();
        } else {
          toast.error("Something went wrong.");
        }
      }));
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      uuid: '',
      country: '',
      name: '',
      short_name: '',
      stateTerritory: '',
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

  // Conditional render
  if (!show) return null;

  return (
    <div
      className="modal fade show common-ctl-popup"
      tabIndex={-1}
      role="dialog"
      aria-labelledby="AddEditStateModalLabel"
      aria-hidden={!show}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="AddEditStateModalLabel">
              {mode === 'edit' ? 'Edit State' : 'Add State'}
            </h1>
            <button type="button" className="btn-close" onClick={onClose} aria-label="Close" />
          </div>

          <div className="modal-body p-24">
            <form onSubmit={handleSubmit}>
              <div className="row">
                {/* Country Dropdown */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Country Name <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={countryListData.map((option) => ({
                      value: option.uuid,
                      label: option.name,
                    }))}
                    value={
                      formData.country
                        ? countryListData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.name,
                            }))
                            .find((opt) => opt.value === formData.country)
                        : null
                    }
                    onChange={handleSelectChange}
                    placeholder="Select Country"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${
                      errors.country ? "is-invalid" : ""
                    }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.country && (
                    <div className="text-danger text-sm mt-1">
                      {errors.country}
                    </div>
                  )}
                </div>

                {/* State Name */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    State Name <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.name ? 'is-invalid' : ''}`}
                    placeholder="Enter state name"
                  />
                  {errors.name && (
                    <div className="text-danger text-sm mt-1">{errors.name}</div>
                  )}
                </div>

                {/* State Short Name */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    State Short Name
                  </label>
                  <input
                    type="text"
                    name="short_name"
                    value={formData.short_name}
                    onChange={handleChange}
                    className="form-control radius-8"
                    placeholder="Enter short name"
                  />
                </div>
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    State / Territory <span className="text-danger">*</span>
                  </label>
                  <select
                    name="stateTerritory"
                    value={formData.stateTerritory}
                    onChange={handleChange}
                    className={`form-control form-select radius-8 ${errors.stateTerritory ? 'is-invalid' : ''}`}
                  >
                    <option value="">State / Territory</option>
                    <option value="State">State</option>
                    <option value="Territory">Territory</option>

                  </select>
                  {errors.stateTerritory && (
                    <div className="text-danger text-sm mt-1">
                      {errors.stateTerritory}
                    </div>
                  )}
                </div>
                {/* Description */}
                <div className="col-12 mb-20">
                  <label htmlFor="desc" className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Description
                  </label>
                  <textarea
                    className="form-control"
                    id="desc"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    rows={4}
                    placeholder="Description"
                  />
                </div>

                {/* Buttons */}
                <div className="d-flex align-items-center justify-content-center gap-3 mt-24">
                  <button
                    type="button"
                    onClick={onClose}
                    className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-16 py-4 radius-6"
                    disabled={loading}
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

export default AddEditStateModal;