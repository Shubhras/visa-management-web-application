import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";

const AddEditLanguageAbilityModal = ({
  show,
  handleClose,
  mode = "add",
  rowData = null,
}) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);

  // Form state with only specified fields
  const [formData, setFormData] = useState({
    uuid: "",
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

  const [errors, setErrors] = useState({
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

  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        uuid: rowData.uuid || "",
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
    } else {
      setFormData({
        uuid: "",
        language: "",
        testName: "",
        testLevel: "",
        listening: "",
        speaking: "",
        reading: "",
        writing: "",
        overall: "", //  ADDED
        testDate: "",
      });
    }
  }, [mode, rowData, show]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    // Language
    if (!formData.language.trim()) {
      newErrors.language = "Language is required";
      isValid = false;
    }

    // Test Name
    if (!formData.testName.trim()) {
      newErrors.testName = "Test Name is required";
      isValid = false;
    }

    // Test Level
    if (!formData.testLevel.trim()) {
      newErrors.testLevel = "Test Level is required";
      isValid = false;
    }

    // Listening
    if (!formData.listening.trim()) {
      newErrors.listening = "Listening score is required";
      isValid = false;
    }

    // Speaking
    if (!formData.speaking.trim()) {
      newErrors.speaking = "Speaking score is required";
      isValid = false;
    }

    // Reading
    if (!formData.reading.trim()) {
      newErrors.reading = "Reading score is required";
      isValid = false;
    }

    // Writing
    if (!formData.writing.trim()) {
      newErrors.writing = "Writing score is required";
      isValid = false;
    }

    // Overall
    if (!formData.overall.trim()) {
      newErrors.overall = "Overall score is required";
      isValid = false;
    }

    //TestDate
    if (!formData.testDate.trim()) {
      newErrors.testDate = "Test Date is required";
      isValid = false;
    }
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
              language: formData.language,
              testName: formData.testName,
              testLevel: formData.testLevel,
              listening: formData.listening,
              speaking: formData.speaking,
              reading: formData.reading,
              writing: formData.writing,
              overall: formData.overall,
              testDate: formData.testDate,
            }
          : {
              language: formData.language,
              testName: formData.testName,
              testLevel: formData.testLevel,
              listening: formData.listening,
              speaking: formData.speaking,
              reading: formData.reading,
              writing: formData.writing,
              overall: formData.overall,
              testDate: formData.testDate,
            };

      setLoading(true);

      // For now, just close the modal
      setTimeout(() => {
        setLoading(false);
        toast.success(
          `Education ${mode === "edit" ? "updated" : "added"} successfully`
        );
        resetForm();
        handleClose(true);
      }, 1000);
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      uuid: "",
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
      aria-labelledby="educationModalLabel"
      aria-hidden={!show}
    >
      <div
        className="modal-dialog modal-xl modal-dialog-centered"
        role="document"
      >
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-20 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="educationModalLabel">
              {mode === "edit" ? "Edit Education" : "Add Education"}
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
                <div className="col-12">
                  <div className="row gx-2">
                    {/* Language */}
                    <div className="col-6 mb-3">
                      <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                        Language <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        name="language"
                        value={formData.language}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.language ? "is-invalid" : ""
                        }`}
                        placeholder="Enter language"
                      />
                      {errors.language && (
                        <div className="text-danger text-sm mt-1">
                          {errors.language}
                        </div>
                      )}
                    </div>

                    {/* Test Name */}
                    <div className="col-6 mb-3">
                      <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                        Test Name <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        name="testName"
                        value={formData.testName}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.testName ? "is-invalid" : ""
                        }`}
                        placeholder="Enter test name"
                      />
                      {errors.testName && (
                        <div className="text-danger text-sm mt-1">
                          {errors.testName}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                <div className="col-12">
                  <div className="row gx-2">
                    {/* Test Level */}
                    <div className="col-6 mb-3">
                      <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                        Test Level <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        name="testLevel"
                        value={formData.testLevel}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.testLevel ? "is-invalid" : ""
                        }`}
                        placeholder="Enter test level"
                      />
                      {errors.testLevel && (
                        <div className="text-danger text-sm mt-1">
                          {errors.testLevel}
                        </div>
                      )}
                    </div>

                    {/* Listening */}
                    <div className="col-6 mb-3">
                      <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                        Listening <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        name="listening"
                        value={formData.listening}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.listening ? "is-invalid" : ""
                        }`}
                        placeholder="Enter listening score"
                      />
                      {errors.listening && (
                        <div className="text-danger text-sm mt-1">
                          {errors.listening}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                <div className="col-12">
                  <div className="row gx-2">
                    {/* Speaking */}
                    <div className="col-6 mb-3">
                      <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                        Speaking <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        name="speaking"
                        value={formData.speaking}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.speaking ? "is-invalid" : ""
                        }`}
                        placeholder="Enter speaking score"
                      />
                      {errors.speaking && (
                        <div className="text-danger text-sm mt-1">
                          {errors.speaking}
                        </div>
                      )}
                    </div>

                    {/* Reading */}
                    <div className="col-6 mb-3">
                      <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                        Reading <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        name="reading"
                        value={formData.reading}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.reading ? "is-invalid" : ""
                        }`}
                        placeholder="Enter reading score"
                      />
                      {errors.reading && (
                        <div className="text-danger text-sm mt-1">
                          {errors.reading}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                <div className="col-12">
                  <div className="row gx-2">
                    {/* Writing */}
                    <div className="col-6 mb-3">
                      <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                        Writing <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        name="writing"
                        value={formData.writing}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.writing ? "is-invalid" : ""
                        }`}
                        placeholder="Enter writing score"
                      />
                      {errors.writing && (
                        <div className="text-danger text-sm mt-1">
                          {errors.writing}
                        </div>
                      )}
                    </div>

                    {/* Overall */}
                    <div className="col-6 mb-3">
                      <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                        Overall <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        name="overall"
                        value={formData.overall}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.overall ? "is-invalid" : ""
                        }`}
                        placeholder="Enter overall score"
                      />
                      {errors.overall && (
                        <div className="text-danger text-sm mt-1">
                          {errors.overall}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-0">
                    Test Date <span className="text-danger">*</span>
                  </label>
                  <div className="row gx-2">
                    <div className="col-6">
                      <input
                        type="date"
                        name="testDate"
                        value={formData.testDate}
                        onChange={handleChange}
                        className={`form-control radius-8 ${
                          errors.testDate ? "is-invalid" : ""
                        }`}
                        placeholder="Test Date"
                      />
                      {errors.testDate && (
                        <div className="text-danger text-sm mt-1">
                          {errors.testDate}
                        </div>
                      )}
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

export default AddEditLanguageAbilityModal;
