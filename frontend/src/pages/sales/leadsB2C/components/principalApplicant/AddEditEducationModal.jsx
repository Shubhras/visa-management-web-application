import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";

const AddEditEducationModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);

    // Form state with only specified fields
    const [formData, setFormData] = useState({
        uuid: '',
        consider: 'Yes',
        country: '',
        state: '',
        educationLevel: '',
        educationDuration: '',
        studyMainArea: '',
        studyMajorArea: '',
        startDate: '',
        endDate: '',
        resultType: '',
        academicResult: '',
        backlogs: '',
        mediumOfEducation: '',
        educationType: '',
        englishResultType: '',
        englishResult: '',
        mathematicsResultType: '',
        mathematicsResult: '',
        physicsResultType: '',
        physicsResult: ''
    });

    const [errors, setErrors] = useState({
        country: '',
        state: '', // 
        educationLevel: '',
        educationDuration: '',
        studyMajorArea: '', //ADDED
        startDate: '',
        endDate: '', // ADDED
        academicResult: '',
        backlogs: '', // ADDED
        educationType: '' // ADDED

    });

    useEffect(() => {
        if (mode === 'edit' && rowData) {
            setFormData({
                uuid: rowData.uuid || '',
                consider: rowData.consider || 'Yes',
                country: rowData.country || '',
                state: rowData.state || '',
                educationLevel: rowData.educationLevel || '',
                educationDuration: rowData.educationDuration || '',
                studyMainArea: rowData.studyMainArea || '',
                studyMajorArea: rowData.studyMajorArea || '',
                startDate: rowData.startDate || '',
                endDate: rowData.endDate || '',
                resultType: rowData.resultType || '', //  ADDED
                academicResult: rowData.academicResult || '',
                backlogs: rowData.backlogs || '',
                mediumOfEducation: rowData.mediumOfEducation || '',
                educationType: rowData.educationType || '',
                englishResultType: rowData.englishResultType || '', //  ADDED
                englishResult: rowData.englishResult || '', // ADDED
                mathematicsResultType: rowData.mathematicsResultType || '', //  ADDED
                mathematicsResult: rowData.mathematicsResult || '', //  ADDED
                physicsResultType: rowData.physicsResultType || '', // ADDED
                physicsResult: rowData.physicsResult || '' //  ADDED
            });
        } else {
            setFormData({
                uuid: '',
                consider: 'Yes',
                country: '',
                state: '',
                educationLevel: '',
                educationDuration: '',
                studyMainArea: '',
                studyMajorArea: '',
                startDate: '',
                endDate: '',
                resultType: '', //  ADDED
                academicResult: '',
                backlogs: '',
                mediumOfEducation: '',
                educationType: '',
                englishResultType: '', //  ADDED
                englishResult: '', //  ADDED
                mathematicsResultType: '', //  ADDED
                mathematicsResult: '', //  ADDED
                physicsResultType: '', //  ADDED
                physicsResult: '' //  ADDED
            });
        }
    }, [mode, rowData, show]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));

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

        // Country
        if (!formData.country.trim()) {
            newErrors.country = "Country is required";
            isValid = false;
        }

        // State
        if (!formData.state.trim()) {
            newErrors.state = "State is required";
            isValid = false;
        }

        // Education Level
        if (!formData.educationLevel.trim()) {
            newErrors.educationLevel = "Education level is required";
            isValid = false;
        }

        // Education Duration
        if (!formData.educationDuration.trim()) {
            newErrors.educationDuration = "Education duration is required";
            isValid = false;
        }

        // Study Major Area
        if (!formData.studyMajorArea.trim()) {
            newErrors.studyMajorArea = "Study major area is required";
            isValid = false;
        }

        // Start Date
        if (!formData.startDate.trim()) {
            newErrors.startDate = "Start date is required";
            isValid = false;
        }

        // End Date
        if (!formData.endDate.trim()) {
            newErrors.endDate = "End date is required";
            isValid = false;
        }

        // Academic Result
        if (!formData.academicResult.trim()) {
            newErrors.academicResult = "Academic result is required";
            isValid = false;
        }

        // Backlogs
        if (formData.backlogs === "" || formData.backlogs === null) {
            newErrors.backlogs = "Backlogs count is required";
            isValid = false;
        }

        // Education Type
        if (!formData.educationType.trim()) {
            newErrors.educationType = "Education type is required";
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
                    consider: formData.consider,
                    country: formData.country,
                    state: formData.state,
                    educationLevel: formData.educationLevel,
                    educationDuration: formData.educationDuration,
                    studyMainArea: formData.studyMainArea,
                    studyMajorArea: formData.studyMajorArea,
                    startDate: formData.startDate,
                    endDate: formData.endDate,
                    academicResult: formData.academicResult,
                    resultType: formData.resultType,
                    backlogs: formData.backlogs,
                    mediumOfEducation: formData.mediumOfEducation,
                    educationType: formData.educationType,
                    englishResultType: formData.englishResultType,
                    englishResult: formData.englishResult,
                    mathematicsResultType: formData.mathematicsResultType,
                    mathematicsResult: formData.mathematicsResult,
                    physicsResultType: formData.physicsResultType,
                    physicsResult: formData.physicsResult
                }
                : {
                    consider: formData.consider,
                    country: formData.country,
                    state: formData.state,
                    educationLevel: formData.educationLevel,
                    educationDuration: formData.educationDuration,
                    studyMainArea: formData.studyMainArea,
                    studyMajorArea: formData.studyMajorArea,
                    startDate: formData.startDate,
                    endDate: formData.endDate,
                    academicResult: formData.academicResult,
                    resultType: formData.resultType,
                    backlogs: formData.backlogs,
                    mediumOfEducation: formData.mediumOfEducation,
                    educationType: formData.educationType,
                    englishResultType: formData.englishResultType,
                    englishResult: formData.englishResult,
                    mathematicsResultType: formData.mathematicsResultType,
                    mathematicsResult: formData.mathematicsResult,
                    physicsResultType: formData.physicsResultType,
                    physicsResult: formData.physicsResult

                };

            setLoading(true);

            // For now, just close the modal
            setTimeout(() => {
                setLoading(false);
                toast.success(`Education ${mode === 'edit' ? 'updated' : 'added'} successfully`);
                resetForm();
                handleClose(true);
            }, 1000);
        }
    };

    // Reset form
    const resetForm = () => {
        setFormData({
            uuid: '',
            consider: 'Yes',
            country: '',
            state: '',
            educationLevel: '',
            educationDuration: '',
            studyMainArea: '',
            studyMajorArea: '',
            startDate: '',
            endDate: '',
            resultType: '',
            academicResult: '',
            backlogs: '',
            mediumOfEducation: '',
            educationType: '',
            englishResultType: '',
            englishResult: '',
            mathematicsResultType: '',
            mathematicsResult: '',
            physicsResultType: '',
            physicsResult: ''
        });
        setErrors({});
    };


    // Handle modal close
    const onClose = () => {
        resetForm();
        setLoading(false);
        handleClose(false);
    };

    // Options for dropdowns
    const considerOptions = ['Yes', 'No'];

    const educationLevels = [
        'High School',
        'Diploma',
        'Bachelors',
        'Masters',
        'PhD',
        'Post Graduate'
    ];

    const educationTypes = [
        'Full-Time',
        'Part-Time',
        'Distance Learning',
        'Online'
    ];

    const mediumOfEducationOptions = [
        'English',
        'Hindi',
        'Regional Language',
        'Other'
    ];

    // Conditional return after all hooks
    if (!show) return null;

    return (
        <div
            className="modal fade show common-ctl-popup"
            tabIndex={-1}
            role="dialog"
            aria-labelledby="educationModalLabel"
            aria-hidden={!show}
        >
            <div className="modal-dialog modal-xl modal-dialog-centered" role="document">
                <div className="modal-content radius-16 bg-base">
                    <div className="modal-header py-16 px-20 border border-top-0 border-start-0 border-end-0">
                        <h1 className="modal-title fs-5" id="educationModalLabel">
                            {mode === 'edit' ? 'Edit Education' : 'Add Education'}
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

                                {/* Consider */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">Consider?</label>
                                    <select
                                        name="consider"
                                        value={formData.consider}
                                        onChange={handleChange}
                                        className="form-select radius-8"
                                    >
                                        {considerOptions.map(option => (
                                            <option key={option} value={option}>{option}</option>
                                        ))}
                                    </select>
                                </div>

                                {/* Country + State */}
                                <div className="col-6">
                                    <div className="row gx-2">

                                        {/* Country */}
                                        <div className="col-6 mb-3">
                                            <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                                Country <span className="text-danger">*</span>
                                            </label>
                                            <input
                                                type="text"
                                                name="country"
                                                value={formData.country}
                                                onChange={handleChange}
                                                className={`form-control radius-8 ${errors.country ? 'is-invalid' : ''}`}
                                                placeholder="Enter country"
                                            />
                                            {errors.country && <div className="text-danger text-sm mt-1">{errors.country}</div>}
                                        </div>

                                        {/* State */}
                                        <div className="col-6 mb-3">
                                            <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                                State <span className="text-danger">*</span>
                                            </label>
                                            <input
                                                type="text"
                                                name="state"
                                                value={formData.state}
                                                onChange={handleChange}
                                                className={`form-control radius-8 ${errors.state ? 'is-invalid' : ''}`}
                                                placeholder="Enter state"
                                            />
                                            {errors.state && <div className="text-danger text-sm mt-1">{errors.state}</div>}
                                        </div>

                                    </div>
                                </div>

                                {/* Education Level + Duration */}
                                <div className="col-6">
                                    <div className="row gx-2">

                                        {/* Education Level */}
                                        <div className="col-6 mb-3">
                                            <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                                Education Level <span className="text-danger">*</span>
                                            </label>
                                            <select
                                                name="educationLevel"
                                                value={formData.educationLevel}
                                                onChange={handleChange}
                                                className={`form-select radius-8 ${errors.educationLevel ? 'is-invalid' : ''}`}
                                            >
                                                <option value="">Select Education Level</option>
                                                {educationLevels.map(level => (
                                                    <option key={level} value={level}>{level}</option>
                                                ))}
                                            </select>
                                            {errors.educationLevel && <div className="text-danger text-sm mt-1">{errors.educationLevel}</div>}
                                        </div>

                                        {/* Education Duration */}
                                        <div className="col-6 mb-3">
                                            <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                                Education Duration <span className="text-danger">*</span>
                                            </label>
                                            <input
                                                type="text"
                                                name="educationDuration"
                                                value={formData.educationDuration}
                                                onChange={handleChange}
                                                className={`form-control radius-8 ${errors.educationDuration ? 'is-invalid' : ''}`}
                                                placeholder="e.g., 4 Years, 2 Years"
                                            />
                                            {errors.educationDuration && <div className="text-danger text-sm mt-1">{errors.educationDuration}</div>}
                                        </div>

                                    </div>
                                </div>

                                {/* Study Main Area */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">Study Main Area</label>
                                    <input
                                        type="text"
                                        name="studyMainArea"
                                        value={formData.studyMainArea}
                                        onChange={handleChange}
                                        className={`form-control radius-8 ${errors.studyMainArea ? 'is-invalid' : ''}`}
                                        placeholder="e.g., Engineering, Science"
                                    />
                                    {errors.studyMainArea && <div className="text-danger text-sm mt-1">{errors.studyMainArea}</div>}
                                </div>

                                {/* Study Major Area */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        Study Major Area <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        name="studyMajorArea"
                                        value={formData.studyMajorArea}
                                        onChange={handleChange}
                                        className={`form-control radius-8 ${errors.studyMajorArea ? 'is-invalid' : ''}`}
                                        placeholder="e.g., Computer Science, Mechanical"
                                    />
                                    {errors.studyMajorArea && <div className="text-danger text-sm mt-1">{errors.studyMajorArea}</div>}
                                </div>

                                {/* Start + End Dates */}
                                <div className="col-6">
                                    <div className="row gx-2">

                                        {/* Start Date */}
                                        <div className="col-6 mb-3">
                                            <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                                Start Date <span className="text-danger">*</span>
                                            </label>
                                            <input
                                                type="date"
                                                name="startDate"
                                                value={formData.startDate}
                                                onChange={handleChange}
                                                className={`form-control radius-8 ${errors.startDate ? 'is-invalid' : ''}`}
                                            />
                                            {errors.startDate && <div className="text-danger text-sm mt-1">{errors.startDate}</div>}
                                        </div>

                                        {/* End Date */}
                                        <div className="col-6 mb-3">
                                            <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                                End Date <span className="text-danger">*</span>
                                            </label>
                                            <input
                                                type="date"
                                                name="endDate"
                                                value={formData.endDate}
                                                onChange={handleChange}
                                                className={`form-control radius-8 ${errors.endDate ? 'is-invalid' : ''}`}
                                            />
                                            {errors.endDate && <div className="text-danger text-sm mt-1">{errors.endDate}</div>}
                                        </div>

                                    </div>
                                </div>

                                {/* Academic Result */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        Academic Result <span className="text-danger">*</span>
                                    </label>
                                    <div className="row gx-2">
                                        <div className="col-6">
                                            <input
                                                type="text"
                                                name="resultType"
                                                value={formData.resultType}
                                                onChange={handleChange}
                                                className="form-control radius-8"
                                                placeholder="Result Type"
                                            />
                                        </div>
                                        <div className="col-6">
                                            <input
                                                type="text"
                                                name="academicResult"
                                                value={formData.academicResult}
                                                onChange={handleChange}
                                                className={`form-control radius-8 ${errors.academicResult ? 'is-invalid' : ''}`}
                                                placeholder="Result Value"
                                            />
                                        </div>
                                    </div>
                                    {errors.academicResult && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.academicResult}
                                        </div>
                                    )}
                                </div>

                                {/* Backlogs + Medium */}
                                <div className="col-6">
                                    <div className="row gx-2">

                                        {/* Backlogs */}
                                        <div className="col-6 mb-3">
                                            <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                                Backlogs <span className="text-danger">*</span>
                                            </label>
                                            <input
                                                type="number"
                                                name="backlogs"
                                                value={formData.backlogs}
                                                onChange={handleChange}
                                                className={`form-control radius-8 ${errors.backlogs ? 'is-invalid' : ''}`}
                                                placeholder="Number of backlogs"
                                            />
                                            {errors.backlogs && <div className="text-danger text-sm mt-1">{errors.backlogs}</div>}
                                        </div>

                                        {/* Medium of Education */}
                                        <div className="col-6 mb-3">
                                            <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                                Medium of Education
                                            </label>
                                            <select
                                                name="mediumOfEducation"
                                                value={formData.mediumOfEducation}
                                                onChange={handleChange}
                                                className="form-select radius-8"
                                            >
                                                <option value="">Select Medium</option>
                                                {mediumOfEducationOptions.map(medium => (
                                                    <option key={medium} value={medium}>{medium}</option>
                                                ))}
                                            </select>
                                        </div>

                                    </div>
                                </div>

                                {/* Education Type */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        Education Type <span className="text-danger">*</span>
                                    </label>
                                    <select
                                        name="educationType"
                                        value={formData.educationType}
                                        onChange={handleChange}
                                        className={`form-select radius-8 ${errors.educationType ? 'is-invalid' : ''}`}
                                    >
                                        <option value="">Select Education Type</option>
                                        {educationTypes.map(type => (
                                            <option key={type} value={type}>{type}</option>
                                        ))}
                                    </select>
                                    {errors.educationType && <div className="text-danger text-sm mt-1">{errors.educationType}</div>}
                                </div>

                                {/* English */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        English Subject Result
                                    </label>
                                    <div className="row gx-2">
                                        <div className="col-6">
                                            <input
                                                type="text"
                                                name="englishResultType"
                                                value={formData.englishResultType}
                                                onChange={handleChange}
                                                className="form-control radius-8"
                                                placeholder="Type"
                                            />
                                        </div>
                                        <div className="col-6">
                                            <input
                                                type="text"
                                                name="englishResult"
                                                value={formData.englishResult}
                                                onChange={handleChange}
                                                className="form-control radius-8"
                                                placeholder="Marks"
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Math */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        Mathematics Subject Result
                                    </label>
                                    <div className="row gx-2">
                                        <div className="col-6">
                                            <input
                                                type="text"
                                                name="mathematicsResultType"
                                                value={formData.mathematicsResultType}
                                                onChange={handleChange}
                                                className="form-control radius-8"
                                                placeholder="e.g., Percentage, GPA"
                                            />
                                        </div>
                                        <div className="col-6">
                                            <input
                                                type="text"
                                                name="mathematicsResult"
                                                value={formData.mathematicsResult}
                                                onChange={handleChange}
                                                className="form-control radius-8"
                                                placeholder="e.g., 85, 3.5"
                                            />
                                        </div>
                                    </div>
                                </div>
                                {/* Physics */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        Physics Subject Result
                                    </label>
                                    <div className="row gx-2">
                                        <div className="col-6">
                                            <input
                                                type="text"
                                                name="physicsResultType"
                                                value={formData.physicsResultType}
                                                onChange={handleChange}
                                                className="form-control radius-8"
                                                placeholder="e.g., Percentage, GPA"
                                            />
                                        </div>
                                        <div className="col-6">
                                            <input
                                                type="text"
                                                name="physicsResult"
                                                value={formData.physicsResult}
                                                onChange={handleChange}
                                                className="form-control radius-8"
                                                placeholder="e.g., 85, 3.5"
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Buttons */}
                                <div className="col-12">
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

                            </div>

                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AddEditEducationModal;