import React, { useState, useMemo } from 'react'
import MasterLayout from "../../../masterLayout/MasterLayout";
import Breadcrumb from "../../../components/Breadcrumb";
import { Icon } from '@iconify/react/dist/iconify.js';
import { Link } from 'react-router-dom';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import AddDepartment from './AddDepartment';
import EditDepartment from './EditDepartment';
const DepartmentList = () => {
  // State management
  const [departments, setDepartments] = useState([
    {
      id: 1,
      name: 'John Doe',
      issuedDate: '25-10-2025',
      status: 'Active',
      description: 'success'
    },
    {
      id: 2,
      name: 'Jane Smith',
      issuedDate: '24-10-2025',
      status: 'Inactive',
      description: 'danger'
    },
    {
      id: 3,
      name: 'Mike Johnson',
      issuedDate: '23-10-2025',
      status: 'Active',
      description: 'success'
    },
    {
      id: 4,
      name: 'Sarah Williams',
      issuedDate: '22-10-2025',
      status: 'Pending',
      description: 'warning'
    },
    {
      id: 5,
      name: 'Tom Brown',
      issuedDate: '21-10-2025',
      status: 'Active',
      description: 'success'
    },
    {
      id: 6,
      name: 'Emily Davis',
      issuedDate: '20-10-2025',
      status: 'Inactive',
      description: 'danger'
    },
    {
      id: 7,
      name: 'David Wilson',
      issuedDate: '19-10-2025',
      status: 'Active',
      description: 'success'
    },
    {
      id: 8,
      name: 'Lisa Anderson',
      issuedDate: '18-10-2025',
      status: 'Pending',
      description: 'warning'
    },
    {
      id: 9,
      name: 'Robert Taylor',
      issuedDate: '17-10-2025',
      status: 'Active',
      description: 'success'
    },
    {
      id: 10,
      name: 'Maria Garcia',
      issuedDate: '16-10-2025',
      status: 'Active',
      description: 'success'
    },
    {
      id: 11,
      name: 'James Martinez',
      issuedDate: '15-10-2025',
      status: 'Inactive',
      description: 'danger'
    },
    {
      id: 12,
      name: 'Patricia Lee',
      issuedDate: '14-10-2025',
      status: 'Active',
      description: 'success'
    },
    {
      id: 13,
      name: 'Michael Brown',
      issuedDate: '13-10-2025',
      status: 'Pending',
      description: 'warning'
    },
    {
      id: 14,
      name: 'Jennifer Wilson',
      issuedDate: '12-10-2025',
      status: 'Active',
      description: 'success'
    },
    {
      id: 15,
      name: 'William Moore',
      issuedDate: '11-10-2025',
      status: 'Inactive',
      description: 'danger'
    }
  ]);
  const [show, setShow] = useState(false);
  const handleShow = () => setShow(true);
  const handleClose = () => setShow(false);
  const [showEdit, setShowEdit] = useState(false);
  const [rowSelectData, setRowSelectData] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [pageLength, setPageLength] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedRows, setSelectedRows] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [selectedFile, setSelectedFile] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  // Get unique statuses
  const uniqueStatuses = ['All', ...new Set(departments.map(dept => dept.status))];

  // Filter and search
  const filteredDepartments = useMemo(() => {
    return departments.filter(dept => {
      const matchesStatus = statusFilter === 'All' || dept.status === statusFilter;
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch =
        dept.name.toLowerCase().includes(searchLower) ||
        dept.invoice.toLowerCase().includes(searchLower) ||
        dept.amount.toLowerCase().includes(searchLower);
      return matchesStatus && matchesSearch;
    });
  }, [departments, statusFilter, searchTerm]);

  // Sorting
  const sortedDepartments = useMemo(() => {
    if (!sortConfig.key) return filteredDepartments;

    return [...filteredDepartments].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }, [filteredDepartments, sortConfig]);

  // Pagination
  const totalPages = Math.ceil(sortedDepartments.length / pageLength);
  const startIndex = (currentPage - 1) * pageLength;
  const endIndex = startIndex + pageLength;
  const currentDepartments = sortedDepartments.slice(startIndex, endIndex);

  // Reset to page 1 when filters change
  const handleSearchChange = (value) => {
    setSearchTerm(value);
    setCurrentPage(1);
  };

  const handleStatusChange = (value) => {
    setStatusFilter(value);
    setCurrentPage(1);
  };

  const handlePageLengthChange = (value) => {
    setPageLength(Number(value));
    setCurrentPage(1);
  };

  // Sorting handler
  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };



  // Handle select all
  const handleSelectAll = (e) => {
    const checked = e.target.checked;
    if (checked) {
      setSelectedRows(currentDepartments.map(dept => dept.id));
    } else {
      setSelectedRows([]);
    }
  };

  // Handle individual row selection
  const handleRowSelect = (id) => {
    setSelectedRows(prev => {
      if (prev.includes(id)) {
        return prev.filter(rowId => rowId !== id);
      } else {
        return [...prev, id];
      }
    });
  };

  // Check if all current page rows are selected
  const isAllSelected = currentDepartments.length > 0 &&
    currentDepartments.every(dept => selectedRows.includes(dept.id));

  // Handle bulk delete
  const handleBulkDelete = () => {
    if (selectedRows.length === 0) {
      alert('Please select rows to delete');
      return;
    }
    if (window.confirm(`Are you sure you want to delete ${selectedRows.length} item(s)?`)) {
      setDepartments(prevDepts => prevDepts.filter(dept => !selectedRows.includes(dept.id)));
      setSelectedRows([]);
    }
  };

  // Pagination controls
  const goToPage = (page) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const getPaginationNumbers = () => {
    const pages = [];
    const maxVisible = 5;

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push('...');
        for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      }
    }
    return pages;
  };


  const handleCloseEdit = () => setShowEdit(false);
  const handleShowEdit = (rowData) => {
    setShowEdit(true);
    setRowSelectData(rowData);
  };


  const handleDelete = (id) => {
    setDeleteId(id);
    setShowDeleteConfirm(true);
  };
  const confirmDelete = () => {
    setDepartments(prevDepts => prevDepts.filter(dept => dept.id !== deleteId));
    setSelectedRows(prevSelected => prevSelected.filter(rowId => rowId !== deleteId));
    setShowDeleteConfirm(false);
  }
  const cancelDelete = () => {
    setDeleteId(null);
    setShowDeleteConfirm(false);
  };
  const handleExport = () => {
    // Prepare export data (you can modify columns as needed)
    const exportData = departments.map((dept, index) => ({
      SL: index + 1,
      Name: dept.name,
      Description: dept.description,
      Date: dept.issuedDate,
      Status: dept.status,
    }));

    // Create a new workbook and sheet
    const worksheet = XLSX.utils.json_to_sheet(exportData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Departments");

    // Export as Excel file
    const excelBuffer = XLSX.write(workbook, { bookType: "xlsx", type: "array" });
    const blob = new Blob([excelBuffer], { type: "application/octet-stream" });
    saveAs(blob, `Department_List_${new Date().toISOString().split('T')[0]}.xlsx`);
  };


  const handleImport = async () => {
    if (!selectedFile) {
      alert("Please select a file first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      // const response = await fetch("https://your-api.com/api/department/import", {
      //   method: "POST",
      //   body: formData,
      // });

      // if (!response.ok) throw new Error("Failed to import file");

      // const result = await response.json();
      // console.log("Import success:", result);
      alert("File imported successfully!");
      setSelectedFile(null);
    } catch (error) {
      console.error("Import error:", error);
      alert("Failed to import file");
    }
  };

  return (
    <>
      <MasterLayout>
        <Breadcrumb title="Department" subTitle="List" />

        {/* Sub Header with Import/Export */}
        <div className="mb-20" style={{ backgroundColor: '#e8e8e0', padding: '12px 24px' }}>
          <div className="d-flex align-items-center gap-3">
            {/* <h6 className="mb-0 fw-semibold text-neutral-900">Department</h6> */}
            <div className="d-flex align-items-center gap-3">
              <input
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={(e) => setSelectedFile(e.target.files[0])}
                className="form-control w-auto  form-control-lg"
                id="basic-upload"
              />
              <button
                className="btn btn-sm px-3 py-1 text-white fw-medium"
                style={{ backgroundColor: '#5a6c5b' }}
                onClick={handleImport}
              >
                Import
              </button>
            </div>
            {/* <button className="btn btn-sm px-3 py-1 text-white fw-medium" style={{ backgroundColor: '#5a6c5b' }}>
              Import
            </button> */}
            <button className="btn btn-sm px-3 py-1 text-white fw-medium" style={{ backgroundColor: '#5a6c5b' }} onClick={handleExport}>
              Export
            </button>
            {/* {selectedRows.length > 0 && (
              <button
                onClick={handleBulkDelete}
                className="btn btn-sm px-3 py-1 text-white fw-medium bg-danger"
              >
                Delete Selected ({selectedRows.length})
              </button>
            )} */}
          </div>
        </div>

        <div className="card basic-data-table">
          {/* Filter Section */}
          <div className="card-body" style={{ backgroundColor: '#f5f5ef', paddingBottom: '16px' }}>
            <div className="row align-items-center">
              <div className="col-md-6">
                <div className="d-flex align-items-center gap-3">
                  <select
                    className="form-select form-select-sm"
                    style={{ width: 'auto', minWidth: '100px' }}
                    value={pageLength}
                    onChange={(e) => handlePageLengthChange(e.target.value)}
                  >
                    <option value={10}>Show 10</option>
                    <option value={25}>Show 25</option>
                    <option value={50}>Show 50</option>
                    <option value={100}>Show 100</option>
                  </select>
                  <div className="position-relative" style={{ flex: 1, maxWidth: '300px' }}>
                    <Icon
                      icon="ion:search-outline"
                      className="position-absolute"
                      style={{ left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#999' }}
                      width="18"
                    />
                    <input
                      type="text"
                      className="form-control form-control-sm ps-5"
                      placeholder="Search..."
                      value={searchTerm}
                      onChange={(e) => handleSearchChange(e.target.value)}
                    />
                  </div>
                  <select
                    className="form-select form-select-sm"
                    style={{ width: 'auto', minWidth: '130px' }}
                    value={statusFilter}
                    onChange={(e) => handleStatusChange(e.target.value)}
                  >
                    {uniqueStatuses.map(status => (
                      <option key={status} value={status}>{status}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="col-md-6 text-end">
                <button className="btn btn-sm text-white fw-medium px-3 py-1"
                  style={{ backgroundColor: '#5a6c5b' }} onClick={handleShow}>
                  + ADD New
                </button>
                {/* <button
                  type="button"
                  className="btn btn-primary text-sm btn-sm px-12 py-12 radius-8 d-flex align-items-center gap-2"
                  data-bs-toggle="modal"
                  data-bs-target="#departmentModal" style={{ backgroundColor: '#5a6c5b' }}
                >
                  <Icon
                    icon="ic:baseline-plus"
                    className="icon text-xl line-height-1"
                  />
                  Add New Role
                </button> */}
              </div>
            </div>
          </div>

          <div className="card-body pt-0" style={{ backgroundColor: '#f5f5ef' }}>
            <div style={{ backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden' }}>
              <table className="table mb-0" style={{ borderCollapse: 'separate', borderSpacing: 0 }}>
                <thead style={{ backgroundColor: '#f8f9fa', borderBottom: '2px solid #e9ecef' }}>
                  <tr>
                    <th scope="col" style={{ width: '80px', padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                      <div className="d-flex align-items-center gap-2">
                        <input
                          className="form-check-input"
                          type="checkbox"
                          checked={isAllSelected}
                          onChange={handleSelectAll}
                          style={{ cursor: 'pointer' }}
                        />
                        <span>S.L</span>
                        <Icon icon="ph:caret-up-down" width="16" style={{ color: '#6c757d', opacity: 0.5 }} />
                      </div>
                    </th>
                    <th scope="col" onClick={() => handleSort('invoice')} style={{ cursor: 'pointer', padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                      <div className="d-flex align-items-center gap-2">
                        Name
                        <Icon icon={sortConfig.key === 'invoice' ? (sortConfig.direction === 'asc' ? 'ph:caret-up-fill' : 'ph:caret-down-fill') : 'ph:caret-up-down'} width="16" style={{ color: '#6c757d' }} />
                      </div>
                    </th>
                    <th scope="col" onClick={() => handleSort('invoice')} style={{ cursor: 'pointer', padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                      <div className="d-flex align-items-center gap-2">
                        Description
                        <Icon icon={sortConfig.key === 'invoice' ? (sortConfig.direction === 'asc' ? 'ph:caret-up-fill' : 'ph:caret-down-fill') : 'ph:caret-up-down'} width="16" style={{ color: '#6c757d' }} />
                      </div>
                    </th>
                    <th scope="col" onClick={() => handleSort('issuedDate')} style={{ cursor: 'pointer', padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                      <div className="d-flex align-items-center gap-2">
                        Date
                        <Icon icon={sortConfig.key === 'issuedDate' ? (sortConfig.direction === 'asc' ? 'ph:caret-up-fill' : 'ph:caret-down-fill') : 'ph:caret-up-down'} width="16" style={{ color: '#6c757d' }} />
                      </div>
                    </th>


                    <th scope="col" style={{ width: '150px', padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {currentDepartments.length > 0 ? (
                    currentDepartments.map((dept, index) => (
                      <tr key={dept.id} style={{ borderBottom: '1px solid #f0f0f0' }}>
                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <div className="d-flex align-items-center gap-2">
                            <input
                              className="form-check-input"
                              type="checkbox"
                              checked={selectedRows.includes(dept.id)}
                              onChange={() => handleRowSelect(dept.id)}
                              style={{ cursor: 'pointer' }}
                            />
                            <span style={{ fontSize: '14px', color: '#6c757d' }}>
                              {String(startIndex + index + 1).padStart(2, '0')}
                            </span>
                          </div>
                        </td>

                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <div className="d-flex align-items-center gap-3">

                            <span style={{ fontSize: '14px', color: '#212529', fontWeight: '500' }}>
                              {dept.name}
                            </span>
                          </div>
                        </td>
                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <div className="d-flex align-items-center gap-3">

                            <span style={{ fontSize: '14px', color: '#212529', fontWeight: '500' }}>
                              {dept.description}
                            </span>
                          </div>
                        </td>
                        <td style={{ padding: '16px', verticalAlign: 'middle', fontSize: '14px', color: '#495057' }}>
                          {dept.issuedDate}
                        </td>
                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <div className="d-flex align-items-center gap-2">
                            <Link
                              to="#"
                              style={{
                                width: '36px',
                                height: '36px',
                                display: 'inline-flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                borderRadius: '50%',
                                backgroundColor: '#e0e7ff',
                                transition: 'all 0.2s'
                              }}
                              onClick={() => handleShowEdit(dept)}
                            >
                              <Icon icon="iconamoon:eye-light" width="18" style={{ color: '#6366f1' }} />
                            </Link>
                            <Link
                              to="#"
                              style={{
                                width: '36px',
                                height: '36px',
                                display: 'inline-flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                borderRadius: '50%',
                                backgroundColor: '#d1fae5',
                                transition: 'all 0.2s'
                              }}
                              onClick={() => handleShowEdit(dept)}
                            >
                              <Icon icon="lucide:edit" width="18" style={{ color: '#059669' }} />
                            </Link>
                            <button
                              onClick={() => handleDelete(dept.id)}
                              style={{
                                width: '36px',
                                height: '36px',
                                display: 'inline-flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                borderRadius: '50%',
                                backgroundColor: '#fee2e2',
                                border: 'none',
                                cursor: 'pointer',
                                transition: 'all 0.2s'
                              }}
                            >
                              <Icon icon="mingcute:delete-2-line" width="18" style={{ color: '#dc2626' }} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7" style={{ textAlign: 'center', padding: '32px', color: '#6c757d', fontSize: '14px' }}>
                        No records found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>

              {/* Pagination */}
              {sortedDepartments.length > 0 && (
                <div className="d-flex justify-content-between align-items-center px-4 py-3" style={{ borderTop: '1px solid #e8e8e8' }}>
                  <div style={{ fontSize: '14px', color: '#6c757d' }}>
                    {/* Showing {startIndex + 1} to {Math.min(endIndex, sortedDepartments.length)} of {sortedDepartments.length} entries */}
                  </div>
                  <nav>
                    <ul className="pagination mb-0" style={{ gap: '4px' }}>
                      <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
                        <button
                          className="page-link border-0 bg-transparent"
                          onClick={() => goToPage(1)}
                          disabled={currentPage === 1}
                          style={{
                            padding: '6px 10px',
                            color: currentPage === 1 ? '#ccc' : '#6c757d',
                            fontSize: '18px'
                          }}
                        >
                          «
                        </button>
                      </li>
                      <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
                        <button
                          className="page-link border-0 bg-transparent"
                          onClick={() => goToPage(currentPage - 1)}
                          disabled={currentPage === 1}
                          style={{
                            padding: '6px 10px',
                            color: currentPage === 1 ? '#ccc' : '#6c757d',
                            fontSize: '18px'
                          }}
                        >
                          ‹
                        </button>
                      </li>
                      {getPaginationNumbers().map((page, idx) => (
                        <li key={idx} className="page-item">
                          {page === '...' ? (
                            <span
                              className="page-link border-0 bg-transparent"
                              style={{
                                padding: '6px 12px',
                                color: '#6c757d',
                                cursor: 'default'
                              }}
                            >
                              ...
                            </span>
                          ) : (
                            <button
                              className="page-link border-0"
                              onClick={() => goToPage(page)}
                              style={{
                                padding: '6px 12px',
                                minWidth: '36px',
                                backgroundColor: page === currentPage ? '#487fff' : 'transparent',
                                color: page === currentPage ? '#fff' : '#6c757d',
                                borderRadius: '4px',
                                fontWeight: page === currentPage ? '600' : '400'
                              }}
                            >
                              {page}
                            </button>
                          )}
                        </li>
                      ))}
                      <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
                        <button
                          className="page-link border-0 bg-transparent"
                          onClick={() => goToPage(currentPage + 1)}
                          disabled={currentPage === totalPages}
                          style={{
                            padding: '6px 10px',
                            color: currentPage === totalPages ? '#ccc' : '#6c757d',
                            fontSize: '18px'
                          }}
                        >
                          ›
                        </button>
                      </li>
                      <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
                        <button
                          className="page-link border-0 bg-transparent"
                          onClick={() => goToPage(totalPages)}
                          disabled={currentPage === totalPages}
                          style={{
                            padding: '6px 10px',
                            color: currentPage === totalPages ? '#ccc' : '#6c757d',
                            fontSize: '18px'
                          }}
                        >
                          »
                        </button>
                      </li>
                    </ul>
                  </nav>
                </div>
              )}
            </div>
          </div>
        </div>
        {/* Modal Start */}
        <AddDepartment show={show} handleClose={handleClose} />
        <EditDepartment show={showEdit} handleCloseEdit={handleCloseEdit} rowSelectData={rowSelectData} />
        {showDeleteConfirm && (
          <div className="modal fade show" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}>
            <div className="modal-dialog modal-dialog-centered">
              <div className="modal-content" style={{ borderRadius: '10px' }}>
                <div className="modal-header">
                  <h5 className="modal-title text-danger">Confirm Delete</h5>
                  <button type="button" className="btn-close" onClick={cancelDelete}></button>
                </div>
                <div className="modal-body">
                  <p className="mb-0">Are you sure you want to delete this department?</p>
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={cancelDelete}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="btn btn-danger btn-sm"
                    onClick={confirmDelete}
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Modal End */}
      </MasterLayout>
    </>
  );
};

export default DepartmentList;