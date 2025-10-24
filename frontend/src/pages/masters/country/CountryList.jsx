import React, { useState, useEffect ,useParams} from 'react'
import { useDispatch } from "react-redux";
import MasterLayout from "../../../masterLayout/MasterLayout";
import Breadcrumb from "../../../components/Breadcrumb";
import { Icon } from '@iconify/react/dist/iconify.js';
import { Link } from 'react-router-dom';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { toast } from "react-toastify";
import { countryList, countryDelete, countryExportData } from '../../../store/master/actions';
import AddImportCountryModal from './AddImportCountryModal';
import AddCountry from './AddCountry';
import EditCountry from './EditCountry';

/*const fakeCountries = [
    {
      uuid: 'fake-china-id',
      name: 'China',
      continent: '360a4001-88ef-4312-9838-70c6dd3e96f5',
      shortName: 'CN',
      fullName: 'Republic of China',
      officialName: 'China',
      capitalCity: 'Beijing',
      dialCodes: ['+35'],
      currencyCode: 'Yuan',
      status: true
    },
    {
        uuid: '2',
        name: 'Country B',
        continent: 'Europe',
        shortName: 'CB',
        fullName: 'Country B Full',
        officialName: 'Country B Official',
        capitalCity: 'Capital B',
        dialCodes: ['+44'],
        currencyCode: 'GBP',
        status: false,
      },
  ];
  */
  
 
  



const CountryList = () => {
  const dispatch = useDispatch();

  const [show, setShow] = useState(false);
  const handleShow = () => setShow(true);
  const handleClose = () => {
    setShow(false);
    fetchCountryList();
  };


  const [showEdit, setShowEdit] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [rowSelectData, setRowSelectData] = useState({});
  const [selectedRows, setSelectedRows] = useState([]);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingExport, setLoadingExport] = useState(false);
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



  



  /* Load data on mount
  useEffect(() => {
    fetchCountryList();
  }, []);

  const handleShow = () => setShow(true);

  const handleClose = () => {
    setShow(false);
    fetchCountryList(); // refresh list if needed after closing modal
  };
*/

