import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { languageTestNameAdd, languageTestNameEdit, languageNameTestList } from '../../../../store/master/testMaster/action';
import { toast } from "react-toastify";
import Select from "react-select";
const AddEditLanguageTestNameModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [languageNameTest, setLanguageNameTest] = useState([]);

  // Form state
  const [formData, setFormData] = useState({
    uuid: '',
    languageNameTest: '',
    shortName: '',
    fullName: '',
    description: '',
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    languageNameTest: '',
    shortName: '',
  });

  // Populate form data when in edit mode
  useEffect(() => {
    if (show) {
      if (mode === 'edit' && rowData) {
        setFormData({
          uuid: rowData.uuid || '',
          languageNameTest: rowData?.language?.uuid || '',
          shortName: rowData.name || '',
          fullName: rowData.fullname || '',
          description: rowData.description || '',
        });
      } else {
        // Reset form when switching to add mode
        setFormData({
          uuid: '',
          languageNameTest: '',
          shortName: '',
          fullName: '',
          description: '',
        });
      }
      fetchLanguageTestNameList();
    }
  }, [mode, rowData, show]);

  const fetchLanguageTestNameList = () => {
    // setLoading(true);
    const params = {
      page: 1,
      limit: 2000,
      search: '',
      status: '',
      sortBy: 'updated_at', // Field to sort by
      sortOrder: 'desc', // 'asc' or 'desc'
    };

    dispatch(languageNameTestList(params, (response, error) => {
      // setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {
        setLanguageNameTest(response?.data || []);

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
    if (!formData.languageNameTest.trim()) {
      newErrors.languageNameTest = 'Language name(test) is required';
      isValid = false;
    }
    if (!formData.shortName.trim()) {
      newErrors.shortName = 'Language Test Name is required';
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
          language: formData.languageNameTest,
          name: formData.shortName,
          fullname: formData.fullName,
          description: formData.description,
        }
        : {
          language: formData.languageNameTest,
          name: formData.shortName,
          fullname: formData.fullName,
          description: formData.description,
        };

      setLoading(true);

      const action = mode === 'edit' ? languageTestNameEdit : languageTestNameAdd;

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
      languageNameTest: '',
      shortName: '',
      fullName: '',
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
      aria-labelledby="departmentModalLabel"
      aria-hidden={!show}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="departmentModalLabel">
              {mode === 'edit' ? 'Edit Language Test Name' : 'Add Language Test Name'}
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
                {/* Department Name */}
                <div className="col-12 mb-10">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                    Language Name (Test) <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={languageNameTest.map((option) => ({
                      value: option.uuid,
                      label: option.name,
                    }))}
                    value={
                      formData.languageNameTest
                        ? languageNameTest
                          .map((option) => ({
                            value: option.uuid,
                            label: option.name,
                          }))
                          .find((opt) => opt.value === formData.languageNameTest)
                        : null
                    }
                    onChange={(selectedOption) =>
                      handleChange({
                        target: {
                          name: "languageNameTest",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      })
                    }
                    placeholder="Select language name(test)"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${errors.languageNameTest ? "is-invalid" : ""
                      }`}
                    classNamePrefix="custom-select"
                  />
                  {errors.languageNameTest && (
                    <div className="text-danger text-sm mt-1">
                      {errors.languageNameTest}
                    </div>
                  )}
                </div>
                <div className="col-12 mb-10">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                    Language Test Name <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    name="shortName"
                    value={formData.shortName}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.shortName ? 'is-invalid' : ''}`}
                    placeholder="Enter language test name"
                  />
                  {errors.shortName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.shortName}
                    </div>
                  )}
                </div>
                <div className="col-12 mb-10">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                    Language Test Full Name
                  </label>
                  <input
                    type="text"
                    name="fullName"
                    value={formData.fullName}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.fullName ? 'is-invalid' : ''}`}
                    placeholder="Enter language test full name"
                  />
                  {errors.fullName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.fullName}
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
                    className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-16 py-6 radius-6"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn comman-btn-color border border-primary-600 text-md px-16 py-6 radius-6"
                    disabled={loading}
                  >
                    {/* {loading ? 'Saving...' : 'Save'} */}
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
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

export default AddEditLanguageTestNameModal;