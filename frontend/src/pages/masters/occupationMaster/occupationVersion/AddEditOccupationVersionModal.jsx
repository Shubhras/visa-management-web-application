import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { occupationVersionAdd, occupationVersionEdit, representingCountryList } from "../../../../store/master/occupationMaster/action";
import { toast } from "react-toastify";
// import { countryList } from "../../../../store/master/generalMasters/actions";
import Select from "react-select";
const AddEditOccupationVersionModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    const [countryDate, setCountryData] = useState([]);

    // Form state
    const [formData, setFormData] = useState({
        uuid: '',
        startDate: '',
        endDate: '',
        country: '',
        departmentName: '',
        description: '',
    });

    // Validation errors state
    const [errors, setErrors] = useState({
        startDate: '',
        country: '',
        departmentName: '',
        description: '',
    });

    // Populate form data when in edit mode
    useEffect(() => {
        if (mode === 'edit' && rowData) {
            setFormData({
                uuid: rowData.uuid || '',
                departmentName: rowData.occupation_version || '',
                description: rowData.description || '',
                startDate: rowData.effect_from || '',
                endDate: rowData.valid_upto || '',
                country: rowData.country_uuid || '',

            });
        } else {
            // Reset form when switching to add mode
            setFormData({
                uuid: '',
                departmentName: '',
                description: '',
                startDate: '',
                endDate: '',
                country: '',
            });
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
        dispatch(representingCountryList(params, (response, error) => {
            setLoading(false);
            if (response?.statusCode === 200 && response?.status === true) {
                setCountryData(response?.data || []);

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
        if (!formData.departmentName?.trim()) {
            newErrors.departmentName = 'Occupation version is required';
            isValid = false;
        }
        if (!formData.startDate) {
            newErrors.startDate = 'Start date is required';
            isValid = false;
        }
        if (!formData.country?.trim()) {
            newErrors.country = 'Country is required';
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
                    effect_from: formData.startDate,
                    valid_upto: formData.endDate,
                    country_id: formData.country,
                    occupation_version: formData.departmentName,
                    description: formData.description,
                }
                : {
                    effect_from: formData.startDate,
                    valid_upto: formData.endDate,
                    country_id: formData.country,
                    occupation_version: formData.departmentName,
                    description: formData.description,
                };

            setLoading(true);

            const action = mode === 'edit' ? occupationVersionEdit : occupationVersionAdd;

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
            startDate: '',
            endDate: '',
            country: '',
            departmentName: '',
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
                            {mode === 'edit' ? 'Edit Occupation Version' : 'Add Occupation Version'}
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
                                        Start Date <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="date"
                                        name="startDate"
                                        value={formData.startDate}
                                        onChange={handleChange}
                                        className={`form-control radius-8 ${errors.startDate ? 'is-invalid' : ''}`}
                                        placeholder="Enter start date"
                                    />
                                    {errors.startDate && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.startDate}
                                        </div>
                                    )}
                                </div>
                                <div className="col-12 mb-20">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                        End Date
                                    </label>
                                    <input
                                        type="date"
                                        name="endDate"
                                        value={formData.endDate}
                                        onChange={handleChange}
                                        className={`form-control radius-8 ${errors.endDate ? 'is-invalid' : ''}`}
                                        placeholder="Enter end date"
                                    />
                                    {errors.endDate && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.endDate}
                                        </div>
                                    )}
                                </div>
                                <div className="col-12 mb-20">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                        Country<span className="text-danger">*</span>
                                    </label>
                                    <Select
                                        options={countryDate.map((option) => ({
                                            value: option.uuid,
                                            label: option.name,
                                        }))}
                                        value={
                                            formData.country
                                                ? countryDate
                                                    .map((option) => ({
                                                        value: option.uuid,
                                                        label: option.name,
                                                    }))
                                                    .find((opt) => opt.value === formData.country)
                                                : null
                                        }
                                        onChange={(selectedOption) =>
                                            handleChange({
                                                target: {
                                                    name: "country",
                                                    value: selectedOption ? selectedOption.value : "",
                                                },
                                            })
                                        }
                                        placeholder="Select country"
                                        isClearable
                                        isSearchable
                                        className={`custom-select-container ${errors.country ? "is-invalid" : ""
                                            }`}
                                        classNamePrefix="custom-select"
                                    />
                                    {errors.country && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.country}
                                        </div>
                                    )}
                                </div>
                                <div className="col-12 mb-20">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                        Occupation Version <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        name="departmentName"
                                        value={formData.departmentName}
                                        onChange={handleChange}
                                        className={`form-control radius-8 ${errors.departmentName ? 'is-invalid' : ''}`}
                                        placeholder="Enter occupation version"
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

export default AddEditOccupationVersionModal;