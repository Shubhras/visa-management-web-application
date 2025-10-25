import React, { useState, useMemo } from 'react'
// import MasterLayout from "../masterLayout/MasterLayout";
// import Breadcrumb from "../components/Breadcrumb";
import { Icon } from '@iconify/react/dist/iconify.js';
import { Link } from 'react-router-dom';
import AddLeads from './AddLeads';
import MasterLayout from '../../masterLayout/MasterLayout';
import Breadcrumb from '../../components/Breadcrumb';

const LeadsList = () => {
  // State management
  const [departments, setDepartments] = useState([
    {
      id: 1,
      invoice: '#INV-001',
      name: 'John Doe',
      image: 'https://via.placeholder.com/40',
      issuedDate: '25-10-2025',
      amount: '$1,200',
      status: 'Active',
      statusColor: 'success'
    },
    {
      id: 2,
      invoice: '#INV-002',
      name: 'Jane Smith',
      image: 'https://via.placeholder.com/40',
      issuedDate: '24-10-2025',
      amount: '$950',
      status: 'Inactive',
      statusColor: 'danger'
    },
    {
      id: 3,
      invoice: '#INV-003',
      name: 'Mike Johnson',
      image: 'https://via.placeholder.com/40',
      issuedDate: '23-10-2025',
      amount: '$2,100',
      status: 'Active',
      statusColor: 'success'
    },
    {
      id: 4,
      invoice: '#INV-004',
      name: 'Sarah Williams',
      image: 'https://via.placeholder.com/40',
      issuedDate: '22-10-2025',
      amount: '$1,750',
      status: 'Pending',
      statusColor: 'warning'
    },
    {
      id: 5,
      invoice: '#INV-005',
      name: 'Tom Brown',
      image: 'https://via.placeholder.com/40',
      issuedDate: '21-10-2025',
      amount: '$3,200',
      status: 'Active',
      statusColor: 'success'
    },
    {
      id: 6,
      invoice: '#INV-006',
      name: 'Emily Davis',
      image: 'https://via.placeholder.com/40',
      issuedDate: '20-10-2025',
      amount: '$1,500',
      status: 'Inactive',
      statusColor: 'danger'
    },
    {
      id: 7,
      invoice: '#INV-007',
      name: 'David Wilson',
      image: 'https://via.placeholder.com/40',
      issuedDate: '19-10-2025',
      amount: '$2,800',
      status: 'Active',
      statusColor: 'success'
    },
    {
      id: 8,
      invoice: '#INV-008',
      name: 'Lisa Anderson',
      image: 'https://via.placeholder.com/40',
      issuedDate: '18-10-2025',
      amount: '$1,100',
      status: 'Pending',
      statusColor: 'warning'
    },
    {
      id: 9,
      invoice: '#INV-009',
      name: 'Robert Taylor',
      image: 'https://via.placeholder.com/40',
      issuedDate: '17-10-2025',
      amount: '$3,500',
      status: 'Active',
      statusColor: 'success'
    },
    {
      id: 10,
      invoice: '#INV-010',
      name: 'Maria Garcia',
      image: 'https://via.placeholder.com/40',
      issuedDate: '16-10-2025',
      amount: '$2,200',
      status: 'Active',
      statusColor: 'success'
    },
    {
      id: 11,
      invoice: '#INV-011',
      name: 'James Martinez',
      image: 'https://via.placeholder.com/40',
      issuedDate: '15-10-2025',
      amount: '$1,900',
      status: 'Inactive',
      statusColor: 'danger'
    },
    {
      id: 12,
      invoice: '#INV-012',
      name: 'Patricia Lee',
      image: 'https://via.placeholder.com/40',
      issuedDate: '14-10-2025',
      amount: '$2,600',
      status: 'Active',
      statusColor: 'success'
    },
    {
      id: 13,
      invoice: '#INV-013',
      name: 'Michael Brown',
      image: 'https://via.placeholder.com/40',
      issuedDate: '13-10-2025',
      amount: '$1,400',
      status: 'Pending',
      statusColor: 'warning'
    },
    {
      id: 14,
      invoice: '#INV-014',
      name: 'Jennifer Wilson',
      image: 'https://via.placeholder.com/40',
      issuedDate: '12-10-2025',
      amount: '$3,100',
      status: 'Active',
      statusColor: 'success'
    },
    {
      id: 15,
      invoice: '#INV-015',
      name: 'William Moore',
      image: 'https://via.placeholder.com/40',
      issuedDate: '11-10-2025',
      amount: '$2,400',
      status: 'Inactive',
      statusColor: 'danger'
    }
  ]);
  const [show, setShow] = useState(false)

  const handleShow = () => setShow(true)
  const handleClose = () => setShow(false)
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [pageLength, setPageLength] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedRows, setSelectedRows] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

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

  // Handle delete
  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      setDepartments(prevDepts => prevDepts.filter(dept => dept.id !== id));
      setSelectedRows(prevSelected => prevSelected.filter(rowId => rowId !== id));
    }
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

  return (
    <>
      <MasterLayout>
        <Breadcrumb title="Leads" subTitle="List" />
        {/* Sub Header with Import/Export */}
        <div className="mb-20" style={{ backgroundColor: '#e8e8e0', padding: '12px 24px' }}>
          <div className="d-flex align-items-center gap-3">
            <h6 className="mb-0 fw-semibold text-neutral-900">LEADS</h6>
            <button className="btn btn-sm px-3 py-1 text-white fw-medium" style={{ backgroundColor: '#5a6c5b' }}>
              Import
            </button>
            <button className="btn btn-sm px-3 py-1 text-white fw-medium" style={{ backgroundColor: '#5a6c5b' }}>
              Export
            </button>
            {selectedRows.length > 0 && (
              <button
                onClick={handleBulkDelete}
                className="btn btn-sm px-3 py-1 text-white fw-medium bg-danger"
              >
                Delete Selected ({selectedRows.length})
              </button>
            )}
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

          <div className="card-body pt-0" >
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
                    <th scope="col" onClick={() => handleSort('name')} style={{ cursor: 'pointer', padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                      <div className="d-flex align-items-center gap-2">
                        Name
                        <Icon icon={sortConfig.key === 'name' ? (sortConfig.direction === 'asc' ? 'ph:caret-up-fill' : 'ph:caret-down-fill') : 'ph:caret-up-down'} width="16" style={{ color: '#6c757d' }} />
                      </div>
                    </th>
                    <th scope="col" onClick={() => handleSort('issuedDate')} style={{ cursor: 'pointer', padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                      <div className="d-flex align-items-center gap-2">
                        Date
                        <Icon icon={sortConfig.key === 'issuedDate' ? (sortConfig.direction === 'asc' ? 'ph:caret-up-fill' : 'ph:caret-down-fill') : 'ph:caret-up-down'} width="16" style={{ color: '#6c757d' }} />
                      </div>
                    </th>
                    {/* <th scope="col" onClick={() => handleSort('amount')} style={{ cursor: 'pointer', padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                      <div className="d-flex align-items-center gap-2">
                        Amount
                        <Icon icon={sortConfig.key === 'amount' ? (sortConfig.direction === 'asc' ? 'ph:caret-up-fill' : 'ph:caret-down-fill') : 'ph:caret-up-down'} width="16" style={{ color: '#6c757d' }} />
                      </div>
                    </th> */}
                    <th scope="col" onClick={() => handleSort('status')} style={{ cursor: 'pointer', padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                      <div className="d-flex align-items-center gap-2">
                        Status
                        <Icon icon={sortConfig.key === 'status' ? (sortConfig.direction === 'asc' ? 'ph:caret-up-fill' : 'ph:caret-down-fill') : 'ph:caret-up-down'} width="16" style={{ color: '#6c757d' }} />
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
                          <Link to="#" style={{ color: '#6366f1', textDecoration: 'none', fontSize: '14px', fontWeight: '500' }}>
                            {dept.invoice}
                          </Link>
                        </td>
                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <div className="d-flex align-items-center gap-3">
                           
                            <span style={{ fontSize: '14px', color: '#212529', fontWeight: '500' }}>
                              {dept.name}
                            </span>
                          </div>
                        </td>
                        <td style={{ padding: '16px', verticalAlign: 'middle', fontSize: '14px', color: '#495057' }}>
                          {dept.issuedDate}
                        </td>
                        {/* <td style={{ padding: '16px', verticalAlign: 'middle', fontSize: '14px', color: '#212529', fontWeight: '600' }}>
                          {dept.amount}
                        </td> */}
                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <span style={{
                            display: 'inline-block',
                            padding: '6px 16px',
                            borderRadius: '20px',
                            fontSize: '13px',
                            fontWeight: '500',
                            backgroundColor: dept.statusColor === 'success' ? '#d1fae5' : dept.statusColor === 'warning' ? '#fef3c7' : '#fee2e2',
                            color: dept.statusColor === 'success' ? '#059669' : dept.statusColor === 'warning' ? '#d97706' : '#dc2626'
                          }}>
                            {dept.status}
                          </span>
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
        <AddLeads show={show} handleClose={handleClose} />
        {/* Modal End */}
      </MasterLayout>
    </>
  );
};

export default LeadsList;