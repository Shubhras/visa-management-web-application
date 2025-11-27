import React, { useState, useEffect } from 'react';
import { useDispatch } from "react-redux";
import { documentTypeAdd, documentTypeEdit } from "../../../../store/master/visaProcessMaster/action";
import { toast } from "react-toastify";

const AddEditDocumentTypeModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    // Form state
    const [formData, setFormData] = useState({
        uuid: '',
        departmentName: '',
        description: '',
    });

    // Validation errors state
    const [errors, setErrors] = useState({
        departmentName: '',
        description: '',
    });

    // Populate form data when in edit mode
    useEffect(() => {
        if (mode === 'edit' && rowData) {
            setFormData({
                uuid: rowData.uuid || '',
                departmentName: rowData.name || '',
                description: rowData.description || '',
            });
        } else {
            // Reset form when switching to add mode
            setFormData({
                uuid: '',
                departmentName: '',
                description: '',
            });
        }
    }, [mode, rowData, show]);

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
        if (!formData.departmentName.trim()) {
            newErrors.departmentName = 'Document type is required';
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
                    name: formData.departmentName,
                    description: formData.description,
                }
                : {
                    name: formData.departmentName,
                    description: formData.description,
                };

            setLoading(true);

            const action = mode === 'edit' ? documentTypeEdit : documentTypeAdd;

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
                            {mode === 'edit' ? 'Edit Document Type' : 'Add Document Type'}
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
                                        Document Type <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        name="departmentName"
                                        value={formData.departmentName}
                                        onChange={handleChange}
                                        className={`form-control radius-8 ${errors.departmentName ? 'is-invalid' : ''}`}
                                        placeholder="Enter document type"
                                    />
                                    {errors.departmentName && (
                                        <div className="text-danger text-sm mt-1">
                                            {errors.departmentName}
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

export default AddEditDocumentTypeModal;