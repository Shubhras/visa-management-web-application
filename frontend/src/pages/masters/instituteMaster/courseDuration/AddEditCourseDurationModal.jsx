import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { courseDurationAdd, courseDurationEdit, courseLevelList } from "../../../../store/master/instituteMaster/action";
import { toast } from "react-toastify";
import Select from "react-select";
const AddEditCourseDurationModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    const [courseLevel, setCourseLevel] = useState([]);
    // Form state
    const [formData, setFormData] = useState({
        uuid: '',
        courseLevel: '',
        validPeriod: '',
        validPeriodType: '',
        description: '',
    });

    // Validation errors state
    const [errors, setErrors] = useState({
        validPeriod: '',
        validPeriodType: '',
        courseLevel: '',
        description: '',
    });

    // Populate form data when in edit mode
    useEffect(() => {
        if (mode === 'edit' && rowData) {
            setFormData({
                uuid: rowData.uuid || '',
                courseLevel: rowData.courselevel_uuid || '',
                validPeriod: rowData.valid_duration_value || "",
                validPeriodType: rowData.valid_duration_unit || "",
                description: rowData.description || '',
            });
        } else {
            // Reset form when switching to add mode
            setFormData({
                uuid: '',
                courseLevel: '',
                validPeriod: '',
                validPeriodType: '',
                description: '',
            });
        }
        fetchCourseLevelCode();
    }, [mode, rowData, show]);

    const fetchCourseLevelCode = () => {
        const params = {
            page: 1,
            limit: 2000,
            search: '',
            status: '',
            sortBy: 'name',
            sortOrder: 'asc',
        };
        dispatch(courseLevelList(params, (response, error) => {
            if (response?.statusCode === 200 && response?.status === true) {
                setCourseLevel(response?.data || []);
            }
        }));
    }

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
        if (!formData.courseLevel) {
            newErrors.courseLevel = 'Course level is required';
            isValid = false;
        }
        if (!formData.validPeriod) {
            newErrors.validPeriod = 'Course duration value is required';
            isValid = false;

        }
        if (!formData.validPeriodType) {
            newErrors.validPeriodType = 'Course duration unit is required';
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
                    courselevel_id: formData.courseLevel,
                    valid_duration_value: formData.validPeriod,
                    valid_duration_unit: formData.validPeriodType,
                    description: formData.description,
                }
                : {
                    courselevel_id: formData.courseLevel,
                    valid_duration_value: formData.validPeriod,
                    valid_duration_unit: formData.validPeriodType,
                    description: formData.description,
                };

            setLoading(true);

            const action = mode === 'edit' ? courseDurationEdit : courseDurationAdd;

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
            courseLevel: '',
            validPeriod: '',
            validPeriodType: '',
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

    const customFilterOption = (option, inputValue) => {
        if (!inputValue) return true;
        return option.label.toLowerCase().startsWith(inputValue.toLowerCase());
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
                            {mode === 'edit' ? 'Edit Course Duration' : 'Add Course Duration'}
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
                                        Course Level <span className="text-danger">*</span>
                                    </label>
                                    <Select
                                        options={courseLevel.map((option) => ({
                                            value: option.uuid,
                                            label: option.name,
                                        }))}
                                        value={
                                            formData.courseLevel
                                                ? courseLevel
                                                    .map((option) => ({
                                                        value: option.uuid,
                                                        label: option.name,
                                                    }))
                                                    .find((opt) => opt.value === formData.courseLevel)
                                                : null
                                        }
                                        onChange={(selectedOption) =>
                                            handleChange({
                                                target: {
                                                    name: "courseLevel",
                                                    value: selectedOption ? selectedOption.value : "",
                                                },
                                            })
                                        }
                                        filterOption={customFilterOption}
                                        placeholder="Select course level"
                                        isClearable
                                        isSearchable
                                        className={`custom-select-container ${errors.courseLevel ? "is-invalid" : ""
                                            }`}
                                        classNamePrefix="custom-select"
                                    />
                                    {errors.courseLevel && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.courseLevel}
                                        </div>
                                    )}
                                </div>
                                <div className="col-12 mb-10">

                                    <div className="row gx-2">
                                        <div className="col-6">
                                            <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                                Course Duration Value <span className="text-danger">*</span>
                                            </label>
                                            <input
                                                type="number"
                                                name="validPeriod"
                                                value={formData.validPeriod}
                                                onChange={handleChange}
                                                className={`form-control radius-8 ${errors.validPeriod ? 'is-invalid' : ''}`}
                                                placeholder="Numeric"
                                            />
                                            {errors.validPeriod && (
                                                <div className="text-danger text-sm mt-1">
                                                    {errors.validPeriod}
                                                </div>
                                            )}
                                        </div>
                                        <div className="col-6">
                                            <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                                Course Duration Unit <span className="text-danger">*</span>
                                            </label>
                                            <select
                                                name="validPeriodType"
                                                value={formData.validPeriodType || ""}
                                                onChange={handleChange}
                                                className={`form-control form-select radius-8 ${errors.validPeriodType ? 'is-invalid' : ''}`}
                                            >
                                                <option value="">Select Course Duration unit</option>
                                                <option value="Weeks">Weeks</option>
                                                <option value="Months">Months</option>
                                                <option value="Years">Years</option>
                                            </select>
                                            {errors.validPeriodType && (
                                                <div className="text-danger text-sm mt-1">
                                                    {errors.validPeriodType}
                                                </div>
                                            )}
                                        </div>
                                    </div>
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
                                        className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-16 py-6 radius-8"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="btn comman-btn-color border border-primary-600 text-md px-16 py-6 radius-8"
                                        disabled={loading}
                                    >
                                        {loading ? (
                                            <>
                                                <span
                                                    className="spinner-border spinner-border-sm me-2"
                                                    role="status"
                                                    aria-hidden="true"
                                                ></span>
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

export default AddEditCourseDurationModal;