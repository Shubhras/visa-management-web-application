import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import Select from "react-select";
import {
  backlogsGroupList,
  factorForList,
  studyFactorBacklogsAdd,
  studyFactorBacklogsEdit,
} from "../../../../store/actions";

const AddEditStudyFactorBacklogsModal = ({
  show,
  handleClose,
  mode = "add",
  rowData = null,
}) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [factorForData, setFactorForData] = useState([]);
  const [backlogsGroupData, setBacklogsGroupData] = useState([]);

  // Form state
  const [formData, setFormData] = useState({
    uuid: "",
    factorForName: "",
    studyBacklogsGroup: "",
    backlogsAccepted: "",
    maxBacklogsAccepted: "",
    description: "",
  });

  // Validation errors state
  const [errors, setErrors] = useState({
    factorForName: "",
    studyBacklogsGroup: "",
    backlogsAccepted: "",
    maxBacklogsAccepted: "",
  });

  // Populate form data when in edit mode
  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        uuid: rowData.uuid || "",
        factorForName: rowData.factor_for_uuid || "",
        studyBacklogsGroup: rowData.studyAcademicResultGroup || "",
        backlogsAccepted: rowData.minimumAcademicResultType || "",
        maxBacklogsAccepted: rowData.minimumAcademicResult || "",
        description: rowData.description || "",
      });
    } else {
      resetForm();
    }
    fetchLists();
  }, [mode, rowData, show]);

  // Fetch Factor For & Backlogs Group lists
  const fetchLists = () => {
    const params = { page: 1, limit: 2000, search: "", status: "", sortBy: "name", sortOrder: "asc" };

    dispatch(
      factorForList(params, (response) => {
        if (response?.statusCode === 200 && response?.status === true) {
          setFactorForData(response?.data || []);
        }
      })
    );

    dispatch(
      backlogsGroupList(params, (response) => {
        if (response?.statusCode === 200 && response?.status === true) {
          setBacklogsGroupData(response?.data || []);
        }
      })
    );
  };

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
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

    if (!formData.factorForName.trim()) {
      newErrors.factorForName = "Factor For is required";
      isValid = false;
    }

    if (!formData.studyBacklogsGroup.trim()) {
      newErrors.studyBacklogsGroup = "Backlogs Group is required";
      isValid = false;
    }

    if (!formData.backlogsAccepted.trim()) {
      newErrors.backlogsAccepted = "Backlogs Accepted is required";
      isValid = false;
    }

    if (!formData.maxBacklogsAccepted.trim()) {
      newErrors.maxBacklogsAccepted = "Maximum Backlogs Accepted is required";
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    const payload = {
      factor_for: formData.factorForName,
      studyBacklogsGroup: formData.studyBacklogsGroup,
      backlogsAccepted: formData.backlogsAccepted,
      maxBacklogsAccepted: formData.maxBacklogsAccepted,
      description: formData.description.trim(),
    };

    if (mode === "edit") payload.uuid = formData.uuid;

    setLoading(true);
    const action = mode === "edit" ? studyFactorBacklogsEdit : studyFactorBacklogsAdd;

    dispatch(
      action(payload, (response, error) => {
        setLoading(false);
        if (error) {
          toast.error(error?.response?.data?.message || "Server error");
        } else if (response?.statusCode === 200 && response?.status === true) {
          toast.success(response?.message);
          resetForm();
          handleClose(true);
        } else {
          toast.error("Something went wrong.");
        }
      })
    );
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      uuid: "",
      factorForName: "",
      studyBacklogsGroup: "",
      backlogsAccepted: "",
      maxBacklogsAccepted: "",
      description: "",
    });
    setErrors({});
  };

  // Handle modal close
  const onClose = () => {
    resetForm();
    setLoading(false);
    handleClose(false);
  };

  if (!show) return null;

  return (
    <div className="modal fade show common-ctl-popup" tabIndex={-1} role="dialog" aria-labelledby="AddEditStudyFactorBacklogsModalLabel" aria-hidden={!show}>
      <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5" id="AddEditStudyFactorBacklogsModalLabel">
              {mode === "edit" ? "Edit Study Factor : Backlogs" : "Add Study Factor : Backlogs"}
            </h1>
            <button type="button" className="btn-close" onClick={onClose} aria-label="Close" />
          </div>

          <div className="modal-body p-24">
            <form onSubmit={handleSubmit}>
              <div className="row">
                {/* Factor For */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Factor For <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={factorForData.map((option) => ({ value: option.uuid, label: option.name }))}
                    value={factorForData.find((opt) => opt.value === formData.factorForName) || null}
                    onChange={(selected) =>
                      handleChange({ target: { name: "factorForName", value: selected ? selected.value : "" } })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Factor For"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${errors.factorForName ? "is-invalid" : ""}`}
                    classNamePrefix="custom-select"
                  />
                  {errors.factorForName && <div className="text-danger text-sm mt-1">{errors.factorForName}</div>}
                </div>

                {/* Backlogs Group */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Study : Backlogs Group <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={backlogsGroupData.map((option) => ({ value: option.uuid, label: option.name }))}
                    value={backlogsGroupData.find((opt) => opt.value === formData.studyBacklogsGroup) || null}
                    onChange={(selected) =>
                      handleChange({ target: { name: "studyBacklogsGroup", value: selected ? selected.value : "" } })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Backlogs Group"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${errors.studyBacklogsGroup ? "is-invalid" : ""}`}
                    classNamePrefix="custom-select"
                  />
                  {errors.studyBacklogsGroup && <div className="text-danger text-sm mt-1">{errors.studyBacklogsGroup}</div>}
                </div>

                {/* Backlogs Accepted */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Backlogs Accepted <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={[
                      { value: "Yes", label: "Yes" },
                      { value: "No", label: "No" },
                    ]}
                    value={formData.backlogsAccepted ? { value: formData.backlogsAccepted, label: formData.backlogsAccepted } : null}
                    onChange={(selected) =>
                      handleChange({ target: { name: "backlogsAccepted", value: selected ? selected.value : "" } })
                    }
                    filterOption={customFilterOption}
                    placeholder="Select Yes / No"
                    isClearable
                    isSearchable
                    className={`custom-select-container ${errors.backlogsAccepted ? "is-invalid" : ""}`}
                    classNamePrefix="custom-select"
                  />
                  {errors.backlogsAccepted && <div className="text-danger text-sm mt-1">{errors.backlogsAccepted}</div>}
                </div>

                {/* Maximum Backlogs Accepted */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Maximum Backlogs Accepted <span className="text-danger">*</span>
                  </label>
                  <input
                    type="number"
                    name="maxBacklogsAccepted"
                    value={formData.maxBacklogsAccepted}
                    onChange={handleChange}
                    placeholder="Maximum Backlogs Accepted"
                    className={`form-control custom-select-container ${errors.maxBacklogsAccepted ? "is-invalid" : ""}`}
                  />
                  {errors.maxBacklogsAccepted && <div className="text-danger text-sm mt-1">{errors.maxBacklogsAccepted}</div>}
                </div>

                {/* Description */}
                <div className="col-12 mb-20">
                  <label htmlFor="desc" className="form-label fw-semibold text-primary-light text-sm mb-8">
                    Description
                  </label>
                  <textarea
                    className="form-control"
                    id="desc"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    rows={4}
                    placeholder="Description"
                  />
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

export default AddEditStudyFactorBacklogsModal;
