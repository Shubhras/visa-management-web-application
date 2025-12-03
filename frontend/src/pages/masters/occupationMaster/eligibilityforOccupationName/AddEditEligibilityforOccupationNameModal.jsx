import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import Select from "react-select";
import {
    occupationCodeList,
    occupationNameList,
    eligibilityOccupationNameAdd,
    eligibilityOccupationNameEdit,
    occupationVersionList,
    representingCountryList,
} from "../../../../store/master/occupationMaster/action";
import { studyMainAreaList, studyMajorAreaList } from '../../../../store/master/educationMaster/action';

const AddEditEligibilityforOccupationNameModal = ({
    show,
    handleClose,
    mode = "add",
    rowData = null,
}) => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);

    // State for dropdown data
    const [countryListData, setCountryListData] = useState([]);
    const [occupationVersionListData, setOccupationVersionListData] = useState([]);
    const [occupationNameListData, setOccupationNameListData] = useState([]);
    const [occupationCodeListData, setOccupationCodeListData] = useState([]);
    const [studyMainAreaData, setstudyMainAreaData] = useState([]); // Required Study Main Area
    const [studyMajorAreaData, setstudyMajorAreaData] = useState([]); // Required Study Major Area

    // Form state - Changed to arrays for multi-select
    const [formData, setFormData] = useState({
        uuid: "",
        country: "",
        occupationVersion: "",
        occupationName: "",
        occupationCode: "",
        requiredStudyMainArea: [],  // Changed to array
        requiredStudyMajorArea: [],  // Changed to array
    });

    // Validation errors state
    const [errors, setErrors] = useState({
        country: "",
        occupationVersion: "",
        occupationName: "",
        occupationCode: "",
        requiredStudyMainArea: "",
        requiredStudyMajorArea: "",
    });

    // Helper function to convert string to array for edit mode
    const stringToArray = (value) => {
        if (!value) return [];
        if (Array.isArray(value)) return value;
        if (typeof value === 'string') {
            // Check if it's a JSON string or comma-separated string
            try {
                const parsed = JSON.parse(value);
                if (Array.isArray(parsed)) {
                    return parsed;
                }
            } catch (e) {
                // If not JSON, try splitting by comma
                return value.split(',').map(item => item.trim()).filter(item => item);
            }
        }
        return [value];
    };

    // Populate form data when in edit mode
    useEffect(() => {
        if (mode === "edit" && rowData) {
            // Convert string values to arrays for multi-select
            const mainAreas = stringToArray(rowData.required_study_main_area || rowData.occupation_category || "");
            const majorAreas = stringToArray(rowData.required_study_major_area || rowData.occupation_level_code || "");

            setFormData({
                uuid: rowData.uuid || "",
                country: rowData.country || "",
                occupationVersion: rowData.occupation_version || "",
                occupationName: rowData.occupation_name || "",
                occupationCode: rowData.occupation_code || "",
                requiredStudyMainArea: mainAreas,
                requiredStudyMajorArea: majorAreas,
            });
        } else {
            resetForm();
        }

        // Fetch all dropdowns
        fetchAllDropdowns();
    }, [mode, rowData, show]);

    // Fetch all dropdowns
    const fetchAllDropdowns = () => {
        setLoading(true);
        const params = {
            page: 1,
            limit: 2000,
            search: "",
            status: "",
            sortBy: "name",
            sortOrder: "asc",
        };

        // 1. Country List
        dispatch(
            representingCountryList(params, (response, error) => {
                if (response?.statusCode === 200 && response?.status === true) {
                    setCountryListData(response?.data || []);
                }
            })
        );

        // 2. Occupation Version
        dispatch(
            occupationVersionList(params, (response, error) => {
                if (response?.statusCode === 200 && response?.status === true) {
                    setOccupationVersionListData(response?.data || []);
                }
            })
        );

        // 3. Occupation Name
        dispatch(
            occupationNameList(params, (response, error) => {
                if (response?.statusCode === 200 && response?.status === true) {
                    setOccupationNameListData(response?.data || []);
                }
            })
        );

        // 4. Occupation Code
        dispatch(
            occupationCodeList(params, (response, error) => {
                if (response?.statusCode === 200 && response?.status === true) {
                    setOccupationCodeListData(response?.data || []);
                }
            })
        );

        // 5. Occupation Category (Required Study Main Area)
        dispatch(
            studyMainAreaList(params, (response, error) => {
                if (response?.statusCode === 200 && response?.status === true) {
                    setstudyMainAreaData(response?.data || []);
                }
            })
        );

        // 6. Occupation Level Code (Required Study Major Area)
        dispatch(
            studyMajorAreaList(params, (response, error) => {
                setLoading(false);
                if (response?.statusCode === 200 && response?.status === true) {
                    setstudyMajorAreaData(response?.data || []);
                }
            })
        );
    };

    // Handle single select input changes
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));

        // Clear error when user starts typing
        if (errors[name]) {
            setErrors((prev) => ({
                ...prev,
                [name]: "",
            }));
        }
    };

    // Handle multi-select changes
    const handleMultiSelectChange = (selectedOptions, name) => {
        const values = selectedOptions ? selectedOptions.map(option => option.value) : [];
        
        setFormData((prev) => ({
            ...prev,
            [name]: values,
        }));

        // Clear error when user makes a selection
        if (errors[name]) {
            setErrors((prev) => ({
                ...prev,
                [name]: "",
            }));
        }
    };

    // Get selected values for multi-select display
    const getSelectedOptions = (fieldName, dataArray) => {
        const values = formData[fieldName];
        if (!Array.isArray(values) || values.length === 0) return [];
        
        return dataArray
            .filter(option => values.includes(option.uuid))
            .map(option => ({
                value: option.uuid,
                label: fieldName === 'requiredStudyMajorArea' ? option.majorarea : option.name
            }));
    };

    // Custom filter for Select
    const customFilterOption = (option, inputValue) => {
        if (!inputValue) return true;
        return option.label.toLowerCase().startsWith(inputValue.toLowerCase());
    };

    // Validate form
    const validateForm = () => {
        const newErrors = {};
        let isValid = true;

        if (!formData.country) {
            newErrors.country = "Country is required";
            isValid = false;
        }

        if (!formData.occupationVersion) {
            newErrors.occupationVersion = "Occupation Version is required";
            isValid = false;
        }

        if (!formData.occupationName) {
            newErrors.occupationName = "Occupation Name is required";
            isValid = false;
        }

        if (!formData.occupationCode) {
            newErrors.occupationCode = "Occupation Code is required";
            isValid = false;
        }

        // if (!formData.requiredStudyMainArea || formData.requiredStudyMainArea.length === 0) {
        //     newErrors.requiredStudyMainArea = "Required Study Main Area is required";
        //     isValid = false;
        // }

        // if (!formData.requiredStudyMajorArea || formData.requiredStudyMajorArea.length === 0) {
        //     newErrors.requiredStudyMajorArea = "Required Study Major Area is required";
        //     isValid = false;
        // }
        setErrors(newErrors);
        return isValid;
    };

    // Handle form submission
    const handleSubmit = (e) => {
        e.preventDefault();

        if (validateForm()) {
            const sendPayload =
                mode === "edit"
                    ? {
                        uuid: formData.uuid,
                        country: formData.country,
                        occupation_version: formData.occupationVersion,
                        occupation_name: formData.occupationName,
                        occupation_code: formData.occupationCode,
                        required_study_main_area: formData.requiredStudyMainArea.join(','),
                        required_study_major_area: formData.requiredStudyMajorArea.join(','),
                        
                    }
                    : {
                        country: formData.country,
                        occupation_version: formData.occupationVersion,
                        occupation_name: formData.occupationName,
                        occupation_code: formData.occupationCode,
                        required_study_main_area: formData.requiredStudyMainArea.join(','),
                        required_study_major_area: formData.requiredStudyMajorArea.join(','),
                    };

            setLoading(true);
            const action =
                mode === "edit"
                    ? eligibilityOccupationNameEdit
                    : eligibilityOccupationNameAdd;

            dispatch(
                action(sendPayload, (response, error) => {
                    setLoading(false);
                    if (error) {
                        toast.error(error?.response?.data?.message || "Server error");
                    } else if (
                        response?.statusCode === 200 &&
                        response?.status === true
                    ) {
                        toast.success(response?.message);
                        resetForm();
                        handleClose(true);
                    } else {
                        toast.error("Something went wrong.");
                    }
                })
            );
        }
    };

    // Reset form
    const resetForm = () => {
        setFormData({
            uuid: "",
            country: "",
            occupationVersion: "",
            occupationName: "",
            occupationCode: "",
            requiredStudyMainArea: [],
            requiredStudyMajorArea: [],
        });
        setErrors({});
    };

    // Handle modal close
    const onClose = () => {
        resetForm();
        setLoading(false);
        handleClose(false);
    };

    // Conditional render
    if (!show) return null;

    return (
        <div
            className="modal fade show common-ctl-popup"
            tabIndex={-1}
            role="dialog"
            aria-labelledby="AddEditStateModalLabel"
            aria-hidden={!show}
        >
            <div
                className="modal-dialog modal-lg modal-dialog-centered"
                role="document"
            >
                <div className="modal-content radius-16 bg-base">
                    <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
                        <h1 className="modal-title fs-5" id="AddEditStateModalLabel">
                            {mode === "edit"
                                ? "Eligibility for Occupation Name"
                                : "Eligibility for Occupation Name"}
                        </h1>
                        <button
                            type="button"
                            className="btn-close"
                            onClick={onClose}
                            aria-label="Close"
                        />
                    </div>
                    <div className="modal-body">
                        <form onSubmit={handleSubmit}>
                            <div className="">
                                {/* Country */}
                                <div className='row '>
                                    <div className="col-6 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Country<span className="text-danger">*</span>
                                        </label>
                                        <Select
                                            options={countryListData.map((option) => ({
                                                value: option.uuid,
                                                label: option.name,
                                            }))}
                                            value={
                                                formData.country
                                                    ? countryListData
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
                                            filterOption={customFilterOption}
                                            placeholder="Select Country"
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

                                    {/* Occupation Version */}
                                    <div className="col-6 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Occupation Version<span className="text-danger">*</span>
                                        </label>
                                        <Select
                                            options={occupationVersionListData.map((option) => ({
                                                value: option.uuid,
                                                label: option.occupation_version,
                                            }))}
                                            value={
                                                formData.occupationVersion
                                                    ? occupationVersionListData
                                                        .map((option) => ({
                                                            value: option.uuid,
                                                            label: option.occupation_version,
                                                        }))
                                                        .find(
                                                            (opt) => opt.value === formData.occupationVersion
                                                        )
                                                    : null
                                            }
                                            onChange={(selectedOption) =>
                                                handleChange({
                                                    target: {
                                                        name: "occupationVersion",
                                                        value: selectedOption ? selectedOption.value : "",
                                                    },
                                                })
                                            }
                                            filterOption={customFilterOption}
                                            placeholder="Select Occupation Version"
                                            isClearable
                                            isSearchable
                                            className={`custom-select-container ${errors.occupationVersion ? "is-invalid" : ""
                                                }`}
                                            classNamePrefix="custom-select"
                                        />
                                        {errors.occupationVersion && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.occupationVersion}
                                            </div>
                                        )}
                                    </div>

                                    {/* Occupation Name */}
                                    <div className="col-6 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Occupation Name<span className="text-danger">*</span>
                                        </label>
                                        <Select
                                            options={occupationNameListData.map((option) => ({
                                                value: option.uuid,
                                                label: option.occupationname,
                                            }))}
                                            value={
                                                formData.occupationName
                                                    ? occupationNameListData
                                                        .map((option) => ({
                                                            value: option.uuid,
                                                            label: option.occupationname,
                                                        }))
                                                        .find(
                                                            (opt) => opt.value === formData.occupationName
                                                        )
                                                    : null
                                            }
                                            onChange={(selectedOption) =>
                                                handleChange({
                                                    target: {
                                                        name: "occupationName",
                                                        value: selectedOption ? selectedOption.value : "",
                                                    },
                                                })
                                            }
                                            filterOption={customFilterOption}
                                            placeholder="Select Occupation Name"
                                            isClearable
                                            isSearchable
                                            className={`custom-select-container ${errors.occupationName ? "is-invalid" : ""
                                                }`}
                                            classNamePrefix="custom-select"
                                        />
                                        {errors.occupationName && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.occupationName}
                                            </div>
                                        )}
                                    </div>

                                    {/* Occupation Code */}
                                    <div className="col-6 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Occupation Code<span className="text-danger">*</span>
                                        </label>
                                        <Select
                                            options={occupationCodeListData.map((option) => ({
                                                value: option.uuid,
                                                label: option.occupationcode,
                                            }))}
                                            value={
                                                formData.occupationCode
                                                    ? occupationCodeListData
                                                        .map((option) => ({
                                                            value: option.uuid,
                                                            label: option.occupationcode,
                                                        }))
                                                        .find(
                                                            (opt) => opt.value === formData.occupationCode
                                                        )
                                                    : null
                                            }
                                            onChange={(selectedOption) =>
                                                handleChange({
                                                    target: {
                                                        name: "occupationCode",
                                                        value: selectedOption ? selectedOption.value : "",
                                                    },
                                                })
                                            }
                                            filterOption={customFilterOption}
                                            placeholder="Select Occupation Code"
                                            isClearable
                                            isSearchable
                                            className={`custom-select-container ${errors.occupationCode ? "is-invalid" : ""
                                                }`}
                                            classNamePrefix="custom-select"
                                        />
                                        {errors.occupationCode && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.occupationCode}
                                            </div>
                                        )}
                                    </div>

                                    {/* Required Study Main Area (Occupation Category) - MULTI-SELECT */}
                                    <div className="col-6 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Required Study Main Area
                                        </label>
                                        <Select
                                            options={studyMainAreaData.map((option) => ({
                                                value: option.uuid,
                                                label: option.name,
                                            }))}
                                            value={getSelectedOptions('requiredStudyMainArea', studyMainAreaData)}
                                            onChange={(selectedOptions) =>
                                                handleMultiSelectChange(selectedOptions, 'requiredStudyMainArea')
                                            }
                                            filterOption={customFilterOption}
                                            placeholder="Select Required Study Main Area"
                                            isClearable
                                            isSearchable
                                            isMulti
                                            className={`custom-select-container ${errors.requiredStudyMainArea ? "is-invalid" : ""
                                                }`}
                                            classNamePrefix="custom-select"
                                            closeMenuOnSelect={false}
                                        />
                                        {errors.requiredStudyMainArea && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.requiredStudyMainArea}
                                            </div>
                                        )}
                                    </div>

                                    {/* Required Study Major Area (Occupation Level Code) - MULTI-SELECT */}
                                    <div className="col-6 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Required Study Major Area
                                        </label>
                                        <Select
                                            options={studyMajorAreaData.map((option) => ({
                                                value: option.uuid,
                                                label: option.majorarea,
                                            }))}
                                            value={getSelectedOptions('requiredStudyMajorArea', studyMajorAreaData)}
                                            onChange={(selectedOptions) =>
                                                handleMultiSelectChange(selectedOptions, 'requiredStudyMajorArea')
                                            }
                                            filterOption={customFilterOption}
                                            placeholder="Select Required Study Major Area"
                                            isClearable
                                            isSearchable
                                            isMulti
                                            className={`custom-select-container ${errors.requiredStudyMajorArea ? "is-invalid" : ""
                                                }`}
                                            classNamePrefix="custom-select"
                                            closeMenuOnSelect={false}
                                        />
                                        {errors.requiredStudyMajorArea && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.requiredStudyMajorArea}
                                            </div>
                                        )}
                                    </div>

                                </div>

                                {/* Buttons */}
                                <div className="d-flex align-items-center justify-content-center gap-3 mt-24">
                                    <button
                                        type="button"
                                        onClick={onClose}
                                        className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-16 py-4 radius-6"
                                        disabled={loading}
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

export default AddEditEligibilityforOccupationNameModal;