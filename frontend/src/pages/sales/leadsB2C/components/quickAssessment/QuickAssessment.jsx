import { Icon } from "@iconify/react/dist/iconify.js";
import React, { useRef, useState } from "react";
import Select from "react-select";

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
      {/* <div className="card-header d-flex justify-content-between align-items-center py-3 px-4 border-bottom">
        <h6 className="mb-0 fw-semibold fs-5" style={{ color: "#5a6c5b" }}>
          {title}
        </h6>
        <button
          onClick={handleAddNew}
          className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color"
        >
          New
        </button>
      </div> */}

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
const QuickAssessment = () => {
  const [mainAreas, setMainAreas] = useState([]);
  const [majorAreas, setMajorAreas] = useState([]);

  const mainOptions = [
    { value: "engineering", label: "Engineering" },
    { value: "business", label: "Business" },
    { value: "it", label: "Information Technology" },
    { value: "health", label: "Health Sciences" },
  ];

  const majorOptions = [
    { value: "software", label: "Software Development" },
    { value: "civil", label: "Civil Engineering" },
    { value: "marketing", label: "Marketing" },
    { value: "nursing", label: "Nursing" },
  ];
  const [data, setData] = useState([
    {
      id: 1,
      country: "Canada",
      state: "British Columbia",
      occupationLevel: "TEER 02",
      occupationName: "Sales Supervisor",
    },
    {
      id: 2,
      country: "Canada",
      state: "Alberta",
      occupationLevel: "TEER 02",
      occupationName: "Assistant Sales Manager",
    },
    {
      id: 3,
      country: "Canada",
      state: "Manitoba",
      occupationLevel: "TEER 02",
      occupationName: "Team Leader",
    },
  ]);

  const [dataModal, setDataModal] = useState({
    show: false,
    mode: "add",
    rowData: null,
  });

  const handleDataShow = (mode = "add", rowData = null) => {
    setDataModal({ show: true, mode, rowData });
  };

  const handleDataClose = (shouldRefresh = false) => {
    setDataModal({ show: false, mode: "add", rowData: null });
    if (shouldRefresh) console.log("Refresh data");
  };

  const handleDataEdit = (rowData) => {
    handleDataShow("edit", rowData);
  };

  const handleAddNewData = () => {
    handleDataShow("add");
  };

  // --- TABLE COLUMNS ---
  const dataColumns = [
    { id: "country", label: "Country", field: "country" },
    { id: "state", label: "State", field: "state" },
    {
      id: "occupationLevel",
      label: "Occupation Level",
      field: "occupationLevel",
    },
    { id: "occupationName", label: "Occupation Name", field: "occupationName" },
  ];

  const [dataVisible, setDataVisible] = useState(dataColumns.map((c) => c.id));

  const [visaType, setVisaType] = useState(null);

  // ---- STATIC OPTIONS ----
  const visaMainOptions = [
    { value: "", label: "Master (Visa Main Category)" },
    { value: "1", label: "Main Category 1" },
    { value: "2", label: "Main Category 2" },
  ];

  const visaMajorOptions = [
    { value: "", label: "Master (Visa Major Category)" },
    { value: "1", label: "Major Category 1" },
  ];

  const countryOptions = [
    { value: "", label: "Master (Representing Country)" },
    { value: "in", label: "India" },
    { value: "ca", label: "Canada" },
  ];

  const visaNameOptions = [
    { value: "student", label: "Student Visa" },
    { value: "skilled", label: "Skilled PR" },
    { value: "condition", label: "Condition Base" },
    { value: "work", label: "Work Permit" },
  ];

  const yesNoOptions = [
    { value: "yes", label: "Yes" },
    { value: "no", label: "No" },
  ];

  return (
    <div
      className="section-block p-3 bg-white border"
      style={{ minWidth: 320 }}
    >
      {/* CREATE BUTTON */}
      <div className="d-flex align-items-center justify-content-end mb-3">
        <button
          type="button"
          className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color"
        >
          Create
        </button>
      </div>

      {/* ===================== MAIN SELECTORS ===================== */}
      <div className="row g-3">
        {/* Visa Main Category */}
        <div className="col-md-4">
          <label className="form-label fw-semibold">
            Visa Main Category <span className="text-danger">*</span>
          </label>
          <Select options={visaMainOptions} />
        </div>

        {/* Visa Major Category */}
        <div className="col-md-4">
          <label className="form-label fw-semibold">
            Visa Major Category <span className="text-danger">*</span>
          </label>
          <Select options={visaMajorOptions} />
        </div>

        {/* Country */}
        <div className="col-md-4">
          <label className="form-label fw-semibold">
            Country <span className="text-danger">*</span>
          </label>
          <Select options={countryOptions} />
        </div>

        {/* Visa Name */}
        <div className="col-4">
          <label className="form-label fw-semibold">
            Visa Name <span className="text-danger">*</span>
          </label>
          <Select
            options={visaNameOptions}
            value={visaNameOptions.find((o) => o.value === visaType) || null}
            onChange={(option) => setVisaType(option?.value || null)}
          />
        </div>
      </div>

      {/* ===================== STUDENT FORM ===================== */}
      {visaType === "student" && (
        <div className="mt-4">
          <div className="row g-3 mb-20">
            <div className="col-4">
              <label className="form-label">State</label>
              <Select
                options={[{ value: "", label: "Master (As per country)" }]}
              />
            </div>

            <div className="col-4">
              <label className="form-label">City</label>
              <Select
                options={[
                  { value: "", label: "Master (As per Country & State)" },
                ]}
              />
            </div>
          </div>
          <div className="row g-3 mb-20">
            <div className="col-4">
              <label className="form-label">Course Level</label>
              <Select
                options={[
                  { value: "", label: "Master (Eligible Course Level)" },
                ]}
              />
            </div>

            {/* Course Duration */}
            <div className="col-md-4">
              <label className="form-label">Course Duration</label>
              <div className="d-flex gap-2">
                <Select
                  options={[{ value: "", label: "Master" }]}
                  className="flex-grow-1"
                />
                <Select
                  options={[{ value: "months", label: "Months" }]}
                  className="flex-grow-1"
                />
              </div>
            </div>
          </div>

          <div className="row g-3 mb-20">
            <div className="col-md-12">
              <label className="form-label">Study Main Areas</label>
              <Select
                isMulti
                options={mainOptions}
                value={mainAreas}
                onChange={(selected) => setMainAreas(selected || [])}
                placeholder="Select Study Main Areas"
              />
            </div>

            <div className="col-md-12">
              <label className="form-label">Study Major Areas</label>
              <Select
                isMulti
                options={majorOptions}
                value={majorAreas}
                onChange={(selected) => setMajorAreas(selected || [])}
                placeholder="Select Study Major Areas"
              />
            </div>
          </div>

          <div className="row g-3 mb-20">
            {/* Intake */}
            <div className="col-md-2">
              <label className="form-label">Intake Month</label>
              <Select options={[{ value: "", label: "Month Name" }]} />
            </div>
            <div className="col-md-2">
              <label className="form-label">Intake Name</label>
              <Select options={[{ value: "", label: "Master" }]} />
            </div>

            {/* Fees */}
            <div className="col-md-4 ">
              <label className="form-label">Max. Application Fee</label>
              <div className="d-flex gap-2">
                <input
                  className="form-control form-control-sm w-full"
                  placeholder="Amount"
                />
                <input
                  className="form-control form-control-sm w-full"
                  placeholder="Amount"
                />
              </div>
            </div>

            <div className="col-md-4">
              <label className="form-label">Max. Course Fee</label>
              <div className="d-flex gap-2">
                <input
                  className="form-control form-control-sm w-full"
                  placeholder="Amount"
                />
                <input
                  className="form-control form-control-sm w-full"
                  placeholder="Amount"
                />
              </div>{" "}
            </div>
          </div>
          <div className="row g-3 mb-20">
            {/* Scholarship */}
            <div className="col-md-4">
              <label className="form-label">Scholarship</label>

              <div className="row g-2">
                <div className="col-md-6 ">
                  <Select options={yesNoOptions}  />
                </div>

                <div className="col-md-6 ">
                  <input
                    className="form-control form-control-sm "
                    placeholder="Amount"
                  />
                </div>
              </div>
            </div>

            <div className="col-md-4">
              <label className="form-label">MOI Acceptable</label>
              <Select options={yesNoOptions} />
            </div>

            {/* ESL */}
            <div className="col-md-4">
              <label className="form-label">With ESL Available</label>
              <Select options={yesNoOptions} />
            </div>
          </div>
          <div className="row g-3 mb-20">
            <div className="col-md-3">
              <label className="form-label">With Pre-Course</label>
              <Select options={yesNoOptions} />
            </div>
          </div>
        </div>
      )}

      {/* ===================== PR & WORK PERMIT FORM ===================== */}
      {(visaType === "skilled" ||
        visaType === "condition" ||
        visaType === "work") && (
        <div className="mt-4">
          <div className="row g-3">
            <div className="col-md-4 mb-10">
              <label className="form-label">With Job Offer?</label>
              <Select options={yesNoOptions} />
            </div>

            {/* Table */}
            <ReusableTable
              data={data}
              setData={setData}
              columns={dataColumns}
              visibleColumns={dataVisible}
              setVisibleColumns={setDataVisible}
              tableSize="small"
              enableSorting={true}
              onEditClick={handleDataEdit}
              onAddNew={handleAddNewData}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default QuickAssessment;
