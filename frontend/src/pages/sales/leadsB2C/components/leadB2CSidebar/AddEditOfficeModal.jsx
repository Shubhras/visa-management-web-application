import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";

const AddEditOfficeModal = ({ show, handleClose, mode, rowData }) => {
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    teamName: "",
    department: "",
    teamLeader: "",
    teamSupervisor: "",
    operativeExecutive: "",
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        teamName: rowData.teamName || "",
        department: rowData.department || "",
        teamLeader: rowData.teamLeader || "",
        teamSupervisor: rowData.teamSupervisor || "",
        operativeExecutive: rowData.operativeExecutive || "",
      });
    }
  }, [mode, rowData]);

  const resetForm = () => {
    setFormData({
      teamName: "",
      department: "",
      teamLeader: "",
      teamSupervisor: "",
      operativeExecutive: "",
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

    if (!formData.teamName) {
      temp.teamName = "Team Name is required";
      valid = false;
    }
    if (!formData.department) {
      temp.department = "Department is required";
      valid = false;
    }
    if (!formData.teamLeader) {
      temp.teamLeader = "Team Leader is required";
      valid = false;
    }
    if (!formData.teamSupervisor) {
      temp.teamSupervisor = "Team Supervisor is required";
      valid = false;
    }
    if (!formData.operativeExecutive) {
      temp.operativeExecutive = "Operative Executive is required";
      valid = false;
    }

    setErrors(temp);
    return valid;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (validateForm()) {
      const payload = {
        ...formData,
        ...(mode === "edit" && rowData?.uuid ? { uuid: rowData.uuid } : {}),
      };

      setLoading(true);

      setTimeout(() => {
        setLoading(false);

        toast.success(
          ` Team ${mode === "edit" ? "updated" : "added"} successfully`
        );

        resetForm();

        handleClose(true, payload); // return data to parent
      }, 1000);
    }
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
      tabIndex="-1"
      role="dialog"
      aria-hidden={!show}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered">
        <div className="modal-content radius-16 bg-base">
          {/* HEADER */}
          <div className="modal-header py-16 px-20 border-bottom">
            <h1 className="modal-title fs-5">
              {mode === "edit" ? "Edit Team" : "Add Team"}
            </h1>
            <button type="button" className="btn-close" onClick={onClose} />
          </div>

          {/* BODY */}
          <div className="modal-body p-24 pt-10">
            <form onSubmit={handleSubmit}>
              <div className="row gx-2">
                {/* Team Name */}
                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Team Name <span className="text-danger">*</span>
                  </label>
                  <input
                    name="teamName"
                    placeholder="Enter team name"
                    className={`form-control radius-8 ${
                      errors.teamName ? "is-invalid" : ""
                    }`}
                    value={formData.teamName}
                    onChange={handleInput}
                  />
                  {errors.teamName && (
                    <div className="text-danger text-sm mt-1">
                      {errors.teamName}
                    </div>
                  )}
                </div>

                {/* Department */}
                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Department <span className="text-danger">*</span>
                  </label>
                  <input
                    name="department"
                    placeholder="Enter department"
                    className={`form-control radius-8 ${
                      errors.department ? "is-invalid" : ""
                    }`}
                    value={formData.department}
                    onChange={handleInput}
                  />
                  {errors.department && (
                    <div className="text-danger text-sm mt-1">
                      {errors.department}
                    </div>
                  )}
                </div>

                {/* Team Leader */}
                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Team Leader <span className="text-danger">*</span>
                  </label>
                  <input
                    name="teamLeader"
                    placeholder="Enter team leader name"
                    className={`form-control radius-8 ${
                      errors.teamLeader ? "is-invalid" : ""
                    }`}
                    value={formData.teamLeader}
                    onChange={handleInput}
                  />
                  {errors.teamLeader && (
                    <div className="text-danger text-sm mt-1">
                      {errors.teamLeader}
                    </div>
                  )}
                </div>

                {/* Team Supervisor */}
                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Team Supervisor <span className="text-danger">*</span>
                  </label>
                  <input
                    name="teamSupervisor"
                    placeholder="Enter team supervisor name"
                    className={`form-control radius-8 ${
                      errors.teamSupervisor ? "is-invalid" : ""
                    }`}
                    value={formData.teamSupervisor}
                    onChange={handleInput}
                  />
                  {errors.teamSupervisor && (
                    <div className="text-danger text-sm mt-1">
                      {errors.teamSupervisor}
                    </div>
                  )}
                </div>

                {/* Operative Executive */}
                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold text-sm mb-0">
                    Operative Executive <span className="text-danger">*</span>
                  </label>
                  <input
                    name="operativeExecutive"
                    placeholder="Enter operative executive name"
                    className={`form-control radius-8 ${
                      errors.operativeExecutive ? "is-invalid" : ""
                    }`}
                    value={formData.operativeExecutive}
                    onChange={handleInput}
                  />
                  {errors.operativeExecutive && (
                    <div className="text-danger text-sm mt-1">
                      {errors.operativeExecutive}
                    </div>
                  )}
                </div>

                {/* BUTTONS */}
                <div className="col-12 d-flex justify-content-center gap-3 mt-24">
                  <button
                    type="button"
                    onClick={onClose}
                    className="border border-danger-600 bg-hover-danger-200 text-danger-600 px-16 py-6 radius-6"
                  >
                    Cancel
                  </button>

                  <button
                    type="submit"
                    disabled={loading}
                    className="btn comman-btn-color border border-primary-600 px-16 py-6 radius-6"
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

export default AddEditOfficeModal;
