import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { ecaAwardingBodyAdd, ecaAwardingBodyEdit, ecaForList } from '../../../../store/master/educationMaster/action';
import { toast } from "react-toastify";
import { countryList } from "../../../../store/master/generalMasters/actions";
import Select from "react-select";
const AddEditECAAwardingBodyModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [countryListData, setCountryListData] = useState([]);

  // Form state
  const [formData, setFormData] = useState({
    uuid: '',
    countryUuid: '',
    ecaFor: '',
    fullName: '',
    shortName: '',
    validPeriod: '',
    validPeriodType: '',
    description: '',
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    countryUuid: '',
    ecaFor: '',
    fullName: '',
    shortName: '',
    validPeriod: '',

  });

  // Populate form data when in edit mode
  useEffect(() => {
    if (mode === 'edit' && rowData) {
      let validNumber = "";
      let validType = "";

      if (rowData.eca_valid_period) {
        const parts = rowData.eca_valid_period.split(" ");
        validNumber = parts[0] || "";
        validType = parts[1] || "";
      }
      setFormData({
        uuid: rowData.uuid || '',
        countryUuid: rowData.country || '',
        ecaFor: rowData.selection_type_display || '',
        fullName: rowData.eca_body_full_name || '',
        shortName: rowData.eca_body_short_name || '',
        validPeriod: validNumber,
        validPeriodType: validType,
        description: rowData.description || '',
      });
    } else {
      // Reset form when switching to add mode
      setFormData({
        uuid: '',
        countryUuid: '',
        ecaFor: '',
        fullName: '',
        shortName: '',
        validPeriod: '',
        validPeriodType: '',
        description: '',
      });
    }
    fetchStudyList();
  }, [mode, rowData, show]);

  const fetchStudyList = () => {
    setLoading(true);
    const params = {
      page: 1,
      limit: 2000,
      search: '',
      status: '',
      sortBy: 'updated_at',
      sortOrder: 'desc',
    };
    dispatch(countryList(params, (response, error) => {
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

  // Validate form
  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    // Department Name validation
    if (!formData.countryUuid.trim()) {
      newErrors.countryUuid = 'Country is required';
      isValid = false;
    }
    if (!formData.ecaFor.trim()) {
      newErrors.ecaFor = 'ECA For is required';
      isValid = false;
    }
    if (!formData.fullName.trim()) {
      newErrors.fullName = 'ECA Body Full Name is required';
      isValid = false;
    }
    if (!formData.shortName.trim()) {
      newErrors.shortName = 'ECA Body Short Name is required';
      isValid = false;
    }


    setErrors(newErrors);
    return isValid;
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();

    if (validateForm()) {
      const formattedValidPeriod = formData.validPeriod && formData.validPeriodType
        ? `${formData.validPeriod} ${formData.validPeriodType}`
        : '';

      const sendPayload = mode === 'edit'
        ? {
          uuid: formData.uuid,
          country: formData.countryUuid,
          selection_type: formData.ecaFor,
          eca_body_full_name: formData.fullName,
          eca_body_short_name: formData.shortName,
          eca_valid_period: formattedValidPeriod,
          // validPeriodType: formData.validPeriodType,
          description: formData.description,
        }
        : {
          country: formData.countryUuid,
          selection_type: formData.ecaFor,
          eca_body_full_name: formData.fullName,
          eca_body_short_name: formData.shortName,
          eca_valid_period: formattedValidPeriod,
          // validPeriodType: formData.validPeriodType,
          description: formData.description,

        };

      setLoading(true);
      // console.log("Payload Sent to API:", sendPayload);
      const action = mode === 'edit' ? ecaAwardingBodyEdit : ecaAwardingBodyAdd;

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
      countryUuid: '',
      ecaFor: '',
      fullName: '',
      shortName: '',
      validPeriod: '',
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
      aria-labelledby="departmentModalLabel"
      aria-hidden={!show}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="departmentModalLabel">
              {mode === 'edit' ? 'Edit ECA Awarding Body' : 'Add ECA Awarding Body'}
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
                {/* Department Name */}

                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Country<span className="text-danger">*</span>
                  </label>
                  <Select
                    options={countryListData.map((option) => ({
                      value: option.uuid,
                      label: option.name,
                    }))}
                    value={
                      formData.countryUuid
                        ? countryListData
                          .map((option) => ({
                            value: option.uuid,
                            label: option.name,
                          }))
                          .find((opt) => opt.value === formData.countryUuid)
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "countryUuid",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    placeholder="Select country"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${errors.countryUuid ? "is-invalid" : ""
                      }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.countryUuid && (
                    <div className="text-danger text-sm mt-1">
                      {errors.countryUuid}
                    </div>
                  )}
                </div>
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    ECA For <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="ecaFor"
                    value={formData.ecaFor}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.ecaFor ? 'is-invalid' : ''}`}
                    placeholder="Enter ECA For"
                  />
                  {errors.ecaFor && (
                    <div className="text-danger text-sm mt-1">
                      {errors.ecaFor}
                    </div>
                  )}
                </div>
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    ECA Body Full Name <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="fullName"
                    value={formData.fullName}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.fullName ? 'is-invalid' : ''}`}
                    placeholder="Enter eca body fullName"
                  />
                  {errors.fullName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.fullName}
                    </div>
                  )}
                </div>
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    ECA Body Short Name <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="shortName"
                    value={formData.shortName}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.shortName ? 'is-invalid' : ''}`}
                    placeholder="Enter eca body shortName"
                  />
                  {errors.shortName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.shortName}
                    </div>
                  )}
                </div>
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    ECA Valid Period
                  </label>
                  <div className="row gx-2">
                    <div className="col-6">
                      <input
                        type="number"
                        name="validPeriod"
                        value={formData.validPeriod}
                        onChange={handleChange}
                        className={`form-control radius-8 ${errors.validPeriod ? 'is-invalid' : ''}`}
                        placeholder="Numeric"
                      />
                    </div>
                    <div className="col-6">
                      <select
                        name="validPeriodType"
                        value={formData.validPeriodType || ""}
                        onChange={handleChange}
                        className="form-control form-select radius-8"
                      >
                        <option value="">Weeks / Months / Years</option>
                        <option value="weeks">Weeks</option>
                        <option value="months">Months</option>
                        <option value="years">Years</option>
                      </select>
                    </div>
                  </div>

                  {errors.validPeriod && (
                    <div className="text-danger text-sm mt-1">
                      {errors.validPeriod}
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

export default AddEditECAAwardingBodyModal;