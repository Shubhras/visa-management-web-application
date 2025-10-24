// import React, { useState } from 'react'
// import { useDispatch } from "react-redux";
// import { employeeTypeExportData } from '../../../store/master/actions';
// import { toast } from "react-toastify";

// const AddImportModal = ({ show, handleClose }) => {
//     const dispatch = useDispatch();
//     const [loading, setLoading] = useState(false);
//     const [file, setFile] = useState(null);
//     const [error, setError] = useState('');

//     // Handle file change
//     const handleFileChange = (e) => {
//         setFile(e.target.files[0]);
//         setError('');
//     };

//     // Handle submit
//     const handleSubmit = (e) => {
//         e.preventDefault();

//         if (!file) {
//             setError('Please upload a file');
//             return;
//         }

//         const formData = new FormData();
//         formData.append('file', file);

//         setLoading(true);
//         dispatch(employeeTypeExportData(formData, (response, error) => {
//             setLoading(false);
//             if (error) {
//                 toast.error(error?.response?.data?.message || "Server error");
//             } else {
//                 if (response?.statusCode === 200 && response?.status === true) {
//                     toast.success(response?.message);
//                     setFile(null);
//                     handleClose();
//                 } else {
//                     toast.error("Something went wrong.");
//                 }
//             }
//         }));
//     };

//     // Handle modal close
//     const onClose = () => {
//         setFile(null);
//         setError('');
//         handleClose();
//     };

//     if (!show) return null;

//     return (
//         <div
//             className="modal fade show"
//             style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}
//             tabIndex={-1}
//             role="dialog"
//             aria-labelledby="employeeTypeModalLabel"
//             aria-hidden={!show}
//         >
//             <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
//                 <div className="modal-content radius-16 bg-base">
//                     <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
//                         <h1 className="modal-title fs-5" id="employeeTypeModalLabel">
//                             Upload Employee Type
//                         </h1>
//                         <button
//                             type="button"
//                             className="btn-close"
//                             onClick={onClose}
//                             aria-label="Close"
//                         />
//                     </div>

//                     <div className="modal-body p-24">
//                         <form onSubmit={handleSubmit}>
//                             <div className="row">
//                                 {/* File Upload */}
//                                 <div className="col-12 mb-20">
//                                     <label className="form-label fw-semibold text-primary-light text-sm mb-8">
//                                         Upload File <span className="text-danger">*</span>
//                                     </label>
//                                     <input
//                                         type="file"
//                                         className={`form-control radius-8 ${error ? 'is-invalid' : ''}`}
//                                         onChange={handleFileChange}
//                                         accept=".csv,.xlsx,.xls,.pdf,.docx"
//                                     />
//                                     {error && <div className="text-danger text-sm mt-1">{error}</div>}
//                                 </div>

//                                 {/* Buttons */}
//                                 <div className="d-flex align-items-center justify-content-center gap-3 mt-24">
//                                     <button
//                                         type="button"
//                                         onClick={onClose}
//                                         className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-40 py-11 radius-8"
//                                     >
//                                         Cancel
//                                     </button>
//                                     <button
//                                         type="submit"
//                                         disabled={loading}
//                                         className="btn btn-primary border border-primary-600 text-md px-48 py-12 radius-8"
//                                     >
//                                         {loading ? "Uploading..." : "Upload"}
//                                     </button>
//                                 </div>
//                             </div>
//                         </form>
//                     </div>
//                 </div>
//             </div>
//         </div>
//     );
// };

// export default AddImportModal;

import React, { useState } from 'react'
import { useDispatch } from "react-redux";
import { employeeTypeExportData } from '../../../store/master/actions';
import { toast } from "react-toastify";
import * as XLSX from 'xlsx';

const AddImportModal = ({ show, handleClose }) => {
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
        dispatch(employeeTypeExportData(formData, (response, error) => {
            setLoading(false);
            if (error) {
                toast.error(error?.response?.data?.message || "Server error");
            } else {
                if (response?.statusCode === 200 && response?.status === true) {
                    toast.success(response?.message);
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
    };

    if (!show) return null;

    return (
        <div
            className="modal fade show"
            style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}
            tabIndex={-1}
            role="dialog"
            aria-labelledby="departmentModalLabel"
            aria-hidden={!show}
        >
            <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
                <div className="modal-content radius-16 bg-base">
                    <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
                        <h1 className="modal-title fs-5" id="departmentModalLabel">
                             Upload Employee Type
                        </h1>
                        <button
                            type="button"
                            className="btn-close"
                            onClick={onClose}
                            aria-label="Close"
                        />
                    </div>

                    <div className="modal-body p-24">
                        <form onSubmit={handleSubmit}>
                            <div className="row">
                                {/* File Upload */}
                                <div className="col-12 mb-20">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                        Upload File <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="file"
                                        className={`form-control radius-8 ${error && !selectedSheet ? 'is-invalid' : ''}`}
                                        onChange={handleFileChange}
                                        accept=".csv,.xlsx,.xls,.pdf,.docx"
                                    />
                                    {error && !sheetNames.length && <div className="text-danger text-sm mt-1">{error}</div>}
                                </div>

                                {/* Sheet Selection with Checkboxes - Only show for Excel files */}
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
                                                        type="checkbox"
                                                        id={`sheet-${index}`}
                                                        value={sheetName}
                                                        checked={selectedSheet === sheetName}
                                                        onChange={(e) => setSelectedSheet(e.target.checked ? sheetName : '')}
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

                                {/* Buttons */}
                                <div className="d-flex align-items-center justify-content-center gap-3 mt-24">
                                    <button
                                        type="button"
                                        onClick={onClose}
                                        className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-40 py-11 radius-8"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        disabled={loading}
                                        className="btn btn-primary border border-primary-600 text-md px-48 py-12 radius-8"
                                    >
                                        {loading ? "Uploading..." : "Upload"}
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

export default AddImportModal;