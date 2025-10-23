import React, { useState, useEffect } from 'react'
import { useDispatch } from "react-redux";
import MasterLayout from "../../../masterLayout/MasterLayout";
import Breadcrumb from "../../../components/Breadcrumb";
import { Icon } from '@iconify/react/dist/iconify.js';
import { Link } from 'react-router-dom';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { toast } from "react-toastify";
import AddDepartment from './AddDepartment';
import EditDepartment from './EditDepartment';
import { departmentList, departmentDelete, departmentExportData } from '../../../store/master/actions';
import AddImportModal from './AddImportModal';

const DepartmentList = () => {
  const dispatch = useDispatch();

  const [show, setShow] = useState(false);
  const handleShow = () => setShow(true);
  const handleClose = () => {
    setShow(false);
    fetchDepartmentList();
  };

  const [showEdit, setShowEdit] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [rowSelectData, setRowSelectData] = useState({});
  const [selectedRows, setSelectedRows] = useState([]);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showExportPopop, setShowExportPopop] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingExport, setLoadingExport] = useState(false);

  const [items, setItems] = useState(["name", "description", "test", "tes1"]); // All items
  const [selectedItems, setSelectedItems] = useState([...items]); // Checked items



  // Merged state for filters and pagination
  const [tableState, setTableState] = useState({
    page: 1,
    limit: 10,
    search: '',
    status: '',
    total: 0,
    totalPages: 0,
    currentPage: 1,
    hasNext: false,
    hasPrevious: false
  });

  useEffect(() => {
    const timer = setTimeout(() => {
      if (tableState.search !== undefined) {
        fetchDepartmentList();
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [tableState.search]);

  useEffect(() => {
    fetchDepartmentList();
  }, [tableState.page, tableState.limit, tableState.status]);

  const fetchDepartmentList = () => {
    setLoading(true);
    const params = {
      page: tableState.page,
      limit: tableState.limit,
      search: tableState.search || '',
      status: tableState.status || ''
    };

    dispatch(departmentList(params, (response, error) => {
      setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {
        //console.log('Response data:', response);

        // Extract pagination from the nested pagination object
        const paginationData = response?.pagination || {};

        setDepartments(response?.data || []);
        setTableState(prev => ({
          ...prev,
          total: paginationData.totalItems || 0,
          totalPages: paginationData.totalPages || 0,
          currentPage: paginationData.currentPage || 1,
          hasNext: paginationData.nextPage || false,
          hasPrevious: paginationData.previousPage || false
        }));
      } else {
        setDepartments([]);
        setTableState(prev => ({
          ...prev,
          total: 0,
          totalPages: 0,
          currentPage: 1,
          hasNext: false,
          hasPrevious: false
        }));
      }
    }));
  };

  const handleSearchChange = (value) => {
    setTableState(prev => ({
      ...prev,
      search: value,
      page: 1
    }));
  };

  const handleStatusChange = (value) => {
    setTableState(prev => ({
      ...prev,
      status: value === 'All' ? '' : value,
      page: 1
    }));
  };

  const handlePageLengthChange = (value) => {
    setTableState(prev => ({
      ...prev,
      limit: Number(value),
      page: 1
    }));
  };

  const handleSelectAll = (e) => {
    const checked = e.target.checked;
    if (checked) {
      setSelectedRows(departments.map(dept => dept.uuid));
    } else {
      setSelectedRows([]);
    }
  };

  const handleRowSelect = (uuid) => {
    setSelectedRows(prev => {
      if (prev.includes(uuid)) {
        return prev.filter(rowId => rowId !== uuid);
      } else {
        return [...prev, uuid];
      }
    });
  };

  const isAllSelected = departments.length > 0 &&
    departments.every(dept => selectedRows.includes(dept.uuid));

  const goToPage = (page) => {
    if (page >= 1 && page <= tableState.totalPages) {
      setTableState(prev => ({
        ...prev,
        page: page
      }));
    }
  };

  const getPaginationNumbers = () => {
    const pages = [];
    const maxVisible = 5;
    const totalPages = tableState.totalPages;
    const currentPage = tableState.currentPage;

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

  const handleCloseEdit = () => {
    setShowEdit(false);
    fetchDepartmentList();
  };

  const handleShowEdit = (rowData) => {
    setShowEdit(true);
    setRowSelectData(rowData);
  };

  const handleDelete = (uuid) => {
    setDeleteId(uuid);
    setShowDeleteConfirm(true);
  };

  // Handle bulk delete
  const handleBulkDelete = () => {
    if (selectedRows.length === 0) {
      alert('Please select rows to delete');
      return;
    }
    setShowDeleteConfirm(true);

  };
  const confirmDelete = () => {
    // Determine which IDs to send — either single deleteId or multiple selectedRows
    const sendPayload = deleteId ? [deleteId] : selectedRows;
    console.log('Deleting departments:', sendPayload);

    if (!sendPayload || sendPayload.length === 0) {
      toast.error("No department selected for deletion.");
      return;
    }

    dispatch(departmentDelete(sendPayload, (response, error) => {

      if (error) {
        toast.error(error?.response?.data?.message || "server error");
      } else {
        if (response?.statusCode === 200 && response?.status === true) {
          toast.success(response?.message);
          setDepartments(prevDepts => prevDepts.filter(dept => dept.uuid !== deleteId));
          setSelectedRows(prevSelected => prevSelected.filter(rowId => rowId !== deleteId));
          setShowDeleteConfirm(false);
          setSelectedRows([])
          setDeleteId(null);
          fetchDepartmentList();

        } else {
          toast.error("Something went wrong.");
        }
      }
    }));
  };

  const cancelDelete = () => {
    setShowDeleteConfirm(false);
    setDeleteId(null);
    setSelectedRows([])
  };

  const handleCloseImport = () => {
    setShowImport(false);
    fetchDepartmentList();
  };

  const handleShowImport = () => {
    setShowImport(true);
  };


  const handleExportTest = () => {
    console.log('ffffffffffffffffffffffffff')
    setShowExportPopop(true);
  }

  const cancelExportTest = () => {
    setShowExportPopop(false);

  };

  const handleDragStart = (e, index) => {
    e.dataTransfer.setData("dragIndex", index);
  };

  const handleDrop = (e, dropIndex) => {
    const dragIndex = e.dataTransfer.getData("dragIndex");
    const newItems = [...items];
    const draggedItem = newItems.splice(dragIndex, 1)[0];
    newItems.splice(dropIndex, 0, draggedItem);
    setItems(newItems);

    // Also reorder selectedItems to match
    const newSelected = newItems.filter((item) => selectedItems.includes(item));
    setSelectedItems(newSelected);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleCheckboxChange = (item, checked) => {
    if (checked) {
      // Find the index of the item in the full items list
      const indexInItems = items.indexOf(item);

      // Insert it into selectedItems at the correct position
      const newSelected = [...selectedItems];
      // Find the first item in selectedItems that comes after this item
      const insertIndex = newSelected.findIndex(
        (i) => items.indexOf(i) > indexInItems
      );
      if (insertIndex === -1) {
        newSelected.push(item); // If no item after, add at end
      } else {
        newSelected.splice(insertIndex, 0, item); // Insert at correct position
      }
      setSelectedItems(newSelected);
    } else {
      // Remove unchecked item
      setSelectedItems(selectedItems.filter((i) => i !== item));
    }
  }



  const handleExport = () => {
    if(selectedItems.length == 0){
     toast.error("Please select at least one field");
      return
    }
    const fieldsString = selectedItems.join(',');
  
    const sendPayload = {
      file: "csv",
      fields:fieldsString //"name,description"
    };
    setLoadingExport(true);

    dispatch(departmentExportData(sendPayload, (response, error) => {
      if (error) {
        setLoadingExport(false);
        toast.error(error?.response?.message || "server error");
      } else {
        setLoadingExport(false);
        if (response?.status === 200) {
          // Create a Blob from the CSV data
          const blob = new Blob([response.data], { type: 'text/csv' });

          // Create a temporary download link
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `departments_${new Date().toISOString().split('T')[0]}.csv`;

          // Trigger download
          document.body.appendChild(link);
          link.click();

          // Cleanup
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);

          toast.success("Export successful");
          cancelExportTest();
        } else {
          toast.error("Something went wrong.");
        }
      }
    }));
  };
  // const handleDragStart = (e, index) => {
  //   e.dataTransfer.setData("dragIndex", index);
  // };

  // const handleDrop = (e, dropIndex) => {
  //   const dragIndex = e.dataTransfer.getData("dragIndex");
  //   const newItems = [...items];
  //   const draggedItem = newItems.splice(dragIndex, 1)[0];
  //   newItems.splice(dropIndex, 0, draggedItem);
  //   console.log('fffffffffffff', newItems)
  //   setItems(newItems);
  // };

  // const handleDragOver = (e) => {
  //   e.preventDefault();
  // };

  const startIndex = (tableState.currentPage - 1) * tableState.limit;
  const statusOptions = ['All', 'Active', 'Inactive'];

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);

    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();

    let hours = date.getHours();
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12; // Convert to 12-hour format
    hours = String(hours).padStart(2, '0');

    return `${day}-${month}-${year} ${hours}:${minutes}:${seconds} ${ampm}`
  };
  return (
    <>
      <MasterLayout>
        <Breadcrumb title="Department" subTitle="List" />

        {/* <div className="mb-20" style={{ backgroundColor: '#e8e8e0', padding: '12px 24px' }}>
          <div className="d-flex align-items-center gap-3">
            <div className="d-flex align-items-center gap-3">

              <button
                className="btn btn-sm px-3 py-1 text-white fw-medium"
                style={{ backgroundColor: '#5a6c5b' }}
                onClick={handleShowImport}
              // disabled={!selectedFile}
              >
                Import
              </button>
            </div>
            <button
              className="btn btn-sm px-3 py-1 text-white fw-medium"
              style={{ backgroundColor: '#5a6c5b' }}
              onClick={handleExport}
              disabled={loadingExport}
            >
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
        </div> */}

        <div className="card basic-data-table">
          <div className="card-body" style={{ backgroundColor: '#f5f5ef', paddingBottom: '16px' }}>
            <div className="row align-items-center g-3">
              <div className="col-lg-9 col-md-8 col-12">
                <div className="d-flex flex-wrap align-items-center gap-2 gap-md-3">
                  <button
                    className="btn btn-sm px-3 py-1 text-white fw-medium"
                    style={{ backgroundColor: '#5a6c5b' }}
                    onClick={handleShowImport}
                  >
                    Import
                  </button>

                  <button
                    className="btn btn-sm px-3 py-1 text-white fw-medium"
                    style={{ backgroundColor: '#5a6c5b' }}
                    onClick={handleExportTest}
                    disabled={loadingExport}
                  >
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

                  <select
                    className="form-select form-select-sm"
                    style={{ width: 'auto', minWidth: '100px' }}
                    value={tableState.limit}
                    onChange={(e) => handlePageLengthChange(e.target.value)}
                  >
                    <option value={10}>Show 10</option>
                    <option value={25}>Show 25</option>
                    <option value={50}>Show 50</option>
                    <option value={100}>Show 100</option>
                  </select>

                  <div className="position-relative" style={{ flex: 1, minWidth: '200px', maxWidth: '300px' }}>
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
                      value={tableState.search}
                      onChange={(e) => handleSearchChange(e.target.value)}
                    />
                  </div>

                  {/* <select
                    className="form-select form-select-sm"
                    style={{ width: 'auto', minWidth: '130px' }}
                    value={tableState.status || 'All'}
                    onChange={(e) => handleStatusChange(e.target.value)}
                  >
                    {statusOptions.map(status => (
                      <option key={status} value={status}>{status}</option>
                    ))}
                  </select> */}
                </div>
              </div>

              <div className="col-lg-3 col-md-4 col-12 text-md-end text-end">
                <button
                  className="btn btn-sm text-white fw-medium px-3 py-1 w-md-auto"
                  style={{ backgroundColor: '#5a6c5b' }}
                  onClick={handleShow}
                >
                  + ADD New
                </button>
              </div>
            </div>
          </div>
          <div className="card-body pt-0" style={{ backgroundColor: '#f5f5ef' }}>
            <div style={{ backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden' }}>
              <table className="table mb-0" style={{ borderCollapse: 'separate', borderSpacing: 0 }}>
                <thead style={{ backgroundColor: '#f8f9fa', borderBottom: '2px solid #e9ecef' }}>
                  <tr>
                    <th scope="col" style={{ width: '80px' }}>
                      <div className="d-flex align-items-center gap-2">
                        <input
                          className="form-check-input"
                          type="checkbox"
                          checked={isAllSelected}
                          onChange={handleSelectAll}
                          style={{ cursor: 'pointer' }}
                          disabled={departments.length === 0}
                        />
                        <span>S.L</span>
                      </div>
                    </th>
                    <th scope="col" >
                      Name
                    </th>
                    <th scope="col" >
                      Description
                    </th>
                    <th scope="col" >
                      Created At
                    </th>
                    <th scope="col" style={{ width: '150px' }}>
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr>
                      <td colSpan="5" style={{ textAlign: 'center', padding: '32px', color: '#6c757d', fontSize: '14px' }}>
                        <div className="d-flex justify-content-center align-items-center gap-2">
                          <div className="spinner-border spinner-border-sm" role="status">
                            <span className="visually-hidden">Loading...</span>
                          </div>
                          Loading...
                        </div>
                      </td>
                    </tr>
                  ) : departments.length > 0 ? (
                    departments.map((dept, index) => (
                      <tr key={dept.uuid} style={{ borderBottom: '1px solid #f0f0f0' }}>
                        <td >
                          <div className="d-flex align-items-center gap-2">
                            <input
                              className="form-check-input"
                              type="checkbox"
                              checked={selectedRows.includes(dept.uuid)}
                              onChange={() => handleRowSelect(dept.uuid)}
                              style={{ cursor: 'pointer' }}
                            />
                            <span>
                              {String(startIndex + index + 1).padStart(2, '0')}
                            </span>
                          </div>
                        </td>
                        <td >
                          <span >
                            {dept.name}
                          </span>
                        </td>
                        <td >
                          <span >
                            {dept.description}
                          </span>
                        </td>
                        {/* <td >
                          {new Date(dept.created_at).toLocaleDateString('en-GB', {
                            day: '2-digit',
                            month: '2-digit',
                            year: 'numeric'
                          })}
                        </td> */}
                        <td>
                          <span>{formatDateTime(dept.created_at)}</span>
                        </td>
                        <td >
                          <div className="d-flex align-items-center gap-2">
                            <Link
                              to="#"
                              style={{
                                width: '28px',
                                height: '28px',
                                display: 'inline-flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                borderRadius: '50%',
                                backgroundColor: '#d1fae5',
                                transition: 'all 0.2s'
                              }}
                              onClick={(e) => {
                                e.preventDefault();
                                handleShowEdit(dept);
                              }}
                            >
                              <Icon icon="lucide:edit" width="16" style={{ color: '#059669' }} />
                            </Link>
                            <button
                              onClick={() => handleDelete(dept.uuid)}
                              style={{
                                width: '28px',
                                height: '28px',
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
                              <Icon icon="mingcute:delete-2-line" width="16" style={{ color: '#dc2626' }} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" style={{ textAlign: 'center', padding: '32px', color: '#6c757d', fontSize: '14px' }}>
                        No records found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>

              {tableState.total > 0 && (
                <div className="d-flex justify-content-between align-items-center px-4 py-3" style={{ borderTop: '1px solid #e8e8e8' }}>
                  <div style={{ fontSize: '14px', color: '#6c757d' }}>
                    Showing {startIndex + 1} to {Math.min(startIndex + tableState.limit, tableState.total)} of {tableState.total} entries
                  </div>
                  <nav>
                    <ul className="pagination mb-0" style={{ gap: '4px' }}>
                      <li className={`page-item ${!tableState.hasPrevious ? 'disabled' : ''}`}>
                        <button
                          className="page-link border-0 bg-transparent"
                          onClick={() => goToPage(1)}
                          disabled={!tableState.hasPrevious}
                          style={{
                            padding: '6px 10px',
                            color: !tableState.hasPrevious ? '#ccc' : '#6c757d',
                            fontSize: '18px',
                            cursor: !tableState.hasPrevious ? 'not-allowed' : 'pointer'
                          }}
                        >
                          «
                        </button>
                      </li>
                      <li className={`page-item ${!tableState.hasPrevious ? 'disabled' : ''}`}>
                        <button
                          className="page-link border-0 bg-transparent"
                          onClick={() => goToPage(tableState.currentPage - 1)}
                          disabled={!tableState.hasPrevious}
                          style={{
                            padding: '6px 10px',
                            color: !tableState.hasPrevious ? '#ccc' : '#6c757d',
                            fontSize: '18px',
                            cursor: !tableState.hasPrevious ? 'not-allowed' : 'pointer'
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
                                backgroundColor: page === tableState.currentPage ? '#487fff' : 'transparent',
                                color: page === tableState.currentPage ? '#fff' : '#6c757d',
                                borderRadius: '4px',
                                fontWeight: page === tableState.currentPage ? '600' : '400',
                                cursor: 'pointer'
                              }}
                            >
                              {page}
                            </button>
                          )}
                        </li>
                      ))}
                      <li className={`page-item ${!tableState.hasNext ? 'disabled' : ''}`}>
                        <button
                          className="page-link border-0 bg-transparent"
                          onClick={() => goToPage(tableState.currentPage + 1)}
                          disabled={!tableState.hasNext}
                          style={{
                            padding: '6px 10px',
                            color: !tableState.hasNext ? '#ccc' : '#6c757d',
                            fontSize: '18px',
                            cursor: !tableState.hasNext ? 'not-allowed' : 'pointer'
                          }}
                        >
                          ›
                        </button>
                      </li>
                      <li className={`page-item ${!tableState.hasNext ? 'disabled' : ''}`}>
                        <button
                          className="page-link border-0 bg-transparent"
                          onClick={() => goToPage(tableState.totalPages)}
                          disabled={!tableState.hasNext}
                          style={{
                            padding: '6px 10px',
                            color: !tableState.hasNext ? '#ccc' : '#6c757d',
                            fontSize: '18px',
                            cursor: !tableState.hasNext ? 'not-allowed' : 'pointer'
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

        <AddDepartment show={show} handleClose={handleClose} />
        <EditDepartment show={showEdit} handleCloseEdit={handleCloseEdit} rowSelectData={rowSelectData} />
        {showImport && (
          <AddImportModal show={showImport} handleClose={handleCloseImport} />)}

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

        {showExportPopop && (
          <div
            className="modal fade show"
            style={{ display: "block", backgroundColor: "rgba(0,0,0,0.5)" }}
            tabIndex={-1}
            role="dialog"
          >
            <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
              <div className="modal-content radius-16 bg-base">
                <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
                  <h1 className="modal-title fs-5">Export Department</h1>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={cancelExportTest}
                    aria-label="Close"
                  />
                </div>
                <div className="modal-body p-24">
                  <div className="row">
                    {/* Draggable List with Checkbox */}
                    <div className="col-12 mb-20">
                      {items.map((item, index) => (
                        <div
                          key={index}
                          draggable
                          onDragStart={(e) => handleDragStart(e, index)}
                          onDrop={(e) => handleDrop(e, index)}
                          onDragOver={handleDragOver}
                          className="border p-2 mb-10 radius-8 d-flex align-items-center justify-content-start gap-2  cursor-pointer"
                          style={{
                            cursor: "grab",
                            margin: "10px !important",
                            height: "40px"
                          }}
                        >
                          <input
                            type="checkbox"
                            id={`item-${index}`}
                            checked={selectedItems.includes(item)}
                            onChange={(e) =>
                              handleCheckboxChange(item, e.target.checked)
                            }
                            className="form-check-input"
                            style={{ marginLeft: "5px" }}
                          />
                          <label htmlFor={`item-${index}`} className="mb-0">
                            {item}
                          </label>
                        </div>
                      ))}
                    </div>

                    {/* Buttons */}
                    <div className="d-flex align-items-center justify-content-center gap-3 mt-24">
                      <button
                        type="button"
                        onClick={cancelExportTest}
                        className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-40 py-11 radius-8"
                      >
                        Cancel
                      </button>
                      <button onClick={handleExport}
                        type="button"
                        className="btn btn-primary border border-primary-600 text-md px-48 py-12 radius-8"
                      >
                        Submit
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </MasterLayout>
    </>
  );
};

export default DepartmentList;