import React, { useState, useEffect, useRef } from 'react'
import { useDispatch } from "react-redux";
import MasterLayout from "../../../../masterLayout/MasterLayout";
import Breadcrumb from "../../../../components/Breadcrumb";
import { Icon } from '@iconify/react/dist/iconify.js';
import { Link } from 'react-router-dom';
// import * as XLSX from 'xlsx';
// import { saveAs } from 'file-saver';
import { toast } from "react-toastify";
import AddLostReasonB2C from './AddLostReasonB2C';
import EditLostReasonB2C from './EditLostReasonB2C';
import AddImportLostReasonB2CModal from './AddImportLostReasonB2CModal';
import { lostReasonB2CDelete, lostReasonB2CExportData, lostReasonB2CList } from '../../../../store/master/salesMasters/actions';
import { formatDateDDMMYYYYTime } from '../../../../helper/utils/commanHelper';
import { useGlobalSearch } from '../../../../components/comman/GlobalSearchContext';
const LostReasonB2CList = () => {
  const dispatch = useDispatch();
  const { globalSearch, setGlobalSearch } = useGlobalSearch();
  const [show, setShow] = useState(false);
  const handleShow = () => setShow(true);
  const handleClose = () => {
    setShow(false);
    fetchLostReasonB2CList();
  };

  const [showEdit, setShowEdit] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [rowSelectData, setRowSelectData] = useState({});
  const [selectedRows, setSelectedRows] = useState([]);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmMessage, setDeleteConfirmMessage] = useState("Are you sure you want to delete this lost reason (B2C)?");
  const [showExportPopop, setShowExportPopop] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const [selectAllOrNot, setSelectAllOrNot] = useState('');
  const [lostReasonB2CListData, setLostReasonB2CListData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingExport, setLoadingExport] = useState(false);
  const [items] = useState(["Lost Reason (B2C)", "Description", "Modified On"]);
  const [selectedItems, setSelectedItems] = useState(["Lost Reason (B2C)"]);
  const [ItemsRequired] = useState(["Lost Reason (B2C)"]);

  const [tableColumns] = useState([
    { id: 'name', label: 'Lost Reason (B2C)', field: 'name', visible: true, required: false },
    { id: 'description', label: 'Description', field: 'description', visible: true, required: false },
    { id: 'updated_at', label: 'Modified On', field: 'updated_at', visible: true, required: false },
  ]);

  const [visibleColumns, setVisibleColumns] = useState(
    tableColumns.filter(col => col.visible).map(col => col.id)
  );
  const [showColumnDropdown, setShowColumnDropdown] = useState(false);
  const columnDropdownRef = useRef(null);
  // Column visibility toggle handler
  const toggleColumnVisibility = (columnId) => {
    const column = tableColumns.find(col => col.id === columnId);
    if (column?.required) return; // Don't allow hiding required columns

    setVisibleColumns(prev => {
      if (prev.includes(columnId)) {
        return prev.filter(id => id !== columnId);
      } else {
        return [...prev, columnId];
      }
    });
  };

  // Check if column is visible
  const isColumnVisible = (columnId) => {
    return visibleColumns.includes(columnId);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (columnDropdownRef.current && !columnDropdownRef.current.contains(event.target)) {
        setShowColumnDropdown(false);
      }
    };

    if (showColumnDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showColumnDropdown]);
  // Updated state with sorting
  const [tableState, setTableState] = useState({
    page: 1,
    limit: 25,
    search: '',
    status: '',
    sortBy: '', // Field to sort by
    sortOrder: '', // 'asc' or 'desc'
    sort: [
      { field: "created_at", order: "desc" }
    ],
    total: 0,
    totalPages: 0,
    currentPage: 1,
    hasNext: false,
    hasPrevious: false
  });
  useEffect(() => {
    setTableState(prev => ({ ...prev, search: globalSearch, page: 1 }));
  }, [globalSearch]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (tableState.search !== undefined) {
        fetchLostReasonB2CList();
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [tableState.search]);

  useEffect(() => {
    fetchLostReasonB2CList();
  }, [tableState.page, tableState.limit, tableState.status, tableState.sort]);

  const fetchLostReasonB2CList = () => {
    setLoading(true);
    const params = {
      page: tableState.page,
      limit: tableState.limit,
      search: tableState.search || '',
      status: tableState.status || '',
      sortBy: tableState.sortBy || '',
      sortOrder: tableState.sortOrder || '',
      sort: tableState.sort,
    };

    dispatch(lostReasonB2CList(params, (response, error) => {
      setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {
        const paginationData = response?.pagination || {};

        setLostReasonB2CListData(response?.data || []);
        setTableState(prev => ({
          ...prev,
          total: paginationData.totalItems || 0,
          totalPages: paginationData.totalPages || 0,
          currentPage: paginationData.currentPage || 1,
          hasNext: paginationData.nextPage || false,
          hasPrevious: paginationData.previousPage || false
        }));
        setSelectedRows(prev => {
          const filtered = prev.filter(rowId =>
            response?.data.some(rowItems => rowItems.uuid === rowId)
          );
          return filtered;
        });
      } else {
        setLostReasonB2CListData([]);
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

  const handleSort = (field) => {
    setTableState(prev => {
      let newSort = [...prev.sort];
      const existingIndex = newSort.findIndex(s => s.field === field);
      if (existingIndex === -1) {
        newSort.push({ field, order: "asc" });
      }
      else {
        const existing = newSort[existingIndex];
        if (existing.order === "asc") {
          newSort[existingIndex].order = "desc";
        }
        else if (existing.order === "desc") {
          newSort.splice(existingIndex, 1);
        }
      }
      return { ...prev, sort: newSort, page: 1 };
    });
  };

  const getSortIcon = (field) => {
    const sortObj = tableState.sort.find(s => s.field === field);
    if (!sortObj) {
      return <Icon icon="ri:menu-line" className="sorting-th-icone" />;
    }
    if (sortObj.order === "asc") {
      return <Icon icon="ri:sort-asc" className="sorting-th-icone" />;
    }
    return <Icon icon="ri:sort-desc" className="sorting-th-icone" />;
  };

  const clearAllFilters = () => {
    setTableState(prev => ({
      ...prev,
      page: 1,
      limit: 25,
      search: '',
      status: '',
      sortBy: '',
      sortOrder: '',
      sort: [
        { field: "created_at", order: "desc" }   // default sort
      ],
      total: 0,
      totalPages: 0,
      currentPage: 1,
      hasNext: false,
      hasPrevious: false
    }));
    // Reset Global Search
    setGlobalSearch('');
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

  // For "Select All" button
  const handleSelectAllButton = () => {
    if (isAllSelected) {
      setSelectedRows([]);
    } else {
      setSelectedRows(lostReasonB2CListData.map(dept => dept.uuid));
    }
  };
  // For checkbox in table header
  const handleSelectAll = (e) => {
    const checked = e.target.checked;
    if (checked) {
      setSelectedRows(lostReasonB2CListData.map(dept => dept.uuid));
    } else {
      setSelectedRows([]);
      setSelectAllOrNot('');
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

  const isAllSelected = lostReasonB2CListData.length > 0 &&
    lostReasonB2CListData.every(dept => selectedRows.includes(dept.uuid));

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
    fetchLostReasonB2CList();
  };

  const handleShowEdit = (rowData) => {
    setShowEdit(true);
    setRowSelectData(rowData);
  };
  const handleSelectAllOrNot = (a) => {
    setSelectAllOrNot(a);
  }
  const handleDelete = (uuid) => {
    setDeleteId(uuid);
    setShowDeleteConfirm(true);
    setDeleteConfirmMessage(`Are you sure you want to delete this lost reason (B2C)?`);
  };

  const handleBulkDelete = () => {
    if (selectedRows.length === 0) {
      toast.error("Please select at least one row to delete");
      return;
    }
    // Choose message based on delete type
    const message = selectAllOrNot === "all" ? `${tableState.total} all lost reason (B2C)` : `${selectedRows.length} selected lost reason (B2C)`;
    setDeleteConfirmMessage(`Are you sure you want to delete this lost reason (B2C) (${message})?`);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = () => {
    // const sendPayload = isAllSelected ? "all" : deleteId ? [deleteId] : selectedRows;
    const sendPayload = selectAllOrNot === "all" ? "all" : deleteId ? [deleteId] : selectedRows;
    if (!sendPayload || sendPayload.length === 0) {
      toast.error("No lost reason (B2C) selected for deletion.");
      return;
    }

    dispatch(lostReasonB2CDelete(sendPayload, (response, error) => {
      if (error) {
        toast.error(error?.response?.data?.message || "server error");
      } else {
        if (response?.statusCode === 200 && response?.status === true) {
          toast.success(response?.message);
          setLostReasonB2CListData(prevDepts => prevDepts.filter(dept => dept.uuid !== deleteId));
          setSelectedRows(prevSelected => prevSelected.filter(rowId => rowId !== deleteId));
          setShowDeleteConfirm(false);
          setSelectedRows([]);
          setSelectAllOrNot('');
          setDeleteId(null);
          fetchLostReasonB2CList();
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
    fetchLostReasonB2CList();
  };

  const handleShowImport = () => {
    setShowImport(true);
  };

  const handleExportTest = () => {
    setShowExportPopop(true);
  }

  const cancelExportTest = () => {
    setShowExportPopop(false);
  };

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


  const handleExport = () => {
    if (selectedItems.length == 0) {
      toast.error("Please select at least one field");
      return
    }
    // Map frontend labels to backend field names
    const fieldMapping = {
      "Lost Reason (B2C)": "name",
      "Modified On": "updated_at",
      "Description": "description",
    };
    // Convert selectedItems to backend field names
    const mappedFields = selectedItems.map((item) => fieldMapping[item] || item);
    // Convert to comma-separated string
    const fieldsString = mappedFields.join(",");
    const sendPayload = {
      file: "xlsx",
      fields: fieldsString,
      uuids: selectAllOrNot === "all" ? [] : selectedRows,
      search: tableState.search || '', // Add search parameter
      sort: tableState.sort, // Add sort parameter

    };
    setLoadingExport(true);

    dispatch(lostReasonB2CExportData(sendPayload, (response, error) => {
      if (error) {
        setLoadingExport(false);
        toast.error(error?.response?.message || "server error");
      } else {
        setLoadingExport(false);
        if (response?.status === 200) {
          const blob = new Blob([response.data], {
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          });

          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `LostReason(B2C).xlsx`;
          document.body.appendChild(link);
          link.click();
          link.remove();
          window.URL.revokeObjectURL(url);
          toast.success("Export successful");
          cancelExportTest();
          setSelectedRows([]);
          setSelectAllOrNot('');
          setDeleteId(null);
        } else {
          toast.error("Something went wrong.");
        }
      }
    }));
  };

  const startIndex = (tableState.currentPage - 1) * tableState.limit;
  const statusOptions = ['All', 'Active', 'Inactive'];


  return (
    <>
      <MasterLayout>
        {/* <Breadcrumb title="Lost Reason (B2C)" subTitle="List" /> */}
        <div className="card basic-data-table main-container-data">
          <div className="card-body container-data">
            <div className="row align-items-center gy-3 gx-2 flex-wrap filter-action-btn">
              {/* Left Section: Import / Export / Delete */}
              <div className="col-xl-6 col-lg-4 col-md-12">
                <div className="d-flex flex-wrap align-items-center gap-2">
                  <button
                    className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color"
                    onClick={handleShow}
                  >New</button>
                  <button
                    className="btn btn-sm py-1 text-white fw-medium comman-btn-color"
                    onClick={handleShowImport}
                  >
                    Import
                  </button>
                  <button
                    className="btn btn-sm py-1 text-white fw-medium comman-btn-color"
                    onClick={handleExportTest}
                    disabled={loadingExport}
                  >
                    Export
                  </button>
                  <button
                    onClick={handleBulkDelete}
                    className="btn btn-sm py-1 text-white fw-medium comman-btn-color"
                  >
                    Delete
                  </button>
                  {(selectedRows?.length > 0 && selectedRows?.length === lostReasonB2CListData?.length) && (
                    <>
                      <button
                        onClick={() => handleSelectAllOrNot("onlySelected")}
                        className={`btn btn-sm py-1 fw-medium ${selectAllOrNot === "onlySelected" ? "comman-btn-color" : "comman-inactive-btn"}`}
                      >
                        {`Select (${selectedRows.length})`}
                      </button>
                      <button
                        onClick={() => handleSelectAllOrNot("all")}
                        className={`btn btn-sm py-1 fw-medium ${selectAllOrNot === "all" ? "comman-btn-color" : "comman-inactive-btn"}`}
                      >
                        {`Select All (${tableState.total})`}
                      </button>
                    </>
                  )}
                  <button
                    onClick={clearAllFilters}
                    className="btn btn-sm py-1 text-white fw-medium comman-btn-color"
                  >Reset </button>
                </div>
              </div>
              {/* Right Section: Select / Search / +Add New */}
              <div className="col-xl-6 col-lg-8 col-md-12">
                <div className="d-flex flex-wrap align-items-center justify-content-end gap-2">
                  <select
                    className="form-select form-select-sm select-page-filter"
                    value={tableState.limit}
                    onChange={(e) => handlePageLengthChange(e.target.value)}
                  >
                    <option value={10}>10</option>
                    <option value={25}>25</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                  </select>
                  {tableState.total > 0 && (
                    <div className="d-flex justify-content-between align-items-center px-4 py-0">
                      <div className="showing-total-page">
                        {startIndex + 1}-{" "}
                        {Math.min(startIndex + tableState.limit, tableState.total)}{" "}
                        of {tableState.total}
                      </div>
                      <nav>
                        <ul className="pagination mb-0 gap-4px">
                          <li className={`page-item ${!tableState.hasPrevious ? 'disabled' : ''}`}>
                            <button
                              className="border-0 bg-transparent"
                              onClick={() => goToPage(1)}
                              disabled={!tableState.hasPrevious}
                              style={{
                                padding: '0px 8px',
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
                              className="border-0 bg-transparent"
                              onClick={() => goToPage(tableState.currentPage - 1)}
                              disabled={!tableState.hasPrevious}
                              style={{
                                padding: '0px 8px',
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
                                  className="border-0 bg-transparent"
                                  style={{
                                    padding: '0px 10px',
                                    color: '#6c757d',
                                    cursor: 'default'
                                  }}
                                >
                                  ...
                                </span>
                              ) : (
                                <button
                                  className="border-0"
                                  onClick={() => goToPage(page)}
                                  style={{
                                    padding: '0px 10px',
                                    minWidth: '30px',
                                    backgroundColor: page === tableState.currentPage ? '#5a6c5b' : 'transparent',
                                    color: page === tableState.currentPage ? '#fff' : '#6c757d',
                                    borderRadius: '4px',
                                    fontWeight: page === tableState.currentPage ? '500' : '400',
                                    cursor: 'pointer',
                                    fontSize: "14px"
                                  }}
                                >
                                  {page}
                                </button>
                              )}
                            </li>
                          ))}
                          <li className={`page-item ${!tableState.hasNext ? 'disabled' : ''}`}>
                            <button
                              className="border-0 bg-transparent"
                              onClick={() => goToPage(tableState.currentPage + 1)}
                              disabled={!tableState.hasNext}
                              style={{
                                padding: '0px 8px',
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
                              className="border-0 bg-transparent"
                              onClick={() => goToPage(tableState.totalPages)}
                              disabled={!tableState.hasNext}
                              style={{
                                padding: '0px 8px',
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
          </div>
          <div className="card-body pt-0 container-table" >
            <div className='container-table-div'>

              <table className="table mb-0">
                <thead>
                  <tr>
                    <th scope="col" className='sl-numbar-th'>
                      <div className="d-flex align-items-center gap-2">
                        <input className="form-check-input" type="checkbox" checked={isAllSelected} onChange={handleSelectAll}
                          disabled={lostReasonB2CListData.length === 0} />
                        <span>No.</span>
                      </div>
                    </th>
                    {tableColumns.map((column) => (
                      isColumnVisible(column.id) && (
                        <th key={column.id} scope="col" className='sorting-th' onClick={() => handleSort(column.field)}
                        >
                          <div className="d-flex align-items-center">
                            {column.label}
                            {getSortIcon(column.field)}
                          </div>
                        </th>
                      )
                    ))}
                    <th scope="col" className='action-th'>
                      <div className="position-relative table-header-hide-show" ref={columnDropdownRef}>
                        <button className="position-relative table-header-hide-show" onClick={() =>
                          setShowColumnDropdown(!showColumnDropdown)}
                        >
                          Action
                          <Icon icon="mdi:table-column" width="20" className='icone' />
                        </button>
                        {showColumnDropdown && (
                          <div className="position-absolute bg-white border rounded shadow-sm p-2 show-dropdowns-header">
                            {tableColumns.map((column) => (
                              <div key={column.id} className="bg-white p-2 mb-2 d-flex align-items-center gap-2">
                                <input type="checkbox" id={`column-${column.id}`} checked={isColumnVisible(column.id)} onChange={() =>
                                  toggleColumnVisibility(column.id)}
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
                  {loading ? (
                    <tr>
                      <td colSpan={visibleColumns.length + 2} className='loding-data'>
                        <div className="d-flex justify-content-center align-items-center gap-2">
                          <div className="spinner-border spinner-border-sm" role="status">
                            <span className="visually-hidden">Loading...</span>
                          </div>
                          Loading...
                        </div>
                      </td>
                    </tr>
                  ) : lostReasonB2CListData.length > 0 ? (
                    lostReasonB2CListData.map((rowItem, index) => (
                      <tr key={rowItem.uuid}>
                        <td>
                          <div className="d-flex align-items-center gap-2">
                            <input className="form-check-input" type="checkbox" checked={selectedRows.includes(rowItem.uuid)}
                              onChange={() => handleRowSelect(rowItem.uuid)}
                            />
                            <span>{String(startIndex + index + 1).padStart(2, '0')}</span>
                          </div>
                        </td>
                        {isColumnVisible('name') && (
                          <td><span>{rowItem.name}</span></td>
                        )}

                        {isColumnVisible('description') && (
                          <td><span>{rowItem.description}</span></td>
                        )}
                        {isColumnVisible('updated_at') && (
                          <td><span>{formatDateDDMMYYYYTime(rowItem.updated_at)}</span></td>
                        )}
                        <td className='action-td'>
                          <div className="d-flex align-items-end gap-2">
                            <Link to="#" className='edit-btn-icone' onClick={(e) => { e.preventDefault(); handleShowEdit(rowItem); }}>
                              <Icon icon="lucide:edit" width="18" className='icone' />
                            </Link>
                            <button onClick={() => handleDelete(rowItem.uuid)} className='delete-btn-icone'>
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

        <AddLostReasonB2C show={show} handleClose={handleClose} />
        <EditLostReasonB2C show={showEdit} handleCloseEdit={handleCloseEdit} rowSelectData={rowSelectData} />
        {showImport && (
          <AddImportLostReasonB2CModal show={showImport} handleClose={handleCloseImport} />)}
        {showDeleteConfirm && (
          <div className="modal fade show common-ctl-popup" >
            <div className="modal-dialog modal-dialog-centered">
              <div className="modal-content" style={{ borderRadius: '10px' }}>
                <div className="modal-header">
                  <h6 className="modal-title text-danger">Confirm Delete</h6>
                  <button type="button" className="btn-close" onClick={cancelDelete}></button>
                </div>
                <div className="modal-body">
                  {/* <p className="mb-0">Are you sure you want to delete this Activity?</p> */}
                  {/* <p className="mb-0"> Are you sure you want to delete this Activity ({selectedRows.length})?</p> */}
                  <p className="mb-0">{deleteConfirmMessage}</p>

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
            className="modal fade show common-ctl-popup"
            tabIndex={-1}
            role="dialog"
          >
            <div className="modal-dialog modal-xl modal-dialog-centered" role="document">
              <div className="modal-content radius-16 bg-base">
                <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
                  <h1 className="modal-title fs-5">Export Lost Reason (B2C)</h1>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={cancelExportTest}
                    aria-label="Close"
                  />
                </div>
                <div className="modal-body p-24 pt-10">
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
                      onClick={cancelExportTest}
                      className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-16 py-4 radius-6"
                    >
                      Cancel
                    </button>
                    <button onClick={handleExport} type="button"
                      className="btn comman-btn-color border border-primary-600 text-md px-16 py-4 radius-6"
                      disabled={loadingExport}>{loadingExport ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Submit...
                        </>
                      ) : (
                        "Submit"
                      )}
                    </button>
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

export default LostReasonB2CList;