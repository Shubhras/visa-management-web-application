import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import {
    languageTestResultAdd, languageTestResultEdit, languageNameTestList, languageTestNameList, languageTestModuleNameList, languageBenchmarkLevelList,
    languageNameTestId
} from '../../../../store/master/testMaster/action';
import { toast } from "react-toastify";
import Select from "react-select";
const AddEditLanguageTestResultModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    const [languageNameTest, setLanguageNameTest] = useState([]);
    const [languageTestName, setLanguageTestName] = useState([]);
    const [languageTestModuleName, setLanguageTestModuleName] = useState([]);
    const [languageBenchmarkLevel, setLanguageBenchmarkLevel] = useState([]);
    const [languageTestLoading, setLanguageTestLoading] = useState(false);

    // Form state
    const [formData, setFormData] = useState({
        uuid: '',
        languageNameTest: '',
        shortName: '',
        moduleName: '',
        testResult: '',
        benchmarkLevel: '',
        description: '',
    });

    // Validation errors state
    const [errors, setErrors] = useState({
        languageNameTest: '',
        shortName: '',
        moduleName: '',
        testResult: '',
    });

    // Populate form data when in edit mode
    useEffect(() => {
        if (show) {
            if (mode === 'edit' && rowData) {
                setFormData({
                    uuid: rowData.uuid || '',
                    languageNameTest: rowData?.language?.uuid || '',
                    shortName: rowData?.language_test?.uuid || '',
                    moduleName: rowData?.module_name?.uuid || '',
                    testResult: rowData.numeric_score || '',
                    benchmarkLevel: rowData?.lb_level?.uuid || '',
                    description: rowData.description || '',
                });
                if (rowData?.language?.uuid) {
                    fetchLanguageTestName(rowData?.language?.uuid);
                }
            } else {
                // Reset form when switching to add mode
                setFormData({
                    uuid: '',
                    languageNameTest: '',
                    shortName: '',
                    moduleName: '',
                    testResult: '',
                    benchmarkLevel: '',
                    description: '',
                });
            }
            fetchLanguageTestNameList();
        }
    }, [mode, rowData, show]);

    const fetchLanguageTestNameList = () => {
        setLoading(true);
        const params = {
            page: 1,
            limit: 2000,
            search: '',
            status: '',
            sortBy: 'name', // Field to sort by
            sortOrder: 'asc', // 'asc' or 'desc'
        };
        dispatch(languageNameTestList(params, (response, error) => {
            setLoading(false);
            if (response?.statusCode === 200 && response?.status === true) {
                setLanguageNameTest(response?.data || []);

            }
        }));
        // dispatch(languageTestNameList(params, (response, error) => {
        //     setLoading(false);
        //     if (response?.statusCode === 200 && response?.status === true) {
        //         setLanguageTestName(response?.data || []);

        //     }
        // }));
        dispatch(languageTestModuleNameList(params, (response, error) => {
            setLoading(false);
            if (response?.statusCode === 200 && response?.status === true) {
                setLanguageTestModuleName(response?.data || []);

            }
        }));
        dispatch(languageBenchmarkLevelList(params, (response, error) => {
            setLoading(false);
            if (response?.statusCode === 200 && response?.status === true) {
                setLanguageBenchmarkLevel(response?.data || []);

            }
        }));
    };

    const fetchLanguageTestName = (languageNameId) => {
        setLanguageTestLoading(true);
        const params = {
            page: 1,
            limit: 2000,
            search: '',
            status: '',
            sortBy: 'name',
            sortOrder: 'asc',
            language_id: languageNameId
        };
        dispatch(languageNameTestId(params, (response, error) => {
            setLanguageTestLoading(false);
            if (response?.statusCode === 200 && response?.status === true) {
                setLanguageTestName(response?.data || []);
            } else {
                setLanguageTestName([]);
            }
        }));
    };

    const handleTestChange = (selectedOption) => {
        const languageNameId = selectedOption ? selectedOption.value : "";

        setFormData(prev => ({
            ...prev,
            languageNameTest: languageNameId,
            shortName: ''
        }));
        if (errors.shortName) {
            setErrors(prev => ({
                ...prev,
                shortName: ''
            }));
        }
        if (languageNameId) {
            fetchLanguageTestName(languageNameId);
        } else {
            setLanguageTestName([]);
        }
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
        if (!formData.languageNameTest.trim()) {
            newErrors.languageNameTest = 'Language name(test) is required';
            isValid = false;
        }
        if (!formData.shortName.trim()) {
            newErrors.shortName = 'Language Test Name is required';
            isValid = false;
        }
        if (!formData.moduleName.trim()) {
            newErrors.moduleName = 'Module Name is required';
            isValid = false;
        }

        if (!formData.testResult.trim()) {
            newErrors.testResult = 'Language Test Result is required';
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
                    language_id: formData.languageNameTest,
                    language_test_id: formData.shortName,
                    module_name_id: formData.moduleName,
                    numeric_score: formData.testResult,
                    lb_level_id: formData.benchmarkLevel,
                    description: formData.description,
                }
                : {
                    language_id: formData.languageNameTest,
                    language_test_id: formData.shortName,
                    module_name_id: formData.moduleName,
                    numeric_score: formData.testResult,
                    lb_level_id: formData.benchmarkLevel,
                    description: formData.description,

                };

            setLoading(true);

            const action = mode === 'edit' ? languageTestResultEdit : languageTestResultAdd;

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
            languageNameTest: '',
            shortName: '',
            moduleName: '',
            testResult: '',
            benchmarkLevel: '',
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
                            {mode === 'edit' ? 'Edit Language Test Result' : 'Add Language Test Result'}
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
                                        Language Name (Test) <span className="text-danger">*</span>
                                    </label>
                                    <Select
                                        options={languageNameTest.map((option) => ({
                                            value: option.uuid,
                                            label: option.name,
                                        }))}
                                        value={
                                            formData.languageNameTest
                                                ? languageNameTest
                                                    .map((option) => ({
                                                        value: option.uuid,
                                                        label: option.name,
                                                    }))
                                                    .find((opt) => opt.value === formData.languageNameTest)
                                                : null
                                        }
                                        // onChange={(selectedOption) =>
                                        //     handleChange({
                                        //         target: {
                                        //             name: "languageNameTest",
                                        //             value: selectedOption ? selectedOption.value : "",
                                        //         },
                                        //     })
                                        // }
                                        onChange={handleTestChange}
                                        placeholder="Select language name(test)"
                                        isClearable
                                        isSearchable
                                        className={`custom-select-container ${errors.languageNameTest ? "is-invalid" : ""
                                            }`}
                                        classNamePrefix="custom-select"
                                    />
                                    {errors.languageNameTest && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.languageNameTest}
                                        </div>
                                    )}
                                </div>
                                <div className="col-12 mb-10">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        Language Test Name <span className="text-danger">*</span>
                                    </label>
                                    <Select
                                        options={languageTestName.map((option) => ({
                                            value: option.uuid,
                                            label: option.name,
                                        }))}
                                        value={
                                            formData.shortName
                                                ? languageTestName
                                                    .map((option) => ({
                                                        value: option.uuid,
                                                        label: option.name,
                                                    }))
                                                    .find((opt) => opt.value === formData.shortName)
                                                : null
                                        }
                                        onChange={(selectedOption) =>
                                            handleChange({
                                                target: {
                                                    name: "shortName",
                                                    value: selectedOption ? selectedOption.value : "",
                                                },
                                            })
                                        }
                                        placeholder={
                                            languageTestLoading
                                                ? "Loading language test name..."
                                                : formData.languageNameTest
                                                    ? "Select languge test name"
                                                    : "Please select language name(test)"
                                        }
                                        isClearable
                                        isSearchable
                                        isDisabled={!formData.languageNameTest || languageTestLoading}
                                        isLoading={languageTestLoading}
                                        className={`custom-select-container ${errors.shortName ? "is-invalid" : ""
                                            }`}
                                        classNamePrefix="custom-select"
                                    />
                                    {errors.shortName && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.shortName}
                                        </div>
                                    )}
                                </div>
                                <div className="col-12 mb-10">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        Module Name <span className="text-danger">*</span>
                                    </label>
                                    <Select
                                        options={languageTestModuleName.map((option) => ({
                                            value: option.uuid,
                                            label: option.name,
                                        }))}
                                        value={
                                            formData.moduleName
                                                ? languageTestModuleName
                                                    .map((option) => ({
                                                        value: option.uuid,
                                                        label: option.name,
                                                    }))
                                                    .find((opt) => opt.value === formData.moduleName)
                                                : null
                                        }
                                        onChange={(selectedOption) =>
                                            handleChange({
                                                target: {
                                                    name: "moduleName",
                                                    value: selectedOption ? selectedOption.value : "",
                                                },
                                            })
                                        }
                                        placeholder="Select module name"
                                        isClearable
                                        isSearchable
                                        className={`custom-select-container ${errors.moduleName ? "is-invalid" : ""
                                            }`}
                                        classNamePrefix="custom-select"
                                    />
                                    {errors.moduleName && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.moduleName}
                                        </div>
                                    )}
                                </div>
                                <div className="col-12 mb-10">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        Language Test Result <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="number"
                                        name="testResult"
                                        value={formData.testResult}
                                        onChange={handleChange}
                                        className={`form-control radius-8 ${errors.testResult ? 'is-invalid' : ''}`}
                                        placeholder="Enter language test result"
                                    />
                                    {errors.testResult && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.testResult}
                                        </div>
                                    )}
                                </div>
                                <div className="col-12 mb-10">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        Language Banchmark Level
                                    </label>
                                    <Select
                                        options={languageBenchmarkLevel.map((option) => ({
                                            value: option.uuid,
                                            label: option.name,
                                        }))}
                                        value={
                                            formData.benchmarkLevel
                                                ? languageBenchmarkLevel
                                                    .map((option) => ({
                                                        value: option.uuid,
                                                        label: option.name,
                                                    }))
                                                    .find((opt) => opt.value === formData.benchmarkLevel)
                                                : null
                                        }
                                        onChange={(selectedOption) =>
                                            handleChange({
                                                target: {
                                                    name: "benchmarkLevel",
                                                    value: selectedOption ? selectedOption.value : "",
                                                },
                                            })
                                        }
                                        placeholder="Select language banchmark level"
                                        isClearable
                                        isSearchable
                                        className={`custom-select-container ${errors.benchmarkLevel ? "is-invalid" : ""
                                            }`}
                                        classNamePrefix="custom-select"
                                    />
                                    {errors.benchmarkLevel && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.benchmarkLevel}
                                        </div>
                                    )}
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
                                        className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-16 py-6 radius-6"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="btn comman-btn-color border border-primary-600 text-md px-16 py-6 radius-6"
                                        disabled={loading}
                                    >
                                        {/* {loading ? 'Saving...' : 'Save'} */}
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
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AddEditLanguageTestResultModal;