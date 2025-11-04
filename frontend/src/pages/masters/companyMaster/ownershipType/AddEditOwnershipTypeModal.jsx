import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { ownershipTypeEdit, ownershipTypeAdd } from '../../../../store/master/companyMasters/actions';
import { toast } from "react-toastify";
import { companyList, stakeholderCategoryList } from '../../../../store/master/actions';
const AddEditOwnershipTypeModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
 const [stakeholderListData, setStakeholderListData] = useState([]);
  // Form state
  const [formData, setFormData] = useState({
    uuid: '',
    name: '',
    company_type: '',
    description: '',
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    name: '',
    company_type: '',
    description: '',
  });

  

  // Populate form data when in edit mode
  useEffect(() => {
    if (mode === 'edit' && rowData) {
      setFormData({
        uuid: rowData.uuid || '',
        name: rowData.name || '',
        company_type: rowData.company_type || '',
        description: rowData.description || '',
      });
    } else {
      // Reset form when switching to add mode
      setFormData({
        uuid: '',
        name: '',
        company_type: '',
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
      sortBy: 'updated_at', // Field to sort by
      sortOrder: 'desc', // 'asc' or 'desc'
    };

    dispatch(companyList(params, (response, error) => {
      setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {

        setStakeholderListData(response?.data || []);

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

    // Name validation
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
      isValid = false;
    }

    // company_type validation
    if (!formData.company_type) {
      newErrors.company_type = 'Company type is required';
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
          company_type: formData.company_type,
          description: formData.description,
        }
        : {
          name: formData.name,
          company_type: formData.company_type,
          description: formData.description,
        };

      setLoading(true);

      const action = mode === 'edit' ? ownershipTypeEdit : ownershipTypeAdd;

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
      company_type: '',
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
      aria-labelledby="ownershipTypeModalLabel"
      aria-hidden={!show}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="ownershipTypeModalLabel">
              {mode === 'edit' ? 'Edit Ownership Type' : 'Add Ownership Type'}
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
                {/* Company Type*/}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Company Type <span className="text-danger">*</span>
                  </label>
                  <select
                    name="company_type"
                    value={formData.company_type}
                    onChange={handleChange}
                    className={`form-control form-select radius-8 ${errors.company_type ? 'is-invalid' : ''}`}
                  >
                     <option value="">Select  company type</option>
                    {stakeholderListData.map((option) => (
                      <option key={option.uuid} value={option.uuid}>
                        {option.name}
                      </option>
                    ))}
                  </select>
                  {errors.company_type && (
                    <div className="text-danger text-sm mt-1">
                      {errors.company_type}
                    </div>
                  )}
                </div>
                {/* Stakeholder Type Name */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Ownership Type <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.name ? 'is-invalid' : ''}`}
                    placeholder="Enter ownership type"
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

export default AddEditOwnershipTypeModal;