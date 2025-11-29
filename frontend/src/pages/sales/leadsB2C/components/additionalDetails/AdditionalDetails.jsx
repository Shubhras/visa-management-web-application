import React, { useState, useRef } from "react";
import { Icon } from "@iconify/react/dist/iconify.js";
import AddEditRelativesDetailsModal from "./AddEditRelativesDetailsModal";
import AddEditVisitedModal from "./AddEditVisitedModal";
import AddEditRefusedModal from "./AddEditRefusedModal";
import AddEditBusinessModal from "./AddEditBusinessModal";

const ReusableTable = ({
  title,
  data,
  setData,
  columns,
  visibleColumns,
  setVisibleColumns,
  tableSize = "small",
  enableSorting = true,
  onEditClick,
  onAddNew,
}) => {
  const [selectedRows, setSelectedRows] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  // Sorting state
  const [sortState, setSortState] = useState([]);

  const isAllSelected =
    data.length > 0 && data.every((item) => selectedRows.includes(item.id));

  // Sorting functions
  const handleSort = (field) => {
    if (!enableSorting) return;

    setSortState((prev) => {
      let newSort = [...prev];
      const existingIndex = newSort.findIndex((s) => s.field === field);

      if (existingIndex === -1) {
        newSort.push({ field, order: "asc" });
      } else {
        const existing = newSort[existingIndex];
        if (existing.order === "asc") {
          newSort[existingIndex].order = "desc";
        } else if (existing.order === "desc") {
          newSort.splice(existingIndex, 1);
        }
      }
      return newSort;
    });
  };

  const getSortIcon = (field) => {
    if (!enableSorting) return null;

    const sortObj = sortState.find((s) => s.field === field);
    if (!sortObj) {
      return <Icon icon="ri:menu-line" className="sorting-th-icone" />;
    }
    if (sortObj.order === "asc") {
      return <Icon icon="ri:sort-asc" className="sorting-th-icone" />;
    }
    return <Icon icon="ri:sort-desc" className="sorting-th-icone" />;
  };

  // Sort data based on sortState
  const getSortedData = () => {
    if (sortState.length === 0) return data;

    return [...data].sort((a, b) => {
      for (const sort of sortState) {
        const { field, order } = sort;
        const aValue = a[field];
        const bValue = b[field];

        // Handle different data types
        if (typeof aValue === "string" && typeof bValue === "string") {
          const comparison = aValue.localeCompare(bValue);
          if (comparison !== 0) {
            return order === "asc" ? comparison : -comparison;
          }
        } else {
          // For numbers and other types
          if (aValue < bValue) return order === "asc" ? -1 : 1;
          if (aValue > bValue) return order === "asc" ? 1 : -1;
        }
      }
      return 0;
    });
  };

  const sortedData = getSortedData();

  const toggleColumn = (colId) => {
    setVisibleColumns((prev) =>
      prev.includes(colId)
        ? prev.filter((id) => id !== colId)
        : [...prev, colId]
    );
  };

  const handleSelectAll = (e) => {
    setSelectedRows(e.target.checked ? data.map((d) => d.id) : []);
  };

  const handleRowSelect = (id) => {
    setSelectedRows((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const handleDelete = (id) => {
    setData((prev) => prev.filter((item) => item.id !== id));
    setSelectedRows((prev) => prev.filter((rowId) => rowId !== id));
  };

  const handleAddNew = () => {
    if (onAddNew) {
      onAddNew();
    } else {
      // Default behavior
      const newId = data.length ? Math.max(...data.map((d) => d.id)) + 1 : 1;
      const newRow = { id: newId };
      columns.forEach((col) => {
        newRow[col.field] = col.field.includes("Date") ? "DD/MM/YYYY" : "—";
      });
      setData([...data, newRow]);
    }
  };

  return (
    <div className={`${tableSize}-table-container`}>
      <div className="card-header d-flex justify-content-between align-items-center py-3 px-4 border-bottom">
        <h6 className="mb-0 fw-semibold" style={{ color: "#5a6c5b" }}>
          {title}
        </h6>
        <button
          onClick={handleAddNew}
          className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color"
        >
          New
        </button>
      </div>

      <div className="card-body pt-0 container-table">
        <div className="principle-table-div">
          <table className="table mb-0">
            <thead>
              <tr>
                <th scope="col" className="sl-numbar-th">
                  <div className="d-flex align-items-center gap-2">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      checked={isAllSelected}
                      onChange={handleSelectAll}
                      disabled={data.length === 0}
                    />
                    <span>No.</span>
                  </div>
                </th>
                {columns.map(
                  (col) =>
                    visibleColumns.includes(col.id) && (
                      <th
                        key={col.id}
                        scope="col"
                        className="sorting-th"
                        onClick={() => handleSort(col.field)}
                        style={{
                          cursor: enableSorting ? "pointer" : "default",
                          userSelect: "none",
                        }}
                      >
                        <div className="d-flex align-items-center">
                          {col.label}
                          {enableSorting && getSortIcon(col.field)}
                        </div>
                      </th>
                    )
                )}
                <th scope="col" className="action-th">
                  <div
                    className="position-relative table-header-hide-show"
                    ref={dropdownRef}
                  >
                    <button
                      className="border-0 bg-transparent"
                      onClick={() => setShowDropdown(!showDropdown)}
                    >
                      Action{" "}
                      <Icon
                        icon="mdi:table-column"
                        width="20"
                        className="icone"
                      />
                    </button>
                    {showDropdown && (
                      <div
                        className="position-absolute bg-white border rounded shadow-sm p-2 show-dropdowns-header"
                        style={{ zIndex: 999, right: 0 }}
                      >
                        {columns.map((col) => (
                          <div
                            key={col.id}
                            className="d-flex align-items-center gap-2 mb-1"
                          >
                            <input
                              type="checkbox"
                              className="form-check-input"
                              checked={visibleColumns.includes(col.id)}
                              onChange={() => toggleColumn(col.id)}
                            />
                            <label className="form-label mb-0 small">
                              {col.label}
                            </label>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedData.length === 0 ? (
                <tr>
                  <td
                    colSpan={visibleColumns.length + 2}
                    className="no-records-found text-center py-4"
                  >
                    No records found
                  </td>
                </tr>
              ) : (
                sortedData.map((row, index) => (
                  <tr key={row.id}>
                    <td>
                      <div className="d-flex align-items-center gap-2">
                        <input
                          className="form-check-input"
                          type="checkbox"
                          checked={selectedRows.includes(row.id)}
                          onChange={() => handleRowSelect(row.id)}
                        />
                        <span>{String(index + 1).padStart(2, "0")}</span>
                      </div>
                    </td>
                    {columns.map(
                      (col) =>
                        visibleColumns.includes(col.id) && (
                          <td key={col.id}>
                            <span>{row[col.field] || "—"}</span>
                          </td>
                        )
                    )}
                    <td className="action-td">
                      <div className="d-flex align-items-center gap-2">
                        <button
                          className="edit-btn-icone border-0 bg-transparent"
                          onClick={() => onEditClick(row)}
                        >
                          <Icon
                            icon="lucide:edit"
                            width="18"
                            className="icone"
                          />
                        </button>
                        <button
                          onClick={() => handleDelete(row.id)}
                          className="delete-btn-icone border-0 bg-transparent"
                        >
                          <Icon
                            icon="mingcute:delete-2-line"
                            width="18"
                            className="icone"
                          />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const AdditionalDetails = () => {
  const [formData, setFormData] = useState({
    hasRelatives: "",
    hasVisited: "",
    hasRefused: "",
    hasBusinessExperience: "",
    tradeCertificate: false,
    educationalAssessment: false,
    itaProvince: false,
    techStartupFounder: false,
    resideOutsideCity: false,
  });

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleCheckboxChange = (field) => {
    setFormData((prev) => ({ ...prev, [field]: !prev[field] }));
  };

  // -----------------------------
  // TABLE STATES (DUMMY DATA)
  // -----------------------------

  const [relatives, setRelatives] = useState([
    {
      id: 1,
      applicantType: "Self",
      country: "Canada",
      state: "Ontario",
      city: "Toronto",
      relation: "Brother",
      visaCategory: "PR",
    },
    {
      id: 2,
      applicantType: "Spouse",
      country: "Australia",
      state: "Victoria",
      city: "Melbourne",
      relation: "Sister",
      visaCategory: "Work Visa",
    },
  ]);
  const relativesColumns = [
    { id: "applicantType", label: "Applicant Type", field: "applicantType" },
    { id: "country", label: "Country", field: "country" },
    { id: "state", label: "State", field: "state" },
    { id: "city", label: "City", field: "city" },
    { id: "relation", label: "Relation", field: "relation" },
    { id: "visaCategory", label: "Visa Category", field: "visaCategory" },
  ];
  const [relativesVisible, setRelativesVisible] = useState(
    relativesColumns.map((c) => c.id)
  );

  const [visited, setVisited] = useState([
    {
      id: 1,
      applicantType: "Self",
      country: "USA",
      visaCategory: "Tourist",
      issueDate: "2022-04-10",
      travelFrom: "2022-05-01",
      travelTo: "2022-05-20",
      purpose: "Vacation",
    },
    {
      id: 2,
      applicantType: "Spouse",
      country: "Dubai",
      visaCategory: "Tourist",
      issueDate: "2021-10-01",
      travelFrom: "2021-11-12",
      travelTo: "2021-11-25",
      purpose: "Family Visit",
    },
  ]);
  const visitedColumns = [
    { id: "applicantType", label: "Applicant Type", field: "applicantType" },
    { id: "country", label: "Country", field: "country" },
    { id: "visaCategory", label: "Visa Category", field: "visaCategory" },
    { id: "issueDate", label: "Issue Date", field: "issueDate" },
    { id: "travelFrom", label: "Travel From", field: "travelFrom" },
    { id: "travelTo", label: "Travel To", field: "travelTo" },
    { id: "purpose", label: "Purpose of Visit", field: "purpose" },
  ];
  const [visitedVisible, setVisitedVisible] = useState(
    visitedColumns.map((c) => c.id)
  );

  const [refused, setRefused] = useState([
    {
      id: 1,
      applicantType: "Self",
      country: "UK",
      visaCategory: "Student Visa",
      refuseDate: "2020-02-15",
      reason: "Insufficient funds",
    },
  ]);
  const refusedColumns = [
    { id: "applicantType", label: "Applicant Type", field: "applicantType" },
    { id: "country", label: "Country", field: "country" },
    { id: "visaCategory", label: "Visa Category", field: "visaCategory" },
    { id: "refuseDate", label: "Refuse Date", field: "refuseDate" },
    { id: "reason", label: "Reason", field: "reason" },
  ];
  const [refusedVisible, setRefusedVisible] = useState(
    refusedColumns.map((c) => c.id)
  );

  const [business, setBusiness] = useState([
    {
      id: 1,
      country: "India",
      companyName: "Rajput Enterprises",
      companyType: "Partnership",
      share: "40",
      startDate: "2019-01-01",
      endDate: "2022-12-31",
      turnover: "1500000",
    },
    {
      id: 2,
      country: "Canada",
      companyName: "TechNova Solutions",
      companyType: "Proprietorship",
      share: "100",
      startDate: "2023-01-01",
      endDate: "",
      turnover: "800000",
    },
  ]);
  const businessColumns = [
    { id: "country", label: "Country", field: "country" },
    { id: "companyName", label: "Company Name", field: "companyName" },
    { id: "companyType", label: "Company Type", field: "companyType" },
    { id: "share", label: "Your Share (%)", field: "share" },
    { id: "startDate", label: "Start Date", field: "startDate" },
    { id: "endDate", label: "End Date", field: "endDate" },
    { id: "turnover", label: "Turnover", field: "turnover" },
  ];
  const [businessVisible, setBusinessVisible] = useState(
    businessColumns.map((c) => c.id)
  );

  const [property, setProperty] = useState([
    {
      id: 1,
      applicantType: "Self",
      country: "India",
      currency: "INR",
      immovable: 5000000, // Numeric
      movable: 2000000,   // Numeric
      liquid: 1000000,    // Numeric
      totalNetWorth: 8000000, // Auto-calculated
    },
    {
      id: 2,
      applicantType: "Spouse",
      country: "USA",
      currency: "USD",
      immovable: 300000,
      movable: 150000,
      liquid: 50000,
      totalNetWorth: 500000,
    },
  ]);

  // Columns definition
  const propertyColumns = [
    { id: "applicantType", label: "Applicant Type", field: "applicantType" },
    { id: "country", label: "Country", field: "country" },
    { id: "currency", label: "Currency", field: "currency" },
    { id: "immovable", label: "Immovable Property", field: "immovable" },
    { id: "movable", label: "Movable Property", field: "movable" },
    { id: "liquid", label: "Liquid Amount", field: "liquid" },
    { id: "totalNetWorth", label: "Total Net Worth", field: "totalNetWorth" },
  ];

  // Columns visible in the table
  const [propertyVisible, setPropertyVisible] = useState(
    propertyColumns.map((c) => c.id)
  );

  // Auto-calculate totalNetWorth whenever immovable, movable, or liquid changes
  const updatePropertyField = (id, field, value) => {
    setProperty((prev) =>
      prev.map((item) => {
        if (item.id === id) {
          const updatedItem = { ...item, [field]: Number(value) };
          updatedItem.totalNetWorth =
            (updatedItem.immovable || 0) +
            (updatedItem.movable || 0) +
            (updatedItem.liquid || 0);
          return updatedItem;
        }
        return item;
      })
    );
  };

  // -----------------------------
  // MODAL STATE
  // -----------------------------
  const [relativesModal, setRelativesModal] = useState({
    show: false,
    mode: "add",
    rowData: null,
  });

  const [visitedModal, setVisitedModal] = useState({
    show: false,
    mode: "add",
    rowData: null,
  });

  const [refusedModal, setRefusedModal] = useState({
    show: false,
    mode: "add",
    rowData: null,
  });

  const [businessModal, setBusinessModal] = useState({
    show: false,
    mode: "add",
    rowData: null,
  });

  // Relatives Modal Handlers
  const handleRelativesShow = (mode = "add", rowData = null) => {
    setRelativesModal({ show: true, mode, rowData });
  };

  const handleRelativesClose = (shouldRefresh = false) => {
    setRelativesModal({ show: false, mode: "add", rowData: null });
    if (shouldRefresh) console.log("Refresh relatives details data");
  };

  const handleRelativesEdit = (rowData) => {
    handleRelativesShow("edit", rowData);
  };

  const handleAddNewRelative = () => {
    handleRelativesShow("add");
  };

  const handleVisitedShow = (mode = "add", rowData = null) => {
    setVisitedModal({ show: true, mode, rowData });
  };

  const handleVisitedClose = (shouldRefresh = false) => {
    setVisitedModal({ show: false, mode: "add", rowData: null });
  };

  const handleVisitedEdit = (rowData) => {
    handleVisitedShow("edit", rowData);
  };

  const handleAddNewVisited = () => {
    handleVisitedShow("add");
  };

  const handleRefusedShow = (mode = "add", rowData = null) => {
    setRefusedModal({ show: true, mode, rowData });
  };

  const handleRefusedClose = () => {
    setRefusedModal({ show: false, mode: "add", rowData: null });
  };

  const handleRefusedEdit = (rowData) => {
    handleRefusedShow("edit", rowData);
  };

  const handleAddNewRefused = () => {
    handleRefusedShow("add");
  };
  const handleBusinessShow = (mode = "add", rowData = null) => {
    setBusinessModal({ show: true, mode, rowData });
  };

  const handleBusinessClose = () => {
    setBusinessModal({ show: false, mode: "add", rowData: null });
  };

  const handleBusinessEdit = (rowData) => {
    handleBusinessShow("edit", rowData);
  };

  const handleAddNewBusiness = () => {
    handleBusinessShow("add");
  };

  return (
    <div className="section-block container-fluid">
      {/* RELATIVES TABLE */}
      <div className="card mb-4">
        <div className="card-header bg-light py-3 d-flex align-items-center gap-2">
          <input
            type="checkbox"
            className="form-check-input"
            checked={formData.hasRelatives === "yes"}
            onChange={(e) =>
              handleInputChange("hasRelatives", e.target.checked ? "yes" : "no")
            }
          />
          <h6 className="mb-0 fw-semibold text-dark">
            Have you/spouse's RELATIVE in interested country?
          </h6>
        </div>

        {formData.hasRelatives === "yes" && (
          <ReusableTable
            title="Relatives Details"
            data={relatives}
            setData={setRelatives}
            columns={relativesColumns}
            visibleColumns={relativesVisible}
            setVisibleColumns={setRelativesVisible}
            onEditClick={handleRelativesEdit}
            onAddNew={handleAddNewRelative}
          />
        )}
      </div>

      {/* VISITED TABLE */}
      <div className="card mb-4">
        <div className="card-header bg-light py-3 d-flex align-items-center gap-2">
          <input
            type="checkbox"
            className="form-check-input"
            checked={formData.hasVisited === "yes"}
            onChange={(e) =>
              handleInputChange("hasVisited", e.target.checked ? "yes" : "no")
            }
          />
          <h6 className="mb-0 fw-semibold text-dark">
            Have you/spouse ever VISITED any country?
          </h6>
        </div>

        {formData.hasVisited === "yes" && (
          <ReusableTable
            title="Visited Countries"
            data={visited}
            setData={setVisited}
            columns={visitedColumns}
            visibleColumns={visitedVisible}
            setVisibleColumns={setVisitedVisible}
            onEditClick={handleVisitedEdit}
            onAddNew={handleAddNewVisited}
          />
        )}
      </div>

      {/* REFUSED TABLE */}
      <div className="card mb-4">
        <div className="card-header bg-light py-3 d-flex align-items-center gap-2">
          <input
            type="checkbox"
            className="form-check-input"
            checked={formData.hasRefused === "yes"}
            onChange={(e) =>
              handleInputChange("hasRefused", e.target.checked ? "yes" : "no")
            }
          />
          <h6 className="mb-0 fw-semibold text-dark">
            Have you/spouse ever been REFUSED by any country?
          </h6>
        </div>

        {formData.hasRefused === "yes" && (
          <ReusableTable
            title="Refused Country Details"
            data={refused}
            setData={setRefused}
            columns={refusedColumns}
            visibleColumns={refusedVisible}
            setVisibleColumns={setRefusedVisible}
            onEditClick={handleRefusedEdit}
            onAddNew={handleAddNewRefused}
          />
        )}
      </div>

      {/* BUSINESS EXPERIENCE TABLE */}
      <div className="card mb-4">
        <div className="card-header bg-light py-3 d-flex align-items-center gap-2">
          <input
            type="checkbox"
            className="form-check-input"
            checked={formData.hasBusinessExperience === "yes"}
            onChange={(e) =>
              handleInputChange(
                "hasBusinessExperience",
                e.target.checked ? "yes" : "no"
              )
            }
          />
          <h6 className="mb-0 fw-semibold text-dark">
            Do you have experience managing a business?
          </h6>
        </div>

        {formData.hasBusinessExperience === "yes" && (
          <ReusableTable
            title="Business Experience"
            data={business}
            setData={setBusiness}
            columns={businessColumns}
            visibleColumns={businessVisible}
            setVisibleColumns={setBusinessVisible}
            onEditClick={handleBusinessEdit}
            onAddNew={handleAddNewBusiness}
          />
        )}
      </div>

      <div className="card mb-4">
        <div className="card-header bg-light py-3 d-flex align-items-center gap-2">
          <input
            type="checkbox"
            className="form-check-input"
            // checked={formData.hasBusinessExperience === "yes"}
            // onChange={(e) =>
            //   handleInputChange(
            //     "hasBusinessExperience",
            //     e.target.checked ? "yes" : "no"
            //   )
            // }
          />
          <h6 className="mb-0 fw-semibold text-dark">
            Your Networth & Investment
          </h6>
        </div>

          <ReusableTable
            title="Networth & Investment"
            data={property}
            setData={setProperty}
            columns={propertyColumns}
            visibleColumns={propertyVisible}
            setVisibleColumns={setPropertyVisible}
            // onEditClick={handleBusinessEdit}
            // onAddNew={handleAddNewBusiness}
          />
      </div>




      {/* OTHER CHECKBOX QUESTIONS */}
      <div className="card mb-4">
        <div className="card-header bg-light py-3 d-flex flex-column ">
          {[
            ["tradeCertificate", "Do you have a Trade Certificate Assessment?"],
            [
              "educationalAssessment",
              "Do you have an Educational Credential Assessment?",
            ],
            ["itaProvince", "Do you have an ITA from Province?"],
            ["techStartupFounder", "Are you a Tech Startup Founder?"],
            [
              "resideOutsideCity",
              "Is your intention to reside outside a Greater City?",
            ],
          ].map(([field, label]) => (
            <div className="d-flex align-items-center mb-2 gap-2" key={field}>
              <input
                type="checkbox"
                className="form-check-input me-2"
                id={field}
                checked={formData[field]}
                onChange={() => handleCheckboxChange(field)}
              />
              <label className="form-check-label fw-medium" htmlFor={field}>
                {label}
              </label>
            </div>
          ))}
        </div>
      </div>

      {/* MODAL */}
      {relativesModal.show && (
        <AddEditRelativesDetailsModal
          show={relativesModal.show}
          mode={relativesModal.mode}
          rowData={relativesModal.rowData}
          handleClose={handleRelativesClose}
        />
      )}
      {visitedModal.show && (
        <AddEditVisitedModal
          show={visitedModal.show}
          mode={visitedModal.mode}
          rowData={visitedModal.rowData}
          handleClose={handleVisitedClose}
        />
      )}

      {refusedModal.show && (
        <AddEditRefusedModal
          show={refusedModal.show}
          mode={refusedModal.mode}
          rowData={refusedModal.rowData}
          handleClose={handleRefusedClose}
        />
      )}

      {businessModal.show && (
        <AddEditBusinessModal
          show={businessModal.show}
          mode={businessModal.mode}
          rowData={businessModal.rowData}
          handleClose={handleBusinessClose}
        />
      )}
    </div>
  );
};

export default AdditionalDetails;
