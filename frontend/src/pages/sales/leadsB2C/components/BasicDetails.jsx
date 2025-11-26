import React from 'react';

const BasicDetails = () => {
    return (
        <div className="section-block">
            <div className="row g-3">
                {/* First row */}
                <div className="col-md-3">
                    <label className="form-label">
                        First Name<span className="text-danger">*</span>
                    </label>
                    <input className="form-control form-control-sm" placeholder="Text" />
                </div>
                <div className="col-md-3">
                    <label className="form-label">
                        Last Name<span className="text-danger">*</span>
                    </label>
                    <input className="form-control form-control-sm" placeholder="Text" />
                </div>
                <div className="col-md-3">
                    <label className="form-label">
                        Gender<span className="text-danger">*</span>
                    </label>
                    <select className="form-select form-select-sm">
                        <option>Master</option>
                    </select>
                </div>
                <div className="col-md-3">
                    <label className="form-label">Date of Birth</label>
                    <input type="date" className="form-control form-control-sm" />
                </div>

                {/* Second row */}
                <div className="col-md-3">
                    <label className="form-label">Marital Status</label>
                    <select className="form-select form-select-sm">
                        <option>Master</option>
                    </select>
                </div>
                <div className="col-md-3">
                    <label className="form-label">Along with</label>
                    <input
                        className="form-control form-control-sm"
                        placeholder="Yes / No (Auto as per Marital Status)"
                        readOnly
                    />
                </div>
                <div className="col-md-3">
                    <label className="form-label">Country to Citizen</label>
                    <input
                        className="form-control form-control-sm"
                        placeholder="Master (Country)"
                    />
                </div>
                <div className="col-md-3">
                    <label className="form-label">Country of Residency</label>
                    <input
                        className="form-control form-control-sm"
                        placeholder="Master (Country)"
                    />
                </div>

                {/* Third row */}
                <div className="col-md-3">
                    <label className="form-label">Residency Status</label>
                    <input
                        className="form-control form-control-sm"
                        placeholder="Master (Visa Main Category) / Default Citizen"
                    />
                </div>
                <div className="col-md-3">
                    <label className="form-label">
                        Email ID<span className="text-danger">*</span>
                    </label>
                    <input type="email" className="form-control form-control-sm" placeholder="Text" />
                </div>
                <div className="col-md-3">
                    <label className="form-label">
                        Mobile No.<span className="text-danger">*</span>
                    </label>
                    <div className="d-flex gap-2">
                        <input
                            className="form-control form-control-sm"
                            placeholder="Code"
                            style={{ maxWidth: 80 }}
                        />
                        <input
                            className="form-control form-control-sm"
                            placeholder="Number"
                        />
                    </div>
                </div>
                <div className="col-md-3">
                    <label className="form-label">
                        WhatsApp No.<span className="text-danger">*</span>
                    </label>
                    <div className="d-flex gap-2">
                        <input
                            className="form-control form-control-sm"
                            placeholder="Code"
                            style={{ maxWidth: 80 }}
                        />
                        <input
                            className="form-control form-control-sm"
                            placeholder="Number"
                        />
                    </div>
                </div>

                {/* Address rows */}
                <div className="col-md-3">
                    <label className="form-label">Address Line - 01</label>
                    <input className="form-control form-control-sm" placeholder="Text" />
                </div>
                <div className="col-md-3">
                    <label className="form-label">Landmark / Area</label>
                    <input className="form-control form-control-sm" placeholder="Text" />
                </div>
                <div className="col-md-3">
                    <label className="form-label">Country</label>
                    <input
                        className="form-control form-control-sm"
                        placeholder="Master (Country)"
                    />
                </div>
                <div className="col-md-3">
                    <label className="form-label">State</label>
                    <input
                        className="form-control form-control-sm"
                        placeholder="Master (State)"
                    />
                </div>

                <div className="col-md-3">
                    <label className="form-label">District</label>
                    <input className="form-control form-control-sm" placeholder="Master" />
                </div>
                <div className="col-md-3">
                    <label className="form-label">City / Taluka</label>
                    <input className="form-control form-control-sm" placeholder="Master" />
                </div>
                <div className="col-md-3">
                    <label className="form-label">Village</label>
                    <input className="form-control form-control-sm" placeholder="Text" />
                </div>
                <div className="col-md-3">
                    <label className="form-label">PIN / ZIP</label>
                    <input className="form-control form-control-sm" placeholder="Text" />
                </div>
            </div>
        </div>
    );
};

export default BasicDetails;