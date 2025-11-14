import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { degreeAwardedByAdd, degreeAwardedByEdit } from '../../../../store/master/educationMaster/action';
import { toast } from "react-toastify";
import { educationLevelList } from "../../../../store/master/educationMaster/action";
import { countryList } from "../../../../store/master/generalMasters/actions";
import Select from "react-select";
const AddEditDegreeAwardedByModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    const [countryListData, setCountryListData] = useState([]);
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
        fetchCountrylList();
        fetchEducationLevelList();
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
        dispatch(countryList(params, (response, error) => {

            if (response?.statusCode === 200 && response?.status === true) {
                setCountryListData(response?.data || []);
            } else {
                setCountryListData([]);
            }
        }));

    };
    const fetchEducationLevelList = () => {
        const params = {
            page: 1,
            limit: 2000,
            search: '',
            status: '',
            sortBy: 'educationlevel',
            sortOrder: 'asc',
        };
        dispatch(educationLevelList(params, (response, error) => {
            if (response?.statusCode === 200 && response?.status === true) {
                setStudyMajorArea(response?.data || []);
            } else {
                setStudyMajorArea([]);
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

    const customFilterOption = (option, inputValue) => {
        if (!inputValue) return true;
        return option.label.toLowerCase().startsWith(inputValue.toLowerCase());
    };
    const customFilterOptionEducation = (option, inputValue) => {
        if (!inputValue) return true;
        return option.label.toLowerCase().startsWith(inputValue.toLowerCase());
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
                                    <Select
                                        options={countryListData.map((option) => ({
                                            value: option.uuid,
                                            label: option.name,
                                        }))}
                                        value={
                                            formData.countryUuid
                                                ? countryListData
                                                    .map((option) => ({
                                                        value: option.uuid,
                                                        label: option.name,
                                                    }))
                                                    .find((opt) => opt.value === formData.countryUuid)
                                                : null
                                        }
                                        onChange={(selectedOption) =>
                                            handleChange({
                                                target: {
                                                    name: "countryUuid",
                                                    value: selectedOption ? selectedOption.value : "",
                                                },
                                            })
                                        }
                                        filterOption={customFilterOption}
                                        placeholder="Select country"
                                        isClearable
                                        isSearchable
                                        className={`custom-select-container ${errors.countryUuid ? "is-invalid" : ""
                                            }`}
                                        classNamePrefix="custom-select"
                                    />
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
                                    <Select
                                        options={studyMajorArea.map((option) => ({
                                            value: option.uuid,
                                            label: option.educationlevel,
                                        }))}
                                        value={
                                            formData.educationLevelUuid
                                                ? studyMajorArea
                                                    .map((option) => ({
                                                        value: option.uuid,
                                                        label: option.educationlevel,
                                                    }))
                                                    .find((opt) => opt.value === formData.educationLevelUuid)
                                                : null
                                        }
                                        onChange={(selectedOption) =>
                                            handleChange({
                                                target: {
                                                    name: "educationLevelUuid",
                                                    value: selectedOption ? selectedOption.value : "",
                                                },
                                            })
                                        }
                                        filterOption={customFilterOptionEducation}
                                        placeholder="Select education level"
                                        isClearable
                                        isSearchable
                                        className={`custom-select-container ${errors.educationLevelUuid ? "is-invalid" : ""
                                            }`}
                                        classNamePrefix="custom-select"
                                    />
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
export default AddEditDegreeAwardedByModal;