import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { academicResultListByAcademicType, degreeAwardedInstituteAdd, degreeAwardedInstituteEdit } from '../../../../store/master/educationMaster/action';
import { toast } from "react-toastify";
import { educationLevelList } from "../../../../store/master/educationMaster/action";
import { countryDemoList } from '../../../../store/master/companyMasters/actions';
import { stateListByCountry } from '../../../../store/master/generalMasters/actions';
import Select from "react-select";

const AddEditDegreeAwardedInstituteModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    const [educationLevelListData, setEducationLevelListData] = useState([]);
    const [countryListData, setCountryListData] = useState([]);
    const [stateListData, setStateListData] = useState([]);
    const [degreeAwardedBy, setDegreeAwardedBy] = useState([]);

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
        if (show) {
            if (mode === 'edit' && rowData) {
                setFormData({
                    uuid: rowData.uuid || '',
                    countryUuid: rowData.country_uuid || "",
                    stateUuid: rowData.state_uuid || "",
                    educationLevelUuid: rowData.education_level_uuid || "",
                    degreeAwardedBy: rowData.degree_awarded_by_uuid || "",
                    degreeAwardedInstitute: rowData.name || "",
                    description: rowData.description || "",
                });
                if (rowData.country_uuid) {
                    fetchStateList(rowData.country_uuid);
                }
                if (rowData.education_level_uuid) {
                    fetchDegreeAwardedByList(rowData.education_level_uuid);
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
            fetchEducationlevelList();
            fetchCountryList();
        }
    }, [mode, rowData, show]);

    const fetchEducationlevelList = () => {
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
                setEducationLevelListData(response?.data || []);
            }
        }));
    };

    const fetchDegreeAwardedByList = (educationLevelId) => {
        if (!educationLevelId) {
            setDegreeAwardedBy([]);
            return;
        }
        const params = {
            page: 1,
            limit: 2000,
            search: '',
            status: '',
            sortBy: 'degree_name',
            sortOrder: 'asc',
            educationLevelId: educationLevelId
        };

        dispatch(academicResultListByAcademicType(params, (response, error) => {
            if (response?.statuscode === 200 && response?.status === true) {
                setDegreeAwardedBy(response?.data || []);
            } else {
                setDegreeAwardedBy([]);
            }
        }));
    };

    const fetchCountryList = () => {
        const params = { page: 1, limit: 2000, search: '', sortBy: 'name', sortOrder: 'asc' };
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
        if (!countryId) {
            setStateListData([]);
            return;
        }

        const params = { countryId };
        dispatch(stateListByCountry(params, (response, error) => {
            if (response?.statusCode === 200 && response?.status) {
                setStateListData(response?.data || []);
            } else {
                setStateListData([]);
            }
        }));
    };

    const handleChange = (e) => {
        const { name, value } = e.target;

        setFormData(prev => ({
            ...prev,
            [name]: value,
            ...(name === "countryUuid" ? { stateUuid: "" } : {}),
            ...(name === "educationLevelUuid" ? { degreeAwardedBy: "" } : {})
        }));

        if (name === "countryUuid") {
            fetchStateList(value);
        }

        if (name === "educationLevelUuid") {
            fetchDegreeAwardedByList(value);
        }

        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    const customFilterOptionCountry = (option, inputValue) => {
        if (!inputValue) return true;
        return option.label.toLowerCase().startsWith(inputValue.toLowerCase());
    };

    const customFilterOptionState = (option, inputValue) => {
        if (!inputValue) return true;
        return option.label.toLowerCase().startsWith(inputValue.toLowerCase());
    };

    const customFilterOptionEducationLevel = (option, inputValue) => {
        if (!inputValue) return true;
        return option.label.toLowerCase().startsWith(inputValue.toLowerCase());
    };

    const customFilterOptionDegreeAwardedBy = (option, inputValue) => {
        if (!inputValue) return true;
        return option.label.toLowerCase().startsWith(inputValue.toLowerCase());
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
                        handleClose(true);
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

    const onClose = () => {
        resetForm();
        setLoading(false);
        handleClose(false);
    };

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
                                        filterOption={customFilterOptionCountry}
                                        placeholder="Select country"
                                        isClearable
                                        isSearchable
                                        className={`custom-select-container ${errors.countryUuid ? "is-invalid" : ""}`}
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
                                        filterOption={customFilterOptionState}
                                        placeholder="Select state"
                                        isClearable
                                        isSearchable
                                        isDisabled={!formData.countryUuid}
                                        className={`custom-select-container ${errors.stateUuid ? "is-invalid" : ""}`}
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
                                        options={educationLevelListData.map((option) => ({
                                            value: option.uuid,
                                            label: option.educationlevel,
                                        }))}
                                        value={
                                            formData.educationLevelUuid
                                                ? educationLevelListData
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
                                        filterOption={customFilterOptionEducationLevel}
                                        placeholder="Select education level"
                                        isClearable
                                        isSearchable
                                        className={`custom-select-container ${errors.educationLevelUuid ? "is-invalid" : ""}`}
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
                                        filterOption={customFilterOptionDegreeAwardedBy}
                                        placeholder="Select degree awarded by"
                                        isClearable
                                        isSearchable
                                        isDisabled={!formData.educationLevelUuid}
                                        className={`custom-select-container ${errors.degreeAwardedBy ? "is-invalid" : ""}`}
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

export default AddEditDegreeAwardedInstituteModal;