import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { districtAdd, districtEdit, stateListByCountry } from '../../../../store/master/generalMasters/actions';
import { toast } from "react-toastify";
import { countryDemoList } from '../../../../store/master/companyMasters/actions';

const AddEditDistrictModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [countryListData, setCountryListData] = useState([]);
  const [stateListData, setStateListData] = useState([]);
  
  // Form state
  const [formData, setFormData] = useState({
    uuid: '',
    country: '',
    state: '',
    name: '',
    description: '',
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    country: '',
    name: '',
    description: '',
  });

  // Populate form data when in edit mode
  useEffect(() => {
    if (mode === 'edit' && rowData) {

      setFormData({
        uuid: rowData.uuid || '',
        country: rowData.country_uuid || '',
        state: rowData.state_uuid || '',
        name: rowData.districtName || '',
        description: rowData.description || '',
      });
      // If country is already selected in edit mode, fetch states
      if (rowData.country_uuid) {
        fetchStateList(rowData.country_uuid);
      }
    } else {
      // Reset form when switching to add mode
      setFormData({
        uuid: '',
        country: '',
        state: '',
        name: '',
        description: '',
      });
      setStateListData([]); // Clear state list
    }
    fetchCountryList();
  }, [mode, rowData, show]);

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

  const fetchStateList = (countryId) => {
    if (!countryId) {
      setStateListData([]);
      return;
    }
    
    setLoading(true);
    const params = {
      countryId: countryId,
    };

    dispatch(stateListByCountry(params, (response, error) => {
      setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {
        setStateListData(response?.data || []);
      } else {
        setStateListData([]);
      }
    }));
  };

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
  
    // When country changes, fetch states and reset state selection
    if (name === 'country') {
      setFormData(prev => ({
        ...prev,
        country: value,
        state: '' // Reset state when country changes
      }));
      fetchStateList(value);
    } else {
      // For all other fields including state
      setFormData(prev => {
        const newData = {
          ...prev,
          [name]: value
        };
        return newData;
      });
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

    // Country validation
    if (!formData.country.trim()) {
      newErrors.country = 'Country is required';
      isValid = false;
    }

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
      const sendPayload = mode === 'edit'
        ? {
          uuid: formData.uuid,
          country_id: formData.country,
          state_id: formData.state || '', // Ensure empty string if no state
          districtName: formData.name,
          description: formData.description,
        }
        : {
          country_id: formData.country,
          state_id: formData.state || '', // Ensure empty string if no state
          districtName: formData.name,
          description: formData.description,
        };

      setLoading(true);

      const action = mode === 'edit' ? districtEdit : districtAdd;

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
      state: '',
      name: '',
      description: '',
    });
    setErrors({});
    setStateListData([]);
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
      aria-labelledby="AddEditDistrictModalLabel"
      aria-hidden={!show}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="AddEditDistrictModalLabel">
              {mode === 'edit' ? 'Edit District' : 'Add District'}
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
                {/* Country Dropdown */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Country Name <span className="text-danger">*</span>
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

                {/* State Dropdown */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    State Name
                  </label>
                  <select
                    name="state"
                    value={formData.state}
                    onChange={handleChange}
                    className="form-control form-select radius-8"
                    disabled={!formData.country}
                  >
                    <option value="">Select State</option>
                    {stateListData.map((option) => (
                      <option key={option.uuid} value={option.uuid}>
                        {option.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* District Name  */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    District Name <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.name ? 'is-invalid' : ''}`}
                    placeholder="Enter district name"
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

export default AddEditDistrictModal;