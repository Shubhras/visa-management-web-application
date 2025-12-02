import React, { useState, useRef } from "react";
import { Icon } from "@iconify/react/dist/iconify.js";
import AddEditSpouseEducationModal from "./AddEditSpouseEducationModal";
import AddEditSpouseExperienceModal from "./AddEditSpouseExperienceModal";
import AddEditSpouseLanguageModal from "./AddEditSpouseLanguageModal";
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
        <h6 className="mb-0 fw-semibold fs-5" style={{ color: "#5a6c5b" }}>
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

const SpouseDetails = () => {
  const [spouseEducation, setSpouseEducation] = useState([
    {
      id: 1,
      educationLevel: "Bachelors",
      duration: "48",
      studyMainArea: "Engineering",
      eduType: "Full-Time",
      startDate: "2000-01-31",
      endDate: "2004-04-02",
      result: "67.04%",
    },
    {
      id: 2,
      educationLevel: "Masters",
      duration: "24",
      studyMainArea: "Computer Science",
      eduType: "Full-Time",
      startDate: "2000-01-31",
      endDate: "2004-01-31",
      result: "78.50%",
    },
  ]);
  const [spouseExperience, setSpouseExperience] = useState([
    {
      id: 1,
      employerName: "ABC Technologies",
      occupation: "Software Engineer",
      jobType: "Full-Time",
      startDate: "2015-06-01",
      endDate: "2018-03-15",
      salary: 45000,
    },
    {
      id: 2,
      employerName: "XYZ Pvt Ltd",
      occupation: "Senior Developer",
      jobType: "Part-Time",
      startDate: "2018-04-01",
      endDate: "2022-01-10",
      salary: 60000,
    },
  ]);
  const [spouseLanguage, setSpouseLanguage] = useState([
    {
      id: 1,
      language: "English",
      testName: "IELTS",
      testLevel: "Advanced",
      listening: 8,
      speaking: 7.5,
      reading: 8.5,
      writing: 7,
      overall: 7.8,
      testDate: "2023-06-15",
    },
  ]);

  const [educationModal, setEducationModal] = useState({
    show: false,
    mode: "add",
    rowData: null,
  });
  const [experienceModal, setExperienceModal] = useState({
    show: false,
    mode: "add",
    rowData: null,
  });
  const [languageModal, setLanguageModal] = useState({
    show: false,
    mode: "add",
    rowData: null,
  });
  // Education Modal Handlers
  const handleEducationShow = (mode = "add", rowData = null) => {
    setEducationModal({ show: true, mode, rowData });
  };

  const handleEducationClose = (shouldRefresh = false) => {
    setEducationModal({ show: false, mode: "add", rowData: null });
    if (shouldRefresh) console.log("Refresh education data");
  };

  const handleEducationEdit = (rowData) => {
    handleEducationShow("edit", rowData);
  };

  const handleAddNewEducation = () => {
    handleEducationShow("add");
  };

  const handleExperienceShow = (mode = "add", rowData = null) => {
    setExperienceModal({ show: true, mode, rowData });
  };

  const handleExperienceClose = (shouldRefresh = false) => {
    setExperienceModal({ show: false, mode: "add", rowData: null });
    if (shouldRefresh) console.log("Refresh spouse experience data");
  };

  const handleExperienceEdit = (rowData) => {
    handleExperienceShow("edit", rowData);
  };

  const handleAddNewExperience = () => {
    handleExperienceShow("add");
  };

  const handleLanguageShow = (mode = "add", rowData = null) => {
    setLanguageModal({ show: true, mode, rowData });
  };

  const handleLanguageClose = (shouldRefresh = false) => {
    setLanguageModal({ show: false, mode: "add", rowData: null });
    if (shouldRefresh) console.log("Refresh language data");
  };

  const handleLanguageEdit = (rowData) => {
    handleLanguageShow("edit", rowData);
  };

  const handleAddNewLanguage = () => {
    handleLanguageShow("add");
  };

  // Column Definitions
  const spouseEducationColumns = [
    { id: "educationLevel", label: "Education Level", field: "educationLevel" },
    { id: "duration", label: "Duration", field: "duration" },
    { id: "studyMainArea", label: "Study Main Area", field: "studyMainArea" },
    { id: "eduType", label: "Edu. Type", field: "eduType" },
    { id: "startDate", label: "Start Date", field: "startDate" },
    { id: "endDate", label: "End Date", field: "endDate" },
    { id: "result", label: "Result", field: "result" },
  ];
  const spouseExperienceColumns = [
    { id: "employerName", label: "Employer Name", field: "employerName" },
    { id: "occupation", label: "Occupation", field: "occupation" },
    { id: "jobType", label: "Job Type", field: "jobType" },
    { id: "startDate", label: "Start Date", field: "startDate" },
    { id: "endDate", label: "End Date", field: "endDate" },
    { id: "salary", label: "Salary", field: "salary" },
  ];

  const spouseLanguageColumns = [
    { id: "language", label: "Language", field: "language" },
    { id: "testName", label: "Test Name", field: "testName" },
    { id: "testLevel", label: "Test Level", field: "testLevel" },
    { id: "listening", label: "Listening", field: "listening" },
    { id: "speaking", label: "Speaking", field: "speaking" },
    { id: "reading", label: "Reading", field: "reading" },
    { id: "writing", label: "Writing", field: "writing" },
    { id: "overall", label: "Overall", field: "overall" },
    { id: "testDate", label: "Test Date", field: "testDate" },
  ];

  const [spouseEduVisible, setSpouseEduVisible] = useState(
    spouseEducationColumns.map((c) => c.id)
  );
  const [spouseExperienceVisible, setSpouseExperienceVisible] = useState(
    spouseExperienceColumns.map((c) => c.id)
  );
  const [spouseLanguageVisible, setSpouseLanguageVisible] = useState(
    spouseLanguageColumns.map((c) => c.id)
  );

  return (
    <div className="section-block">
      <style>{`
                .small-table-container .principle-table-div {
                    max-height: 300px !important;
                    min-height: 150px !important;
                    overflow-y: auto;
                    position: relative;
                    background-color: white;
                }
            `}</style>

      <div className="container-fluid">
        {/* Education - Small Table */}
        <ReusableTable
          title="Spouse : Education"
          data={spouseEducation}
          setData={setSpouseEducation}
          columns={spouseEducationColumns}
          visibleColumns={spouseEduVisible}
          setVisibleColumns={setSpouseEduVisible}
          tableSize="small"
          enableSorting={true}
          onEditClick={handleEducationEdit}
          onAddNew={handleAddNewEducation}
        />
        <ReusableTable
          title="Spouse : Experience"
          data={spouseExperience}
          setData={setSpouseExperience}
          columns={spouseExperienceColumns}
          visibleColumns={spouseExperienceVisible}
          setVisibleColumns={setSpouseExperienceVisible}
          tableSize="small"
          enableSorting={true}
          onEditClick={handleExperienceEdit}
          onAddNew={handleAddNewExperience}
        />

        <ReusableTable
          title="Spouse : Language Ability"
          data={spouseLanguage}
          setData={setSpouseLanguage}
          columns={spouseLanguageColumns}
          visibleColumns={spouseLanguageVisible}
          setVisibleColumns={setSpouseLanguageVisible}
          tableSize="small"
          enableSorting={true}
          onEditClick={handleLanguageEdit}
          onAddNew={handleAddNewLanguage}
        />
      </div>
      <AddEditSpouseEducationModal
        show={educationModal.show}
        mode={educationModal.mode}
        rowData={educationModal.rowData}
        handleClose={handleEducationClose}
      />
      <AddEditSpouseExperienceModal
        show={experienceModal.show}
        mode={experienceModal.mode}
        rowData={experienceModal.rowData}
        handleClose={handleExperienceClose}
      />
      <AddEditSpouseLanguageModal
        show={languageModal.show}
        mode={languageModal.mode}
        rowData={languageModal.rowData}
        handleClose={handleLanguageClose}
      />
    </div>
  );
};

export default SpouseDetails;
