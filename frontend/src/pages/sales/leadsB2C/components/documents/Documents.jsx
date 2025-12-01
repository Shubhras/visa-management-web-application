import React, { useState, useRef } from "react";
import { Icon } from "@iconify/react/dist/iconify.js";
import AddEditDocumentsModal from "./AddEditDocumentsModal";
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

const Documents = () => {
  const [documents, setDocuments] = useState([
    {
      id: 1,
      documentCategory: "Passport",
      documentName: "Main Passport",
      attachment: "passport.jpg",
    },
    {
      id: 2,
      documentCategory: "Education",
      documentName: "Bachelors Degree",
      attachment: "degree.pdf",
    },
  ]);

  const [documentsModal, setDocumentsModal] = useState({
    show: false,
    mode: "add",
    rowData: null,
  });

  // --- MODAL HANDLERS ---
  const handleDocumentsShow = (mode = "add", rowData = null) => {
    setDocumentsModal({ show: true, mode, rowData });
  };

  const handleDocumentsClose = (shouldRefresh = false) => {
    setDocumentsModal({ show: false, mode: "add", rowData: null });
    if (shouldRefresh) console.log("Refresh documents data");
  };

  const handleDocumentsEdit = (rowData) => {
    handleDocumentsShow("edit", rowData);
  };

  const handleAddNewDocument = () => {
    handleDocumentsShow("add");
  };

  // --- TABLE COLUMNS ---
  const documentColumns = [
    {
      id: "documentCategory",
      label: "Document Category",
      field: "documentCategory",
    },
    { id: "documentName", label: "Document Name", field: "documentName" },
    { id: "attachment", label: "Attachment", field: "attachment" },
  ];

  const [documentVisible, setDocumentVisible] = useState(
    documentColumns.map((c) => c.id)
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
          title="Documents"
          data={documents}
          setData={setDocuments}
          columns={documentColumns}
          visibleColumns={documentVisible}
          setVisibleColumns={setDocumentVisible}
          tableSize="small"
          enableSorting={true}
          onEditClick={handleDocumentsEdit}
          onAddNew={handleAddNewDocument}
        />

        <AddEditDocumentsModal
          show={documentsModal.show}
          mode={documentsModal.mode}
          rowData={documentsModal.rowData}
          handleClose={handleDocumentsClose}
        />
      </div>
    </div>
  );
};

export default Documents;
