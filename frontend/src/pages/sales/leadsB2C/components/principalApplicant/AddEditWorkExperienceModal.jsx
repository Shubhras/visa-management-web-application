import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";

const AddEditWorkExperienceModal = ({ show, handleClose, mode = "add", rowData = null }) => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);


    const [formData, setFormData] = useState({
        uuid: "",
        consider: "Yes",
        country: "",
        state: "",
        employerName: "",
        designation: "",
        startDate: "",
        endDate: "",
        jobType: "Full-Time",
        modeOfSalary: "",
        salaryCurrency: "",
        salaryAmount: "",
        itrStatus: "",
        amount: "",
        expYears: "",
        expMonths: "",
        expDays: ""
    });

    const [errors, setErrors] = useState({});

    // Load rowData in edit mode
    useEffect(() => {
        if (mode === "edit" && rowData) {
            setFormData({
                uuid: rowData.uuid || "",
                consider: rowData.consider || "Yes",
                country: rowData.country || "",
                state: rowData.state || "",
                employerName: rowData.employerName || "",
                designation: rowData.designation || "",
                startDate: rowData.startDate || "",
                endDate: rowData.endDate || "",
                jobType: rowData.jobType || "Full-Time",
                modeOfSalary: rowData.modeOfSalary || "",
                salaryCurrency: rowData.salaryCurrency || "",
                salaryAmount: rowData.salaryAmount || "",
                itrStatus: rowData.itrStatus || "",
                amount: rowData.amount || "",
                expYears: rowData.expYears || "",
                expMonths: rowData.expMonths || "",
                expDays: rowData.expDays || ""
            });
        } else {
            resetForm();
        }
    }, [mode, rowData, show]);

    // Handle Input
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));

        if (errors[name]) {
            setErrors((prev) => ({ ...prev, [name]: "" }));
        }
    };

    // Validate
    const validateForm = () => {
        const newErrors = {};
        let valid = true;

        const required = [
            "country",
            "state",
            "employerName",
            "designation",
            "startDate",
            "endDate",
            "jobType",
            "salaryCurrency",
            "salaryAmount"
        ];

        required.forEach((field) => {
            if (!formData[field]?.toString().trim()) {
                newErrors[field] = "This field is required";
                valid = false;
            }
        });

        setErrors(newErrors);
        return valid;
    };

    // Submit
    const handleSubmit = (e) => {
        e.preventDefault();

        if (!validateForm()) return;

        const payload = {
            ...formData
        };

        setLoading(true);

        setTimeout(() => {
            setLoading(false);
            toast.success(`Work experience ${mode === "edit" ? "updated" : "added"} successfully`);
            resetForm();
            handleClose(true);
        }, 800);
    };

    const resetForm = () => {
        setFormData({
            uuid: "",
            consider: "Yes",
            country: "",
            state: "",
            employerName: "",
            designation: "",
            startDate: "",
            endDate: "",
            jobType: "Full-Time",
            modeOfSalary: "",
            salaryCurrency: "",
            salaryAmount: "",
            itrStatus: "",
            amount: "",
            expYears: "",
            expMonths: "",
            expDays: ""
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
        <div className="modal fade show common-ctl-popup" tabIndex={-1} aria-hidden={!show}>
            <div className="modal-dialog modal-xl modal-dialog-centered">
                <div className="modal-content radius-16 bg-base">

                    {/* Header */}
                    <div className="modal-header py-16 px-20 border border-top-0 border-start-0 border-end-0">
                        <h1 className="modal-title fs-5">
                            {mode === "edit" ? "Edit Work Experience" : "Add Work Experience"}
                        </h1>

                        <button type="button" className="btn-close" onClick={onClose} />
                    </div>

                    {/* Body */}
                    <div className="modal-body p-24 pt-10">
                        <form onSubmit={handleSubmit}>
                            <div className="row">

                                {/* Consider */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        Consider?
                                    </label>
                                    <select
                                        name="consider"
                                        value={formData.consider}
                                        onChange={handleChange}
                                        className="form-select radius-8"
                                    >
                                        <option value="Yes">Yes</option>
                                        <option value="No">No</option>
                                    </select>
                                </div>

                                {/* Country + State */}
                                <div className="col-6">
                                    <div className="row gx-2">

                                        <div className="col-6 mb-3">
                                            <label className="form-label text-sm fw-semibold text-primary-light">
                                                Country *
                                            </label>
                                            <input
                                                type="text"
                                                name="country"
                                                value={formData.country}
                                                onChange={handleChange}
                                                className={`form-control radius-8 ${errors.country ? "is-invalid" : ""}`}
                                                placeholder="Enter country"
                                            />
                                            {errors.country && <div className="text-danger text-sm">{errors.country}</div>}
                                        </div>

                                        <div className="col-6 mb-3">
                                            <label className="form-label text-sm fw-semibold text-primary-light">
                                                State *
                                            </label>
                                            <input
                                                type="text"
                                                name="state"
                                                value={formData.state}
                                                onChange={handleChange}
                                                className={`form-control radius-8 ${errors.state ? "is-invalid" : ""}`}
                                                placeholder="Enter state"
                                            />
                                            {errors.state && <div className="text-danger text-sm">{errors.state}</div>}
                                        </div>
                                    </div>
                                </div>

                                {/* Employer Name */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        Employer Name *
                                    </label>
                                    <input
                                        type="text"
                                        name="employerName"
                                        value={formData.employerName}
                                        onChange={handleChange}
                                        className={`form-control radius-8 ${errors.employerName ? "is-invalid" : ""}`}
                                        placeholder="Enter employer name"
                                    />
                                    {errors.employerName && <div className="text-danger text-sm">{errors.employerName}</div>}
                                </div>

                                {/* Designation */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        Designation (Job Title) *
                                    </label>
                                    <input
                                        type="text"
                                        name="designation"
                                        value={formData.designation}
                                        onChange={handleChange}
                                        className={`form-control radius-8 ${errors.designation ? "is-invalid" : ""}`}
                                        placeholder="Enter job title"
                                    />
                                    {errors.designation && <div className="text-danger text-sm">{errors.designation}</div>}
                                </div>

                                {/* Job Duration */}
                                <div className="col-6 mb-3">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        Job Duration *
                                    </label>
                                    <div className="row gx-2">
                                        <div className="col-6">
                                            <input
                                                type="date"
                                                name="startDate"
                                                value={formData.startDate}
                                                onChange={handleChange}
                                                className={`form-control radius-8 ${errors.startDate ? "is-invalid" : ""}`}
                                                placeholder="Start Date"
                                            />
                                            {errors.startDate && <div className="text-danger text-sm mt-1">{errors.startDate}</div>}
                                        </div>
                                        <div className="col-6">
                                            <input
                                                type="date"
                                                name="endDate"
                                                value={formData.endDate}
                                                onChange={handleChange}
                                                className={`form-control radius-8 ${errors.endDate ? "is-invalid" : ""}`}
                                                placeholder="End Date"
                                            />
                                            {errors.endDate && <div className="text-danger text-sm mt-1">{errors.endDate}</div>}
                                        </div>
                                    </div>
                                </div>

                                {/* Experience Duration (auto calc placeholder) */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        Experience Duration
                                    </label>
                                    <div className="row gx-2">
                                        <div className="col-4">
                                            <input
                                                type="text"
                                                name="expYears"
                                                value={formData.expYears}
                                                onChange={handleChange}
                                                className="form-control radius-8"
                                                placeholder="Years"
                                            />
                                        </div>
                                        <div className="col-4">
                                            <input
                                                type="text"
                                                name="expMonths"
                                                value={formData.expMonths}
                                                onChange={handleChange}
                                                className="form-control radius-8"
                                                placeholder="Months"
                                            />
                                        </div>
                                        <div className="col-4">
                                            <input
                                                type="text"
                                                name="expDays"
                                                value={formData.expDays}
                                                onChange={handleChange}
                                                className="form-control radius-8"
                                                placeholder="Days"
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Job Type + Mode of Salary */}
                                <div className="col-6">
                                    <div className="row gx-2">

                                        <div className="col-6 mb-3">
                                            <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                                Job Type *
                                            </label>
                                            <select
                                                name="jobType"
                                                value={formData.jobType}
                                                onChange={handleChange}
                                                className="form-select radius-8"
                                            >
                                                <option value="Full-Time">Full-Time</option>
                                                <option value="Part-Time">Part-Time</option>
                                                <option value="Contract">Contract</option>
                                                <option value="Internship">Internship</option>
                                            </select>
                                        </div>

                                        <div className="col-6 mb-3">
                                            <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                                Mode of Salary
                                            </label>
                                            <input
                                                type="text"
                                                name="modeOfSalary"
                                                value={formData.modeOfSalary}
                                                onChange={handleChange}
                                                className="form-control radius-8"
                                                placeholder="e.g., Bank, Cash"
                                            />
                                        </div>

                                    </div>
                                </div>

                                {/* Monthly Salary */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                        Monthly Salary *
                                    </label>
                                    <div className="row gx-2">
                                        <div className="col-4">
                                            <input
                                                type="text"
                                                name="salaryCurrency"
                                                value={formData.salaryCurrency}
                                                onChange={handleChange}
                                                className={`form-control radius-8 ${errors.salaryCurrency ? "is-invalid" : ""}`}
                                                placeholder="Currency"
                                            />
                                            {errors.salaryCurrency && (
                                                <div className="text-danger text-sm">{errors.salaryCurrency}</div>
                                            )}
                                        </div>

                                        <div className="col-8">
                                            <input
                                                type="number"
                                                name="salaryAmount"
                                                value={formData.salaryAmount}
                                                onChange={handleChange}
                                                className={`form-control radius-8 ${errors.salaryAmount ? "is-invalid" : ""}`}
                                                placeholder="Amount"
                                            />
                                            {errors.salaryAmount && (
                                                <div className="text-danger text-sm">{errors.salaryAmount}</div>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                {/* ITR Status + Amount */}
                                <div className="col-6">
                                    <div className="row gx-2">

                                        <div className="col-6 mb-3">
                                            <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                                ITR Status
                                            </label>
                                            <input
                                                type="text"
                                                name="itrStatus"
                                                value={formData.itrStatus}
                                                onChange={handleChange}
                                                className="form-control radius-8"
                                                placeholder="Enter ITR status"
                                            />
                                        </div>

                                        <div className="col-6 mb-3">
                                            <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                                                Amount
                                            </label>
                                            <input
                                                type="number"
                                                name="amount"
                                                value={formData.amount}
                                                onChange={handleChange}
                                                className="form-control radius-8"
                                                placeholder="Numeric"
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

export default AddEditWorkExperienceModal;
