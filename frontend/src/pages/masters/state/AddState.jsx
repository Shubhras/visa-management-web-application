import React,{useState} from 'react';
import { Icon } from '@iconify/react/dist/iconify.js';
import { Link } from 'react-router-dom';
import { useDispatch } from "react-redux";
import { stateAdd } from '../../../store/master/actions';
import { toast } from "react-toastify";

const AddState = ({show,handleClose})=>{

      const dispatch = useDispatch();
      const [loading, setLoading] = useState(false);
      // IMPORTANT: All hooks must be declared BEFORE any conditional returns
    
      // Form state
      const [formData, setFormData] = useState({
        name: '',
        countryName: '',
        stateshortName:'',
        description:'',
      
      });
    
      // Validation errors state
      const [errors, setErrors] = useState({
        name: '',
        countryName: '',
        stateshortName:'',
        description:'',
      });
    
      // Handle input changes
      const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
          ...prev,
          [name]: value
        }));
    
        // Clear error when user starts typing
        if (errors[name]) {
          setErrors(prev => ({
            ...prev,
            [name]: ''
          }));
        }
      };
    
      // Validate form
      const validateForm = () => {
        const newErrors = {};
        let isValid = true;
    
        Object.entries(formData).forEach(([key, value]) => {
            if (!value.trim()) {
              newErrors[key] = `${key.charAt(0).toUpperCase() + key.slice(1)} is required`;
              isValid = false;
            }
          });
        
          setErrors(newErrors);
          return isValid;
        };
       
    
      // Handle form submission
      const handleSubmit = (e) => {
        e.preventDefault();
    
        if (validateForm()) {
          const sendPayload = {...formData};
    
          dispatch(stateAdd(sendPayload, (response, error) => {
            setLoading(false);
            if (error) {
              toast.error(error?.response?.data?.message || "server error");
            } else {
              if (response?.statusCode === 200 && response?.status === true) {
                toast.success(response?.message);
                setFormData({
                    name: '',
                     countryName: '',
                      stateshortName:'',
                    description:'',
                 
                });
                setErrors({});
                handleClose();
              } else {
                toast.error("Something went wrong.");
              }
            }
          }));
        }
      };
    
      // Handle modal close
      const onClose = () => {
        // Reset form and errors
        setFormData({
            name: '',
        countryName: '',
        stateshortName:'',
        description:'',
        });
        setErrors({});
        handleClose();
      };
    
      // NOW we can do the conditional return - AFTER all hooks
      if (!show) return null;
    
      return (
        <>
          <div
            className={`modal fade show`}
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
                    Add New State
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
                      {/* Department Name */}
                      <div className="col-12 mb-20">
                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                           Name <span className="text-danger">*</span>
                        </label>
                        <input
                          type="text"
                          name="name"
                          value={formData.name}
                          onChange={handleChange}
                          className={`form-control radius-8 ${errors.name ? 'is-invalid' : ''}`}
                          placeholder="Enter Country Name"
                        />
                        {errors.name && (
                          <div className="text-danger text-sm mt-1">
                            {errors.name}
                          </div>
                        )}
                      </div>
    
                      {/* Continent*/}
                      <div className="col-12 mb-20">
                        <label
                          htmlFor="desc"
                          className="form-label fw-semibold text-primary-light text-sm mb-8"
                        >
                          Country Name <span className="text-danger">*</span>
                        </label>
                        <input
                          type="text"
                          name="countryName"
                          value={formData.countryName}
                          onChange={handleChange}
                          className={`form-control radius-8 ${errors.name ? 'is-invalid' : ''}`}
                          placeholder="Enter Country Name"
                        />
                        
                        {errors.countryName && (
                          <div className="text-danger text-sm mt-1">
                            {errors.countryName}
                          </div>
                        )}
                      </div>
    
                      {/* state shortname*/}
                    <div className="col-12 mb-20">
                        <label
                       
                          className="form-label fw-semibold text-primary-light text-sm mb-8"
                        >
                          State Short Name <span className="text-danger">*</span>
                        </label>
                        <input
                          type="text"
                          name="stateshortName"
                          value={formData.shortName}
                          onChange={handleChange}
                          className={`form-control radius-8 ${errors.stateshortName ? 'is-invalid' : ''}`}
                          placeholder="Enter Short Name"
                        />
                        
                        {errors.stateshortName && (
                          <div className="text-danger text-sm mt-1">
                            {errors.stateshortName}
                          </div>
                        )}
                      </div>
    
                         {/* Full Name*/}
                    <div className="col-12 mb-20">
                        <label
                          htmlFor="desc"
                          className="form-label fw-semibold text-primary-light text-sm mb-8"
                        >
                          Description <span className="text-danger">*</span>
                        </label>
                        <input
                          type="text"
                          name="description"
                          value={formData.description}
                          onChange={handleChange}
                          className={`form-control radius-8 ${errors.description ? 'is-invalid' : ''}`}
                          placeholder="Enter Description"
                        />
    
    
                        {errors.description && (
                          <div className="text-danger text-sm mt-1">
                            {errors.description}
                          </div>
                        )}
                      </div>
                        
                        
                  
                      
    
                      
    
                      
    
    
    
                      
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
                      {/* Status */}
                      {/* <div className="col-12 mb-20">
                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                          Status <span className="text-danger">*</span>
                        </label>
                        <div className="d-flex align-items-center flex-wrap gap-28">
                          <div className="form-check checked-success d-flex align-items-center gap-2">
                            <input
                              className="form-check-input"
                              type="radio"
                              name="status"
                              id="active"
                              value="active"
                              checked={formData.status === 'active'}
                              onChange={handleChange}
                            />
                            <label
                              className="form-check-label fw-medium text-secondary-light text-sm d-flex align-items-center gap-1"
                              htmlFor="active"
                            >
                              <span className="w-8-px h-8-px bg-success-600 rounded-circle" />
                              Active
                            </label>
                          </div>
    
                          <div className="form-check checked-danger d-flex align-items-center gap-2">
                            <input
                              className="form-check-input"
                              type="radio"
                              name="status"
                              id="inactive"
                              value="inactive"
                              checked={formData.status === 'inactive'}
                              onChange={handleChange}
                            />
                            <label
                              className="form-check-label fw-medium text-secondary-light text-sm d-flex align-items-center gap-1"
                              htmlFor="inactive"
                            >
                              <span className="w-8-px h-8-px bg-danger-600 rounded-circle" />
                              Inactive
                            </label>
                          </div>
                        </div>
                        {errors.status && (
                          <div className="text-danger text-sm mt-1">
                            {errors.status}
                          </div>
                        )}
                      </div> */}
    
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
                          className="btn btn-primary border border-primary-600 text-md px-48 py-12 radius-8"
                        >
                          Save
                        </button>
                      </div>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </>
      );

}
export default AddState;