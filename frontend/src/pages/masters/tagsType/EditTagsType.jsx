import React, { useState, useEffect } from 'react'
import { useDispatch } from "react-redux";
import { tagsTypeEdit } from '../../../store/master/actions';
import { toast } from "react-toastify";
const EditTagsType = ({ show, handleCloseEdit, rowSelectData }) => {
    const [loading, setLoading] = useState(false);
    const dispatch = useDispatch();
    // Form state
    const [formData, setFormData] = useState({
        uuid: '',
        name: '',
        description: '',
    });

    useEffect(() => {
        if (rowSelectData) {
            setFormData({
                uuid: rowSelectData.uuid || '',
                name: rowSelectData.name || '',
                description: rowSelectData.description || '',
            })
        }
    }, [rowSelectData]);

    // Validation errors state
    const [errors, setErrors] = useState({
        name: '',
        description: '',
    });

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

        // Name validation
        if (!formData.name.trim()) {
            newErrors.name = 'Name is required';
            isValid = false;
        }
        setErrors(newErrors);
        return isValid;
    };

    // Handle form submission
    const handleSubmit = (e) => {
        e.preventDefault();
        if (validateForm()) {
            setLoading(true);
            const sendPayload = {
                uuid: formData.uuid,
                name: formData.name,
                description: formData.description,

            };
            dispatch(tagsTypeEdit(sendPayload, (response, error) => {
                setLoading(false);
                if (error) {
                    toast.error(error?.response?.data?.message || "server error");
                } else {
                    if (response?.statusCode === 200 && response?.status === true) {
                        toast.success(response?.message);
                        setFormData({
                            uuid: '',
                            name: '',
                            description: '',
                        });
                        setErrors({});
                        handleCloseEdit();
                    } else {
                        toast.error("Something went wrong.");
                    }
                }
            }));
        }
    };

    // Handle modal close
    const onClose = () => {
        // Reset form and errors
        setFormData({
            id: '',
            name: '',
            description: '',
        });
        setErrors({});
        handleCloseEdit();
        setLoading(false);
    };

    // NOW we can do the conditional return - AFTER all hooks
    if (!show) return null;

    return (
        <>
            <div
                className={`modal fade show common-ctl-popup`}
                tabIndex={-1}
                role="dialog"
                aria-labelledby="TagsTypeModalLabel"
                aria-hidden={!show}

            >
                <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
                    <div className="modal-content radius-16 bg-base">
                        <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
                            <h1 className="modal-title fs-5" id="TagsTypeModalLabel">
                                Edit Tags
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
                                    {/*  Name */}
                                    <div className="col-12 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Tags <span className="text-danger">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="name"
                                            value={formData.name}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.name ? 'is-invalid' : ''}`}
                                            placeholder="Enter tags"
                                        />
                                        {errors.name && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.name}
                                            </div>
                                        )}
                                    </div>
                                    {/* Description */}
                                    <div className="col-12 mb-20">
                                        <label
                                            htmlFor="desc"
                                            className="form-label fw-semibold text-primary-light text-sm mb-8"
                                        >
                                            Description <span className="text-danger"></span>
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
        </>
    );
};

export default EditTagsType;