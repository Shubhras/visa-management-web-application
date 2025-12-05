import React, { useState } from "react";
import Select from "react-select";

const BasicDetails = () => {
  const genderOptions = [
    { value: "master", label: "Master" },
    { value: "male", label: "Male" },
    { value: "female", label: "Female" },
    { value: "other", label: "Other" },
  ];

  const maritalOptions = [
    { value: "master", label: "Master" },
    { value: "single", label: "Single" },
    { value: "married", label: "Married" },
  ];

  const [gender, setGender] = useState(null);
  const [maritalStatus, setMaritalStatus] = useState(null);

  return (
    <div className="section-block no-overflow compact-inputs">
      <div className="row gx-5 gy-1">
        {/* First row */}

        <div className="col-md-4">
          <div className="row g-2">
            <div className="col-6">
              <label className="form-label">
                First Name <span className="text-danger">*</span>
              </label>
              <input
                className="form-control form-control-sm "
                placeholder="Text"
              />
            </div>

            <div className="col-6">
              <label className="form-label">
                Last Name <span className="text-danger">*</span>
              </label>
              <input
                className="form-control form-control-sm"
                placeholder="Text"
              />
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="row g-2">
            <div className="col-6">
              <label className="form-label">
                Gender<span className="text-danger">*</span>
              </label>

              {/* React Select Added */}
              <Select
                options={genderOptions}
                value={genderOptions.find((o) => o.value === gender)}
                onChange={(opt) => setGender(opt?.value || null)}
                placeholder="Master"
                isClearable
                classNamePrefix="custom-select"
                className="custom-select-container"
              />
            </div>

            <div className="col-6">
              <label className="form-label">Date of Birth</label>
              <input type="date" className="form-control form-control-sm" />
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="row g-2">
            <div className="col-6">
              <label className="form-label">Marital Status</label>

              {/* React Select Added */}
              <Select
                options={maritalOptions}
                value={maritalOptions.find((o) => o.value === maritalStatus)}
                onChange={(opt) => setMaritalStatus(opt?.value || null)}
                placeholder="Master"
                isClearable
                classNamePrefix="custom-select"
                className="custom-select-container"
              />
            </div>

            <div className="col-6">
              <label className="form-label">Along with</label>
              <input
                className="form-control form-control-sm"
                placeholder="Yes / No (Auto as per Marital Status)"
              />
            </div>
          </div>
        </div>

        {/* Second row */}
        <div className="col-md-4">
          <label className="form-label">Country to Citizen</label>
          <input
            className="form-control form-control-sm"
            placeholder="Master (Country)"
          />
        </div>

        <div className="col-md-4">
          <label className="form-label">Country of Residency</label>
          <input
            className="form-control form-control-sm"
            placeholder="Master (Country)"
          />
        </div>

        <div className="col-md-4">
          <label className="form-label">Residency Status</label>
          <input
            className="form-control form-control-sm"
            placeholder="Master (Visa Main Category) / Default Citizen"
          />
        </div>

        {/* Third row */}
        <div className="col-md-4">
          <label className="form-label">
            Mobile No.<span className="text-danger">*</span>
          </label>
          <div className="d-flex gap-2">
            <input
              className="form-control form-control-sm"
              placeholder="Code"
              style={{ maxWidth: 84 }}
            />
            <input
              className="form-control form-control-sm"
              placeholder="Number"
            />
          </div>
        </div>

        <div className="col-md-4">
          <label className="form-label">
            WhatsApp No.<span className="text-danger">*</span>
          </label>
          <div className="d-flex gap-2">
            <input
              className="form-control form-control-sm"
              placeholder="Code"
              style={{ maxWidth: 84 }}
            />
            <input
              className="form-control form-control-sm"
              placeholder="Number"
            />
          </div>
        </div>

        <div className="col-md-4">
          <label className="form-label">
            Email ID<span className="text-danger">*</span>
          </label>
          <input
            type="email"
            className="form-control form-control-sm"
            placeholder="Text"
          />
        </div>

        {/* Fourth row */}
        <div className="col-md-4">
          <label className="form-label">Address Line - 01</label>
          <input className="form-control form-control-sm" placeholder="Text" />
        </div>

        <div className="col-md-4">
          <label className="form-label">Address Line - 02</label>
          <input className="form-control form-control-sm" placeholder="Text" />
        </div>

        <div className="col-md-4">
          <label className="form-label">Landmark / Area</label>
          <input className="form-control form-control-sm" placeholder="Text" />
        </div>

        {/* Fifth row */}
        <div className="col-md-4">
          <div className="row g-2">
            <div className="col-6">
              <label className="form-label">Country</label>
              <input
                className="form-control form-control-sm"
                placeholder="Master (Country)"
              />
            </div>
            <div className="col-6">
              <label className="form-label">State</label>
              <input
                className="form-control form-control-sm"
                placeholder="Master (State)"
              />
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="row g-2">
            <div className="col-6">
              <label className="form-label">District</label>
              <input
                className="form-control form-control-sm"
                placeholder="Master"
              />
            </div>
            <div className="col-6">
              <label className="form-label">City / Taluka</label>
              <input
                className="form-control form-control-sm"
                placeholder="Master"
              />
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="row g-2">
            <div className="col-6">
              <label className="form-label">Village</label>
              <input
                className="form-control form-control-sm"
                placeholder="Text"
              />
            </div>
            <div className="col-6">
              <label className="form-label">PIN / ZIP</label>
              <input
                className="form-control form-control-sm"
                placeholder="Text"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BasicDetails;
