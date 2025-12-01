import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";

const AddEditSpouseLanguageModal = ({ show, handleClose, mode, rowData }) => {
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    language: "",
    testName: "",
    testLevel: "",
    listening: "",
    speaking: "",
    reading: "",
    writing: "",
    overall: "",
    testDate: "",
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        language: rowData.language || "",
        testName: rowData.testName || "",
        testLevel: rowData.testLevel || "",
        listening: rowData.listening || "",
        speaking: rowData.speaking || "",
        reading: rowData.reading || "",
        writing: rowData.writing || "",
        overall: rowData.overall || "",
        testDate: rowData.testDate || "",
      });
    }
  }, [mode, rowData]);

  const resetForm = () => {
    setFormData({
      language: "",
      testName: "",
      testLevel: "",
      listening: "",
      speaking: "",
      reading: "",
      writing: "",
      overall: "",
      testDate: "",
    });
    setErrors({});
  };

  const handleInput = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (errors[e.target.name]) {
      setErrors({ ...errors, [e.target.name]: "" });
    }
  };

  const validateForm = () => {
    let temp = {};
    let valid = true;

    const requiredFields = [
      "language",
      "testName",
      "testLevel",
      "listening",
      "speaking",
      "reading",
      "writing",
      "overall",
      "testDate",
    ];

    requiredFields.forEach((field) => {
      if (!formData[field]?.toString().trim()) {
        temp[field] = `${field.replace(/([A-Z])/g, " $1")} is required`;
        valid = false;
      }
    });

    ["listening", "speaking", "reading", "writing", "overall"].forEach((field) => {
      if (formData[field] && isNaN(parseFloat(formData[field]))) {
        temp[field] = `${field.replace(/([A-Z])/g, " $1")} must be numeric`;
        valid = false;
      }
    });

    setErrors(temp);
    return valid;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    const payload = mode === "edit" ? { uuid: rowData?.uuid, ...formData } : { ...formData };

    setLoading(true);

    setTimeout(() => {
      setLoading(false);
      toast.success(
        `Spouse Language Ability ${mode === "edit" ? "updated" : "added"} successfully`
      );
      resetForm();
      handleClose(true);
    }, 1000);
  };

  const onClose = () => {
    resetForm();
    setLoading(false);
    handleClose(false);
  };

  if (!show) return null;

  return (
    <div className="modal fade show common-ctl-popup" tabIndex="-1" role="dialog" aria-hidden={!show}>
      <div className="modal-dialog modal-xl modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          
          {/* HEADER */}
          <div className="modal-header py-16 px-20 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5">
              {mode === "edit" ? "Edit Spouse Language Ability" : "Add Spouse Language Ability"}
            </h1>
            <button type="button" className="btn-close" onClick={onClose} />
          </div>

          {/* BODY */}
          <div className="modal-body p-24 pt-10">
            <form onSubmit={handleSubmit}>
              <div className="row gx-2">

                {/* Language */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">Language <span className="text-danger">*</span></label>
                  <input
                    type="text"
                    name="language"
                    value={formData.language}
                    onChange={handleInput}
                    placeholder="Enter language"
                    className={`form-control radius-8 ${errors.language ? "is-invalid" : ""}`}
                  />
                  {errors.language && <div className="text-danger text-sm mt-1">{errors.language}</div>}
                </div>

                {/* Test Name */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">Test Name <span className="text-danger">*</span></label>
                  <input
                    type="text"
                    name="testName"
                    value={formData.testName}
                    onChange={handleInput}
                    placeholder="Enter test name"
                    className={`form-control radius-8 ${errors.testName ? "is-invalid" : ""}`}
                  />
                  {errors.testName && <div className="text-danger text-sm mt-1">{errors.testName}</div>}
                </div>

                {/* Test Level */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">Test Level <span className="text-danger">*</span></label>
                  <input
                    type="text"
                    name="testLevel"
                    value={formData.testLevel}
                    onChange={handleInput}
                    placeholder="Enter test level"
                    className={`form-control radius-8 ${errors.testLevel ? "is-invalid" : ""}`}
                  />
                  {errors.testLevel && <div className="text-danger text-sm mt-1">{errors.testLevel}</div>}
                </div>

                {/* Listening */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">Listening <span className="text-danger">*</span></label>
                  <input
                    type="number"
                    name="listening"
                    value={formData.listening}
                    onChange={handleInput}
                    placeholder="Enter listening score"
                    className={`form-control radius-8 ${errors.listening ? "is-invalid" : ""}`}
                  />
                  {errors.listening && <div className="text-danger text-sm mt-1">{errors.listening}</div>}
                </div>

                {/* Speaking */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">Speaking <span className="text-danger">*</span></label>
                  <input
                    type="number"
                    name="speaking"
                    value={formData.speaking}
                    onChange={handleInput}
                    placeholder="Enter speaking score"
                    className={`form-control radius-8 ${errors.speaking ? "is-invalid" : ""}`}
                  />
                  {errors.speaking && <div className="text-danger text-sm mt-1">{errors.speaking}</div>}
                </div>

                {/* Reading */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">Reading <span className="text-danger">*</span></label>
                  <input
                    type="number"
                    name="reading"
                    value={formData.reading}
                    onChange={handleInput}
                    placeholder="Enter reading score"
                    className={`form-control radius-8 ${errors.reading ? "is-invalid" : ""}`}
                  />
                  {errors.reading && <div className="text-danger text-sm mt-1">{errors.reading}</div>}
                </div>

                {/* Writing */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">Writing <span className="text-danger">*</span></label>
                  <input
                    type="number"
                    name="writing"
                    value={formData.writing}
                    onChange={handleInput}
                    placeholder="Enter writing score"
                    className={`form-control radius-8 ${errors.writing ? "is-invalid" : ""}`}
                  />
                  {errors.writing && <div className="text-danger text-sm mt-1">{errors.writing}</div>}
                </div>

                {/* Overall */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">Overall <span className="text-danger">*</span></label>
                  <input
                    type="number"
                    name="overall"
                    value={formData.overall}
                    onChange={handleInput}
                    placeholder="Enter overall score"
                    className={`form-control radius-8 ${errors.overall ? "is-invalid" : ""}`}
                  />
                  {errors.overall && <div className="text-danger text-sm mt-1">{errors.overall}</div>}
                </div>

                {/* Test Date */}
                <div className="col-6 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">Test Date <span className="text-danger">*</span></label>
                  <input
                    type="date"
                    name="testDate"
                    value={formData.testDate}
                    onChange={handleInput}
                    placeholder="Select test date"
                    className={`form-control radius-8 ${errors.testDate ? "is-invalid" : ""}`}
                  />
                  {errors.testDate && <div className="text-danger text-sm mt-1">{errors.testDate}</div>}
                </div>

                {/* BUTTONS */}
                <div className="col-12 d-flex justify-content-center gap-3 mt-24">
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
                    ) : mode === "edit" ? (
                      "Update"
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

export default AddEditSpouseLanguageModal;
