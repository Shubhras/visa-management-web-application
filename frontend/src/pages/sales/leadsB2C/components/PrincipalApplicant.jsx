import React, { useState, useRef } from 'react';
import { Icon } from '@iconify/react/dist/iconify.js';

const ReusableTable = ({
    title,
    data,
    setData,
    columns,
    visibleColumns,
    setVisibleColumns,
    tableSize = 'small',
    enableSorting = true // New prop to enable/disable sorting
}) => {
    const [selectedRows, setSelectedRows] = useState([]);
    const [showDropdown, setShowDropdown] = useState(false);
    const dropdownRef = useRef(null);

    // Sorting state
    const [sortState, setSortState] = useState([]);

    const isAllSelected = data.length > 0 && data.every(item => selectedRows.includes(item.id));

    // Sorting functions
    const handleSort = (field) => {
        if (!enableSorting) return;

        setSortState(prev => {
            let newSort = [...prev];
            const existingIndex = newSort.findIndex(s => s.field === field);

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

        const sortObj = sortState.find(s => s.field === field);
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
                if (typeof aValue === 'string' && typeof bValue === 'string') {
                    const comparison = aValue.localeCompare(bValue);
                    if (comparison !== 0) {
                        return order === 'asc' ? comparison : -comparison;
                    }
                } else {
                    // For numbers and other types
                    if (aValue < bValue) return order === 'asc' ? -1 : 1;
                    if (aValue > bValue) return order === 'asc' ? 1 : -1;
                }
            }
            return 0;
        });
    };

    const sortedData = getSortedData();

    const toggleColumn = (colId) => {
        setVisibleColumns(prev =>
            prev.includes(colId) ? prev.filter(id => id !== colId) : [...prev, colId]
        );
    };

    const handleSelectAll = (e) => {
        setSelectedRows(e.target.checked ? data.map(d => d.id) : []);
    };

    const handleRowSelect = (id) => {
        setSelectedRows(prev =>
            prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
        );
    };

    const handleDelete = (id) => {
        setData(prev => prev.filter(item => item.id !== id));
        setSelectedRows(prev => prev.filter(rowId => rowId !== id));
    };

    const handleAddNew = () => {
        const newId = data.length ? Math.max(...data.map(d => d.id)) + 1 : 1;
        const newRow = { id: newId };
        columns.forEach(col => {
            newRow[col.field] = col.field.includes('Date') ? 'DD/MM/YYYY' : '—';
        });
        setData([...data, newRow]);
    };

    return (
        <div className={`${tableSize}-table-container`}>
            <div className="card-header d-flex justify-content-between align-items-center py-3 px-4 border-bottom">
                <h6 className="mb-0 fw-semibold" style={{ color: '#5a6c5b' }}>{title}</h6>
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
                                {columns.map(col => (
                                    visibleColumns.includes(col.id) && (
                                        <th
                                            key={col.id}
                                            scope="col"
                                            className="sorting-th"
                                            onClick={() => handleSort(col.field)}
                                            style={{
                                                cursor: enableSorting ? 'pointer' : 'default',
                                                userSelect: 'none'
                                            }}
                                        >
                                            <div className="d-flex align-items-center">
                                                {col.label}
                                                {enableSorting && getSortIcon(col.field)}
                                            </div>
                                        </th>
                                    )
                                ))}
                                <th scope="col" className="action-th">
                                    <div className="position-relative table-header-hide-show" ref={dropdownRef}>
                                        <button
                                            className="border-0 bg-transparent"
                                            onClick={() => setShowDropdown(!showDropdown)}
                                        >
                                            Action <Icon icon="mdi:table-column" width="20" className="icone" />
                                        </button>
                                        {showDropdown && (
                                            <div className="position-absolute bg-white border rounded shadow-sm p-2 show-dropdowns-header" style={{ zIndex: 999, right: 0 }}>
                                                {columns.map(col => (
                                                    <div key={col.id} className="d-flex align-items-center gap-2 mb-1">
                                                        <input
                                                            type="checkbox"
                                                            className="form-check-input"
                                                            checked={visibleColumns.includes(col.id)}
                                                            onChange={() => toggleColumn(col.id)}
                                                        />
                                                        <label className="form-label mb-0 small">{col.label}</label>
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
                                    <td colSpan={visibleColumns.length + 2} className="no-records-found text-center py-4">
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
                                                <span>{String(index + 1).padStart(2, '0')}</span>
                                            </div>
                                        </td>
                                        {columns.map(col => (
                                            visibleColumns.includes(col.id) && (
                                                <td key={col.id}><span>{row[col.field] || '—'}</span></td>
                                            )
                                        ))}
                                        <td className="action-td">
                                            <div className="d-flex align-items-center gap-2">
                                                <button className="edit-btn-icone border-0 bg-transparent">
                                                    <Icon icon="lucide:edit" width="18" className="icone" />
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(row.id)}
                                                    className="delete-btn-icone border-0 bg-transparent"
                                                >
                                                    <Icon icon="mingcute:delete-2-line" width="18" className="icone" />
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
const PrincipalApplicantTables = () => {

    const [educations, setEducations] = useState([
        { id: 1, educationLevel: 'Bachelors', duration: '48', studyMainArea: 'Engineering', eduType: 'Full-Time', startDate: '16/07/2000', endDate: '02/04/2004', result: '67.04%' },
        { id: 2, educationLevel: 'Masters', duration: '24', studyMainArea: 'Computer Science', eduType: 'Full-Time', startDate: '01/08/2004', endDate: '30/06/2006', result: '78.50%' }
    ]);

    const [workExperiences, setWorkExperiences] = useState([
        { id: 1, employerName: 'ABCD Corporation', occupation: 'Sales Manager', jobType: 'Full-Time', startDate: '01/01/2023', endDate: '15/07/2025', salary: '27,000' },
        { id: 2, employerName: 'XYZ Technologies', occupation: 'Senior Developer', jobType: 'Full-Time', startDate: '15/03/2020', endDate: '31/12/2022', salary: '45,000' }
    ]);

    const [languageAbilities, setLanguageAbilities] = useState([
        { id: 1, language: 'English', testName: 'IELTS', testLevel: 'First', listening: '7.5', speaking: '8.0', reading: '7.0', writing: '7.5', overall: '7.5', testDate: '15/03/2024' }
    ]);

    const [entranceTests, setEntranceTests] = useState([
        { id: 1, entranceTestName: 'GRE', module01: '160', module02: '155', module03: '4.5', module04: 'N/A', total: '319.5', testDate: '20/02/2024' }
    ]);

    const [appearedEntranceTest, setAppearedEntranceTest] = useState('Yes');

    // Column Definitions
    const educationColumns = [
        { id: 'educationLevel', label: 'Education Level', field: 'educationLevel' },
        { id: 'duration', label: 'Duration (Months)', field: 'duration' },
        { id: 'studyMainArea', label: 'Study Main Area', field: 'studyMainArea' },
        { id: 'eduType', label: 'Edu. Type', field: 'eduType' },
        { id: 'startDate', label: 'Start Date', field: 'startDate' },
        { id: 'endDate', label: 'End Date', field: 'endDate' },
        { id: 'result', label: 'Result', field: 'result' }
    ];

    const workColumns = [
        { id: 'employerName', label: 'Employer Name', field: 'employerName' },
        { id: 'occupation', label: 'Occupation', field: 'occupation' },
        { id: 'jobType', label: 'Job Type', field: 'jobType' },
        { id: 'startDate', label: 'Start Date', field: 'startDate' },
        { id: 'endDate', label: 'End Date', field: 'endDate' },
        { id: 'salary', label: 'Salary', field: 'salary' }
    ];

    const languageColumns = [
        { id: 'language', label: 'Language', field: 'language' },
        { id: 'testName', label: 'Test Name', field: 'testName' },
        { id: 'testLevel', label: 'Test Level', field: 'testLevel' },
        { id: 'listening', label: 'Listening', field: 'listening' },
        { id: 'speaking', label: 'Speaking', field: 'speaking' },
        { id: 'reading', label: 'Reading', field: 'reading' },
        { id: 'writing', label: 'Writing', field: 'writing' },
        { id: 'overall', label: 'Overall', field: 'overall' },
        { id: 'testDate', label: 'Test Date', field: 'testDate' }
    ];

    const entranceColumns = [
        { id: 'entranceTestName', label: 'Entrance Test Name', field: 'entranceTestName' },
        { id: 'module01', label: 'Module 01', field: 'module01' },
        { id: 'module02', label: 'Module 02', field: 'module02' },
        { id: 'module03', label: 'Module 03', field: 'module03' },
        { id: 'module04', label: 'Module 04', field: 'module04' },
        { id: 'total', label: 'Total', field: 'total' },
        { id: 'testDate', label: 'Test Date', field: 'testDate' }
    ];

    // Visibility States
    const [eduVisible, setEduVisible] = useState(educationColumns.map(c => c.id));
    const [workVisible, setWorkVisible] = useState(workColumns.map(c => c.id));
    const [langVisible, setLangVisible] = useState(languageColumns.map(c => c.id));
    const [entranceVisible, setEntranceVisible] = useState(entranceColumns.map(c => c.id));

    return (
        <div className="section-block">
            <style>{`
  .small-table-container .principle-table-div {
    max-height: 300px !important;
    min-height: 150px !important;
    overflow-y: auto;
    position: relative;
    background-color: white;
    // border-radius: 8px;
  }

  
`}</style>

            <div className="container-fluid">
                {/* Education - Small Table */}
                <ReusableTable
                    title="Education (PA)"
                    data={educations}
                    setData={setEducations}
                    columns={educationColumns}
                    visibleColumns={eduVisible}
                    setVisibleColumns={setEduVisible}
                    tableSize="small"
                    enableSorting={true}
                />

                {/* Work Experience - Small Table */}
                <ReusableTable
                    title="Work Experience (PA)"
                    data={workExperiences}
                    setData={setWorkExperiences}
                    columns={workColumns}
                    visibleColumns={workVisible}
                    setVisibleColumns={setWorkVisible}
                    tableSize="small"
                    enableSorting={true}
                />


                <ReusableTable
                    title="Language Ability (PA)"
                    data={languageAbilities}
                    setData={setLanguageAbilities}
                    columns={languageColumns}
                    visibleColumns={langVisible}
                    setVisibleColumns={setLangVisible}
                    tableSize="small"
                    enableSorting={true}
                />


                <div className="mb-4 small-table-container">
                    <div className="card-header py-3 px-4 ">
                        <h6 className="mb-0 fw-semibold" style={{ color: '#5a6c5b' }}>Entrance Test Ability (PA)</h6>
                    </div>
                    <div className="mt-1">
                        <div className="row g-3 align-items-end">
                            <div className="col-md-4">
                                <label className="form-label fw-medium">Appeared Any Entrance Test?</label>
                                <select
                                    className="form-select form-select-sm"
                                    value={appearedEntranceTest}
                                    onChange={(e) => setAppearedEntranceTest(e.target.value)}
                                >
                                    <option value="">Select</option>
                                    <option value="Yes">Yes</option>
                                    <option value="No">No</option>
                                </select>
                            </div>
                            {appearedEntranceTest === "Yes" && (
                                <div className="col-md-4">
                                    <label className="form-label fw-medium">Entrance Test Name</label>
                                    <select className="form-select form-select-sm">
                                        <option>Select Test</option>
                                        <option>GRE</option>
                                        <option>GMAT</option>
                                        <option>SAT</option>
                                        <option>ACT</option>
                                    </select>
                                </div>
                            )}
                        </div>

                        {appearedEntranceTest === "Yes" && (
                            <div className="mt-4">
                                <ReusableTable
                                    title="Entrance Test Results"
                                    data={entranceTests}
                                    setData={setEntranceTests}
                                    columns={entranceColumns}
                                    visibleColumns={entranceVisible}
                                    setVisibleColumns={setEntranceVisible}
                                    tableSize="small"
                                    enableSorting={true}
                                />
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PrincipalApplicantTables;