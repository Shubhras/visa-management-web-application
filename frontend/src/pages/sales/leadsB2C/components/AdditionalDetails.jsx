import React from 'react';

const AdditionalDetails = () => {
    return (
        <div className="section-block">
            <div className="row g-3">
                <div className="col-12">
                    <h6 className="text-primary mb-3">Additional Information</h6>
                </div>
                
                <div className="col-md-6">
                    <label className="form-label">
                        Source of Lead
                    </label>
                    <select className="form-select form-select-sm">
                        <option>Select Source</option>
                        <option>Website</option>
                        <option>Referral</option>
                        <option>Social Media</option>
                        <option>Advertisement</option>
                        <option>Other</option>
                    </select>
                </div>
                
                <div className="col-md-6">
                    <label className="form-label">
                        Preferred Contact Time
                    </label>
                    <select className="form-select form-select-sm">
                        <option>Any Time</option>
                        <option>Morning (9AM-12PM)</option>
                        <option>Afternoon (12PM-5PM)</option>
                        <option>Evening (5PM-8PM)</option>
                    </select>
                </div>
                
                <div className="col-12">
                    <label className="form-label">
                        Additional Notes
                    </label>
                    <textarea 
                        className="form-control form-control-sm" 
                        placeholder="Enter any additional notes or comments"
                        rows="3"
                    />
                </div>
            </div>
        </div>
    );
};

export default AdditionalDetails;