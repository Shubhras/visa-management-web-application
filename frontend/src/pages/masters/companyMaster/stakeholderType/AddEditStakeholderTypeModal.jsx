import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import Select from "react-select";
import { stakeholderTypeEdit, stakeholderTypeAdd } from '../../../../store/master/companyMasters/actions';
import { toast } from "react-toastify";
import { stakeholderCategoryList } from '../../../../store/master/actions';

const AddEditStakeholderTypeModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [stakeholderListData, setStakeholderListData] = useState([]);

  // Form state
  const [formData, setFormData] = useState({
    uuid: '',
    name: '',
    category: '',
    description: '',
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    name: '',
    category: '',
    description: '',
  });

  // Populate form data when in edit mode
  useEffect(() => {
    if (mode === 'edit' && rowData) {
      setFormData({
        uuid: rowData.uuid || '',
        name: rowData.name || '',
        category: rowData.category || '',
        description: rowData.description || '',
      });
    } else {
      // Reset form when switching to add mode
      setFormData({
        uuid: '',
        name: '',
        category: '',
        description: '',
      });
    }
    fetchStakeholderCategoriesList();
  }, [mode, rowData, show]);

  const fetchStakeholderCategoriesList = () => {
    setLoading(true);
    const params = {
      page: 1,
      limit: 2000,
      search: '',
      status: '',
      sortBy: 'name',
      sortOrder: 'asc',
    };

    dispatch(stakeholderCategoryList(params, (response, error) => {
      setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {
        setStakeholderListData(response?.data || []);
      } else {
        toast.error("Failed to load stakeholder categories");
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

  // Handle Select dropdown change
  const handleSelectChange = (selectedOption) => {
    setFormData(prev => ({
      ...prev,
      category: selectedOption ? selectedOption.value : ''
    }));
    if (errors.category) {
      setErrors(prev => ({ ...prev, category: '' }));
    }
  };
  // Custom filter function for search from start
  const customFilterOption = (option, inputValue) => {
    if (!inputValue) return true;
    return option.label.toLowerCase().startsWith(inputValue.toLowerCase());
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    // Name validation
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
      isValid = false;
    }

    // Category validation
    if (!formData.category) {
      newErrors.category = 'Category is required';
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
          category: formData.category,
          description: formData.description,
        }
        : {
          name: formData.name,
          category: formData.category,
          description: formData.description,
        };

      setLoading(true);

      const action = mode === 'edit' ? stakeholderTypeEdit : stakeholderTypeAdd;

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
      category: '',
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
      aria-labelledby="StakeholderTypeModalLabel"
      aria-hidden={!show}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="StakeholderTypeModalLabel">
              {mode === 'edit' ? 'Edit Stakeholder Type' : 'Add Stakeholder Type'}
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
                {/* Stakeholder Category */}
                <div className='modal-scrollable-content'>
                  <div className="col-12 mb-10">
                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                      Stakeholder Category <span className="text-danger">*</span>
                    </label>
                    <Select
                      options={stakeholderListData.map((option) => ({
                        value: option.uuid,
                        label: option.name,
                      }))}
                      value={
                        formData.category
                          ? stakeholderListData
                            .map((option) => ({
                              value: option.uuid,
                              label: option.name,
                            }))
                            .find((opt) => opt.value === formData.category)
                          : null
                      }
                      onChange={handleSelectChange}
                      filterOption={customFilterOption}
                      placeholder="Select Stakeholder Category"
                      isClearable
                      isSearchable
                      className={`custom-select-container ${errors.category ? "is-invalid" : ""
                        }`}
                      classNamePrefix="custom-select"
                    />
                    {errors.category && (
                      <div className="text-danger text-sm mt-1">
                        {errors.category}
                      </div>
                    )}
                  </div>

                  {/* Stakeholder Type Name */}
                  <div className="col-12 mb-10">
                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                      Stakeholder Type <span className="text-danger">*</span>
                    </label>
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      className={`form-control radius-8 ${errors.name ? 'is-invalid' : ''}`}
                      placeholder="Enter stakeholder type"
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

export default AddEditStakeholderTypeModal;