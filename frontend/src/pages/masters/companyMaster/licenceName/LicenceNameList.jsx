import React, { useState, useEffect, useRef } from 'react'
import { useDispatch } from "react-redux";
import MasterLayout from "../../../../masterLayout/MasterLayout";
import { Icon } from '@iconify/react/dist/iconify.js';
import { Link } from 'react-router-dom';
import { toast } from "react-toastify";
import AddImportLicenceNameModal from './AddImportLicenceNameModal';
import AddEditLicenceNameModal from './AddEditLicenceNameModal';
import { licenceNameExportData, licenceNameList, licenceNameDelete } from '../../../../store/master/companyMasters/actions';
import { formatDateDDMMYYYY, formatDateDDMMYYYYTime } from '../../../../helper/utils/commanHelper';

const LicenceNameList = () => {
  const dispatch = useDispatch();
  const [modalState, setModalState] = useState({
    show: false,
    mode: 'add', // 'add' or 'edit'
    rowData: null
  })
  const handleShow = () => {
    setModalState({
      show: true,
      mode: 'add',
      rowData: null
    });
  };
  // For closing modal
  const handleClose = () => {
    setModalState({
      show: false,
      mode: 'add',
      rowData: null
    });
    fetchLicenceNameList();
  }

  // const [showEdit, setShowEdit] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [rowSelectData, setRowSelectData] = useState({});
  const [selectedRows, setSelectedRows] = useState([]);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmMessage, setDeleteConfirmMessage] = useState("Are you sure you want to delete this licence name?");
  const [showExportPopop, setShowExportPopop] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const [selectAllOrNot, setSelectAllOrNot] = useState('');
  const [licenceNameData, setLicenceNameData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingExport, setLoadingExport] = useState(false);
  const [items] = useState(["Country", "License Full Name", "License Short Name", "License Issuing Authority Name", "License Valid Upto", "Description", "Modified On"]);
  const [selectedItems, setSelectedItems] = useState(["Country", "License Full Name", "License Short Name"]);
  const [ItemsRequired] = useState(["Country", "License Full Name", "License Short Name"]);

  // Table columns configuration
  const [tableColumns] = useState([
    { id: 'country_name', label: 'Country', field: 'country_name', visible: true, required: false },
    { id: 'full_name', label: 'License Full Name', field: 'full_name', visible: true, required: false },
    { id: 'short_name', label: 'License Short Name', field: 'short_name', visible: true, required: false },
    { id: 'issuing_authority', label: 'License Issuing Authority Name', field: 'issuing_authority', visible: false, required: false },
    { id: 'valid_type', label: 'License Valid Upto', field: 'valid_type', visible: false, required: false },
    { id: 'valid_date', label: 'License Valid Date', field: 'valid_date', visible: false, required: false },
    { id: 'valid_duration_value', label: 'License Valid Duration Value', field: 'valid_duration_value', visible: false, required: false },
    { id: 'valid_duration_unit', label: 'License Valid Duration Unit', field: 'valid_duration_unit', visible: false, required: false },

    { id: 'description', label: 'Description', field: 'description', visible: false, required: false },
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
    sortBy: 'created_at', // Field to sort by
    sortOrder: 'desc', // 'asc' or 'desc'
    total: 0,
    totalPages: 0,
    currentPage: 1,
    hasNext: false,
    hasPrevious: false
  });

  useEffect(() => {
    const timer = setTimeout(() => {
      if (tableState.search !== undefined) {
        fetchLicenceNameList();
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [tableState.search]);

  useEffect(() => {
    fetchLicenceNameList();
  }, [tableState.page, tableState.limit, tableState.status, tableState.sortBy, tableState.sortOrder]);

  const fetchLicenceNameList = () => {
    setLoading(true);
    const params = {
      page: tableState.page,
      limit: tableState.limit,
      search: tableState.search || '',
      status: tableState.status || '',
      sortBy: tableState.sortBy || '',
      sortOrder: tableState.sortOrder || ''
    };

    dispatch(licenceNameList(params, (response, error) => {
      setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {
        const paginationData = response?.pagination || {};

        setLicenceNameData(response?.data || []);
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
        setLicenceNameData([]);
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

  // Handle sorting
  const handleSort = (field) => {
    setTableState(prev => {
      // If clicking the same field, toggle between asc -> desc -> no sort
      if (prev.sortBy === field) {
        if (prev.sortOrder === 'asc') {
          return { ...prev, sortOrder: 'desc', page: 1 };
        } else if (prev.sortOrder === 'desc') {
          return { ...prev, sortBy: '', sortOrder: '', page: 1 };
        }
      }
      // If clicking a new field, start with asc
      return { ...prev, sortBy: field, sortOrder: 'asc', page: 1 };
    });
  };

  // Get sort icon for a column
  const getSortIcon = (field) => {
    if (tableState.sortBy !== field) {
      return <Icon icon="ri:sort-desc" className='sorting-th-icone' />;
    }
    if (tableState.sortOrder === 'asc') {
      return <Icon icon="ri:sort-asc" className='sorting-th-icone' />;
    }
    return <Icon icon="ri:sort-desc" className='sorting-th-icone' />;
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
      setSelectedRows(licenceNameData.map(Item => Item.uuid));
    }
  };
  // For checkbox in table header
  const handleSelectAll = (e) => {
    const checked = e.target.checked;
    if (checked) {
      setSelectedRows(licenceNameData.map(Item => Item.uuid));
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

  const isAllSelected = licenceNameData.length > 0 &&
    licenceNameData.every(Item => selectedRows.includes(Item.uuid));

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

  const handleShowEdit = (rowData) => {
    setModalState({
      show: true,
      mode: 'edit',
      rowData: rowData
    });
  };

  const handleSelectAllOrNot = (a) => {
    setSelectAllOrNot(a);
  }
  const handleDelete = (uuid) => {
    setDeleteId(uuid);
    setShowDeleteConfirm(true);
    setDeleteConfirmMessage(`Are you sure you want to delete this licence name?`);
  };

  const handleBulkDelete = () => {
    if (selectedRows.length === 0) {
      toast.error("Please select at least one row to delete");
      return;
    }
    // Choose message based on delete type
    const message = selectAllOrNot === "all" ? `${tableState.total} all licence name` : `${selectedRows.length} selected licence name`;
    setDeleteConfirmMessage(`Are you sure you want to delete this licence name (${message})?`);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = () => {
    // const sendPayload = isAllSelected ? "all" : deleteId ? [deleteId] : selectedRows;
    const sendPayload = selectAllOrNot === "all" ? "all" : deleteId ? [deleteId] : selectedRows;
    if (!sendPayload || sendPayload.length === 0) {
      toast.error("No licence name selected for deletion.");
      return;
    }
    dispatch(licenceNameDelete(sendPayload, (response, error) => {
      if (error) {
        toast.error(error?.response?.data?.message || "server error");
      } else {
        if (response?.statusCode === 200 && response?.status === true) {
          toast.success(response?.message);
          setLicenceNameData(prevRowItems => prevRowItems.filter(Item => Item.uuid !== deleteId));
          setSelectedRows(prevSelected => prevSelected.filter(rowId => rowId !== deleteId));
          setShowDeleteConfirm(false);
          setSelectedRows([]);
          setSelectAllOrNot('');
          setDeleteId(null);
          fetchLicenceNameList();
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
    setDeleteConfirmMessage('');
    setSelectAllOrNot('');
  };

  const handleCloseImport = () => {
    setShowImport(false);
    fetchLicenceNameList();
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
      "Country": "country",
      "License Full Name": "full_name",
      "License Short Name": "short_name",
      "License Issuing Authority Name": "issuing_authority",
      "License Valid Upto": "valid_type",
      "License Valid Duration Value": "valid_duration_value",
      "License Valid Duration Unit": "valid_duration_unit",
      "License Valid Date": "valid_date",
      "Modified On": "updated_at",
      "Description": "description",
    };
    let mappedFields = selectedItems.map((item) => fieldMapping[item] || item);

    // 👉 If "License Valid Upto" is selected, add related fields too
    if (mappedFields.includes("valid_type")) {
      mappedFields.push("valid_date", "valid_duration_value", "valid_duration_unit");
    }

    // Remove duplicates (optional)
    mappedFields = [...new Set(mappedFields)];

    // Convert to comma-separated string
    const fieldsString = mappedFields.join(",");
    const sendPayload = {
      file: "xlsx",
      fields: fieldsString,
      uuids: selectAllOrNot === "all" ? [] : selectedRows,
    };
    setLoadingExport(true);
    dispatch(licenceNameExportData(sendPayload, (response, error) => {
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
          link.download = `LicenceName.xlsx`;
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
        {/* <Breadcrumb title="Licence Name" subTitle="List" /> */}
        <div className="card basic-data-table main-container-data">
          <div className="card-body container-data">
            <div className="row align-items-center gy-3 gx-2 flex-wrap filter-action-btn">
              {/* Left Section: Import / Export / Delete */}
              <div className="col-xl-6 col-lg-4 col-md-12">
                <div className="d-flex flex-wrap align-items-center gap-2">
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
                  {(selectedRows?.length > 0 && selectedRows?.length === licenceNameData?.length) && (
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
                  <div className="position-relative flex-grow-1 search-filter-div">
                    <Icon
                      icon="ion:search-outline"
                      className="position-absolute search-filter-icone"
                    />
                    <input
                      type="text"
                      className="form-control form-control-sm ps-5 search-filter-input"
                      placeholder="Search..."
                      value={tableState.search}
                      onChange={(e) => handleSearchChange(e.target.value)}
                    />
                    {tableState.search && tableState.search.length > 0 && (
                      <span
                        className="position-absolute"
                        style={{
                          right: '10px',
                          top: '50%',
                          transform: 'translateY(-50%)',
                          cursor: 'pointer',
                          zIndex: 999,
                          fontSize: '20px',
                          color: '#6c757d',
                          lineHeight: 1
                        }}
                        onClick={() => {

                          handleSearchChange('');
                        }}
                      >
                        ×
                      </span>
                    )}
                  </div>
                  <button
                    className="btn btn-sm text-white fw-medium px-3 py-1 comman-btn-color"
                    onClick={handleShow}
                  >New</button>
                </div>
              </div>
            </div>
          </div>
          <div className="card-body pt-0 container-table" >
            <div className='container-table-div'>
              <table className="table mb-0"  >
                <thead>
                  <tr>
                    <th scope="col" className='sl-numbar-th'>
                      <div className="d-flex align-items-center gap-2">
                        <input
                          className="form-check-input"
                          type="checkbox"
                          checked={isAllSelected}
                          onChange={handleSelectAll}
                          disabled={licenceNameData.length === 0}
                        />
                        <span>No.</span>
                      </div>
                    </th>
                    {tableColumns.map((column) => (
                      isColumnVisible(column.id) && (
                        <th
                          key={column.id}
                          scope="col"
                          className='sorting-th'
                          onClick={() => handleSort(column.field)}
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
                        <button
                          className="position-relative table-header-hide-show"
                          onClick={() => setShowColumnDropdown(!showColumnDropdown)}
                        >
                          Action <Icon icon="mdi:table-column" width="20" className='icone' />
                        </button>
                        {showColumnDropdown && (
                          <div className="position-absolute bg-white border rounded shadow-sm p-2 show-dropdowns-header">
                            {tableColumns.map((column) => (
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
                  ) : licenceNameData.length > 0 ? (
                    licenceNameData.map((rowItem, index) => (
                      <tr key={rowItem.uuid}>
                        <td>
                          <div className="d-flex align-items-center gap-2">
                            <input
                              className="form-check-input"
                              type="checkbox"
                              checked={selectedRows.includes(rowItem.uuid)}
                              onChange={() => handleRowSelect(rowItem.uuid)}
                            />
                            <span>{String(startIndex + index + 1).padStart(2, '0')}</span>
                          </div>
                        </td>
                        {isColumnVisible('country_name') && (
                          <td><span>{rowItem.country_name}</span></td>
                        )}
                        {isColumnVisible('full_name') && (
                          <td><span>{rowItem.full_name}</span></td>
                        )}
                        {isColumnVisible('short_name') && (
                          <td><span>{rowItem.short_name}</span></td>
                        )}
                        {isColumnVisible('issuing_authority') && (
                          <td><span>{rowItem.issuing_authority}</span></td>
                        )}
                        {isColumnVisible('valid_type') && (
                          <td><span>{rowItem.valid_type}</span></td>
                        )}
                       {isColumnVisible('valid_date') && (
                          <td>
                            <span>
                              {rowItem?.valid_date != null && rowItem?.valid_date !== ""
                                ? formatDateDDMMYYYY(rowItem.valid_date)
                                : ""}
                            </span>
                          </td>
                        )}

                        {isColumnVisible('valid_duration_value') && (
                          <td><span>{rowItem.valid_duration_value}</span></td>
                        )}
                        {isColumnVisible('valid_duration_unit') && (
                          <td><span>{rowItem.valid_duration_unit}</span></td>
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

              {tableState.total > 0 && (
                <div className="d-flex justify-content-between align-items-center px-4 py-3" >
                  <div className='showing-total-page' >
                    Showing {startIndex + 1} to {Math.min(startIndex + tableState.limit, tableState.total)} of {tableState.total} entries
                  </div>
                  <nav>
                    <ul className="pagination mb-0" style={{ gap: '4px' }}>
                      <li className={`page-item ${!tableState.hasPrevious ? 'disabled' : ''}`}>
                        <button
                          className="border-0 bg-transparent"
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
                          className="border-0 bg-transparent"
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
                              className="border-0 bg-transparent"
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
                              className="border-0 "
                              onClick={() => goToPage(page)}
                              style={{
                                padding: '6px 12px',
                                minWidth: '36px',
                                backgroundColor: page === tableState.currentPage ? '#5a6c5b' : 'transparent',
                                color: page === tableState.currentPage ? '#fff' : '#6c757d',
                                borderRadius: '4px',
                                fontWeight: page === tableState.currentPage ? '500' : '400',
                                cursor: 'pointer',
                                fontSize: "16px"
                              }}
                            >
                              {page}
                            </button>
                          )}
                        </li>
                      ))}
                      <li className={`page-item ${!tableState.hasNext ? 'disabled' : ''}`}>
                        <button
                          className=" border-0 bg-transparent"
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
                          className="border-0 bg-transparent"
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
        <AddEditLicenceNameModal
          show={modalState.show}
          handleClose={handleClose}
          mode={modalState.mode}
          rowData={modalState.rowData}
        />
        {showImport && (
          <AddImportLicenceNameModal show={showImport} handleClose={handleCloseImport} />)}
        {showDeleteConfirm && (
          <div className="modal fade show common-ctl-popup">
            <div className="modal-dialog modal-dialog-centered">
              <div className="modal-content" style={{ borderRadius: '10px' }}>
                <div className="modal-header">
                  <h6 className="modal-title text-danger">Confirm Delete</h6>
                  <button type="button" className="btn-close" onClick={cancelDelete}></button>
                </div>
                <div className="modal-body">
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
                  <h1 className="modal-title fs-5">Export Licence Name</h1>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={cancelExportTest}
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
                      onClick={cancelExportTest}
                      className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-16 py-4 radius-6"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleExport}
                      type="button"
                      className="btn comman-btn-color border border-primary-600 text-md px-16 py-4 radius-6"
                      disabled={loadingExport}
                    >{loadingExport ? (
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

export default LicenceNameList;