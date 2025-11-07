import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { cityAdd, cityEdit, districtListByState, stateListByCountry } from '../../../../store/master/generalMasters/actions';
import { toast } from "react-toastify";
import { countryDemoList } from '../../../../store/master/companyMasters/actions';

const AddEditCityModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [countryListData, setCountryListData] = useState([]);
  const [stateListData, setStateListData] = useState([]);
  const [districtListData, setDistrictListData] = useState([]);

  // Form state
  const [formData, setFormData] = useState({
    uuid: '',
    country: '',
    state: '',
    district: '',
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
        district: rowData.district_uuid || '',
        name: rowData.cityName || '',
        description: rowData.description || '',
      });
      // If country is already selected in edit mode, fetch states
      if (rowData.country_uuid) {
        fetchStateList(rowData.country_uuid);
        fetchDistrictList(rowData.country_uuid, rowData.state_uuid);
      }
    } else {
      // Reset form when switching to add mode
      setFormData({
        uuid: '',
        country: '',
        state: '',
        district:'',
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
  const fetchDistrictList = (countryId, stateId) => {
    if (!countryId) {
      setDistrictListData([]);
      return;
    }

    setLoading(true);
    const params = {
      countryId: countryId,
      stateId: stateId
    };

    dispatch(districtListByState(params, (response, error) => {
      setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {
        setDistrictListData(response?.data || []);
      } else {
        setDistrictListData([]);
      }
    }));
  };

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;

    // When country changes, fetch states and reset state and district selection
    if (name === 'country') {
      setFormData(prev => ({
        ...prev,
        country: value,
        state: '', // Reset state when country changes
        district: '' // Reset district when country changes
      }));
      fetchStateList(value);
      setDistrictListData([]); // Clear district list
    } else if (name === 'state') {
      // When state changes, fetch districts and reset district selection
      setFormData(prev => ({
        ...prev,
        state: value,
        district: '' // Reset district when state changes
      }));
      if (value && formData.country) {
        fetchDistrictList(formData.country, value);
      } else {
        setDistrictListData([]);
      }
    } else {
      // For all other fields
      setFormData(prev => ({
        ...prev,
        [name]: value
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
          state_id: formData.state || null,
          district_id: formData.district || null,
          cityName: formData.name,
          description: formData.description || null,
        }
        : {
          country_id: formData.country,
          state_id: formData.state || null,
          district_id: formData.district || null,
          cityName: formData.name,
          description: formData.description || null,
        };

      setLoading(true);

      const action = mode === 'edit' ? cityEdit : cityAdd;

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
      district:'',
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
      aria-labelledby="AddEditCityModalLabel"
      aria-hidden={!show}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="AddEditCityModalLabel">
              {mode === 'edit' ? 'Edit City' : 'Add City'}
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

                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    District Name
                  </label>
                  <select
                    name="district"
                    value={formData.district}
                    onChange={handleChange}
                    className="form-control form-select radius-8"
                    disabled={!formData.state}
                  >
                    <option value="">Select District</option>
                    {districtListData.map((option) => (
                      <option key={option.uuid} value={option.uuid}>
                        {option.districtName}
                      </option>
                    ))}
                  </select>
                </div>
                {/* City Name  */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    City Name <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.name ? 'is-invalid' : ''}`}
                    placeholder="Enter city name"
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

export default AddEditCityModal;