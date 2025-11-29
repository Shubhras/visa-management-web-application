import React, { useState } from 'react';

const AdditionalDetails = () => {
    const [formData, setFormData] = useState({
        hasRelatives: '',
        hasVisited: '',
        hasRefused: '',
        hasBusinessExperience: '',
        tradeCertificate: false,
        educationalAssessment: false,
        itaProvince: false,
        techStartupFounder: false,
        resideOutsideCity: false
    });

    const handleInputChange = (field, value) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleCheckboxChange = (field) => {
        setFormData(prev => ({
            ...prev,
            [field]: !prev[field]
        }));
    };

    return (
        <div className="section-block">
            <div className="container-fluid">
                {/* Table 1: Relatives in Interested Country */}
                <div className="card mb-4">
                    <div className="card-header bg-light py-3">
                        <h6 className="mb-0 fw-semibold text-dark">
                            Have you / your spouse's RELATIVE in interested country? - If Yes, Open below Table
                        </h6>
                    </div>
                    <div className="card-body">
                        <div className="row align-items-center mb-3">
                            <div className="col-md-6">
                                <label className="form-label fw-medium">Select Option</label>
                                <select 
                                    className="form-select form-select-sm"
                                    value={formData.hasRelatives}
                                    onChange={(e) => handleInputChange('hasRelatives', e.target.value)}
                                >
                                    <option value="">Select</option>
                                    <option value="yes">Yes</option>
                                    <option value="no">No</option>
                                </select>
                            </div>
                        </div>
                        
                        {formData.hasRelatives === 'yes' && (
                            <>
                                <div className="table-responsive">
                                    <table className="table table-bordered table-sm mb-3">
                                        <thead className="table-light">
                                            <tr>
                                                <th>Applicant Type</th>
                                                <th>Country</th>
                                                <th>State</th>
                                                <th>City</th>
                                                <th>Relation</th>
                                                <th>Visa Category</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>
                                                    <select className="form-select form-select-sm">
                                                        <option>Master</option>
                                                    </select>
                                                </td>
                                                <td>
                                                    <select className="form-select form-select-sm">
                                                        <option>Master</option>
                                                    </select>
                                                </td>
                                                <td>
                                                    <select className="form-select form-select-sm">
                                                        <option>Master</option>
                                                    </select>
                                                </td>
                                                <td>
                                                    <select className="form-select form-select-sm">
                                                        <option>Master</option>
                                                    </select>
                                                </td>
                                                <td>
                                                    <select className="form-select form-select-sm">
                                                        <option>Master</option>
                                                    </select>
                                                </td>
                                                <td>
                                                    <select className="form-select form-select-sm">
                                                        <option>Master</option>
                                                    </select>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                                <button className="btn btn-sm btn-outline-primary">
                                    Add Relative ……
                                </button>
                            </>
                        )}
                    </div>
                </div>

                {/* Table 2: Visited Countries */}
                <div className="card mb-4">
                    <div className="card-header bg-light py-3">
                        <h6 className="mb-0 fw-semibold text-dark">
                            Have you / your spouse's ever VISITED any country? - If Yes, Open below Table
                        </h6>
                    </div>
                    <div className="card-body">
                        <div className="row align-items-center mb-3">
                            <div className="col-md-6">
                                <label className="form-label fw-medium">Select Option</label>
                                <select 
                                    className="form-select form-select-sm"
                                    value={formData.hasVisited}
                                    onChange={(e) => handleInputChange('hasVisited', e.target.value)}
                                >
                                    <option value="">Select</option>
                                    <option value="yes">Yes</option>
                                    <option value="no">No</option>
                                </select>
                            </div>
                        </div>
                        
                        {formData.hasVisited === 'yes' && (
                            <>
                                <div className="table-responsive">
                                    <table className="table table-bordered table-sm mb-3">
                                        <thead className="table-light">
                                            <tr>
                                                <th>Applicant Type</th>
                                                <th>Country</th>
                                                <th>Visa Category</th>
                                                <th>Issue Date</th>
                                                <th>Travel From</th>
                                                <th>Travel To</th>
                                                <th>Purpose of Visit</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>
                                                    <select className="form-select form-select-sm">
                                                        <option>Master</option>
                                                    </select>
                                                </td>
                                                <td>
                                                    <select className="form-select form-select-sm">
                                                        <option>Master</option>
                                                    </select>
                                                </td>
                                                <td>
                                                    <select className="form-select form-select-sm">
                                                        <option>Master</option>
                                                    </select>
                                                </td>
                                                <td><input type="date" className="form-control form-control-sm" /></td>
                                                <td><input type="date" className="form-control form-control-sm" /></td>
                                                <td><input type="date" className="form-control form-control-sm" /></td>
                                                <td>
                                                    <select className="form-select form-select-sm">
                                                        <option>Master</option>
                                                    </select>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                                <button className="btn btn-sm btn-outline-primary">
                                    Add Visit ……
                                </button>
                            </>
                        )}
                    </div>
                </div>

                {/* Table 3: Refused Countries */}
                <div className="card mb-4">
                    <div className="card-header bg-light py-3">
                        <h6 className="mb-0 fw-semibold text-dark">
                            Have you / your spouse's ever REFUSED any country? - If Yes, Open below Table
                        </h6>
                    </div>
                    <div className="card-body">
                        <div className="row align-items-center mb-3">
                            <div className="col-md-6">
                                <label className="form-label fw-medium">Select Option</label>
                                <select 
                                    className="form-select form-select-sm"
                                    value={formData.hasRefused}
                                    onChange={(e) => handleInputChange('hasRefused', e.target.value)}
                                >
                                    <option value="">Select</option>
                                    <option value="yes">Yes</option>
                                    <option value="no">No</option>
                                </select>
                            </div>
                        </div>
                        
                        {formData.hasRefused === 'yes' && (
                            <>
                                <div className="table-responsive">
                                    <table className="table table-bordered table-sm mb-3">
                                        <thead className="table-light">
                                            <tr>
                                                <th>Applicant Type</th>
                                                <th>Country</th>
                                                <th>Visa Category</th>
                                                <th>Refuse Date</th>
                                                <th>Reason for Refusal</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>
                                                    <select className="form-select form-select-sm">
                                                        <option>Master</option>
                                                    </select>
                                                </td>
                                                <td>
                                                    <select className="form-select form-select-sm">
                                                        <option>Master</option>
                                                    </select>
                                                </td>
                                                <td>
                                                    <select className="form-select form-select-sm">
                                                        <option>Master</option>
                                                    </select>
                                                </td>
                                                <td><input type="date" className="form-control form-control-sm" /></td>
                                                <td><input type="text" className="form-control form-control-sm" placeholder="Text" /></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                                <button className="btn btn-sm btn-outline-primary">
                                    Add Visit ……
                                </button>
                            </>
                        )}
                    </div>
                </div>

                {/* Table 4: Business Experience */}
                <div className="card mb-4">
                    <div className="card-header bg-light py-3">
                        <h6 className="mb-0 fw-semibold text-dark">
                            Do you have experience to Manage Business? - If Yes, Open below Table
                        </h6>
                    </div>
                    <div className="card-body">
                        <div className="row align-items-center mb-3">
                            <div className="col-md-6">
                                <label className="form-label fw-medium">Select Option</label>
                                <select 
                                    className="form-select form-select-sm"
                                    value={formData.hasBusinessExperience}
                                    onChange={(e) => handleInputChange('hasBusinessExperience', e.target.value)}
                                >
                                    <option value="">Select</option>
                                    <option value="yes">Yes</option>
                                    <option value="no">No</option>
                                </select>
                            </div>
                        </div>
                        
                        {formData.hasBusinessExperience === 'yes' && (
                            <>
                                <div className="table-responsive">
                                    <table className="table table-bordered table-sm mb-3">
                                        <thead className="table-light">
                                            <tr>
                                                <th>Country</th>
                                                <th>Company Name</th>
                                                <th>Company Type</th>
                                                <th>Your Share(%)</th>
                                                <th>Start Date</th>
                                                <th>End Date</th>
                                                <th>Turnover</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>
                                                    <select className="form-select form-select-sm">
                                                        <option>Master</option>
                                                    </select>
                                                </td>
                                                <td><input type="text" className="form-control form-control-sm" placeholder="Text" /></td>
                                                <td>
                                                    <select className="form-select form-select-sm">
                                                        <option>Master</option>
                                                    </select>
                                                </td>
                                                <td><input type="number" className="form-control form-control-sm" placeholder="Numeric" /></td>
                                                <td><input type="date" className="form-control form-control-sm" /></td>
                                                <td><input type="date" className="form-control form-control-sm" /></td>
                                                <td><input type="number" className="form-control form-control-sm" placeholder="Numeric" /></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                                <button className="btn btn-sm btn-outline-primary">
                                    Add Business ……
                                </button>
                            </>
                        )}
                    </div>
                </div>

                {/* Table 5: Network & Investment (Always Visible) */}
                <div className="card mb-4">
                    <div className="card-header bg-light py-3">
                        <h6 className="mb-0 fw-semibold text-dark">Your Network & Investment</h6>
                    </div>
                    <div className="card-body">
                        <div className="table-responsive">
                            <table className="table table-bordered table-sm">
                                <thead className="table-light">
                                    <tr>
                                        <th>Applicant Type</th>
                                        <th>Country</th>
                                        <th>Currency</th>
                                        <th>Immovable Property</th>
                                        <th>Movable Property</th>
                                        <th>Liquid Amt.</th>
                                        <th>Total Networth</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Principal</td>
                                        <td>India</td>
                                        <td>INR</td>
                                        <td><input type="number" className="form-control form-control-sm" placeholder="Numeric" /></td>
                                        <td><input type="number" className="form-control form-control-sm" placeholder="Numeric" /></td>
                                        <td><input type="number" className="form-control form-control-sm" placeholder="Numeric" /></td>
                                        <td className="text-muted">Auto Calculation</td>
                                    </tr>
                                    <tr>
                                        <td>Spouse</td>
                                        <td>India</td>
                                        <td>INR</td>
                                        <td><input type="number" className="form-control form-control-sm" placeholder="Numeric" /></td>
                                        <td><input type="number" className="form-control form-control-sm" placeholder="Numeric" /></td>
                                        <td><input type="number" className="form-control form-control-sm" placeholder="Numeric" /></td>
                                        <td className="text-muted">Auto Calculation</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                {/* Checkbox Questions Section */}
                <div className="card">
                    <div className="card-body">
                        <div className="row g-3">
                            <div className="col-12">
                                <div className="form-check">
                                    <input 
                                        className="form-check-input" 
                                        type="checkbox" 
                                        checked={formData.tradeCertificate}
                                        onChange={() => handleCheckboxChange('tradeCertificate')}
                                    />
                                    <label className="form-check-label fw-medium">
                                        Do you have a Trade Certificate Assessment from Industry Training Authority?
                                    </label>
                                </div>
                            </div>
                            <div className="col-12">
                                <div className="form-check">
                                    <input 
                                        className="form-check-input" 
                                        type="checkbox" 
                                        checked={formData.educationalAssessment}
                                        onChange={() => handleCheckboxChange('educationalAssessment')}
                                    />
                                    <label className="form-check-label fw-medium">
                                        Do you have an Educational Credential Assessment from a Qualified Supplier?
                                    </label>
                                </div>
                            </div>
                            <div className="col-12">
                                <div className="form-check">
                                    <input 
                                        className="form-check-input" 
                                        type="checkbox" 
                                        checked={formData.itaProvince}
                                        onChange={() => handleCheckboxChange('itaProvince')}
                                    />
                                    <label className="form-check-label fw-medium">
                                        Do you have a ITA from Province as a part of Employment / Exploratory Visit?
                                    </label>
                                </div>
                            </div>
                            <div className="col-12">
                                <div className="form-check">
                                    <input 
                                        className="form-check-input" 
                                        type="checkbox" 
                                        checked={formData.techStartupFounder}
                                        onChange={() => handleCheckboxChange('techStartupFounder')}
                                    />
                                    <label className="form-check-label fw-medium">
                                        Are you a Tech Startup Founder?
                                    </label>
                                </div>
                            </div>
                            <div className="col-12">
                                <div className="form-check">
                                    <input 
                                        className="form-check-input" 
                                        type="checkbox" 
                                        checked={formData.resideOutsideCity}
                                        onChange={() => handleCheckboxChange('resideOutsideCity')}
                                    />
                                    <label className="form-check-label fw-medium">
                                        Do your Intention to Reside out side Greater City?
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdditionalDetails;