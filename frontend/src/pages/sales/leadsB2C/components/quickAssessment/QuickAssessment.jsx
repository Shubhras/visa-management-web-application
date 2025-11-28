import React from 'react';

const QuickAssessment = () => {
    return (
        <div className="section-block">
            <div className="row g-3">
                <div className="col-12">
                    <h6 className="text-primary mb-3">Quick Assessment</h6>
                </div>
                
                <div className="col-md-6">
                    <label className="form-label">
                        Eligibility Score
                    </label>
                    <div className="progress" style={{ height: '20px' }}>
                        <div 
                            className="progress-bar bg-success" 
                            role="progressbar" 
                            style={{ width: '75%' }}
                            aria-valuenow="75" 
                            aria-valuemin="0" 
                            aria-valuemax="100"
                        >
                            75%
                        </div>
                    </div>
                </div>
                
                <div className="col-md-6">
                    <label className="form-label">
                        Recommended Visa Categories
                    </label>
                    <div className="border rounded p-2 bg-light">
                        <span className="badge bg-primary me-2">Skilled Worker</span>
                        <span className="badge bg-primary me-2">Student Visa</span>
                        <span className="badge bg-primary">Business</span>
                    </div>
                </div>
                
                <div className="col-12">
                    <label className="form-label">
                        Assessment Notes
                    </label>
                    <textarea 
                        className="form-control form-control-sm" 
                        placeholder="Assessment comments and recommendations"
                        rows="4"
                    />
                </div>
            </div>
        </div>
    );
};

export default QuickAssessment;