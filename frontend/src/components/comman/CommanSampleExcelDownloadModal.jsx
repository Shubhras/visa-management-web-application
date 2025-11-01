import React, { useState } from 'react'
import { Link } from "react-router-dom";
import { toast } from "react-toastify";
import * as XLSX from 'xlsx';
import { saveAs } from "file-saver";
const CommanSampleExcelDownloadModal = ({ show, handleClose, prepareData }) => {
  const [items] = useState(prepareData?.items || []);
  const [selectedItems, setSelectedItems] = useState(prepareData?.selectedItems || []);
  const [ItemsRequired] = useState(prepareData?.ItemsRequired || []);

  const onCloseSampleExcelDownload = () => {
    handleClose();
  }
  const handleDragStart = (e, index) => {
    e.dataTransfer.setData("dragIndex", index);
  };

  const handleDrop = (e, dropIndex) => {
    e.preventDefault();
    const dragIndex = parseInt(e.dataTransfer.getData("dragIndex"));
    const newSelected = [...selectedItems];
    const draggedItem = newSelected.splice(dragIndex, 1)[0];
    newSelected.splice(dropIndex, 0, draggedItem);
    setSelectedItems(newSelected);
  };
  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleCheckboxChange = (item, checked) => {
    // prevent unchecking required items
    if (ItemsRequired.includes(item)) return;

    if (checked) {
      setSelectedItems([...selectedItems, item]);
    } else {
      setSelectedItems(selectedItems.filter((i) => i !== item));
    }
  };
  const handleExcelDonload = () => {
    const header = selectedItems;
    const duplicates = []; // Add your duplicate data here

    // Prepare worksheet data (header + rows)
    const worksheetData = [header, ...duplicates.map((item) => [item])];

    // Create worksheet and workbook
    const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, prepareData?.downloadFileName || "Sheet1");

    // Write workbook to buffer
    const excelBuffer = XLSX.write(workbook, { bookType: "xlsx", type: "array" });

    // Create blob and trigger download
    const blob = new Blob([excelBuffer], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    // saveAs(
    //   blob,
    //   `${prepareData?.downloadFileName || "departments"}_${new Date().toISOString().split("T")[0]}.xlsx`
    // );
     saveAs(
      blob,
      `${prepareData?.downloadFileName || "Sample"}-Sample.xlsx`
    );
    onCloseSampleExcelDownload();
    // Success message
    toast.success("Excel file downloaded successfully!");
  }

  if (!show) return null;
  return (
    <div
      className="modal show common-ctl-popup"
      tabIndex={-1}
      role="dialog"
      aria-labelledby="sampleExcelDownloadModalLabel"
      aria-hidden={!show} style={{ opacity: "1" }}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div className="modal-content radius-16 bg-base">
          <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
            <h1 className="modal-title fs-5">Sample Excel Download</h1>
            <button
              type="button"
              className="btn-close"
              onClick={onCloseSampleExcelDownload}
              aria-label="Close"
            />
          </div>
          <div className="modal-body p-24">
            <div className="row">
              <div className="col-12 col-md-6">
                <h3 className="text-sm font-semibold mb-3 text-gray-700">Available fields</h3>
                <div className="border rounded-lg p-3 bg-gray-50 export-file-left" >
                  {items.map((item, index) => (
                    <div
                      key={index}
                      className="bg-white border rounded p-2 mb-2 d-flex align-items-center gap-2 export-file"
                    >
                      <input
                        type="checkbox"
                        id={`item-${index}`}
                        checked={selectedItems.includes(item)}
                        onChange={(e) => handleCheckboxChange(item, e.target.checked)}
                        disabled={ItemsRequired.includes(item)} // 🔒 Disable required item
                        className="form-check-input"
                      />
                      <label htmlFor={`item-${index}`} className="mb-0 flex-grow-1">
                        {item}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
              <div className="col-12 col-md-6">
                <h3 className="text-sm font-semibold mb-3 text-gray-700">
                  Selected fields ({selectedItems.length})
                </h3>
                <div className="border rounded-lg p-3 bg-blue-50 export-file-righit" >
                  {selectedItems.length === 0 ? (
                    <div className="text-center text-muted py-5">
                      No fields selected
                    </div>
                  ) : (
                    selectedItems.map((item, index) => (
                      <div
                        key={index}
                        draggable
                        onDragStart={(e) => handleDragStart(e, index)}
                        onDrop={(e) => handleDrop(e, index)}
                        onDragOver={handleDragOver}
                        className="bg-white border border-primary rounded p-2 mb-2 d-flex align-items-center gap-2 export-file"
                        style={{ cursor: 'grab' }}
                      >
                        <span className="text-muted move-drop-icone">☰</span>
                        <span className="flex-grow-1">{item}</span>
                        {!ItemsRequired.includes(item) && (
                          <button
                            onClick={() => handleCheckboxChange(item, false)}
                            className="btn btn-sm btn-link text-danger p-0 close-icone"
                          >
                            ×
                          </button>
                        )}
                      </div>
                    ))
                  )}
                </div>
                <small className="text-muted mt-2 d-block">
                  💡 Drag items to reorder the export fields
                </small>
              </div>
            </div>
            <div className="d-flex align-items-center justify-content-center gap-3 mt-24">
              <button
                type="button"
                onClick={onCloseSampleExcelDownload}
                className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-40 py-6 radius-8"
              >
                Cancel
              </button>
              <button
                onClick={handleExcelDonload}
                type="button"
                className="btn comman-btn-color border border-primary-600 text-md px-40 py-6 radius-8"
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CommanSampleExcelDownloadModal;
