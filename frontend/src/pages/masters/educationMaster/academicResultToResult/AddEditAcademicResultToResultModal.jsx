import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { academicResultToResultAdd, academicResultToResultEdit } from '../../../../store/master/educationMaster/action';
import { toast } from "react-toastify";
import { academicResultTypeList, academicResultList } from '../../../../store/master/educationMaster/action';
import Select from "react-select";
const AddEditAcademicResultToResultModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    const [academicResult, setAcademicResult] = useState([]);
    const [academicResultType, setAcademicResultType] = useState([]);
    // Form state
    const [formData, setFormData] = useState({
        uuid: '',
        academicResultType: '',
        academicResult: '',
        compareAcademicResultType: '',
        compareAcademicResult: '',
        description: '',
    });

    // console.log("rowData",rowData);
    // Validation errors state
    const [errors, setErrors] = useState({
        academicResultType: '',
        academicResult: '',
        compareAcademicResultType: '',
        compareAcademicResult: '',
        description: '',
    });

    // Populate form data when in edit mode
    useEffect(() => {
        if (mode === 'edit' && rowData) {
            setFormData({
                uuid: rowData.uuid || '',
                academicResultType: rowData.academicResultTypeUuid || '',
                academicResult: rowData.academicResult || '',
                compareAcademicResultType: rowData.compareAcademicResultTypeUuid || '',
                compareAcademicResult: rowData.compareAcademicResult || '',
                description: rowData.description || '',
            });
        } else {
            // Reset form when switching to add mode
            setFormData({
                uuid: '',
                academicResultType: '',
                academicResult: '',
                compareAcademicResult: '',
                compareAcademicResult: '',
                description: '',
            });
        }
        fetchEducationLevelList();
    }, [mode, rowData, show]);

    const fetchEducationLevelList = () => {
        setLoading(true);
        const params = {
            page: 1,
            limit: 2000,
            search: '',
            status: '',
            sortBy: 'updated_at', // Field to sort by
            sortOrder: 'desc', // 'asc' or 'desc'
        };
        dispatch(academicResultTypeList(params, (response, error) => {
            setLoading(false);
            if (response?.statusCode === 200 && response?.status === true) {
                setAcademicResultType(response?.data || []);

            }
        }));
        dispatch(academicResultList(params, (response, erroe) => {
            setLoading(false);
            if (response?.statusCode === 200 && response?.status === true) {
                setAcademicResult(response?.data || []);
            }

        }))
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

        if (!formData.academicResultType) {
            newErrors.academicResultType = "Academic result type is required";
            isValid = false;
        }
        if (!formData.academicResult.trim()) {
            newErrors.academicResult = "Academic result is required";
            isValid = false;
        }
        if (!formData.compareAcademicResultType) {
            newErrors.compareAcademicResultType = "Compare academic result type is required";
            isValid = false;
        }
        if (!formData.compareAcademicResult.trim()) {
            newErrors.compareAcademicResult = "Compare academic result is required";
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
                    AcademicResulttype_id: formData.academicResultType,
                    Academicresult: formData.academicResult,
                    CompareAcademicResultType_id: formData.compareAcademicResultType,
                    CompareAcademicResult: formData.compareAcademicResult,
                    description: formData.description,
                }
                : {
                    AcademicResulttype_id: formData.academicResultType,
                    Academicresult: formData.academicResult,
                    CompareAcademicResultType_id: formData.compareAcademicResultType,
                    CompareAcademicResult: formData.compareAcademicResult,
                    description: formData.description,
                };

            setLoading(true);

            const action = mode === 'edit' ? academicResultToResultEdit : academicResultToResultAdd;

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
            academicResultType: '',
            academicResult: '',
            compareAcademicResultType: '',
            compareAcademicResult: '',
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
                            {mode === 'edit' ? 'Edit Compare : Academic Result To Result' : 'Add Compare : Academic Result To Result'}
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
                                        options={academicResultType.map((option) => ({
                                            value: option.uuid,
                                            label: option.name,
                                        }))}
                                        value={
                                            formData.academicResultType
                                                ? academicResultType
                                                    .map((option) => ({
                                                        value: option.uuid,
                                                        label: option.name,
                                                    }))
                                                    .find((opt) => opt.value === formData.academicResultType)
                                                : null
                                        }
                                        onChange={(selectedOption) =>
                                            handleChange({
                                                target: {
                                                    name: "academicResultType",
                                                    value: selectedOption ? selectedOption.value : "",
                                                },
                                            })
                                        }
                                        placeholder="Select Academic Result Type"
                                        isClearable
                                        isSearchable
                                        className={`custom-select-container ${errors.academicResultType ? "is-invalid" : ""
                                            }`}
                                        classNamePrefix="custom-select"
                                    />
                                    {errors.academicResultType && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.academicResultType}
                                        </div>
                                    )}
                                </div>
                                <div className="col-12 mb-20">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                        Academic Result <span className="text-danger">*</span>
                                    </label>
                                    {/* <select
                                        name="academicResult"
                                        value={formData.academicResult}
                                        onChange={handleChange}
                                        className={`form-control form-select radius-8 ${errors.academicResult ? 'is-invalid' : ''}`}
                                    >
                                        <option value=""> Select Academic Result</option>
                                        {
                                            academicResult.map((option) => (
                                                <option key={option.uuid} value={option.uuid}>
                                                    {option.Academicresult}
                                                </option>

                                            ))
                                        }
                                    </select> */}
                                    <Select
                                        options={academicResult.map((option) => ({
                                            value: option.uuid,
                                            label: option.Academicresult,
                                        }))}
                                        value={
                                            formData.academicResult
                                                ? academicResult
                                                    .map((option) => ({
                                                        value: option.uuid,
                                                        label: option.Academicresult,
                                                    }))
                                                    .find((opt) => opt.value === formData.academicResult)
                                                : null
                                        }
                                        onChange={(selectedOption) =>
                                            handleChange({
                                                target: {
                                                    name: "academicResult",
                                                    value: selectedOption ? selectedOption.value : "",
                                                },
                                            })
                                        }
                                        placeholder="Select Academic Result"
                                        isClearable
                                        isSearchable
                                        className={`custom-select-container ${errors.academicResult ? "is-invalid" : ""
                                            }`}
                                        classNamePrefix="custom-select"
                                    />
                                    {errors.academicResult && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.academicResult}
                                        </div>
                                    )}

                                </div>
                                <div className="col-12 mb-20">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                        Compare : Academic Result Type <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        name="compareAcademicResultType"
                                        value={formData.compareAcademicResultType}
                                        onChange={handleChange}
                                        className={`form-control radius-8 ${errors.compareAcademicResultType ? 'is-invalid' : ''}`}
                                        placeholder="Enter academic result"
                                    />
                                    {errors.compareAcademicResultType && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.compareAcademicResultType}
                                        </div>
                                    )}
                                </div>
                                <div className="col-12 mb-20">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                        Compare : Academic Result <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        name="compareAcademicResult"
                                        value={formData.compareAcademicResult}
                                        onChange={handleChange}
                                        className={`form-control radius-8 ${errors.compareAcademicResult ? 'is-invalid' : ''}`}
                                        placeholder="Enter academic result"
                                    />
                                    {errors.compareAcademicResult && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.compareAcademicResult}
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

export default AddEditAcademicResultToResultModal;