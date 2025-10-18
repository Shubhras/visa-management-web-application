import React,{useState,useEffect} from 'react';
import { useDispatch } from 'react-redux';
import { stateImportData } from '../../../store/actions';
import { toast } from "react-toastify";





const AddImportStateModal =({show,handleClose}) =>{
    
   const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    const [file, setFile] = useState(null);
    const [error, setError] = useState('');

    // Handle file change
    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setError('');
    };

    // Handle submit
    const handleSubmit = (e) => {
        e.preventDefault();

        if (!file) {
            setError('Please upload a file');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        setLoading(true);
        dispatch(stateImportData(formData, (response, error) => {
            setLoading(false);
            if (error) {
                toast.error(error?.response?.data?.message || "Server error");
            } else {
                if (response?.statusCode === 200 && response?.status === true) {
                    toast.success(response?.message);
                    setFile(null);
                    handleClose();
                } else {
                    toast.error("Something went wrong.");
                }
            }
        }));
    };

    // Handle modal close
    const onClose = () => {
        setFile(null);
        setError('');
        handleClose();
    };

    if (!show) return null;

    return (
        <div
            className="modal fade show"
            style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}
            tabIndex={-1}
            role="dialog"
            aria-labelledby="stateModalLabel"
            aria-hidden={!show}
        >
            <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
                <div className="modal-content radius-16 bg-base">
                    <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
                        <h1 className="modal-title fs-5" id="stateModalLabel">
                            Upload State File
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
                                {/* File Upload */}
                                <div className="col-12 mb-20">
                                    <label className="form-label fw-semibold text-primary-light text-sm mb-8">
                                        Upload File <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="file"
                                        className={`form-control radius-8 ${error ? 'is-invalid' : ''}`}
                                        onChange={handleFileChange}
                                        accept=".csv,.xlsx,.xls,.pdf,.docx"
                                    />
                                    {error && <div className="text-danger text-sm mt-1">{error}</div>}
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
                                        disabled={loading}
                                        className="btn btn-primary border border-primary-600 text-md px-48 py-12 radius-8"
                                    >
                                        {loading ? "Uploading..." : "Upload"}
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );


}
export default AddImportStateModal;