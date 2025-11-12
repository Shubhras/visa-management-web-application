// utils/excelExportHelper.js
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';


/**
 * Format date to DD-MM-YYYY format
 * @param {string} dateString - Date string to format
 * @returns {string} Formatted date string
 */
export const formatDateDDMMYYYY = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString; // Return original if invalid date
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}-${month}-${year}`;
};



/**
 * Format date to DD-MM-YYYY HH:MM:SS AM/PM format
 * @param {string} dateString - Date string to format
 * @returns {string} Formatted date and time string (e.g., "25-12-2024 03:45:30 PM")
 */
export const formatDateDDMMYYYYTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString; // Return original if invalid date
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    let hours = date.getHours();
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    hours = String(hours).padStart(2, '0');
    return `${day}-${month}-${year} ${hours}:${minutes}:${seconds} ${ampm}`;
};
/**
 * Export data to Excel file with custom headers
 * @param {Array} data - Array of objects to export
 * @param {Array} headers - Array of header names in order
 * @param {string} sheetName - Name of the Excel sheet
 * @param {string} fileName - Name of the Excel file (without extension)
 */
export const exportToExcelWrongData = (data, headers, sheetName = 'Sheet1', fileName = 'ExportedData') => {
    try {
        // Map the data in the same order as headers
        const worksheetData = [
            headers,
            ...data.map(item => 
                headers.map(header => item[header] || "")
            )
        ];

        // Create worksheet and workbook
        const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);

        // Write workbook to buffer
        const excelBuffer = XLSX.write(workbook, {
            bookType: 'xlsx',
            type: 'array'
        });

        // Create Blob and save file
        const blob = new Blob([excelBuffer], {
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        });

        saveAs(blob, `${fileName}-Wrong-Data.xlsx`);
        return true;
    } catch (error) {
        console.error('Error exporting to Excel:', error);
        return false;
    }
};

/**
 * Export simple array data to Excel (for duplicate data)
 * @param {Array} data - Array of simple values
 * @param {string} headerName - Header name for the column
 * @param {string} sheetName - Name of the Excel sheet
 * @param {string} fileName - Name of the Excel file (without extension)
 */
export const exportSimpleArrayToExcel = (data, headerName, sheetName = 'Sheet1', fileName = 'ExportedData') => {
    try {
        const worksheetData = [
            [headerName],
            ...data.map(item => [item])
        ];

        const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);

        const excelBuffer = XLSX.write(workbook, {
            bookType: 'xlsx',
            type: 'array'
        });

        const blob = new Blob([excelBuffer], {
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        });

        saveAs(blob, `${fileName}.xlsx`);
        return true;
    } catch (error) {
        console.error('Error exporting to Excel:', error);
        return false;
    }
};

// Updated Component Usage Example
// import { exportToExcel, exportSimpleArrayToExcel } from '../utils/excelExportHelper';
//
// // For duplicate data:
// exportSimpleArrayToExcel(
//     response.duplicates,
//     "Civil ID Name",
//     "CivilIDName",
//     "CivilIDName-Duplicate-Data"
// );
//
// // For wrong data:
// exportToExcel(
//     response.skipped_rows,
//     ["Civil ID Name", "Reason"],
//     "CivilIDName",
//     "CivilIDName-WrongData-Data"
// );