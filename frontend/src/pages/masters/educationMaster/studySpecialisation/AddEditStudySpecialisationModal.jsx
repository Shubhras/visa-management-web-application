import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { studySpecialisationAdd, studySpecialisationEdit } from '../../../../store/master/educationMaster/action';
import { toast } from "react-toastify";
import { studyMainAreaList, studyMajorAreaList } from '../../../../store/master/educationMaster/action';
import Select from "react-select";
const AddEditStudySpecialisationModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    const [studyMainArea, setStudyMainArea] = useState([]);
    const [studyMajorArea, setStudyMajorArea] = useState([]);


    // console.log("rowData",rowData);
    const [formData, setFormData] = useState({
        uuid: '',
        studyMainAreaUuid: '',
        studyMajorAreaUuid: '',
        studySpecialisationName: '',
        description: '',
    });

    const [errors, setErrors] = useState({
        studyMainAreaUuid: '',
        studyMajorAreaUuid: '',
        studySpecialisationName: '',
        description: '',
    });

    useEffect(() => {
        if (mode === 'edit' && rowData) {
            setFormData({
                uuid: rowData.uuid || '',
                studySpecialisationName: rowData.studyspecialisation || '',
                studyMainAreaUuid: rowData.mainarea_uuid || '',
                studyMajorAreaUuid: rowData.majorarea_uuid || '',
                description: rowData.description || '',
            });
        } else {
            setFormData({
                uuid: '',
                studyMainAreaUuid: '',
                studyMajorAreaUuid: '',
                studySpecialisationName: '',
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
        dispatch(studyMainAreaList(params, (response, error) => {
            setLoading(false);
            if (response?.statusCode === 200 && response?.status === true) {
                setStudyMainArea(response?.data || []);

            }
        }));
        dispatch(studyMajorAreaList(params, (response, error) => {
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
        if (!formData.studyMainAreaUuid?.trim()) {
            newErrors.studyMainAreaUuid = 'Study main area is required';
            isValid = false;
        }
        if (!formData.studyMajorAreaUuid?.trim()) {
            newErrors.studyMajorAreaUuid = 'Study major area is required';
            isValid = false;
        }

        if (!formData.studySpecialisationName?.trim()) {
            newErrors.studySpecialisationName = 'Study specialisation is required';
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
                    studyspecialisation: formData.studySpecialisationName,
                    mainarea_id: formData.studyMainAreaUuid,
                    majorarea_id: formData.studyMajorAreaUuid,
                    description: formData.description,
                }
                : {
                    studyspecialisation: formData.studySpecialisationName,
                    mainarea_id: formData.studyMainAreaUuid,
                    majorarea_id: formData.studyMajorAreaUuid,
                    description: formData.description,
                };

            setLoading(true);

            const action = mode === 'edit' ? studySpecialisationEdit : studySpecialisationAdd;
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
            studyMainAreaUuid: '',
            studyMajorAreaUuid: '',
            studySpecialisationName: '',
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
                            {mode === 'edit' ? 'Edit Study Specialisation' : 'Add Study Specialisation'}
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
                                        Study Main Area <span className="text-danger">*</span>
                                    </label>
                                    {/* <select
                                        name="studyMainAreaUuid"
                                        value={formData.studyMainAreaUuid}
                                        onChange={handleChange}
                                        className={`form-control form-select radius-8 ${errors.studyMainAreaUuid ? 'is-invalid' : ''}`}
                                    >
                                        <option value="">Select  Study Main Area</option>
                                        {studyMainArea.map((option) => (
                                            <option key={option.uuid} value={option.uuid}>
                                                {option.name}
                                            </option>
                                        ))}
                                    </select> */}
                                    <Select
                                        options={studyMainArea.map((option) => ({
                                            value: option.uuid,
                                            label: option.name,
                                        }))}
                                        value={
                                            formData.studyMainAreaUuid
                                                ? studyMainArea
                                                    .map((option) => ({
                                                        value: option.uuid,
                                                        label: option.name,
                                                    }))
                                                    .find((opt) => opt.value === formData.studyMainAreaUuid)
                                                : null
                                        }
                                        onChange={(selectedOption) =>
                                            handleChange({
                                                target: {
                                                    name: "studyMainAreaUuid",
                                                    value: selectedOption ? selectedOption.value : "",
                                                },
                                            })
                                        }
                                        placeholder="Select  Study Main Area"
                                        isClearable
                                        isSearchable
                                        className={`custom-select-container ${errors.studyMainAreaUuid ? "is-invalid" : ""
                                            }`}
                                        classNamePrefix="custom-select"
                                    />
                                    {errors.studyMainAreaUuid && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.studyMainAreaUuid}
                                        </div>
                                    )}
                                </div>
                                <div className="col-12 mb-20">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                        Study Major Area <span className="text-danger">*</span>
                                    </label>
                                    {/* <select
                                        name="studyMajorAreaUuid"
                                        value={formData.studyMajorAreaUuid}
                                        onChange={handleChange}
                                        className={`form-control form-select radius-8 ${errors.studyMajorAreaUuid ? 'is-invalid' : ''}`}
                                    >
                                        <option value="">Select  Study Major Area</option>
                                        {studyMajorArea.map((option) => (
                                            <option key={option.uuid} value={option.uuid}>
                                                {option.majorarea}
                                            </option>
                                        ))}
                                    </select> */}
                                    <Select
                                        options={studyMajorArea.map((option) => ({
                                            value: option.uuid,
                                            label: option.majorarea,
                                        }))}
                                        value={
                                            formData.studyMajorAreaUuid
                                                ? studyMajorArea
                                                    .map((option) => ({
                                                        value: option.uuid,
                                                        label: option.majorarea,
                                                    }))
                                                    .find((opt) => opt.value === formData.studyMajorAreaUuid)
                                                : null
                                        }
                                        onChange={(selectedOption) =>
                                            handleChange({
                                                target: {
                                                    name: "studyMajorAreaUuid",
                                                    value: selectedOption ? selectedOption.value : "",
                                                },
                                            })
                                        }
                                        placeholder="Select Study Major Area"
                                        isClearable
                                        isSearchable
                                        className={`custom-select-container ${errors.studyMajorAreaUuid ? "is-invalid" : ""
                                            }`}
                                        classNamePrefix="custom-select"
                                    />
                                    {errors.studyMajorAreaUuid && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.studyMajorAreaUuid}
                                        </div>
                                    )}
                                </div>
                                <div className="col-12 mb-20">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                        Study Specialisation <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        name="studySpecialisationName"
                                        value={formData.studySpecialisationName}
                                        onChange={handleChange}
                                        className={`form-control radius-8 ${errors.studySpecialisationName ? 'is-invalid' : ''}`}
                                        placeholder="Enter study specialisation"
                                    />
                                    {errors.studySpecialisationName && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.studySpecialisationName}
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

export default AddEditStudySpecialisationModal;