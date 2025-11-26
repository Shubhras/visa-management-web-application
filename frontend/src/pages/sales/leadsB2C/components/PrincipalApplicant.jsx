import React, { useState, useRef } from 'react';
import { Icon } from '@iconify/react/dist/iconify.js';

const PrincipalApplicant = () => {
    // Education Data
    const [educations, setEducations] = useState([
        {
            id: 1,
            educationLevel: 'Bachelors',
            duration: '48',
            studyMainArea: 'Engineering',
            eduType: 'Full-Time',
            startDate: '16/07/2000',
            endDate: '02/04/2004',
            result: '67.04%'
        },
        {
            id: 2,
            educationLevel: 'Masters',
            duration: '24',
            studyMainArea: 'Computer Science',
            eduType: 'Full-Time',
            startDate: '01/08/2004',
            endDate: '30/06/2006',
            result: '78.50%'
        }
    ]);

    // Work Experience Data
    const [workExperiences, setWorkExperiences] = useState([
        {
            id: 1,
            employerName: 'ABCD Corporation',
            occupation: 'Sales Manager',
            jobType: 'Full-Time',
            startDate: '01/01/2023',
            endDate: '15/07/2025',
            salary: '27,000'
        },
        {
            id: 2,
            employerName: 'XYZ Technologies',
            occupation: 'Senior Developer',
            jobType: 'Full-Time',
            startDate: '15/03/2020',
            endDate: '31/12/2022',
            salary: '45,000'
        }
    ]);

    // Language Ability Data
    const [languageAbilities, setLanguageAbilities] = useState([
        {
            id: 1,
            language: 'English',
            testName: 'IELTS',
            testLevel: 'First',
            listening: '7.5',
            speaking: '8.0',
            reading: '7.0',
            writing: '7.5',
            overall: '7.5',
            testDate: '15/03/2024'
        }
    ]);

    // Entrance Test Data
    const [entranceTests, setEntranceTests] = useState([
        {
            id: 1,
            entranceTestName: 'GRE',
            module01: '160',
            module02: '155',
            module03: '4.5',
            module04: 'N/A',
            total: '319.5',
            testDate: '20/02/2024'
        }
    ]);

    const [appearedEntranceTest, setAppearedEntranceTest] = useState('Yes');
    const [selectedEducationRows, setSelectedEducationRows] = useState([]);
    const [selectedWorkRows, setSelectedWorkRows] = useState([]);
    const [selectedLanguageRows, setSelectedLanguageRows] = useState([]);
    const [selectedEntranceRows, setSelectedEntranceRows] = useState([]);

    // Table columns configuration
    const educationColumns = [
        { id: 'educationLevel', label: 'Education Level', field: 'educationLevel', visible: true, required: false },
        { id: 'duration', label: 'Duration', field: 'duration', visible: true, required: false },
        { id: 'studyMainArea', label: 'Study Main Area', field: 'studyMainArea', visible: true, required: false },
        { id: 'eduType', label: 'Edu. Type', field: 'eduType', visible: true, required: false },
        { id: 'startDate', label: 'Start Date', field: 'startDate', visible: true, required: false },
        { id: 'endDate', label: 'End Date', field: 'endDate', visible: true, required: false },
        { id: 'result', label: 'Result', field: 'result', visible: true, required: false }
    ];

    const workExperienceColumns = [
        { id: 'employerName', label: 'Employer Name', field: 'employerName', visible: true, required: false },
        { id: 'occupation', label: 'Occupation', field: 'occupation', visible: true, required: false },
        { id: 'jobType', label: 'Job Type', field: 'jobType', visible: true, required: false },
        { id: 'startDate', label: 'Start Date', field: 'startDate', visible: true, required: false },
        { id: 'endDate', label: 'End date', field: 'endDate', visible: true, required: false },
        { id: 'salary', label: 'Salary', field: 'salary', visible: true, required: false }
    ];

    const languageAbilityColumns = [
        { id: 'language', label: 'Language', field: 'language', visible: true, required: false },
        { id: 'testName', label: 'Test Name', field: 'testName', visible: true, required: false },
        { id: 'testLevel', label: 'Test Level', field: 'testLevel', visible: true, required: false },
        { id: 'listening', label: 'Listening', field: 'listening', visible: true, required: false },
        { id: 'speaking', label: 'Speaking', field: 'speaking', visible: true, required: false },
        { id: 'reading', label: 'Reading', field: 'reading', visible: true, required: false },
        { id: 'writing', label: 'Writing', field: 'writing', visible: true, required: false },
        { id: 'overall', label: 'Overall', field: 'overall', visible: true, required: false },
        { id: 'testDate', label: 'Test Date', field: 'testDate', visible: true, required: false }
    ];

    const entranceTestColumns = [
        { id: 'entranceTestName', label: 'Entrance Test Name', field: 'entranceTestName', visible: true, required: false },
        { id: 'module01', label: 'Module-01', field: 'module01', visible: true, required: false },
        { id: 'module02', label: 'Module-02', field: 'module02', visible: true, required: false },
        { id: 'module03', label: 'Module-03', field: 'module03', visible: true, required: false },
        { id: 'module04', label: 'Module-04', field: 'module04', visible: true, required: false },
        { id: 'total', label: 'Total', field: 'total', visible: true, required: false },
        { id: 'testDate', label: 'Test Date', field: 'testDate', visible: true, required: false }
    ];

    // Column visibility states
    const [educationVisibleColumns, setEducationVisibleColumns] = useState(
        educationColumns.filter(col => col.visible).map(col => col.id)
    );
    const [workVisibleColumns, setWorkVisibleColumns] = useState(
        workExperienceColumns.filter(col => col.visible).map(col => col.id)
    );
    const [languageVisibleColumns, setLanguageVisibleColumns] = useState(
        languageAbilityColumns.filter(col => col.visible).map(col => col.id)
    );
    const [entranceVisibleColumns, setEntranceVisibleColumns] = useState(
        entranceTestColumns.filter(col => col.visible).map(col => col.id)
    );

    // Column dropdown refs
    const educationDropdownRef = useRef(null);
    const workDropdownRef = useRef(null);
    const languageDropdownRef = useRef(null);
    const entranceDropdownRef = useRef(null);

    // Column dropdown visibility states
    const [showEducationDropdown, setShowEducationDropdown] = useState(false);
    const [showWorkDropdown, setShowWorkDropdown] = useState(false);
    const [showLanguageDropdown, setShowLanguageDropdown] = useState(false);
    const [showEntranceDropdown, setShowEntranceDropdown] = useState(false);

    // Column visibility toggle handlers
    const toggleEducationColumnVisibility = (columnId) => {
        const column = educationColumns.find(col => col.id === columnId);
        if (column?.required) return;

        setEducationVisibleColumns(prev => {
            if (prev.includes(columnId)) {
                return prev.filter(id => id !== columnId);
            } else {
                return [...prev, columnId];
            }
        });
    };

    const toggleWorkColumnVisibility = (columnId) => {
        const column = workExperienceColumns.find(col => col.id === columnId);
        if (column?.required) return;

        setWorkVisibleColumns(prev => {
            if (prev.includes(columnId)) {
                return prev.filter(id => id !== columnId);
            } else {
                return [...prev, columnId];
            }
        });
    };

    const toggleLanguageColumnVisibility = (columnId) => {
        const column = languageAbilityColumns.find(col => col.id === columnId);
        if (column?.required) return;

        setLanguageVisibleColumns(prev => {
            if (prev.includes(columnId)) {
                return prev.filter(id => id !== columnId);
            } else {
                return [...prev, columnId];
            }
        });
    };

    const toggleEntranceColumnVisibility = (columnId) => {
        const column = entranceTestColumns.find(col => col.id === columnId);
        if (column?.required) return;

        setEntranceVisibleColumns(prev => {
            if (prev.includes(columnId)) {
                return prev.filter(id => id !== columnId);
            } else {
                return [...prev, columnId];
            }
        });
    };

    // Check if column is visible
    const isEducationColumnVisible = (columnId) => educationVisibleColumns.includes(columnId);
    const isWorkColumnVisible = (columnId) => workVisibleColumns.includes(columnId);
    const isLanguageColumnVisible = (columnId) => languageVisibleColumns.includes(columnId);
    const isEntranceColumnVisible = (columnId) => entranceVisibleColumns.includes(columnId);

    // Row selection handlers
    const handleEducationSelectAll = (e) => {
        const checked = e.target.checked;
        if (checked) {
            setSelectedEducationRows(educations.map(edu => edu.id));
        } else {
            setSelectedEducationRows([]);
        }
    };

    const handleWorkSelectAll = (e) => {
        const checked = e.target.checked;
        if (checked) {
            setSelectedWorkRows(workExperiences.map(work => work.id));
        } else {
            setSelectedWorkRows([]);
        }
    };

    const handleLanguageSelectAll = (e) => {
        const checked = e.target.checked;
        if (checked) {
            setSelectedLanguageRows(languageAbilities.map(lang => lang.id));
        } else {
            setSelectedLanguageRows([]);
        }
    };

    const handleEntranceSelectAll = (e) => {
        const checked = e.target.checked;
        if (checked) {
            setSelectedEntranceRows(entranceTests.map(test => test.id));
        } else {
            setSelectedEntranceRows([]);
        }
    };

    const handleEducationRowSelect = (id) => {
        setSelectedEducationRows(prev => {
            if (prev.includes(id)) {
                return prev.filter(rowId => rowId !== id);
            } else {
                return [...prev, id];
            }
        });
    };

    const handleWorkRowSelect = (id) => {
        setSelectedWorkRows(prev => {
            if (prev.includes(id)) {
                return prev.filter(rowId => rowId !== id);
            } else {
                return [...prev, id];
            }
        });
    };

    const handleLanguageRowSelect = (id) => {
        setSelectedLanguageRows(prev => {
            if (prev.includes(id)) {
                return prev.filter(rowId => rowId !== id);
            } else {
                return [...prev, id];
            }
        });
    };

    const handleEntranceRowSelect = (id) => {
        setSelectedEntranceRows(prev => {
            if (prev.includes(id)) {
                return prev.filter(rowId => rowId !== id);
            } else {
                return [...prev, id];
            }
        });
    };

    // Check if all rows are selected
    const isAllEducationSelected = educations.length > 0 && educations.every(edu => selectedEducationRows.includes(edu.id));
    const isAllWorkSelected = workExperiences.length > 0 && workExperiences.every(work => selectedWorkRows.includes(work.id));
    const isAllLanguageSelected = languageAbilities.length > 0 && languageAbilities.every(lang => selectedLanguageRows.includes(lang.id));
    const isAllEntranceSelected = entranceTests.length > 0 && entranceTests.every(test => selectedEntranceRows.includes(test.id));

    // Delete handlers
    const handleDeleteEducation = (id) => {
        setEducations(educations.filter(edu => edu.id !== id));
        setSelectedEducationRows(prev => prev.filter(rowId => rowId !== id));
    };

    const handleDeleteWork = (id) => {
        setWorkExperiences(workExperiences.filter(work => work.id !== id));
        setSelectedWorkRows(prev => prev.filter(rowId => rowId !== id));
    };

    const handleDeleteLanguage = (id) => {
        setLanguageAbilities(languageAbilities.filter(lang => lang.id !== id));
        setSelectedLanguageRows(prev => prev.filter(rowId => rowId !== id));
    };

    const handleDeleteEntrance = (id) => {
        setEntranceTests(entranceTests.filter(test => test.id !== id));
        setSelectedEntranceRows(prev => prev.filter(rowId => rowId !== id));
    };

    // Add new row handlers
    const handleAddEducation = () => {
        const newEducation = {
            id: educations.length + 1,
            educationLevel: 'New Education',
            duration: '00',
            studyMainArea: 'Field of Study',
            eduType: 'Full-Time',
            startDate: 'DD/MM/YYYY',
            endDate: 'DD/MM/YYYY',
            result: '0.00%'
        };
        setEducations([...educations, newEducation]);
    };

    const handleAddWork = () => {
        const newWork = {
            id: workExperiences.length + 1,
            employerName: 'New Employer',
            occupation: 'Position',
            jobType: 'Full-Time',
            startDate: 'DD/MM/YYYY',
            endDate: 'DD/MM/YYYY',
            salary: '0,000'
        };
        setWorkExperiences([...workExperiences, newWork]);
    };

    const handleAddLanguage = () => {
        const newLanguage = {
            id: languageAbilities.length + 1,
            language: 'New Language',
            testName: 'Test Name',
            testLevel: 'First',
            listening: '0.0',
            speaking: '0.0',
            reading: '0.0',
            writing: '0.0',
            overall: '0.0',
            testDate: 'DD/MM/YYYY'
        };
        setLanguageAbilities([...languageAbilities, newLanguage]);
    };

    const handleAddEntrance = () => {
        const newEntrance = {
            id: entranceTests.length + 1,
            entranceTestName: 'New Test',
            module01: '0',
            module02: '0',
            module03: '0',
            module04: '0',
            total: '0',
            testDate: 'DD/MM/YYYY'
        };
        setEntranceTests([...entranceTests, newEntrance]);
    };

    // Render table function
    const renderTable = (data, columns, visibleColumns, isColumnVisible, selectedRows, 
                        handleSelectAll, handleRowSelect, isAllSelected, handleDelete, 
                        handleAdd, dropdownRef, showDropdown, setShowDropdown, 
                        toggleColumnVisibility, sectionTitle, addButtonText) => (
        <div className="card basic-data-table main-container-data mb-4">
            <div className="card-body pt-0 container-table">
                <div className='container-table-div'>
                    <h6 className="mb-3" style={{color:"#5a6c5b"}}>{sectionTitle}</h6>
                    <table className="table mb-0">
                        <thead>
                            <tr>
                                <th scope="col" className='sl-numbar-th'>
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
                                {columns.map((column) => (
                                    isColumnVisible(column.id) && (
                                        <th
                                            key={column.id}
                                            scope="col"
                                            className='sorting-th'
                                        >
                                            <div className="d-flex align-items-center">
                                                {column.label}
                                            </div>
                                        </th>
                                    )
                                ))}
                                <th scope="col" className='action-th'>
                                    <div className="position-relative table-header-hide-show" ref={dropdownRef}>
                                        <button
                                            className="position-relative table-header-hide-show"
                                            onClick={() => setShowDropdown(!showDropdown)}
                                        >
                                            Action <Icon icon="mdi:table-column" width="20" className='icone' />
                                        </button>
                                        {showDropdown && (
                                            <div className="position-absolute bg-white border rounded shadow-sm p-2 show-dropdowns-header">
                                                {columns.map((column) => (
                                                    <div
                                                        key={column.id}
                                                        className="bg-white p-2 mb-2 d-flex align-items-center gap-2"
                                                    >
                                                        <input
                                                            type="checkbox"
                                                            id={`column-${column.id}`}
                                                            checked={isColumnVisible(column.id)}
                                                            onChange={() => toggleColumnVisibility(column.id)}
                                                            disabled={column.required}
                                                            className="form-check-input"
                                                        />
                                                        <label htmlFor={`column-${column.id}`} className="mb-0 flex-grow-1 form-label">
                                                            {column.label}
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
                            {data.length > 0 ? (
                                data.map((rowItem, index) => (
                                    <tr key={rowItem.id}>
                                        <td>
                                            <div className="d-flex align-items-center gap-2">
                                                <input
                                                    className="form-check-input"
                                                    type="checkbox"
                                                    checked={selectedRows.includes(rowItem.id)}
                                                    onChange={() => handleRowSelect(rowItem.id)}
                                                />
                                                <span>{String(index + 1).padStart(2, '0')}</span>
                                            </div>
                                        </td>
                                        {columns.map((column) => (
                                            isColumnVisible(column.id) && (
                                                <td key={column.id}><span>{rowItem[column.field]}</span></td>
                                            )
                                        ))}
                                        <td className='action-td'>
                                            <div className="d-flex align-items-end gap-2">
                                                <button className='edit-btn-icone' onClick={() => console.log('Edit', rowItem.id)}>
                                                    <Icon icon="lucide:edit" width="18" className='icone' />
                                                </button>
                                                <button onClick={() => handleDelete(rowItem.id)} className='delete-btn-icone'>
                                                    <Icon icon="mingcute:delete-2-line" width="18" className='icone' />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={visibleColumns.length + 2} className='no-records-found'>
                                        No records found
                                    </td>
                                </tr>
                            )}
                            
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );

    return (
        <div className="section-block">
            <div className="row g-3">
                <div className="col-12">
                    {/* Education Table */}
                    {renderTable(
                        educations, educationColumns, educationVisibleColumns, isEducationColumnVisible,
                        selectedEducationRows, handleEducationSelectAll, handleEducationRowSelect,
                        isAllEducationSelected, handleDeleteEducation, handleAddEducation,
                        educationDropdownRef, showEducationDropdown, setShowEducationDropdown,
                        toggleEducationColumnVisibility, "Education (PA)"
                    )}

                    {/* Work Experience Table */}
                    {renderTable(
                        workExperiences, workExperienceColumns, workVisibleColumns, isWorkColumnVisible,
                        selectedWorkRows, handleWorkSelectAll, handleWorkRowSelect,
                        isAllWorkSelected, handleDeleteWork, handleAddWork,
                        workDropdownRef, showWorkDropdown, setShowWorkDropdown,
                        toggleWorkColumnVisibility, "Work Experience (PA)"
                    )}

                    {/* Language Ability Table */}
                    {renderTable(
                        languageAbilities, languageAbilityColumns, languageVisibleColumns, isLanguageColumnVisible,
                        selectedLanguageRows, handleLanguageSelectAll, handleLanguageRowSelect,
                        isAllLanguageSelected, handleDeleteLanguage, handleAddLanguage,
                        languageDropdownRef, showLanguageDropdown, setShowLanguageDropdown,
                        toggleLanguageColumnVisibility, "Language Ability (PA)"
                    )}

                    {/* Entrance Test Section */}
                    <div className="card basic-data-table main-container-data mb-4">
                        <div className="card-body">
                            <h6 className="mb-3" style={{color:"#5a6c5b"}}>Entrance Test Ability (PA)</h6>
                            
                            <div className="row mb-3">
                                <div className="col-md-6">
                                    <label className="form-label">Appeared Any Entrance Test?</label>
                                    <div className="d-flex gap-3">
                                        <div className="form-check">
                                            <input
                                                className="form-check-input"
                                                type="radio"
                                                name="entranceTest"
                                                id="entranceYes"
                                                value="Yes"
                                                checked={appearedEntranceTest === 'Yes'}
                                                onChange={(e) => setAppearedEntranceTest(e.target.value)}
                                            />
                                            <label className="form-check-label" htmlFor="entranceYes">
                                                Yes
                                            </label>
                                        </div>
                                        <div className="form-check">
                                            <input
                                                className="form-check-input"
                                                type="radio"
                                                name="entranceTest"
                                                id="entranceNo"
                                                value="No"
                                                checked={appearedEntranceTest === 'No'}
                                                onChange={(e) => setAppearedEntranceTest(e.target.value)}
                                            />
                                            <label className="form-check-label" htmlFor="entranceNo">
                                                No
                                            </label>
                                        </div>
                                    </div>
                                </div>
                                
                                {appearedEntranceTest === 'Yes' && (
                                    <div className="col-md-6">
                                        <label className="form-label">Entrance Test Name</label>
                                        <select className="form-select form-select-sm">
                                            <option>Master (Entrance Test Name)</option>
                                            <option>IELTS</option>
                                            <option>TOEFL</option>
                                            <option>PTE</option>
                                            <option>GRE</option>
                                            <option>GMAT</option>
                                        </select>
                                        <small className="text-muted">Field - Entrance Test Short Name</small>
                                    </div>
                                )}
                            </div>

                            {appearedEntranceTest === 'Yes' && renderTable(
                                entranceTests, entranceTestColumns, entranceVisibleColumns, isEntranceColumnVisible,
                                selectedEntranceRows, handleEntranceSelectAll, handleEntranceRowSelect,
                                isAllEntranceSelected, handleDeleteEntrance, handleAddEntrance,
                                entranceDropdownRef, showEntranceDropdown, setShowEntranceDropdown,
                                
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PrincipalApplicant;