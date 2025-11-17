import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { degreeAwardedInstituteAdd, degreeAwardedInstituteEdit } from '../../../../store/master/educationMaster/action';
import { toast } from "react-toastify";
import { educationLevelList, degreeAwardedByList } from "../../../../store/master/educationMaster/action";
import { countryDemoList } from '../../../../store/master/companyMasters/actions';
import { stateListByCountry } from '../../../../store/master/generalMasters/actions';
import Select from "react-select";
const AddEditDegreeAwardedInstituteModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    const [studyMajorArea, setStudyMajorArea] = useState([]);
    const [countryListData, setCountryListData] = useState([]);
    const [stateListData, setStateListData] = useState([]);
    const [degreeAwardedBy, setDegreeAwardedBy] = useState([]);

    // console.log("rowData",rowData);
    const [formData, setFormData] = useState({
        uuid: "",
        countryUuid: "",
        stateUuid: "",
        educationLevelUuid: "",
        degreeAwardedBy: "",
        degreeAwardedInstitute: "",
        description: "",
    });

    const [errors, setErrors] = useState({
        countryUuid: '',
        stateUuid: '',
        educationLevelUuid: '',
        degreeAwardedBy: '',
        degreeAwardedInstitute: '',
        description: '',
    });

    useEffect(() => {
        if (mode === 'edit' && rowData) {
            setFormData({
                uuid: rowData.uuid || '',
                countryUuid: rowData.country || "",
                stateUuid: rowData.stateUuid || "",
                educationLevelUuid: rowData.education_level || "",
                degreeAwardedBy: rowData.degreeAwardedBy || "",
                degreeAwardedInstitute: rowData.degreeAwardedInstitute || "",
                description: rowData.description || "",

            });
            if (rowData.countryUuid) {
                fetchStateList(rowData.countryUuid);
            }
        } else {
            setFormData({
                uuid: '',
                countryUuid: '',
                stateUuid: '',
                educationLevelUuid: '',
                degreeAwardedBy: '',
                degreeAwardedInstitute: '',
                description: ''

            });
        }
        fetchStudyList();
        fetchCountryList();
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
        dispatch(educationLevelList(params, (response, error) => {
            setLoading(false);
            if (response?.statusCode === 200 && response?.status === true) {
                setStudyMajorArea(response?.data || []);

            }
        }));
        dispatch(degreeAwardedByList(params, (response, error) => {
            setLoading(false);
            if (response?.statusCode === 200 && response?.status === true) {
                setDegreeAwardedBy(response?.data || []);

            }
        }));
    };

    const fetchCountryList = () => {
        const params = { page: 1, limit: 2000, search: '', sortBy: 'updated_at', sortOrder: 'desc' };
        dispatch(countryDemoList(params, (response, error) => {
            if (response?.statusCode === 200 && response?.status) {
                const formatted = response?.data?.map(item => ({
                    uuid: item.uuid,
                    name: item.name
                })) || [];
                setCountryListData(formatted);

            }
        }));
    };

    const fetchStateList = (countryId) => {
        if (!countryId) return setStateListData([]);

        const params = { countryId };
        dispatch(stateListByCountry(params, (response, error) => {
            if (response?.statusCode === 200 && response?.status) {
                setStateListData(response?.data || []);
            } else {
                setStateListData([]);
            }
        }));
    };



    // const handleChange = (e) => {
    //     const { name, value } = e.target;
    //     setFormData(prev => ({
    //         ...prev,
    //         [name]: value
    //     }));
    //     if (errors[name]) {
    //         setErrors(prev => ({
    //             ...prev,
    //             [name]: ''
    //         }));
    //     }
    // };
    const handleChange = (e) => {
        const { name, value } = e.target;

        setFormData(prev => ({
            ...prev,
            [name]: value,
            ...(name === "countryUuid" ? { stateUuid: "" } : {})
        }));
        if (name === "countryUuid") {
            fetchStateList(value);
        }

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

        if (!formData.countryUuid.trim()) {
            newErrors.countryUuid = "Country is required";
            isValid = false;
        }
        if (!formData.stateUuid.trim()) {
            newErrors.stateUuid = "State is required";
            isValid = false;
        }
        if (!formData.educationLevelUuid.trim()) {
            newErrors.educationLevelUuid = "Education level is required";
            isValid = false;
        }
        if (!formData.degreeAwardedBy.trim()) {
            newErrors.degreeAwardedBy = "Degree awarded by is required";
            isValid = false;
        }
        if (!formData.degreeAwardedInstitute.trim()) {
            newErrors.degreeAwardedInstitute = "Degree awarded institute is required";
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
                    country_id: formData.countryUuid,
                    state_id: formData.stateUuid,
                    education_level_id: formData.educationLevelUuid,
                    degree_awarded_by_id: formData.degreeAwardedBy,
                    name: formData.degreeAwardedInstitute,
                    description: formData.description,
                }
                : {
                    country_id: formData.countryUuid,
                    state_id: formData.stateUuid,
                    education_level_id: formData.educationLevelUuid,
                    degree_awarded_by_id: formData.degreeAwardedBy,
                    name: formData.degreeAwardedInstitute,
                    description: formData.description,
                };

            setLoading(true);

            const action = mode === 'edit' ? degreeAwardedInstituteEdit : degreeAwardedInstituteAdd;
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
            uuid: "",
            countryUuid: "",
            stateUuid: "",
            educationLevelUuid: "",
            degreeAwardedBy: "",
            degreeAwardedInstitute: "",
            description: "",
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
                            {mode === 'edit' ? 'Edit Degree Awarded Institute' : 'Add Degree Awarded Institute'}
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
                                        State<span className="text-danger">*</span>
                                    </label>
                                    <Select
                                        options={stateListData.map((option) => ({
                                            value: option.uuid,
                                            label: option.name,
                                        }))}
                                        value={
                                            formData.stateUuid
                                                ? stateListData
                                                    .map((option) => ({
                                                        value: option.uuid,
                                                        label: option.name,
                                                    }))
                                                    .find((opt) => opt.value === formData.stateUuid)
                                                : null
                                        }
                                        onChange={(selectedOption) =>
                                            handleChange({
                                                target: {
                                                    name: "stateUuid",
                                                    value: selectedOption ? selectedOption.value : "",
                                                },
                                            })
                                        }
                                        placeholder="Select state"
                                        isClearable
                                        isSearchable
                                        className={`custom-select-container ${errors.stateUuid ? "is-invalid" : ""
                                            }`}
                                        classNamePrefix="custom-select"
                                    />
                                    {errors.stateUuid && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.stateUuid}
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
                                    <Select
                                        options={degreeAwardedBy.map((option) => ({
                                            value: option.uuid,
                                            label: option.degree_name,
                                        }))}
                                        value={
                                            formData.degreeAwardedBy
                                                ? degreeAwardedBy
                                                    .map((option) => ({
                                                        value: option.uuid,
                                                        label: option.degree_name,
                                                    }))
                                                    .find((opt) => opt.value === formData.degreeAwardedBy)
                                                : null
                                        }
                                        onChange={(selectedOption) =>
                                            handleChange({
                                                target: {
                                                    name: "degreeAwardedBy",
                                                    value: selectedOption ? selectedOption.value : "",
                                                },
                                            })
                                        }
                                        placeholder="Select degree awarded by"
                                        isClearable
                                        isSearchable
                                        className={`custom-select-container ${errors.degreeAwardedBy ? "is-invalid" : ""
                                            }`}
                                        classNamePrefix="custom-select"
                                    />
                                    {errors.degreeAwardedBy && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.degreeAwardedBy}
                                        </div>
                                    )}
                                </div>
                                <div className="col-12 mb-20">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                        Degree Awarded Institute <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        name="degreeAwardedInstitute"
                                        value={formData.degreeAwardedInstitute}
                                        onChange={handleChange}
                                        className={`form-control radius-8 ${errors.degreeAwardedInstitute ? 'is-invalid' : ''}`}
                                        placeholder="Enter degree awarded institute"
                                    />
                                    {errors.degreeAwardedInstitute && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.degreeAwardedInstitute}
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
export default AddEditDegreeAwardedInstituteModal;