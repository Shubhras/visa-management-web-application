import React from 'react';
import { Icon } from '@iconify/react/dist/iconify.js';

const Documents = () => {
    return (
        <div className="section-block">
            <div className="row g-3">
                <div className="col-12">
                    <h6 className="text-primary mb-3">Required Documents</h6>
                </div>
                
                <div className="col-md-6">
                    <div className="border rounded p-3">
                        <h6 className="mb-3">Upload Documents</h6>
                        
                        <div className="mb-3">
                            <label className="form-label">Passport Copy</label>
                            <input type="file" className="form-control form-control-sm" />
                        </div>
                        
                        <div className="mb-3">
                            <label className="form-label">Educational Certificates</label>
                            <input type="file" className="form-control form-control-sm" />
                        </div>
                        
                        <div className="mb-3">
                            <label className="form-label">Experience Letters</label>
                            <input type="file" className="form-control form-control-sm" />
                        </div>
                    </div>
                </div>
                
                <div className="col-md-6">
                    <div className="border rounded p-3">
                        <h6 className="mb-3">Uploaded Documents</h6>
                        
                        <div className="d-flex align-items-center justify-content-between border-bottom pb-2 mb-2">
                            <span>passport.pdf</span>
                            <div>
                                <button className="btn btn-sm btn-outline-primary me-1">
                                    <Icon icon="mdi:eye" width="16" />
                                </button>
                                <button className="btn btn-sm btn-outline-danger">
                                    <Icon icon="mdi:delete" width="16" />
                                </button>
                            </div>
                        </div>
                        
                        <div className="d-flex align-items-center justify-content-between border-bottom pb-2 mb-2">
                            <span>degree_certificate.pdf</span>
                            <div>
                                <button className="btn btn-sm btn-outline-primary me-1">
                                    <Icon icon="mdi:eye" width="16" />
                                </button>
                                <button className="btn btn-sm btn-outline-danger">
                                    <Icon icon="mdi:delete" width="16" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Documents;