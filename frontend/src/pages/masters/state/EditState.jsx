
import React, { useState, useEffect } from 'react'
import { Icon } from '@iconify/react/dist/iconify.js';
import { Link } from 'react-router-dom';
import { useDispatch } from "react-redux";
import { stateEdit } from '../../../store/master/actions';
import { toast } from "react-toastify";


const EditState = ({show,handleCloseEdit,rowSelectData})=>{


const [loading, setLoading] = useState(false);
    const dispatch = useDispatch();
    // Form state
    const [formData, setFormData] = useState({
        uuid: '',
        name: '',
        countryName: '',
        stateshortName: '',
        description: '',
       
    });

    useEffect(() => {
        console.log('EditState - rowSelectData:', JSON.stringify(rowSelectData, null, 2));
        
        if (rowSelectData) {
            setFormData({
                uuid: rowSelectData.uuid || '',
                name: rowSelectData.name || '',
                countryName: rowSelectData.countryName || '',
                stateshortName: rowSelectData.stateshortName || '',
                description: rowSelectData.description || '',
                
                
                  
                // status: rowSelectData.status || 'active'
            })
        }
    }, [rowSelectData]);

    // Validation errors state
    const [errors, setErrors] = useState({
       

        name: '',
        companyName: '',
        stateshortName: '',
        description: '',
        
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

       
        const requiredFields = ['name', 'countryName', 'stateshortName', 'description'];
    
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
            dispatch(stateEdit(payload, (response, error) => {
                setLoading(false);
                if (error) {
                    toast.error(error?.response?.data?.message || "Server error");
                } else if (response?.statusCode === 200 && response?.status === true) {
                    toast.success(response?.message);
                    setFormData({
                        uuid: '',
                        name: '',
                        countryName: '',
                        stateshortName: '',
                        description: '',
                        
                       
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
            countryName: '',
            stateshortName: '',
            description: '',
            
        
            
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
                aria-labelledby="stateModalLabel"
                aria-hidden={!show}
            >
                <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
                    <div className="modal-content radius-16 bg-base">
                        <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
                            <h1 className="modal-title fs-5" id="statetModalLabel">
                                Edit State
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
                                    {/* state Name */}
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

                                    {/* countryName*/}
                                    <div className="col-12 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Country Name <span className="text-danger">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="countryName"
                                            value={formData.countryName}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.countryName? 'is-invalid' : ''}`}
                                            placeholder="Enter Country Name"
                                        />
                                        {errors.countryName && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.countryName}
                                            </div>
                                        )}
                                    </div>

                                      {/** states short name */ }
                                      <div className="col-12 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                          State Short Name<span className="text-danger">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="stateshortName"
                                            value={formData.stateshortName}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.stateshortName ? 'is-invalid' : ''}`}
                                            placeholder="Enter State short Name"
                                        />
                                        {errors.stateshortName && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.stateshortName}
                                            </div>
                                        )}
                                    </div>
                                    {/** *full name*/ }
                                    <div className="col-12 mb-20">
                                        <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                            Description<span className="text-danger">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="description"
                                            value={formData.description}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.description? 'is-invalid' : ''}`}
                                            placeholder="Enter Description"
                                        />
                                        {errors.description && (
                                            <div className="text-danger text-sm mt-1">
                                                {errors.description}
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




   

export default EditState;