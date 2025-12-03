import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import Select from "react-select";
import {
  factorForList,
  gapGroupList,
} from "../../../../store/master/studyFactorsMasters/action";
import { representingCountryList } from "../../../../store/master/occupationMaster/action";
import {
  instituteTypeList,
  courseLevelList,
} from "../../../../store/master/instituteMaster/action";
import {
  studyFactorGapAdd,
  studyFactorGapEdit,
} from "../../../../store/actions";

const AddEditStudyFactorGapModal = ({
  show,
  handleClose,
  mode = "add",
  rowData = null,
}) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);

  const [countryListData, setCountryListData] = useState([]);
  const [courseLevelData, setCourseLevelData] = useState([]);
  const [factorForData, setFactorForData] = useState([]);
  const [gapGroupData, setGapGroupData] = useState([]);
  const [instituteTypeData, setInstituteTypeData] = useState([]);

  // Form data UPDATED ACCORDING TO LABELS
  const [formData, setFormData] = useState({
    uuid: "",
    factorFor: "",
    gapGroup: "",
    maximumGapAccepted: "",
    countries: [],
    courseLevels: [],
    instituteTypes: [],
    description: "",
  });

  // Errors also updated according to labels
  const [errors, setErrors] = useState({
    factorFor: "",
    gapGroup: "",
    maximumGapAccepted: "",
    countries: "",
    courseLevels: "",
    instituteTypes: "",
  });

  useEffect(() => {
    if (mode === "edit" && rowData) {
      setFormData({
        uuid: rowData.uuid || "",
        factorFor: rowData.factor_for_uuid || "",
        gapGroup: rowData.study_age_group_uuid || "",
        maximumGapAccepted: rowData.maximumAgeAccepted || "",
        countries: rowData.countryName || [],
        courseLevels: rowData.courseLevel || [],
        instituteTypes: rowData.instituteType || [],
        description: rowData.description || "",
      });
    } else {
      resetForm();
    }

    fetchAllLists();
  }, [mode, rowData, show]);

  const fetchAllLists = () => {
    const params = {
      page: 1,
      limit: 2000,
      search: "",
      status: "",
      sortBy: "name",
      sortOrder: "asc",
    };

    dispatch(
      representingCountryList(params, (response) => {
        if (response?.statusCode === 200) {
          setCountryListData(response.data || []);
        }
      })
    );
    dispatch(
      courseLevelList(params, (response) => {
        if (response?.statusCode === 200) {
          setCourseLevelData(response.data || []);
        }
      })
    );
    dispatch(
      factorForList(params, (response) => {
        if (response?.statusCode === 200) {
          setFactorForData(response.data || []);
        }
      })
    );
    dispatch(
      gapGroupList(params, (response) => {
        if (response?.statusCode === 200) {
          setGapGroupData(response.data || []);
        }
      })
    );
    dispatch(
      instituteTypeList(params, (response) => {
        if (response?.statusCode === 200) {
          setInstituteTypeData(response.data || []);
        }
      })
    );
  };

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

  const customFilter = (option, inputValue) =>
    option.label.toLowerCase().startsWith(inputValue.toLowerCase());

  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    if (!formData.factorFor.trim()) {
      newErrors.factorFor = "Factor For is required";
      isValid = false;
    }

    if (!formData.gapGroup.trim()) {
      newErrors.gapGroup = "GAP Group is required";
      isValid = false;
    }

    if (!formData.maximumGapAccepted.trim()) {
      newErrors.maximumGapAccepted = "Maximum GAP Accepted is required";
      isValid = false;
    }

    if (!formData.countries.length) {
      newErrors.countries = "At least one country is required";
      isValid = false;
    }

    if (!formData.courseLevels.length) {
      newErrors.courseLevels = "At least one course level is required";
      isValid = false;
    }

    if (!formData.instituteTypes.length) {
      newErrors.instituteTypes = "At least one institute type is required";
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    const payload = {
      factor_for: formData.factorFor,
      gap_group: formData.gapGroup,
      maximum_gap_accepted: formData.maximumGapAccepted,
      countries: formData.countries,
      course_levels: formData.courseLevels,
      institute_types: formData.instituteTypes,
      description: formData.description.trim(),
    };

    if (mode === "edit") payload.uuid = formData.uuid;

    setLoading(true);

    const action = mode === "edit" ? studyFactorGapEdit : studyFactorGapAdd;

    dispatch(
      action(payload, (response, error) => {
        setLoading(false);
        if (error) {
          toast.error(error.response?.data?.message || "Server error");
        } else if (response?.status === true) {
          toast.success(response.message);
          resetForm();
          handleClose(true);
        } else {
          toast.error("Something went wrong");
        }
      })
    );
  };

  const resetForm = () => {
    setFormData({
      uuid: "",
      factorFor: "",
      gapGroup: "",
      maximumGapAccepted: "",
      countries: [],
      courseLevels: [],
      instituteTypes: [],
      description: "",
    });
    setErrors({});
  };

  const onClose = () => {
    resetForm();
    handleClose(false);
  };

  if (!show) return null;

  return (
    <div className="modal fade show common-ctl-popup" tabIndex={-1}>
      <div className="modal-dialog modal-lg modal-dialog-centered">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border-bottom">
            <h1 className="modal-title fs-5">
              {mode === "edit" ? "Edit Gap" : "Add Gap"}
            </h1>
            <button type="button" className="btn-close" onClick={onClose} />
          </div>

          <div className="modal-body ">
            <form onSubmit={handleSubmit}>
              <div className="row">
                {/* Factor For */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-sm mb-8">
                    Factor For <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={factorForData.map((o) => ({
                      value: o.uuid,
                      label: o.name,
                    }))}
                    value={factorForData
                      .map((o) => ({ value: o.uuid, label: o.name }))
                      .find((opt) => opt.value === formData.factorFor)}
                    onChange={(opt) =>
                      handleChange({
                        target: { name: "factorFor", value: opt?.value || "" },
                      })
                    }
                    filterOption={customFilter}
                    placeholder="Select Factor For"
                    isClearable
                    classNamePrefix="custom-select"
                  />
                  {errors.factorFor && (
                    <div className="text-danger text-sm mt-1">
                      {errors.factorFor}
                    </div>
                  )}
                </div>

                {/* GAP Group */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-sm mb-8">
                    Study : GAP Group <span className="text-danger">*</span>
                  </label>
                  <Select
                    options={gapGroupData.map((o) => ({
                      value: o.uuid,
                      label: o.name,
                    }))}
                    value={gapGroupData
                      .map((o) => ({ value: o.uuid, label: o.name }))
                      .find((opt) => opt.value === formData.gapGroup)}
                    onChange={(opt) =>
                      handleChange({
                        target: { name: "gapGroup", value: opt?.value || "" },
                      })
                    }
                    filterOption={customFilter}
                    placeholder="Select GAP Group"
                    isClearable
                    classNamePrefix="custom-select"
                  />
                  {errors.gapGroup && (
                    <div className="text-danger text-sm mt-1">
                      {errors.gapGroup}
                    </div>
                  )}
                </div>

                {/* Maximum GAP */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-sm mb-8">
                    Maximum GAP Accepted (Months)
                    <span className="text-danger">*</span>
                  </label>
                  <input
                    type="number"
                    name="maximumGapAccepted"
                    value={formData.maximumGapAccepted}
                    onChange={handleChange}
                    className={`form-control radius-8 ${
                      errors.maximumGapAccepted ? "is-invalid" : ""
                    }`}
                    placeholder="Enter Maximum GAP"
                  />
                  {errors.maximumGapAccepted && (
                    <div className="text-danger text-sm mt-1">
                      {errors.maximumGapAccepted}
                    </div>
                  )}
                </div>

                {/* Countries */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-sm mb-8">
                    Country for Admission<span className="text-danger">*</span>
                  </label>
                  <Select
                    options={countryListData.map((o) => ({
                      value: o.uuid,
                      label: o.name,
                    }))}
                    isMulti
                    value={countryListData
                      .map((o) => ({ value: o.uuid, label: o.name }))
                      .filter((opt) => formData.countries.includes(opt.value))}
                    onChange={(opts) =>
                      handleChange({
                        target: {
                          name: "countries",
                          value: opts?.map((x) => x.value) || [],
                        },
                      })
                    }
                    placeholder="Select Country"
                    classNamePrefix="custom-select"
                  />
                  {errors.countries && (
                    <div className="text-danger text-sm mt-1">
                      {errors.countries}
                    </div>
                  )}
                </div>

                {/* Course Levels */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-sm mb-8">
                    Course Level<span className="text-danger">*</span>
                  </label>
                  <Select
                    options={courseLevelData.map((o) => ({
                      value: o.uuid,
                      label: o.name,
                    }))}
                    isMulti
                    value={courseLevelData
                      .map((o) => ({ value: o.uuid, label: o.name }))
                      .filter((opt) =>
                        formData.courseLevels.includes(opt.value)
                      )}
                    onChange={(opts) =>
                      handleChange({
                        target: {
                          name: "courseLevels",
                          value: opts?.map((x) => x.value) || [],
                        },
                      })
                    }
                    placeholder="Select Course Level"
                    classNamePrefix="custom-select"
                  />
                  {errors.courseLevels && (
                    <div className="text-danger text-sm mt-1">
                      {errors.courseLevels}
                    </div>
                  )}
                </div>

                {/* Institute Types */}
                <div className="col-6 mb-20">
                  <label className="form-label fw-semibold text-sm mb-8">
                    Institute Type<span className="text-danger">*</span>
                  </label>
                  <Select
                    options={instituteTypeData.map((o) => ({
                      value: o.uuid,
                      label: o.name,
                    }))}
                    isMulti
                    value={instituteTypeData
                      .map((o) => ({ value: o.uuid, label: o.name }))
                      .filter((opt) =>
                        formData.instituteTypes.includes(opt.value)
                      )}
                    onChange={(opts) =>
                      handleChange({
                        target: {
                          name: "instituteTypes",
                          value: opts?.map((x) => x.value) || [],
                        },
                      })
                    }
                    placeholder="Select Institute Type"
                    classNamePrefix="custom-select"
                  />
                  {errors.instituteTypes && (
                    <div className="text-danger text-sm mt-1">
                      {errors.instituteTypes}
                    </div>
                  )}
                </div>

                {/* Description */}
                <div className="col-12 mb-20">
                  <label className="form-label fw-semibold text-sm mb-8">
                    Description
                  </label>
                  <textarea
                    className="form-control"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    rows={4}
                    placeholder="Description"
                  />
                </div>

                <div className="d-flex justify-content-center gap-3 mt-24">
                  <button
                    type="button"
                    onClick={onClose}
                    className="border border-danger-600 text-danger-600 bg-hover-danger-200 px-16 py-4 radius-6"
                    disabled={loading}
                  >
                    Cancel
                  </button>

                  <button
                    type="submit"
                    className="btn comman-btn-color border border-primary-600 px-16 py-4 radius-6"
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
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddEditStudyFactorGapModal;
