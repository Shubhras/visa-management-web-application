import React, { useState, useEffect } from 'react'
import { Icon } from '@iconify/react/dist/iconify.js';
import { Link } from 'react-router-dom';
import { useDispatch } from "react-redux";
import { countryEdit } from '../../../store/master/actions';
import { toast } from "react-toastify";


const EditCountry = ({show,handleCloseEdit,rowSelectData})=>{


const [loading, setLoading] = useState(false);
    const dispatch = useDispatch();
    // Form state
    const [formData, setFormData] = useState({
        uuid: '',
        name: '',
        continent: '',
        shortName: '',
        fullName: '',
        officialName: '',
        capitalCity: '',
        dialCode: '',
        currency: '',
        status: '',
    });

    useEffect(() => {
        console.log('EditCountry - rowSelectData:', JSON.stringify(rowSelectData, null, 2));
        
        if (rowSelectData) {
            setFormData({
                uuid: rowSelectData.uuid || '',
                name: rowSelectData.name || '',
                continent: rowSelectData.continent || '',
                shortName: rowSelectData.shortName || '',
                fullName: rowSelectData.fullName || '',
                officialName: rowSelectData.officialName || '',
                capitalCity: rowSelectData.capitalCity || '',
               
                dialCode: Array.isArray(rowSelectData.dialCodes) && rowSelectData.dialCodes.length > 0? rowSelectData.dialCodes[0]: '',
                currency: rowSelectData.currencyCode || '',
                   status: rowSelectData.status != null ? String(rowSelectData.status) : '',

                  
                // status: rowSelectData.status || 'active'
            })
        }
    }, [rowSelectData]);

    // Validation errors state
    const [errors, setErrors] = useState({
       

        name: '',
        continent: '',
        shortName: '',
        fullName: '',
        officialName: '',
        capitalCity: '',
        dialCode: '',
        currency: '',
        status: '',
        // status: ''
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

       
        const requiredFields = ['name', 'continent', 'shortName', 'fullName', 'officialName', 'capitalCity', 'dialCode', 'currency'];
    
    requiredFields.forEach(field => {
        if (!formData[field]?.trim()) {
            newErrors[field] = `${field} is required`;
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
            const payload = { ...formData };
    
            setLoading(true);
            dispatch(countryEdit(payload, (response, error) => {
                setLoading(false);
                if (error) {
                    toast.error(error?.response?.data?.message || "Server error");
                } else if (response?.statusCode === 200 && response?.status === true) {
                    toast.success(response?.message);
                    setFormData({
                        uuid: '',
                        name: '',
                        continent: '',
                        shortName: '',
                        fullName: '',
                        officialName: '',
                        capitalCity: '',
                        dialCode: '',
                        currency: '',
                        status: 'active',
                    });
                    setErrors({});
                    handleCloseEdit();
                } else {
                    toast.error("Something went wrong.");
                }
            }));
        }
    };
    
            

            // // Form is valid, proceed with submission
            // console.log('Form submitted:', formData);

            // // Add your API call or form submission logic here
            // // Example: await api.EditDepartment(formData);

            // // Reset form and close modal
            // setFormData({
            //     id: '',
            //     name: '',
            //     description: '',
            //     // status: 'active'
            // });
            // setErrors({});
            // handleCloseEdit();
        








    // Handle modal close
    const onClose = () => {
        // Reset form and errors
        setFormData({
            id: '',
            name: '',
            continent: '',
            shortName: '',
            fullName: '',
            officialName: '',
            capitalCity: '',
            dialCode: '',
            currency: '',
            status: '',

        
            
            // status: 'active'
        });
        setErrors({});
        handleCloseEdit();
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
                aria-labelledby="countryModalLabel"
                aria-hidden={!show}
            >
                <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
                    <div className="modal-content radius-16 bg-base">
                        <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
                            <h1 className="modal-title fs-5" id="countrytModalLabel">
                                Edit Country
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
                                            placeholder="Enter Department Name"
                                        />
                                        {errors.name && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.name}
                                            </div>
                                        )}
                                    </div>

                                    {/* Continent*/}
                                    <div className="col-12 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Continent <span className="text-danger">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="continent"
                                            value={formData.continent}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.continent ? 'is-invalid' : ''}`}
                                            placeholder="Enter continent"
                                        />
                                        {errors.continent && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.continent}
                                            </div>
                                        )}
                                    </div>

                                      {/**short name */ }
                                      <div className="col-12 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Short Name<span className="text-danger">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="shortName"
                                            value={formData.shortName}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.shortName ? 'is-invalid' : ''}`}
                                            placeholder="Enter short Name"
                                        />
                                        {errors.shortName && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.shortName}
                                            </div>
                                        )}
                                    </div>
                                    {/** *full name*/ }
                                    <div className="col-12 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Full Name<span className="text-danger">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="fullName"
                                            value={formData.fullName}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.fullName ? 'is-invalid' : ''}`}
                                            placeholder="Enter full Name"
                                        />
                                        {errors.fullName && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.fullName}
                                            </div>
                                        )}
                                    </div>
                                    {/**official Name */ }
                                    <div className="col-12 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Official Name<span className="text-danger">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="officialName"
                                            value={formData.officialName}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.officialName ? 'is-invalid' : ''}`}
                                            placeholder="Enter official Name"
                                        />
                                        {errors.officialName && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.officialName}
                                            </div>
                                        )}
                                    </div>

                                    {/**captial city */ }
                                    <div className="col-12 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Captial City<span className="text-danger">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="capitalCity"
                                            value={formData.capitalCity}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.capitalCity ? 'is-invalid' : ''}`}
                                            placeholder="Enter Captial City"
                                        />
                                        {errors.capitalCity && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.capitalCity}
                                            </div>
                                        )}
                                    </div>

                                    {/**dial code*/ }
                                    <div className="col-12 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Dial Code<span className="text-danger">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="dialCode"
                                            value={formData.dialCode}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.dialCode ? 'is-invalid' : ''}`}
                                            placeholder="Enter Dial code"
                                        />
                                        {errors.dialCode && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.dialCode}
                                            </div>
                                        )}
                                    </div>

                                    {/**currency*/ }
                                    <div className="col-12 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Currency<span className="text-danger">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="currency"
                                            value={formData.currency}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.currency ? 'is-invalid' : ''}`}
                                            placeholder="Enter Currency"
                                        />
                                        {errors.currency && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.currency}
                                            </div>
                                        )}
                                    </div>


                                    












                                    
                                    {/* Status */}
                                     <div className="col-12 mb-20">
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
                          value="true"
                          checked={formData.status === 'true'}
                          onChange={handleChange}
                        />
                        <label
                          className="form-check-label fw-medium text-secondary-light text-sm d-flex align-items-center gap-1"
                          htmlFor="active"
                        >
                          <span className="w-8-px h-8-px bg-success-600 rounded-circle" />
                          True
                        </label>
                      </div>

                      <div className="form-check checked-danger d-flex align-items-center gap-2">
                        <input
                          className="form-check-input"
                          type="radio"
                          name="status"
                          id="false"
                          value="false"
                          checked={formData.status === 'false'}
                          onChange={handleChange}
                        />
                        <label
                          className="form-check-label fw-medium text-secondary-light text-sm d-flex align-items-center gap-1"
                          htmlFor="False"
                        >
                          <span className="w-8-px h-8-px bg-danger-600 rounded-circle" />
                          False
                        </label>
                      </div>
                    </div>
                    {errors.status && (
                      <div className="text-danger text-sm mt-1">
                        {errors.status}
                      </div>
                    )}
                  </div> 

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
};




   

export default EditCountry;