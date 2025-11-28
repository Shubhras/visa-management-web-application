import React from 'react';

const SpouseDetails = () => {
    return (
        <div className="section-block">
            <div className="row g-3">
                <div className="col-12">
                    <h6 className="text-primary mb-3">Spouse Information</h6>
                </div>
                
                <div className="col-md-4">
                    <label className="form-label">
                        Spouse First Name
                    </label>
                    <input className="form-control form-control-sm" placeholder="Enter first name" />
                </div>
                
                <div className="col-md-4">
                    <label className="form-label">
                        Spouse Last Name
                    </label>
                    <input className="form-control form-control-sm" placeholder="Enter last name" />
                </div>
                
                <div className="col-md-4">
                    <label className="form-label">
                        Spouse Date of Birth
                    </label>
                    <input type="date" className="form-control form-control-sm" />
                </div>
                
                <div className="col-md-6">
                    <label className="form-label">
                        Spouse Education Level
                    </label>
                    <select className="form-select form-select-sm">
                        <option>Select Education Level</option>
                        <option>High School</option>
                        <option>Bachelor's Degree</option>
                        <option>Master's Degree</option>
                        <option>PhD</option>
                    </select>
                </div>
                
                <div className="col-md-6">
                    <label className="form-label">
                        Spouse Work Experience
                    </label>
                    <input type="number" className="form-control form-control-sm" placeholder="Enter years" />
                </div>
            </div>
        </div>
    );
};

export default SpouseDetails;