useEffect(() => {
    const timer = setTimeout(() => {
      if (tableState.search !== undefined) {
        fetchCountryList();
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [tableState.search]);

/*
  const fetchCountryList = () => {
    setLoading(true);
  
    // Filter the fake countries using the search term
    /*const filtered = fakeCountries.filter((country) =>
      country.name.toLowerCase().includes(tableState.search.toLowerCase())
    );*/
  
   /* setCountries(filtered);
  
    setTableState(prev => ({
      ...prev,
      total: filtered.length,
      totalPages: 1,
      currentPage: 1,
      hasNext: false,
      hasPrevious: false,
    }));
  
    setLoading(false);
  };



*/



  useEffect(() => {
    fetchCountryList();
  }, [tableState.page, tableState.limit, tableState.status]);
  
  const fetchCountryList = () => {
    setLoading(true);
    const params = {
      page: tableState.page,
      limit: tableState.limit,
      search: tableState.search || '',
      status: tableState.status || ''
    };

  




    dispatch(countryList(params, (response, error) => {
      setLoading(false);
      if (response?.statusCode === 200 && response?.status === true) {
        //console.log('Response data:', response);

        // Extract pagination from the nested pagination object
        const paginationData = response?.pagination || {};

        setCountries(response?.data || []);
        setTableState(prev => ({
          ...prev,
          total: paginationData.totalItems || 0,
          totalPages: paginationData.totalPages || 0,
          currentPage: paginationData.currentPage || 1,
          hasNext: paginationData.nextPage || false,
          hasPrevious: paginationData.previousPage || false
        }));
      } else {
        setCountries([]);
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
      setSelectedRows(countries.map(dept => dept.uuid));
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

  const isAllSelected = countries.length > 0 &&
    countries.every(dept => selectedRows.includes(dept.uuid));

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
    fetchCountryList();
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
    console.log('Deleting countries:', sendPayload);

    if (!sendPayload || sendPayload.length === 0) {
      toast.error("No country is selected for deletion.");
      return;
    }

   dispatch(countryDelete(sendPayload, (response, error) => {

      if (error) {
        toast.error(error?.response?.data?.message || "server error");
      } else {
        if (response?.statusCode === 200 && response?.status === true) {
          toast.success(response?.message);
          setCountries(prevDepts => prevDepts.filter(dept => dept.uuid !== deleteId));
          setSelectedRows(prevSelected => prevSelected.filter(rowId => rowId !== deleteId));
          setShowDeleteConfirm(false);
          setSelectedRows([])
          setDeleteId(null);
          fetchCountryList();

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
    fetchCountryList();
  };

  const handleShowImport = () => {
    setShowImport(true);
  };


  const handleExport = () => {
    if (!countries || countries.length === 0) {
        toast.error("No data to export.");
        return;
      }
    
    const sendPayload = {
      file: "csv"
    };
    setLoadingExport(true);
    
    /*try {
        // Convert countries data into a flat exportable format
        const exportData = countries.map((country, index) => ({
          "S.L.": index + 1,
          Name: country.name,
          Continent: country.continent,
          "Short Name": country.shortName,
          "Full Name": country.fullName,
          "Official Name": country.officialName,
          "Capital City": country.capitalCity,
          "Dial Codes": Array.isArray(country.dialCodes) ? country.dialCodes.join(", ") : country.dialCodes,
          "Currency Code": country.currencyCode,
          Status: country.status ? "True" : "False"
        }));
        // Convert to worksheet
    const worksheet = XLSX.utils.json_to_sheet(exportData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Countries");

    // Convert to Blob
    const excelBuffer = XLSX.write(workbook, {
      bookType: "xlsx",
      type: "array"
    });
    const blob = new Blob([excelBuffer], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      });
  
      // Save the file
      saveAs(blob, `countries_${new Date().toISOString().split("T")[0]}.xlsx`);
      toast.success("Export successful");
    } catch (err) {
      console.error("Export error:", err);
      toast.error("Failed to export file.");
    }
  
    setLoadingExport(false); */







    dispatch(countryExportData(sendPayload, (response, error) => {
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
          link.download = `countries_${new Date().toISOString().split('T')[0]}.csv`;

          // Trigger download
          document.body.appendChild(link);
          link.click();

          // Cleanup
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);

          toast.success("Export successful");
        } else {
          toast.error("Something went wrong.");
        }
      }
    }));
  };
  const startIndex = (tableState.currentPage - 1) * tableState.limit;
  const statusOptions = ['All', 'True', 'False'];

 /* const filteredCountries = countries.filter(dept => {
    const matchesSearch = dept.name.toLowerCase().includes(tableState.search.toLowerCase());
    
    if (tableState.status === 'All' || !tableState.status) {
      return matchesSearch;
    }
    
    const statusBool = tableState.status === 'True';  // convert string to boolean
  
    return matchesSearch && dept.status === statusBool;
  });
  */
  
  return (
    <>
      <MasterLayout>
        <Breadcrumb title="Country" subTitle="List" />

        <div className="mb-20" style={{ backgroundColor: '#e8e8e0', padding: '12px 24px' }}>
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
        </div>

        <div className="card basic-data-table">
          <div className="card-body" style={{ backgroundColor: '#f5f5ef', paddingBottom: '16px' }}>
            <div className="row align-items-center">
              <div className="col-md-6">
                <div className="d-flex align-items-center gap-3">
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
                      value={tableState.search}
                      onChange={(e) => handleSearchChange(e.target.value)}
                    />
                  </div>
                  <select
                    className="form-select form-select-sm"
                    style={{ width: 'auto', minWidth: '130px' }}
                    value={tableState.status || 'All'}
                    onChange={(e) => handleStatusChange(e.target.value)}
                  >
                    {statusOptions.map(status => (
                      <option key={status} value={status}>{status}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="col-md-6 text-end">
                <button
                  className="btn btn-sm text-white fw-medium px-3 py-1"
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
                    <th scope="col" style={{ width: '80px', padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                      <div className="d-flex align-items-center gap-2">
                        <input
                          className="form-check-input"
                          type="checkbox"
                          checked={isAllSelected}
                          onChange={handleSelectAll}
                          style={{ cursor: 'pointer' }}
                          disabled={countries.length === 0}
                        />
                        <span>S.L</span>
                      </div>
                    </th>
                    <th scope="col" style={{ padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                      Name
                    </th>
                    <th scope="col" style={{ padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                      Continent
                    </th>
                    <th scope="col" style={{ padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                      Short Name
                    </th>
                    <th scope="col" style={{ padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                       Full Name
                    </th>
                    <th scope="col" style={{ padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                       Official Name
                    </th>
                    <th scope="col" style={{ padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                       Captital City
                    </th>
                    <th scope="col" style={{ padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                       Dial Codes
                    </th>
                    <th scope="col" style={{ padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                       Currency Code
                    </th>
                    <th scope="col" style={{ padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                      Status
                    </th>
                    



                    <th scope="col" style={{ width: '150px', padding: '16px', fontWeight: '600', color: '#495057', fontSize: '14px' }}>
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr>
                      <td colSpan="11" style={{ textAlign: 'center', padding: '32px', color: '#6c757d', fontSize: '14px' }}>
                        <div className="d-flex justify-content-center align-items-center gap-2">
                          <div className="spinner-border spinner-border-sm" role="status">
                            <span className="visually-hidden">Loading...</span>
                          </div>
                          Loading...
                        </div>
                      </td>
                    </tr>
  ) : countries.length > 0 ? (
                    countries.map((dept, index) => (
                      <tr key={dept.uuid} style={{ borderBottom: '1px solid #f0f0f0' }}>
                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <div className="d-flex align-items-center gap-2">
                            <input
                              className="form-check-input"
                              type="checkbox"
                              checked={selectedRows.includes(dept.uuid)}
                              onChange={() => handleRowSelect(dept.uuid)}
                              style={{ cursor: 'pointer' }}
                            />
                            <span style={{ fontSize: '14px', color: '#6c757d' }}>
                              {String(startIndex + index + 1).padStart(2, '0')}
                            </span>
                          </div>
                        </td>
                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <span style={{ fontSize: '14px', color: '#212529', fontWeight: '500' }}>
                            {dept.name}
                          </span>
                        </td>
                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <span style={{ fontSize: '14px', color: '#212529', fontWeight: '500' }}>
                            {dept.continent}
                          </span>
                        </td>
                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <span style={{ fontSize: '14px', color: '#212529', fontWeight: '500' }}>
                            {dept.shortName}
                          </span>
                        </td>
                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <span style={{ fontSize: '14px', color: '#212529', fontWeight: '500' }}>
                            {dept.fullName}
                          </span>
                        </td>
                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <span style={{ fontSize: '14px', color: '#212529', fontWeight: '500' }}>
                            {dept.officialName}
                          </span>
                        </td>
                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <span style={{ fontSize: '14px', color: '#212529', fontWeight: '500' }}>
                            {dept.capitalCity}
                          </span>
                        </td>
                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <span style={{ fontSize: '14px', color: '#212529', fontWeight: '500' }}>
                          {Array.isArray(dept.dialCodes) ? dept.dialCodes.join(', ') : dept.dialCodes}
                          </span>
                        </td>
                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <span style={{ fontSize: '14px', color: '#212529', fontWeight: '500' }}>
                            {dept.currencyCode}
                          </span>
                        </td>
                        <td style={{ padding: '16px', verticalAlign: 'middle' }}>
                          <span  className={`badge ${dept.status ? 'bg-success' : 'bg-secondary'}`} style={{ fontSize: '14px', color: '#212529', fontWeight: '500' }}>
                            {dept.status ? 'True':'False'}
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
                                backgroundColor: '#d1fae5',
                                transition: 'all 0.2s'
                              }}
                              onClick={(e) => {
                                e.preventDefault();
                                handleShowEdit(dept);
                              }}
                            >
                              <Icon icon="lucide:edit" width="18" style={{ color: '#059669' }} />
                            </Link>
                            <button
                              onClick={() => handleDelete(dept.uuid)}
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
                      <td colSpan="11" style={{ textAlign: 'center', padding: '32px', color: '#6c757d', fontSize: '14px' }}>
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

        <AddCountry show={show} handleClose={handleClose} />
        <EditCountry show={showEdit} handleCloseEdit={handleCloseEdit} rowSelectData={rowSelectData} />
        {showImport && (
          <AddImportCountryModal show={showImport} handleClose={handleCloseImport} />)}

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
      </MasterLayout>
    </>
  );
};

export default CountryList;