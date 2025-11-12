import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { degreeAwardedByAdd, degreeAwardedByEdit } from '../../../../store/master/educationMaster/action';
import { toast } from "react-toastify";
import { educationLevelList } from "../../../../store/master/educationMaster/action";
import { countryList } from "../../../../store/master/generalMasters/actions";
const AddEditDegreeAwardedByModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    const [studyMainArea, setStudyMainArea] = useState([]);
    const [studyMajorArea, setStudyMajorArea] = useState([]);


    // console.log("rowData",rowData);
    const [formData, setFormData] = useState({
        uuid: '',
        countryUuid: '',
        educationLevelUuid: '',
        degreeAwardedByName: '',
        description: '',
    });

    const [errors, setErrors] = useState({
        countryUuid: '',
        educationLevelUuid: '',
        degreeAwardedByName: '',
        description: '',
    });

    useEffect(() => {
        if (mode === 'edit' && rowData) {
            setFormData({
                uuid: rowData.uuid || '',
                degreeAwardedByName: rowData.degree_name || '',
                countryUuid: rowData.country || '',
                educationLevelUuid: rowData.education_level || '',
                description: rowData.description || '',
            });
        } else {
            setFormData({
                uuid: '',
                degreeAwardedByName: '',
                countryUuid: '',
                educationLevelUuid: '',
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
                setStudyMainArea(response?.data || []);

            }
        }));
        dispatch(educationLevelList(params, (response, error) => {
            setLoading(false);
            if (response?.statusCode === 200 && response?.status === true) {
                setStudyMajorArea(response?.data || []);

            }
        }));
    };


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

    const validateForm = () => {
        const newErrors = {};
        let isValid = true;
        if (!formData.countryUuid?.trim()) {
            newErrors.countryUuid = 'Country is required';
            isValid = false;
        }
        if (!formData.educationLevelUuid?.trim()) {
            newErrors.educationLevelUuid = 'Education level is required';
            isValid = false;
        }

        if (!formData.degreeAwardedByName?.trim()) {
            newErrors.degreeAwardedByName = 'Degree awarded by is required';
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
                    degree_name: formData.degreeAwardedByName,
                    country: formData.countryUuid,
                    education_level: formData.educationLevelUuid,
                    description: formData.description,
                }
                : {
                    degree_name: formData.degreeAwardedByName,
                    country: formData.countryUuid,
                    education_level: formData.educationLevelUuid,
                    description: formData.description
                };

            setLoading(true);

            const action = mode === 'edit' ? degreeAwardedByEdit : degreeAwardedByAdd;
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

    const resetForm = () => {
        setFormData({
            uuid: '',
            countryUuid: '',
            educationLevelUuid: '',
            degreeAwardedByName: '',
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
                            {mode === 'edit' ? 'Edit Degree Awarded By' : 'Add Degree Awarded By'}
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
                                    <select
                                        name="countryUuid"
                                        value={formData.countryUuid}
                                        onChange={handleChange}
                                        className={`form-control form-select radius-8 ${errors.countryUuid ? 'is-invalid' : ''}`}
                                    >
                                        <option value="">Select country</option>
                                        {studyMainArea.map((option) => (
                                            <option key={option.uuid} value={option.uuid}>
                                                {option.name}
                                            </option>
                                        ))}
                                    </select>
                                    {errors.countryUuid && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.countryUuid}
                                        </div>
                                    )}
                                </div>
                                <div className="col-12 mb-20">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                        Education Level <span className="text-danger">*</span>
                                    </label>
                                    <select
                                        name="educationLevelUuid"
                                        value={formData.educationLevelUuid}
                                        onChange={handleChange}
                                        className={`form-control form-select radius-8 ${errors.educationLevelUuid ? 'is-invalid' : ''}`}
                                    >
                                        <option value="">Select education level</option>
                                        {studyMajorArea.map((option) => (
                                            <option key={option.uuid} value={option.uuid}>
                                                {option.educationlevel}
                                            </option>
                                        ))}
                                    </select>
                                    {errors.educationLevelUuid && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.educationLevelUuid}
                                        </div>
                                    )}
                                </div>
                                <div className="col-12 mb-20">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                        Degree Awarded By <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        name="degreeAwardedByName"
                                        value={formData.degreeAwardedByName}
                                        onChange={handleChange}
                                        className={`form-control radius-8 ${errors.degreeAwardedByName ? 'is-invalid' : ''}`}
                                        placeholder="Enter degree awarded by"
                                    />
                                    {errors.degreeAwardedByName && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.degreeAwardedByName}
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
export default AddEditDegreeAwardedByModal;