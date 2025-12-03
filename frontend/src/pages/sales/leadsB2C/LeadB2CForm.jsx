import React, { useState, useRef } from "react";
import { useDispatch } from "react-redux";
import MasterLayout from "../../../masterLayout/MasterLayout";
import { Icon } from "@iconify/react/dist/iconify.js";
import Select from "react-select";
import BasicDetails from "./components/basicDetails/BasicDetails";
import PrincipalApplicant from "./components/principalApplicant/PrincipalApplicant";
import AdditionalDetails from "./components/additionalDetails/AdditionalDetails";
import SpouseDetails from "./components/spouseDetails/SpouseDetails";
import QuickAssessment from "./components/quickAssessment/QuickAssessment";
import Documents from "./components/documents/Documents";
import AddEditActionModal from "./components/leadB2CSidebar/AddEditActionModal";
import AddEditOfficeModal from "./components/leadB2CSidebar/AddEditOfficeModal";
import { Link } from "react-router-dom";

const LeadB2CForm = () => {
  const dispatch = useDispatch();
  const [leadFor, setLeadFor] = useState(null);
  const scrollRef = useRef(null);
  const [activeMainTab, setActiveMainTab] = useState("basic");
  const leadForOptions = [
    { value: "visa", label: "Visa" },
    { value: "coaching", label: "Coaching" },
    { value: "visa_coaching", label: "Visa & Coaching" },
  ];

  const scrollLeft = () => {
    scrollRef.current.scrollBy({ left: -100, behavior: "smooth" });
  };

  const scrollRight = () => {
    scrollRef.current.scrollBy({ left: 100, behavior: "smooth" });
  };

  const mainTabBtnClass = (tab) =>
    `btn border border-primary-600 text-md px-16 py-6  ${
      activeMainTab === tab
        ? "comman-btn-color text-white"
        : "bg-white text-primary-600"
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
  const getTabBtnClass = (tabKey) =>
    `btn border border-primary-600 fw-medium px-3 py-1
   ${
     activeTab === tabKey
       ? "comman-btn-color text-white"
       : "bg-white text-primary-600"
   }`;
  // ACTION STATES
  const [actionsLog, setActionsLog] = useState([
    {
      uuid: "a1",
      action: "call",
      dueDate: "2025-12-05",
      time: "10:30",
    },
    {
      uuid: "a2",
      action: "email",
      dueDate: "2025-12-06",
      time: "14:00",
    },
    {
      uuid: "a3",
      action: "meeting",
      dueDate: "2025-12-08",
      time: "16:45",
    },
  ]);
  const [showActionModal, setShowActionModal] = useState(false);
  const [actionMode, setActionMode] = useState("add");
  const [editActionRow, setEditActionRow] = useState(null);

  // ADD NEW ACTION
  const handleAddNewAction = () => {
    setActionMode("add");
    setEditActionRow(null);
    setShowActionModal(true);
  };

  // CLOSE ACTION MODAL
  const handleCloseActionModal = (refresh, newAction) => {
    setShowActionModal(false);

    if (refresh && newAction) {
      if (actionMode === "edit") {
        setActionsLog((prev) =>
          prev.map((item) => (item.uuid === newAction.uuid ? newAction : item))
        );
      } else {
        setActionsLog((prev) => [...prev, newAction]);
      }
    }
  };

  // EDIT ACTION
  const handleEditAction = (item) => {
    setActionMode("edit");
    setEditActionRow(item);
    setShowActionModal(true);
  };

  // DELETE ACTION
  const handleDeleteAction = (uuid) => {
    setActionsLog((prev) => prev.filter((x) => x.uuid !== uuid));
  };

  // ---- OFFICE STATES ----
  const [officeLog, setOfficeLog] = useState([]);
  const [showOfficeModal, setShowOfficeModal] = useState(false);
  const [officeMode, setOfficeMode] = useState("add");
  const [editOfficeRow, setEditOfficeRow] = useState(null);

  // OPEN NEW OFFICE MODAL
  const handleAddNewOffice = () => {
    setOfficeMode("add");
    setEditOfficeRow(null);
    setShowOfficeModal(true);
  };

  // CLOSE OFFICE MODAL
  const handleCloseOfficeModal = (refresh, newOfficeData) => {
    setShowOfficeModal(false);

    if (refresh && newOfficeData) {
      if (officeMode === "edit") {
        // UPDATE
        setOfficeLog((prev) =>
          prev.map((item) =>
            item.uuid === newOfficeData.uuid ? newOfficeData : item
          )
        );
      } else {
        // ADD
        setOfficeLog((prev) => [...prev, newOfficeData]);
      }
    }
  };

  // EDIT OFFICE
  const handleEditOffice = (item) => {
    setOfficeMode("edit");
    setEditOfficeRow(item);
    setShowOfficeModal(true);
  };

  // DELETE OFFICE ITEM
  const handleDeleteOffice = (uuid) => {
    setOfficeLog((prev) => prev.filter((x) => x.uuid !== uuid));
  };

  const [notificationLog, setNotificationLog] = useState([
    {
      uuid: "n1",
      title: "New Lead Assigned",
      message: "A new lead has been assigned to you.",
      date: "2025-12-01",
    },
    {
      uuid: "n2",
      title: "Reminder",
      message: "Follow up on pending customer documents.",
      date: "2025-12-02",
    },
    {
      uuid: "n3",
      title: "System Alert",
      message: "Your profile needs verification.",
      date: "2025-12-03",
    },
  ]);

  // Internal Notes State
  const [internalNoteInput, setInternalNoteInput] = useState(""); // textarea input
  const [internalNotes, setInternalNotes] = useState([]); // saved notes

  // Save a new internal note
  const handleSaveInternalNote = () => {
    if (!internalNoteInput.trim()) return; // ignore empty notes

    const newNote = {
      id: Date.now(), // unique id
      note: internalNoteInput,
      createdAt: new Date().toLocaleDateString(), // or include time if needed
    };

    setInternalNotes((prev) => [newNote, ...prev]);
    setInternalNoteInput(""); // reset textarea
  };

  // Delete an internal note
  const handleDeleteInternal = (id) => {
    setInternalNotes((prev) => prev.filter((note) => note.id !== id));
  };

  const [activeTab, setActiveTab] = useState("internal");

  const tabs = [
    { key: "internal", label: "Internal Notes" },
    { key: "notification", label: "Notification" },
    { key: "actions", label: "Actions" },
    { key: "office", label: "Office" },
  ];

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

            <div className="d-flex align-items-center gap-3 flex-wrap">
              <div className="lead-stat-box d-flex align-items-center gap-2 px-3 py-2 rounded-3 shadow-sm bg-white">
                <p className="fs-4 fw-bold mb-0">04</p>
                <span className="text-muted fs-6">Quick Assessment</span>
              </div>

              <div className="lead-stat-box d-flex align-items-center gap-2 px-3 py-2 rounded-3 shadow-sm bg-white">
                <p className="fs-4 fw-bold mb-0">12</p>
                <span className="text-muted fs-6">Schedule Meeting</span>
              </div>

              <div className="lead-stat-box d-flex align-items-center gap-2 px-3 py-2 rounded-3 shadow-sm bg-white">
                <p className="fs-4 fw-bold mb-0">20</p>
                <span className="text-muted fs-6">Follow Ups</span>
              </div>
              <div
                style={{ cursor: "pointer" }}
                data-bs-toggle="offcanvas"
                data-bs-target="#leadSidebar"
              >
                {/* <Icon icon="mdi:view-grid" width="26" /> */}
                <Icon icon="material-symbols:menu" width="30" />
              </div>
            </div>
          </div>
        </div>
        <div
          className="offcanvas offcanvas-end"
          tabIndex="-1"
          id="leadSidebar"
          style={{ width: "550px" }}
        >
          {/* Sidebar Header */}
          <div className="offcanvas-header border-bottom">
            <button
              type="button"
              className="btn-close"
              data-bs-dismiss="offcanvas"
            ></button>
          </div>

          {/* Sidebar Body */}
          <div className="offcanvas-body">
            {/* ---------------------- TABS ---------------------- */}
            <div className="d-flex gap-2 mb-3">
              {tabs.map((tab) => (
                <button
                  key={tab.key}
                  className={`${getTabBtnClass(tab.key)}`}
                  onClick={() => setActiveTab(tab.key)}
                >
                  {tab.label}
                </button>
              ))}
            </div>
            <hr />
            {/* ---------------- DETAILS SECTION ---------------- */}
            <div>
              <p className="fw-bold text-success-800  mb-1">
                Interested Visa Category
              </p>
              <p className="fw-bold text-success-800 mb-1">
                Interested Country
              </p>
              <p className="fw-bold text-success-800 mb-1">Test (Exam) Name</p>
            </div>
            <hr />
            {/* ---------------- TAB CONTENT ---------------- */}
            {activeTab === "internal" && (
              <>
                <h5 className="fw-bold text-success-800 fs-6 my-3">
                  Write Notes
                </h5>

                {/* TEXTAREA */}
                <textarea
                  className="form-control mb-3"
                  placeholder="Write your internal notes here..."
                  rows={6}
                  value={internalNoteInput}
                  onChange={(e) => setInternalNoteInput(e.target.value)}
                ></textarea>

                <button
                  type="button"
                  className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color mb-4"
                  onClick={handleSaveInternalNote}
                >
                  Save Notes
                </button>

                {/* LISTING */}
                <div className="d-flex flex-column gap-3 mt-3">
                  {internalNotes.length > 0 ? (
                    internalNotes.map((note) => (
                      <div
                        key={note.id}
                        className="border rounded p-3 d-flex justify-content-between align-items-start"
                        style={{ cursor: "pointer" }}
                      >
                        {/* LEFT CONTENT */}
                        <div>
                          <strong>{note.note}</strong>
                          <br />
                          <span className="text-muted small">
                            {note.createdAt ? note.createdAt : "Internal Note"}
                          </span>
                        </div>

                        {/* DELETE BUTTON */}
                        <div className="d-flex align-items-start gap-2">
                          <button
                            className="btn btn-link text-danger p-0 m-0"
                            onClick={() => handleDeleteInternal(note.id)}
                          >
                            <Icon icon="mingcute:delete-2-line" width="18" />
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div
                      className="border rounded p-3 text-muted"
                      style={{ minHeight: "60px" }}
                    >
                      No internal notes yet
                    </div>
                  )}
                </div>
              </>
            )}

            {activeTab === "notification" && (
              <>
                <div className="d-flex flex-column gap-3 mt-3">
                  {notificationLog.length > 0 ? (
                    notificationLog.map((item) => (
                      <div
                        key={item.uuid}
                        className="border rounded p-3 d-flex justify-content-between align-items-start"
                        style={{ cursor: "pointer" }}
                      >
                        <div>
                          <strong>{item.title}</strong>
                          <br />
                          <span className="text-secondary">{item.message}</span>
                          <br />
                          <span className="text-muted small">{item.date}</span>
                        </div>

                        {/* ACTION BUTTONS */}
                        <div className="d-flex align-items-start gap-2">
                          <button
                            className="btn btn-link text-danger p-0 m-0"
                            onClick={(e) => {
                              e.stopPropagation();
                              setNotificationLog((prev) =>
                                prev.filter((n) => n.uuid !== item.uuid)
                              );
                            }}
                          >
                            <Icon icon="mingcute:delete-2-line" width="18" />
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div
                      className="border rounded p-3 text-muted"
                      style={{ minHeight: "60px" }}
                    >
                      No notifications yet
                    </div>
                  )}
                </div>
              </>
            )}

            {activeTab === "actions" && (
              <>
                <button
                  onClick={handleAddNewAction}
                  className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color mt-3"
                >
                  New
                </button>

                <h5 className="fw-bold text-success-800 fs-6 my-3">
                  Log History
                </h5>

                <div className="d-flex flex-column gap-3">
                  {actionsLog.length > 0 ? (
                    actionsLog.map((action) => (
                      <div
                        key={action.uuid || action.id}
                        className="border rounded p-3 d-flex justify-content-between align-items-start"
                        style={{ cursor: "pointer" }}
                        onClick={() => handleEditAction(action)}
                      >
                        {/* LEFT SIDE DETAILS */}
                        <div className="d-flex flex-column mb-0">
                          <strong>Action: {action.action}</strong>

                          <span className="text-secondary">
                            Due Date: {action.dueDate}
                          </span>

                          <span className="text-secondary">
                            Time: {action.time}
                          </span>
                        </div>

                        {/* ACTION BUTTONS */}
                        <div className="d-flex align-items-start gap-2">
                          <button
                            className="btn btn-link p-0 m-0"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEditAction(action);
                            }}
                          >
                            <Icon icon="lucide:edit" width="18" style={{  color: "#059669" }}/>
                          </button>

                          <button
                            className="btn btn-link text-danger p-0 m-0"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteAction(action.uuid || action.id);
                            }}
                          >
                            <Icon icon="mingcute:delete-2-line" width="18" />
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div
                      className="border rounded p-3 text-muted"
                      style={{ minHeight: "60px" }}
                    >
                      No actions yet
                    </div>
                  )}
                </div>

                {/* ACTION MODAL - FIXED */}
                <AddEditActionModal
                  show={showActionModal}
                  handleClose={handleCloseActionModal}
                  mode={actionMode}
                  rowData={editActionRow}
                />
              </>
            )}

            {activeTab === "office" && (
              <>
                <button
                  onClick={handleAddNewOffice}
                  className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color mt-3"
                >
                  New
                </button>

                <h5 className="fw-bold text-success-800 fs-6 my-3">
                  Log History
                </h5>

                <div className="d-flex flex-column gap-3">
                  {officeLog.length > 0 ? (
                    officeLog.map((item) => (
                      <div
                        key={item.uuid}
                        className="border rounded p-3 d-flex justify-content-between align-items-start"
                        style={{ cursor: "pointer" }}
                        onClick={() => handleEditOffice(item)}
                      >
                        <div className="d-flex flex-column mb-0">
                          <strong>Department: {item.department}</strong>
                          <span className="text-secondary">
                            Team: {item.teamName}
                          </span>
                          <span className="text-secondary">
                            Leader: {item.teamLeader}
                          </span>
                          <span className="text-secondary">
                            Team Supervisor: {item.teamSupervisor}
                          </span>
                          <span className="text-secondary">
                            Operative Executive: {item.operativeExecutive}
                          </span>
                        </div>

                        {/* ACTION BUTTONS */}
                        <div className="d-flex align-items-start gap-2">
                          <button
                            className="btn btn-link p-0 m-0"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEditOffice(item);
                            }}
                          >
                            <Icon icon="lucide:edit" width="18" style={{  color: "#059669" }}/>
                          </button>

                          {/* <Link
                            to="#"
                            className="edit-btn-icone"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEditOffice(item);
                            }}
                          >
                            <Icon
                              icon="lucide:edit"
                              width="18"
                              className="icone"
                            />
                          </Link> */}

                          <button
                            className="btn btn-link text-danger p-0 m-0"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteOffice(item.uuid);
                            }}
                          >
                            <Icon icon="mingcute:delete-2-line" width="18" />
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div
                      className="border rounded p-3 text-muted"
                      style={{ minHeight: "60px" }}
                    >
                      No office records yet
                    </div>
                  )}
                </div>

                {/* -------- OFFICE MODAL ---------- */}
                <AddEditOfficeModal
                  show={showOfficeModal}
                  handleClose={handleCloseOfficeModal}
                  mode={officeMode}
                  rowData={editOfficeRow}
                />
              </>
            )}
          </div>
        </div>

        <div className="card-body pt-0 container-table">
          <div className="container-table-div">
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
                    value={leadForOptions.find((o) => o.value === leadFor)}
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
                  <label className="form-label ">
                    Interested Visa Category
                  </label>
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
                <button
                  type="button"
                  className="btn btn-sm me-1"
                  onClick={scrollLeft}
                >
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
                    className={`${mainTabBtnClass("documents")} me-1`}
                    onClick={() => setActiveMainTab("documents")}
                  >
                    Documents
                  </button>
                  <button
                    type="button"
                    className={`${mainTabBtnClass("quick")} me-1`}
                    onClick={() => setActiveMainTab("quick")}
                  >
                    Quick Assessment
                  </button>
                </div>

                <button
                  type="button"
                  className="btn btn-sm"
                  onClick={scrollRight}
                >
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
                  Save
                </button>
                <button
                  type="button"
                  // className="btn btn-sm comman-btn-color border border-primary-600 text-md px-16 py-6 radius-6"
                  className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color"
                >
                  Next
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
