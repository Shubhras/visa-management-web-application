import React, { useState } from 'react';
import { useDispatch } from "react-redux";
import MasterLayout from "../../../masterLayout/MasterLayout";
import { Icon } from '@iconify/react/dist/iconify.js';
import Select from "react-select";
import BasicDetails from "./components/BasicDetails";
import PrincipalApplicant from "./components/PrincipalApplicant";
import AdditionalDetails from "./components/AdditionalDetails";
import SpouseDetails from "./components/SpouseDetails";
import QuickAssessment from "./components/QuickAssessment";
import Documents from "./components/Documents";

const LeadB2CForm = () => {
    const dispatch = useDispatch();
    const [leadFor, setLeadFor] = useState(null);
    const [activeMainTab, setActiveMainTab] = useState("basic");
    const leadForOptions = [
        { value: "visa", label: "Visa" },
        { value: "coaching", label: "Coaching" },
        { value: "visa_coaching", label: "Visa & Coaching" }
    ];


    const mainTabBtnClass = (tab) =>
        `btn border border-primary-600 text-md px-16 py-6 radius-6 ${activeMainTab === tab ? "comman-btn-color text-white" : "bg-white text-primary-600"
        }`;

    const renderActiveTab = () => {
        switch (activeMainTab) {
            case "basic":
                return <BasicDetails />;
            case "principal":
                return <PrincipalApplicant />;
            case "additional":
                return <AdditionalDetails />;
            case "spouse":
                return <SpouseDetails />;
            case "quick":
                return <QuickAssessment />;
            case "documents":
                return <Documents />;
            default:
                return <BasicDetails />;
        }
    };

    return (
        <MasterLayout>

            <style jsx>{`

.top-stats-container {
    display: flex;
    justify-content: center;
}

.lead-stat-box {
    border: 1px solid #d5d5d5;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    background: white;
    border-radius: 4px;
}

.lead-stat-count {
    font-weight: 600;
    font-size: 16px;
    color: #5a6c5b;
}



/* Section blocks */
.section-block {
    
    padding: 10px 12px;
    background-color: #fff;
}

/* Tabs container row */
.main-tabs-row {
    padding: 6px 8px;
}

/* Correct spacing between ALL buttons */
.main-tabs-row .btn-group {
    display: flex;
    align-items: center;
    gap: 8px; /* BEST spacing */
}


.nav-arrow-btn {
    background-color: #ffffff;
    padding: 4px 8px;
    height: 36px;
    width: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    border: 1px solid #5a6c5b;
    cursor: pointer;
}



/* Main tab + sub tab styles unified */
.main-tabs-row .btn,
.sub-tab-btn,
.tab-btn {
    font-weight: 500;
    min-width: 150px;
    height: 36px;          
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    border: 1px solid #5a6c5b;
    background: #fff;
    cursor: pointer;
}

/* Active tab */
.btn.comman-btn-color,
.main-tabs-row .btn.active,
.sub-tab-btn.active {
    background-color: #5a6c5b !important;
    color: white !important;
    border-color: #5a6c5b !important;
}

/* Hover */
.main-tabs-row .btn:hover,
.sub-tab-btn:hover {
    background-color: #4a5a4b;
    color: white;
    border-color: #4a5a4b;
}

.text-md { font-size: 13px; }
.px-16 { padding-left: 16px !important; padding-right: 16px !important; }
.py-6 { padding-top: 6px !important; padding-bottom: 6px !important; }
.radius-6 { border-radius: 6px !important; }
.border-primary-600 { border-color: #5a6c5b !important; }
.text-primary-600 { color: #5a6c5b !important; }




/* Checkboxes */
.form-check-input {
    width: 20px;
    height: 20px;
    cursor: pointer;
}

.form-check-input:checked {
    background-color: #4a5a4b;
    border-color: #4a5a4b;
}
`}</style>


            <div className="card basic-data-table main-container-data">
                <div className="card-body container-data">
                    <div className="top-stats-container">
                        <div className="row justify-content-center w-100">
                            <div className="col-auto">
                                <div className="lead-stat-box">
                                    <input type="checkbox" className="form-check-input me-2" />
                                    <span className="lead-stat-count">04</span>
                                    <span className="">Quick Assessment</span>
                                </div>
                            </div>

                            <div className="col-auto">
                                <div className="lead-stat-box">
                                    <input type="checkbox" className="form-check-input me-2" />
                                    <span className="lead-stat-count">02</span>
                                    <span className="">Schedule Meeting</span>
                                </div>
                            </div>

                            <div className="col-auto">
                                <div className="lead-stat-box">
                                    <input type="checkbox" className="form-check-input me-2" />
                                    <span className="lead-stat-count">12</span>
                                    <span className="">Follow Ups</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="card-body pt-0 container-table">
                    <div className='container-table-div'>

                        {/* Lead header info */}
                        <div className="section-block mb-3">
                            <div className="row g-3">
                                <div className="col-md-4">
                                    <label className="form-label ">Lead Date &amp; Time</label>
                                    <div className="d-flex gap-2">
                                        <input
                                            type="text"
                                            className="form-control form-control-sm"
                                            placeholder="Date (Auto)"

                                        />
                                        <input
                                            type="text"
                                            className="form-control form-control-sm"
                                            placeholder="Time (Auto)"

                                        />
                                    </div>
                                </div>

                                <div className="col-md-4">
                                    <label className="form-label ">Lead ID</label>
                                    <input
                                        type="text"
                                        className="form-control form-control-sm"
                                        placeholder="Auto As per Company Formate"

                                    />
                                </div>

                                <div className="col-md-4">
                                    <label className="form-label">Lead For</label>

                                    <Select
                                        options={leadForOptions}
                                        value={leadForOptions.find(o => o.value === leadFor)}
                                        onChange={(opt) => setLeadFor(opt?.value || null)}
                                        placeholder="Select"
                                        isClearable
                                        classNamePrefix="custom-select"
                                        className={`custom-select-container`}
                                    />
                                </div>


                            </div>

                            <div className="row g-3 mt-1">
                                <div className="col-md-4">
                                    <label className="form-label ">Test (Exam) Name</label>
                                    <input
                                        type="text"
                                        className="form-control form-control-sm"
                                        placeholder="Master (Language Test Name)"
                                    />
                                </div>

                                <div className="col-md-4">
                                    <label className="form-label ">Interested Visa Category</label>
                                    <input
                                        type="text"
                                        className="form-control form-control-sm"
                                        placeholder="Master (Visa Main Category) - Multiple"
                                    />
                                </div>

                                <div className="col-md-4">
                                    <label className="form-label ">Interested Country</label>
                                    <input
                                        type="text"
                                        className="form-control form-control-sm"
                                        placeholder="Master (Rep. Country) - Multiple"
                                    />
                                </div>
                            </div>
                        </div>


                        {/* Main tabs */}
                        <div className="d-flex align-items-center mb-3 main-tabs-row">
                            <div className="btn-group" role="group">

                                {/* Left arrow */}
                                <button
                                    type="button"
                                    className="btn btn-sm nav-arrow-btn"
                                >
                                    <Icon icon="mdi:chevron-left" />
                                </button>

                                {/* Main tabs */}
                                <button
                                    type="button"
                                    className={mainTabBtnClass("basic")}
                                    onClick={() => setActiveMainTab("basic")}
                                >
                                    Basic Details
                                </button>

                                <button
                                    type="button"
                                    className={mainTabBtnClass("principal")}
                                    onClick={() => setActiveMainTab("principal")}
                                >
                                    Principal Applicant
                                </button>

                                <button
                                    type="button"
                                    className={mainTabBtnClass("additional")}
                                    onClick={() => setActiveMainTab("additional")}
                                >
                                    Additional Details
                                </button>

                                {/* Sub tabs */}
                                <button
                                    type="button"
                                    className={mainTabBtnClass("spouse")}
                                    onClick={() => setActiveMainTab("spouse")}
                                >
                                    Spouse Details
                                </button>

                                <button
                                    type="button"
                                    className={mainTabBtnClass("quick")}
                                    onClick={() => setActiveMainTab("quick")}
                                >
                                    Quick Assessment
                                </button>

                                <button
                                    type="button"
                                    className={mainTabBtnClass("documents")}
                                    onClick={() => setActiveMainTab("documents")}
                                >
                                    Documents
                                </button>

                                {/* Right arrow */}
                                <button
                                    type="button"
                                    className="btn btn-sm nav-arrow-btn"
                                >
                                    <Icon icon="mdi:chevron-right" />
                                </button>

                            </div>
                        </div>

                        {renderActiveTab()}



                        <div className="d-flex justify-content-center py-3">
                            <div className="d-flex gap-2">
                                <button
                                    type="button"
                                    className="btn btn-sm comman-btn-color border border-primary-600 text-md px-16 py-6 radius-6"
                                >
                                    Back
                                </button>

                                <button
                                    type="button"
                                    className="btn btn-sm comman-btn-color border border-primary-600 text-md px-16 py-6 radius-6"
                                >
                                    Next
                                </button>

                                <button
                                    type="button"
                                    className="btn btn-sm comman-btn-color border border-primary-600 text-md px-16 py-6 radius-6"
                                >
                                    Save
                                </button>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </MasterLayout>
    );
};

export default LeadB2CForm;