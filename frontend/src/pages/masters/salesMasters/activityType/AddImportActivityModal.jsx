import React, { useState } from 'react'
import { useDispatch } from "react-redux";
import { activityTypeImportData } from '../../../../store/master/salesMasters/actions';
import { toast } from "react-toastify";
import * as XLSX from 'xlsx';

const AddImportActivityModal = ({ show, handleClose }) => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    const [file, setFile] = useState(null);
    const [error, setError] = useState('');
    const [sheetNames, setSheetNames] = useState([]);
    const [selectedSheet, setSelectedSheet] = useState('');

    // Handle file change and extract sheet names
    const handleFileChange = async (e) => {
        const selectedFile = e.target.files[0];
        setFile(selectedFile);
        setError('');
        setSheetNames([]);
        setSelectedSheet('');

        if (selectedFile) {
            // Check if file is Excel
            const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
            if (fileExtension === 'xlsx' || fileExtension === 'xls') {
                try {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                        const data = new Uint8Array(event.target.result);
                        const workbook = XLSX.read(data, { type: 'array' });
                        const sheets = workbook.SheetNames;
                        setSheetNames(sheets);
                        if (sheets.length > 0) {
                            setSelectedSheet(sheets[0]); // Auto-select first sheet
                        }
                    };
                    reader.readAsArrayBuffer(selectedFile);
                } catch (err) {
                    toast.error("Error reading Excel file");
                }
            }
        }
    };

    // Handle submit
    const handleSubmit = (e) => {
        e.preventDefault();

        if (!file) {
            setError('Please upload a file');
            return;
        }

        if (sheetNames.length > 0 && !selectedSheet) {
            setError('Please select a sheet');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        if (selectedSheet) {
            formData.append('sheet_name', selectedSheet);
        }

        setLoading(true);
        dispatch(activityTypeImportData(formData, (response, error) => {
            setLoading(false);
            if (error) {
                toast.error(error?.response?.data?.message || "Server error");
            } else {
                if (response?.statusCode === 200 && response?.status === true) {
                    // toast.success(response?.message);
                    toast.success(
                        <div>
                            <div>{response?.message}</div>
                            {response?.duplicates?.length > 0 && (
                                <div style={{ marginTop: '6px' }}>
                                    <strong>Duplicate priority skipped:</strong>
                                    <br />
                                    {response.duplicates.map((item, index) => (
                                        <div key={index}>{item}</div>
                                    ))}
                                </div>
                            )}
                        </div>,
                        {
                            autoClose: 10000,
                        }
                    );
                    setFile(null);
                    setSheetNames([]);
                    setSelectedSheet('');
                    handleClose();
                } else {
                    toast.error("Something went wrong.");
                }
            }
        }));
    };

    // Handle modal close
    const onClose = () => {
        setFile(null);
        setError('');
        setSheetNames([]);
        setSelectedSheet('');
        handleClose();
        setLoading(false);
    };
    const handleDownloadSample = () => {
        const fileUrl = 'assets/simplefile/activity.xlsx'; // Update this path according to your project structure

        const link = document.createElement('a');
        link.href = fileUrl;
        link.download = 'activity_sample.xlsx'; // Downloaded file name
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleBackdropClick = (e) => {
        // Only close if clicking the backdrop itself, not the modal content
        if (e.target === e.currentTarget) {
            onClose();
        }
    };
    if (!show) return null;

    return (
        <div
            className="modal fade show common-ctl-popup"
            tabIndex={-1}
            role="dialog"
            aria-labelledby="ActivityTypeModalLabel"
            aria-hidden={!show}
            onClick={handleBackdropClick}
        >
            <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
                <div className="modal-content radius-16 bg-base">
                    <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
                        <h1 className="modal-title fs-5" id="ActivityTypeModalLabel">
                            Upload Activity Type
                        </h1>
                        <button
                            type="button"
                            className="btn-close"
                            onClick={onClose}
                            aria-label="Close"
                        />
                    </div>

                    <div className="modal-body p-24">
                        <div className='text-md-end text-end'>
                            <button
                                type="button"
                                onClick={handleDownloadSample}
                                className="btn btn-sm text-white fw-medium px-3 py-1 w-md-auto comman-btn-color">
                                Sample Excel
                            </button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="row">
                                <div className="col-12 mb-20">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                        Upload File <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="file"
                                        className={`form-control radius-8 ${error && !selectedSheet ? 'is-invalid' : ''}`}
                                        onChange={handleFileChange}
                                        accept=".csv,.xlsx,.xls,.pdf,.docx"
                                        style={{ height: "auto" }}
                                    />
                                    {error && !sheetNames.length && <div className="text-danger text-sm mt-1">{error}</div>}
                                </div>
                                {sheetNames.length > 0 && (
                                    <div className="col-12 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Select name <span className="text-danger">*</span>
                                        </label>
                                        <div className="d-flex flex-column gap-2">
                                            {sheetNames.map((sheetName, index) => (
                                                <div key={index} className="form-check d-flex align-items-center">
                                                    <input
                                                        className="form-check-input mt-0"
                                                        type="radio"
                                                        name="sheetSelection"
                                                        id={`sheet-${index}`}
                                                        value={sheetName}
                                                        checked={selectedSheet === sheetName}
                                                        onChange={(e) => setSelectedSheet(sheetName)}
                                                        style={{
                                                            width: '18px',
                                                            height: '18px',
                                                            cursor: 'pointer'
                                                        }}
                                                    />
                                                    <label
                                                        className="form-check-label ms-2"
                                                        htmlFor={`sheet-${index}`}
                                                        style={{ cursor: 'pointer' }}
                                                    >
                                                        {sheetName}
                                                    </label>
                                                </div>
                                            ))}
                                        </div>
                                        {error && sheetNames.length > 0 && <div className="text-danger text-sm mt-1">{error}</div>}
                                    </div>
                                )}
                                <div className="d-flex align-items-center justify-content-center gap-3 mt-24">
                                    <button
                                        type="button"
                                        onClick={onClose}
                                        className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-40 py-6 radius-8"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        disabled={loading}
                                        className="btn comman-btn-color border border-primary-600 text-md px-40 py-6 radius-8"
                                    >
                                        {loading ? "Upload" : "Upload"}
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AddImportActivityModal;