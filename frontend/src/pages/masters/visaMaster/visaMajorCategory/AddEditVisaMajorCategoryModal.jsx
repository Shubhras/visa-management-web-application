import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import { visaMajorCategoryAdd, visaMajorCategoryEdit } from '../../../../store/master/visaMaster/action';
import { representingCountryData } from "../../../../store/master/visaMaster/action";
import { visaMainCategoryList } from "../../../../store/master/visaConditionsMaster/action";
import Select from "react-select";
const AddEditVisaMajorCategoryModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [countryListData, setCountryListData] = useState([]);
  const [visaMain, setVisaMain] = useState([]);
  // Form state
  const [formData, setFormData] = useState({
    uuid: '',
    name: '',
    country_name: '',
    visaMain: '',
    description: '',
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    name: '',
    country_name: '',
    visaMain: '',
  });

  // Populate form data when in edit mode
  useEffect(() => {
    if (show) {
      if (mode === 'edit' && rowData) {
        setFormData({
          uuid: rowData.uuid || '',
          name: rowData.name || '',
          visaMain: rowData.visaMain || '',
          country_name: rowData.country_name || '',
          description: rowData.description || '',
        });
      } else {
        // Reset form when switching to add mode
        setFormData({
          uuid: '',
          name: '',
          visaMain: '',
          country_name: '',
          description: '',
        });
      }
      fetchCountrylList();
    }
  }, [mode, rowData, show]);

  const fetchCountrylList = () => {
    const params = {
      page: 1,
      limit: 2000,
      search: '',
      status: '',
      sortBy: 'name',
      sortOrder: 'asc',
    };
    dispatch(representingCountryData(params, (response, error) => {
      if (response?.statusCode === 200 && response?.status === true) {
        setCountryListData(response?.data || []);
      } else {
        setCountryListData([]);
      }
    }));
    dispatch(visaMainCategoryList(params, (response, error) => {
      if (response?.statusCode === 200 && response?.status === true) {
        setVisaMain(response?.data || []);
      } else {
        setVisaMain([]);
      }
    }));

  };
  const customFilterOption = (option, inputValue) => {
    if (!inputValue) return true;
    return option.label.toLowerCase().startsWith(inputValue.toLowerCase());
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

    // Gender Name validation
    if (!formData.name.trim()) {
      newErrors.name = 'Visa Major Category is required';
      isValid = false;
    }
    if (!formData.country_name) {
      newErrors.country_name = 'Country is required';
      isValid = false;
    }
    if (!formData.visaMain) {
      newErrors.visaMain = 'Visa Main Category is required';
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
          name: formData.name,
          visaMain: formData.visaMain,
          country_name: formData.country_name,
          description: formData.description,
        }
        : {
          name: formData.name,
          visaMain: formData.visaMain,
          country_name: formData.country_name,
          description: formData.description,
        };

      setLoading(true);

      const action = mode === 'edit' ? visaMajorCategoryEdit : visaMajorCategoryAdd;

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
      name: '',
      country_name: '',
      visaMain: '',
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
      aria-labelledby="GenderModalLabel"
      aria-hidden={!show}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="GenderModalLabel">
              {mode === 'edit' ? 'Edit Visa Major Category' : 'Add Visa Major Category'}
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
                {/* Gender Name */}
                <div className="col-12 mb-10">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                    Country Name <span className="text-danger">*</span>
                  </label>

                  <Select
                    options={countryListData.map((option) => ({
                      value: option.uuid,
                      label: option.name + " (" + option?.continent?.name + ")",
                    }))}
                    value={
                      formData.country_name
                        ? countryListData
                          .map((option) => ({
                            value: option.uuid,
                            label: option.name + " (" + option?.continent?.name + ")",
                          }))
                          .find((opt) => opt.value === formData.country_name)
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "country_name",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select country"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${errors.country_name ? "is-invalid" : ""}`}
                    classNamePrefix="custom-select"
                  />

                  {errors.country_name && <div className="text-danger text-sm mt-1">{errors.country_name}</div>}
                </div>
                <div className="col-12 mb-10">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                    Visa Main Category <span className="text-danger">*</span>
                  </label>

                  <Select
                    options={visaMain.map((option) => ({
                      value: option.uuid,
                      label: option.name
                    }))}
                    value={
                      formData.visaMain
                        ? visaMain
                          .map((option) => ({
                            value: option.uuid,
                            label: option.name
                          }))
                          .find((opt) => opt.value === formData.visaMain)
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "visaMain",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select visa main category"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${errors.visaMain ? "is-invalid" : ""}`}
                    classNamePrefix="custom-select"
                  />

                  {errors.visaMain && <div className="text-danger text-sm mt-1">{errors.visaMain}</div>}
                </div>
                <div className="col-12 mb-10">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                    Visa Major Category <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.name ? 'is-invalid' : ''}`}
                    placeholder="Enter Visa Major Category"
                  />
                  {errors.name && (
                    <div className="text-danger text-sm mt-1">
                      {errors.name}
                    </div>
                  )}
                </div>

                {/* Description */}
                <div className="col-12 mb-10">
                  <label
                    htmlFor="desc"
                    className="form-label fw-semibold text-primary-light text-sm mb-0"
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

export default AddEditVisaMajorCategoryModal;