import React, { useState, useRef } from 'react';
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
    const scrollRef = useRef(null);
    const [activeMainTab, setActiveMainTab] = useState("basic");
    const leadForOptions = [
        { value: "visa", label: "Visa" },
        { value: "coaching", label: "Coaching" },
        { value: "visa_coaching", label: "Visa & Coaching" }
    ];

    const scrollLeft = () => {
        scrollRef.current.scrollBy({ left: -100, behavior: "smooth" });
    };

    const scrollRight = () => {
        scrollRef.current.scrollBy({ left: 100, behavior: "smooth" });
    };


    const mainTabBtnClass = (tab) =>
        `btn border border-primary-600 text-md px-16 py-6  ${activeMainTab === tab ? "comman-btn-color text-white" : "bg-white text-primary-600"
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

.lead-stat-box {
    border: 1px solid #d5d5d5;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    background: white;
    border-radius: 4px;
}

.section-block {
    padding: 10px 12px;
   
}


`}</style>

            <div className="card basic-data-table main-container-data">
                <div className="card-body container-data">
                    <div className="d-flex flex-wrap align-items-center justify-content-between w-100 gap-3">

                        {/* LEFT BUTTON GROUP */}
                        <div className="d-flex align-items-center gap-2 flex-wrap">
                            <button className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color">
                                Create Inquiry
                            </button>

                            <button className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color">
                                Lost
                            </button>

                            <button className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color">
                                Save
                            </button>
                        </div>

                        {/* RIGHT STATUS BOXES */}
                        <div className="d-flex align-items-center gap-2 flex-wrap">
                            <div className="lead-stat-box">
                                <span>Quick Assessment</span>
                            </div>

                            <div className="lead-stat-box">
                                <span>Schedule Meeting</span>
                            </div>

                            <div className="lead-stat-box">
                                <span>Follow Ups</span>
                            </div>
                        </div>

                    </div>
                </div>


                <div className="card-body pt-0 container-table">
                    <div className='container-table-div'>
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


                        <div className="d-flex align-items-center justify-content-center border-top border-bottom py-3">
                            <div role="group" className="d-flex align-items-center">
                                <button type="button" className="btn btn-sm me-1" onClick={scrollLeft}>
                                    <Icon icon="mdi:chevron-left" width="25" height="25" />
                                </button>

                                <div
                                    ref={scrollRef}
                                    className="d-flex overflow-auto flex-nowrap"
                                    style={{ scrollbarWidth: "thin" }}

                                >
                                    <button
                                        type="button"
                                        className={`${mainTabBtnClass("basic")} me-1`}
                                        onClick={() => setActiveMainTab("basic")}
                                    >
                                        Basic Details
                                    </button>

                                    <button
                                        type="button"
                                        className={`${mainTabBtnClass("principal")} me-1`}
                                        onClick={() => setActiveMainTab("principal")}
                                    >
                                        Principal Applicant
                                    </button>

                                    <button
                                        type="button"
                                        className={`${mainTabBtnClass("additional")} me-1`}
                                        onClick={() => setActiveMainTab("additional")}
                                    >
                                        Additional Details
                                    </button>

                                    <button
                                        type="button"
                                        className={`${mainTabBtnClass("spouse")} me-1`}
                                        onClick={() => setActiveMainTab("spouse")}
                                    >
                                        Spouse Details
                                    </button>

                                    <button
                                        type="button"
                                        className={`${mainTabBtnClass("quick")} me-1`}
                                        onClick={() => setActiveMainTab("quick")}
                                    >
                                        Quick Assessment
                                    </button>

                                    <button
                                        type="button"
                                        className={`${mainTabBtnClass("documents")} me-1`}
                                        onClick={() => setActiveMainTab("documents")}
                                    >
                                        Documents
                                    </button>
                                </div>

                                <button type="button" className="btn btn-sm" onClick={scrollRight}>
                                    <Icon icon="mdi:chevron-right" width="25" height="25" />
                                </button>
                            </div>
                            <div>
                                <button
                                    type="button"

                                    className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color"
                                >
                                    Save
                                </button>

                            </div>
                        </div>

                        {renderActiveTab()}

                        <div className="d-flex justify-content-end py-3 px-3">
                            <div className="d-flex gap-2">
                                <button
                                    type="button"
                                    className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color"
                                >
                                    Back
                                </button>

                                <button
                                    type="button"
                                    // className="btn btn-sm comman-btn-color border border-primary-600 text-md px-16 py-6 radius-6"
                                    className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color"
                                >
                                    Next
                                </button>

                                <button
                                    type="button"
                                    // className="btn btn-sm comman-btn-color border border-primary-600 text-md px-16 py-6 radius-6"
                                    className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color"
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