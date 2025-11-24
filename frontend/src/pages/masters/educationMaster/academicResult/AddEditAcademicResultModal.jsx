import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { academicResultAdd, academicResultEdit } from '../../../../store/master/educationMaster/action';
import { toast } from "react-toastify";
import { academicResultTypeList } from '../../../../store/master/educationMaster/action';
import Select from "react-select";
const AddEditAcademicResultModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [educationLevelListData, setEducationLevelListData] = useState([]);
  const [selectedDatatype, setSelectedDatatype] = useState("");


  const [formData, setFormData] = useState({
    uuid: '',
    departmentName: '',
    category: '',
    description: '',
  });

  const [errors, setErrors] = useState({
    departmentName: '',
    category: '',
    description: '',
  });

  useEffect(() => {
    if (show) { // Only run when modal is shown
      if (mode === 'edit' && rowData) {
        setFormData({
          uuid: rowData.uuid || '',
          departmentName: rowData.Academicresult || '',
          category: rowData.AcademicResulttype_uuid || '',
          description: rowData.description || '',
        });
      } else {
        setFormData({
          uuid: '',
          departmentName: '',
          category: '',
          description: '',
        });
      }
      fetchEducationLevelList();
    }
  }, [mode, rowData, show]);

  const fetchEducationLevelList = () => {

    const params = {
      page: 1,
      limit: 2000,
      search: '',
      status: '',
      sortBy: 'name',
      sortOrder: 'asc',
    };

    dispatch(academicResultTypeList(params, (response, error) => {
      if (response?.statusCode === 200 && response?.status === true) {
        setEducationLevelListData(response?.data || []);
      } else {
        setEducationLevelListData([]);
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
    if (!formData.departmentName.trim()) {
      newErrors.departmentName = 'Academic result  is required';
      isValid = false;
    }
    if (!formData.category) {
      newErrors.category = 'Academic result type is required';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (validateForm()) {
      const sendPayload = mode === 'edit'
        ? {
          uuid: formData.uuid,
          Academicresult: formData.departmentName,
          AcademicResulttype_id: formData.category,
          description: formData.description,
        }
        : {
          Academicresult: formData.departmentName,
          AcademicResulttype_id: formData.category,
          description: formData.description,
        };

      setLoading(true);

      const action = mode === 'edit' ? academicResultEdit : academicResultAdd;

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
      departmentName: '',
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
      aria-labelledby="departmentModalLabel"
      aria-hidden={!show}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="departmentModalLabel">
              {mode === 'edit' ? 'Edit Academic Result' : 'Add Academic Result'}
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
                    Academic Result Type <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={educationLevelListData.map((option) => ({
                      value: option.uuid,
                      label: option.name,
                    }))}
                    value={
                      formData.category
                        ? educationLevelListData
                          .map((option) => ({
                            value: option.uuid,
                            label: option.name,
                          }))
                          .find((opt) => opt.value === formData.category)
                        : null
                    }
                    onChange={(selectedOption) => {
                      const selected = educationLevelListData.find(
                        (item) => item.uuid === selectedOption?.value
                      );

                      setSelectedDatatype(selected?.datatype || "Text");

                      handleChange({
                        target: {
                          name: "category",
                          value: selectedOption ? selectedOption.value : "",
                        },
                      });
                    }}

                    placeholder="Select academic result type"
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
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Academic Result <span className="text-danger">*</span>
                  </label>
                  <input
                    type={selectedDatatype === "Numeric" ? "number" : "text"}
                    name="departmentName"
                    value={formData.departmentName}
                    onChange={handleChange}
                    className={`form-control radius-8 ${errors.departmentName ? 'is-invalid' : ''}`}
                    placeholder={
                      selectedDatatype === "Numeric"
                        ? "Enter numeric value"
                        : "Enter academic result"
                    }
                  />

                  {errors.departmentName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.departmentName}
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

export default AddEditAcademicResultModal;