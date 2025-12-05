import React, { useState, useEffect, useRef } from 'react';
import { useDispatch } from "react-redux";
import { representingCountryAdd, representingCountryEdit } from '../../../../store/master/visaMaster/action';
import { toast } from "react-toastify";
import Select from "react-select";
import { countryList, stateListByCountry } from "../../../../store/master/generalMasters/actions";

const AddEditRepresentingCountryModal = ({ show, handleClose, mode = 'add', rowData = null }) => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    const [countryListData, setCountryListData] = useState([]);
    const [stateLoading, setStateLoading] = useState(false);
    const [stateListData, setStateListData] = useState([]);
    const [files, setFiles] = useState({
        national_flag: null,
        country_map: null
    });
    const [filePreviews, setFilePreviews] = useState({
        national_flag: null,
        country_map: null
    });


    // Form state
    const [formData, setFormData] = useState({
        uuid: '',
        country_name: '',
        official_name: '',
        short_name: '',

        continent: '',
        capital_city: '',
        calling_code: '',

        currency_full_name: '',
        currency_short_name: '',
        currency_code: '',

        no_of_states: '',
        no_of_territories: '',
        total_states_territories: '',

        independence_day: '',
        government_type: '',
        official_language: '',

        land_area: '',
        water_area: '',
        total_area: '',

        population: '',
        religions: '',
        monthly_living_cost: '',

        largest_state: '',
        smallest_state: '',
        major_cities: '',

        national_animal: '',
        national_bird: '',
        national_flower: '',

        unemployment: '',
        skilled_shortages: '',
        border_countries: '',

        monthly_living_cost_currency: '',
        monthly_living_cost_amount: '',

        description: '',
        national_flag: '',
        country_map: '',
    });

    // Validation errors state
    const [errors, setErrors] = useState({
        country_name: '',
        official_name: '',
        short_name: '',
        continent: '',
        capital_city: '',
        calling_code: '',
        currency_full_name: '',
        currency_short_name: '',
    });


    // Populate form data when in edit mode
    useEffect(() => {
        if (show) {
            if (mode === 'edit' && rowData) {
                setFormData({
                    uuid: rowData.uuid || '',
                    country_name: rowData.country || '',
                    official_name: rowData.official_name || '',
                    short_name: rowData.short_name || '',
                    continent: rowData.continent || '',
                    capital_city: rowData.capital_city || '',
                    calling_code: rowData.dial_codes || '',
                    currency_full_name: rowData.currency_full_name || '',
                    currency_short_name: rowData.currency_short_name || '',
                    currency_code: rowData.currency_code || '',
                    no_of_states: rowData.no_of_states || '',
                    no_of_territories: rowData.no_of_territories || '',
                    total_states_territories: rowData.total_states_and_territories || '',
                    independence_day: rowData.independence_day || '',
                    government_type: rowData.government_type || '',
                    official_language: rowData.official_language || '',
                    land_area: rowData.land_area_sq_km || '',
                    water_area: rowData.water_area_sq_km || '',
                    total_area: rowData.total_area_sq_km || '',
                    population: rowData.population || '',
                    religions: rowData.religions || '',

                    monthly_living_cost_currency: rowData.monthly_living_cost_currency || '',
                    monthly_living_cost_amount: rowData.monthly_living_cost_amount || '',

                    largest_state: rowData.largest_state || '',
                    smallest_state: rowData.smallest_state || '',
                    major_cities: rowData.major_cities || '',
                    national_animal: rowData.national_animal || '',
                    national_bird: rowData.national_bird || '',
                    national_flower: rowData.national_flower || '',
                    unemployment: rowData.unemployment || '',
                    skilled_shortages: rowData.skilled_shortages || '',
                    border_countries: rowData.border_countries_and_oceans || '',
                    description: rowData.description || '',
                    national_flag: rowData.national_flag || '',
                    country_map: rowData.country_map || '',
                });
                if (rowData.national_flag) {
                    setFilePreviews(prev => ({ ...prev, national_flag: rowData.national_flag }));
                }
                if (rowData.country_map) {
                    setFilePreviews(prev => ({ ...prev, country_map: rowData.country_map }));
                }
            } else {
                // Reset form when switching to add mode
                setFormData({
                    uuid: '',
                    country_name: '',
                    official_name: '',
                    short_name: '',
                    continent: '',
                    capital_city: '',
                    calling_code: '',
                    currency_full_name: '',
                    currency_short_name: '',
                    currency_code: '',
                    no_of_states: '',
                    no_of_territories: '',
                    total_states_territories: '',
                    independence_day: '',
                    government_type: '',
                    official_language: '',
                    land_area: '',
                    water_area: '',
                    total_area: '',
                    population: '',
                    religions: '',
                    monthly_living_cost: '',
                    largest_state: '',
                    smallest_state: '',
                    major_cities: '',
                    national_animal: '',
                    national_bird: '',
                    national_flower: '',
                    unemployment: '',
                    skilled_shortages: '',
                    border_countries: '',
                    national_flag: '',
                    country_map: '',
                    description: '',
                });
                setFiles({ national_flag: null, country_map: null });
                setFilePreviews({ national_flag: null, country_map: null });

            }
            fetchCountrylList();
        }
    }, [mode, rowData, show]);

    const handleSelectChange = (selectedOption, fieldName) => {
        setFormData(prev => ({
            ...prev,
            [fieldName]: selectedOption ? selectedOption.value : ''
        }));
    };
    useEffect(() => {
        if (formData.country_name) {
            fetchStateList(formData.country_name);
        } else {
            setStateListData([]);
            setFormData(prev => ({
                ...prev,
                largest_state: '',
                smallest_state: ''
            }));
        }
    }, [formData.country_name]);

    const fetchCountrylList = () => {
        const params = {
            page: 1,
            limit: 2000,
            search: '',
            status: '',
            sortBy: 'name',
            sortOrder: 'asc',
        };
        dispatch(countryList(params, (response, error) => {
            if (response?.statusCode === 200 && response?.status === true) {
                setCountryListData(response?.data || []);
            } else {
                setCountryListData([]);
            }
        }));

    };
    const fetchStateList = (countryId) => {
        if (!countryId) {
            setStateListData([]);
            return;
        }
        setStateLoading(true);
        const params = {
            page: 1,
            limit: 2000,
            search: '',
            status: '',
            sortBy: 'name',
            sortOrder: 'asc',
            countryId: countryId,
        };

        dispatch(stateListByCountry(params, (response, error) => {
            setStateLoading(false);
            if (response?.statusCode === 200 && response?.status === true) {
                setStateListData(response?.data || []);
            } else {
                setStateListData([]);
            }
        }));
    };
    const customFilterOption = (option, inputValue) => {
        if (!inputValue) return true;
        return option.label.toLowerCase().includes(inputValue.toLowerCase());
    };

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
    useEffect(() => {
        return () => {
            Object.values(filePreviews).forEach(preview => {
                if (preview && preview.startsWith('blob:')) {
                    URL.revokeObjectURL(preview);
                }
            });
        };
    }, [filePreviews]);

    const handleFileChange = (e, fileType) => {
        const file = e.target.files[0];
        if (filePreviews[fileType] && filePreviews[fileType].startsWith('blob:')) {
            URL.revokeObjectURL(filePreviews[fileType]);
        }
        if (file) {
            setFiles(prev => ({ ...prev, [fileType]: file }));

            if (file.type.startsWith('image/')) {
                setFilePreviews(prev => ({
                    ...prev,
                    [fileType]: URL.createObjectURL(file)
                }));
            } else {
                setFilePreviews(prev => ({ ...prev, [fileType]: null }));
            }
        }
    };


    // Validate form
    const validateForm = () => {
        const newErrors = {};
        let isValid = true;

        const requiredFields = [
            "country_name",
            "official_name",
            "short_name",
            "continent",
            "capital_city",
            "calling_code",
            "currency_full_name",
            "currency_short_name"
        ];

        requiredFields.forEach((field) => {
            if (!formData[field] || formData[field].trim() === "") {
                newErrors[field] = `${field.replace(/_/g, " ")} is required`;
                isValid = false;
            }
        });

        // if (formData.largest_state && formData.smallest_state &&
        //     formData.largest_state === formData.smallest_state) {
        //     toast.warning("Largest and smallest states cannot be the same");
        //     isValid = false;
        // }

        setErrors(newErrors);
        return isValid;
    };


    // Handle form submission
    const handleSubmit = (e) => {
        e.preventDefault();

        if (validateForm()) {
            const formDataToSend = new FormData();
            formDataToSend.append('country', formData.country_name);
            formDataToSend.append('official_name', formData.official_name);
            formDataToSend.append('short_name', formData.short_name);
            formDataToSend.append('continent', formData.continent);
            formDataToSend.append('capital_city', formData.capital_city);
            formDataToSend.append('dial_codes', JSON.stringify(formData.calling_code));
            formDataToSend.append('currency_full_name', formData.currency_full_name);
            formDataToSend.append('currency_short_name', formData.currency_short_name);
            formDataToSend.append('currency_code', formData.currency_code);
            formDataToSend.append('no_of_states', formData.no_of_states);
            formDataToSend.append('no_of_territories', formData.no_of_territories);
            formDataToSend.append('total_states_and_territories', formData.total_states_territories);
            formDataToSend.append('independence_day', formData.independence_day);
            formDataToSend.append('government_type', formData.government_type);
            formDataToSend.append('official_language', formData.official_language);
            formDataToSend.append('land_area_sq_km', formData.land_area);
            formDataToSend.append('water_area_sq_km', formData.water_area);
            formDataToSend.append('total_area_sq_km', formData.total_area);
            formDataToSend.append('population', formData.population);
            formDataToSend.append('religions', formData.religions);
            formDataToSend.append('largest_state', formData.largest_state);
            formDataToSend.append('major_cities', formData.major_cities);
            formDataToSend.append('national_animal', formData.national_animal);
            formDataToSend.append('national_bird', formData.national_bird);
            formDataToSend.append('national_flower', formData.national_flower);
            formDataToSend.append('unemployment', formData.unemployment);
            formDataToSend.append('skilled_shortages', formData.skilled_shortages);
            formDataToSend.append('border_countries_and_oceans', formData.border_countries);
            formDataToSend.append('description', formData.description);
            if (files.national_flag instanceof File) {
                formDataToSend.append('national_flag', files.national_flag);
            }
            if (files.country_map instanceof File) {
                formDataToSend.append('country_map', files.country_map);
            }
            formDataToSend.append('smallest_state', formData.smallest_state);
            formDataToSend.append('monthly_living_cost_currency', formData.monthly_living_cost_currency);
            formDataToSend.append('monthly_living_cost_amount', formData.monthly_living_cost_amount);


            if (mode === 'edit') {
                formDataToSend.append('uuid', formData.uuid);
                
            }

            setLoading(true);

            const action = mode === 'edit' ? representingCountryEdit : representingCountryAdd;

            dispatch(action(formDataToSend, (response, error) => {
                setLoading(false);
                if (error) {
                    toast.error(error?.response?.data?.message || "Server error");
                } else {
                    if (response?.statusCode === 200 && response?.status === true) {
                        toast.success(response?.message);
                        resetForm();
                        handleClose(true);
                    } else {
                        toast.error("Something went wrong.");
                    }
                }
            }));
        }
    };

    const resetForm = () => {
        setFormData({
            uuid: '',
            country_name: '',
            official_name: '',
            short_name: '',
            continent: '',
            capital_city: '',
            calling_code: '',
            currency_full_name: '',
            currency_short_name: '',
            currency_code: '',
            no_of_states: '',
            no_of_territories: '',
            total_states_territories: '',
            independence_day: '',
            government_type: '',
            official_language: '',
            land_area: '',
            water_area: '',
            total_area: '',
            population: '',
            religions: '',
            monthly_living_cost: '',
            largest_state: '',
            smallest_state: '',
            major_cities: '',
            national_animal: '',
            national_bird: '',
            national_flower: '',
            unemployment: '',
            skilled_shortages: '',
            border_countries: '',
            monthly_living_cost_currency: '',
            monthly_living_cost_amount: '',
            description: '',
        });
        setFiles({ national_flag: null, country_map: null });
        setFilePreviews({ national_flag: null, country_map: null });

        setErrors({});
    };

    // Handle modal close
    const onClose = () => {
        resetForm();
        setLoading(false);
        handleClose(false);
    };

    // Conditional return after all hooks
    if (!show) return null;


    return (
        <div
            className="modal fade show common-ctl-popup"
            tabIndex={-1}
            role="dialog"
            aria-labelledby="departmentModalLabel"
            aria-hidden={!show}
        >
            <div className="modal-dialog modal-lg modal-dialog-centered" role="document">
                <div className="modal-content radius-16 bg-base">
                    <div className="modal-header py-16 px-24 border border-top-0 border-start-0 border-end-0">
                        <h1 className="modal-title fs-5" id="departmentModalLabel">
                            {mode === 'edit' ? 'Edit Representing Country' : 'Add Representing Country'}
                        </h1>
                        <button
                            type="button"
                            className="btn-close"
                            onClick={onClose}
                            aria-label="Close"
                        />
                    </div>

                    <div className="modal-body ">
                        <form onSubmit={handleSubmit}>
                            <div className=""  >
                                <div className="row modal-scrollable-content"
                                // style={{ maxHeight: "500px", overflowY: "auto", scrollbarWidth: "none" }}  
                                >
                                    {/* Country Name */}
                                    <div className="col-6 mb-20">
                                        <label className="form-label fw-semibold text-sm mb-8">
                                            Country Name <span className="text-danger">*</span>
                                        </label>

                                        <Select
                                            options={countryListData.map((option) => ({
                                                value: option.uuid,
                                                label: option.name + " (" + option?.continent?.name + ")",
                                            }))}
                                            value={
                                                formData.country_name
                                                    ? countryListData
                                                        .map((option) => ({
                                                            value: option.uuid,
                                                            label: option.name + " (" + option?.continent?.name + ")",
                                                        }))
                                                        .find((opt) => opt.value === formData.country_name)
                                                    : null
                                            }
                                            onChange={(selectedOption) => {
                                                const selectedCountry = countryListData.find(
                                                    (c) => c.uuid === selectedOption?.value
                                                );

                                                if (selectedCountry) {
                                                    setFormData((prev) => ({
                                                        ...prev,
                                                        country_name: selectedCountry.uuid || "",
                                                        official_name: selectedCountry.officialName || "",
                                                        short_name: selectedCountry.shortName || "",
                                                        continent: selectedCountry.continent?.name || "",
                                                        capital_city: selectedCountry.capitalCity || "",
                                                        calling_code: selectedCountry.dialCodes || "",
                                                        currency_full_name: selectedCountry.currencyfullname || "",
                                                        currency_short_name: selectedCountry.currencyshortname || "",
                                                        currency_code: selectedCountry.currencyCode || "",
                                                        largest_state: "",
                                                        smallest_state: "",
                                                    }));
                                                } else {
                                                    setFormData((prev) => ({
                                                        ...prev,
                                                        country_name: "",
                                                        official_name: "",
                                                        short_name: "",
                                                        continent: "",
                                                        capital_city: "",
                                                        calling_code: "",
                                                        currency_full_name: "",
                                                        currency_short_name: "",
                                                        currency_code: "",
                                                        largest_state: "",
                                                        smallest_state: "",
                                                    }));
                                                }
                                            }}
                                            filterOption={customFilterOption}
                                            placeholder="Select country"
                                            isClearable
                                            isSearchable
                                            className={`custom-select-container ${errors.country_name ? "is-invalid" : ""}`}
                                            classNamePrefix="custom-select"
                                        />

                                        {errors.country_name && <div className="text-danger text-sm mt-1">{errors.country_name}</div>}
                                    </div>
                                    {/* Official Name */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">
                                            Country Official Name <span className="text-danger">*</span>
                                        </label>
                                        <input
                                            // disabled
                                            type="text"
                                            name="official_name"
                                            value={formData.official_name}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.official_name ? "is-invalid" : ""}`}
                                            placeholder="Enter country official name"
                                        />
                                        {errors.official_name && <div className="text-danger text-sm mt-1">{errors.official_name}</div>}
                                    </div>

                                    {/* Short Name */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">
                                            Country Short Name <span className="text-danger">*</span>
                                        </label>
                                        <input
                                            // disabled
                                            type="text"
                                            name="short_name"
                                            value={formData.short_name}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.short_name ? "is-invalid" : ""}`}
                                            placeholder="Enter country short name"
                                        />
                                        {errors.short_name && <div className="text-danger text-sm mt-1">{errors.short_name}</div>}
                                    </div>

                                    {/* Continent */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">
                                            Continent <span className="text-danger">*</span>
                                        </label>
                                        <input
                                            disabled
                                            type="text"
                                            name="continent"
                                            value={formData.continent}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.continent ? "is-invalid" : ""}`}
                                            placeholder="Enter continent"
                                        />
                                        {errors.continent && <div className="text-danger text-sm mt-1">{errors.continent}</div>}
                                    </div>

                                    {/* Capital City */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">
                                            Capital City <span className="text-danger">*</span>
                                        </label>
                                        <input
                                            // disabled
                                            type="text"
                                            name="capital_city"
                                            value={formData.capital_city}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.capital_city ? "is-invalid" : ""}`}
                                            placeholder="Enter capital city"
                                        />
                                        {errors.capital_city && <div className="text-danger text-sm mt-1">{errors.capital_city}</div>}
                                    </div>

                                    {/* Calling Code */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">
                                            Calling Code <span className="text-danger">*</span>
                                        </label>
                                        <input
                                            // disabled
                                            type="text"
                                            name="calling_code"
                                            value={formData.calling_code}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.calling_code ? "is-invalid" : ""}`}
                                            placeholder="Enter calling code"
                                        />
                                        {errors.calling_code && <div className="text-danger text-sm mt-1">{errors.calling_code}</div>}
                                    </div>

                                    {/* Currency Full Name */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">
                                            Currency Full Name <span className="text-danger">*</span>
                                        </label>
                                        <input
                                            // disabled
                                            type="text"
                                            name="currency_full_name"
                                            value={formData.currency_full_name}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.currency_full_name ? "is-invalid" : ""}`}
                                            placeholder="Enter currency full name"
                                        />
                                        {errors.currency_full_name && <div className="text-danger text-sm mt-1">{errors.currency_full_name}</div>}
                                    </div>

                                    {/* Currency Short Name */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">
                                            Currency Short Name <span className="text-danger">*</span>
                                        </label>
                                        <input
                                            // disabled
                                            type="text"
                                            name="currency_short_name"
                                            value={formData.currency_short_name}
                                            onChange={handleChange}
                                            className={`form-control radius-8 ${errors.currency_short_name ? "is-invalid" : ""}`}
                                            placeholder="USD, INR etc."
                                        />
                                        {errors.currency_short_name && <div className="text-danger text-sm mt-1">{errors.currency_short_name}</div>}
                                    </div>

                                    {/* Currency Code */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Currency Code</label>
                                        <input
                                            // disabled
                                            type="text"
                                            name="currency_code"
                                            value={formData.currency_code}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="(e.g. USD, EUR,INR)"
                                        />
                                    </div>

                                    {/* No of States */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">No. of States</label>
                                        <input
                                            type="number"
                                            name="no_of_states"
                                            value={formData.no_of_states}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Enter number"
                                        />
                                    </div>

                                    {/* No of Territories */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">No. of Territories</label>
                                        <input
                                            type="number"
                                            name="no_of_territories"
                                            value={formData.no_of_territories}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Enter number"
                                        />
                                    </div>

                                    {/* Total States & Territories */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Total States & Territories</label>
                                        <input
                                            type="number"
                                            name="total_states_territories"
                                            value={formData.total_states_territories}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Enter total"
                                        />
                                    </div>

                                    {/* Independence Day */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Independence Day</label>
                                        <input
                                            type="date"
                                            name="independence_day"
                                            value={formData.independence_day}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                        />
                                    </div>

                                    {/* Government Type */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Government Type</label>
                                        <input
                                            type="text"
                                            name="government_type"
                                            value={formData.government_type}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Federal, Republic, etc."
                                        />
                                    </div>

                                    {/* Official Language */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Official Language</label>
                                        <input
                                            type="text"
                                            name="official_language"
                                            value={formData.official_language}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Enter language(s)"
                                        />
                                    </div>

                                    {/* Land Area */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Land Area (sq km)</label>
                                        <input
                                            type="number"
                                            name="land_area"
                                            value={formData.land_area}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Enter land area"
                                        />
                                    </div>

                                    {/* Water Area */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Water Area (sq km)</label>
                                        <input
                                            type="number"
                                            name="water_area"
                                            value={formData.water_area}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Enter water area"
                                        />
                                    </div>

                                    {/* Total Area */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Total Area (sq km)</label>
                                        <input
                                            type="number"
                                            name="total_area"
                                            value={formData.total_area}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Enter total area"
                                        />
                                    </div>

                                    {/* Population */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Population</label>
                                        <input
                                            type="number"
                                            name="population"
                                            value={formData.population}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Enter population"
                                        />
                                    </div>

                                    {/* Religions */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Religions</label>
                                        <input
                                            type="text"
                                            name="religions"
                                            value={formData.religions}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Enter major religions"
                                        />
                                    </div>

                                    {/* Monthly Living Cost */}
                                    <div className="col-md-6 mb-10">
                                        <div className="row gx-2">
                                            <div className="col-12">
                                                <label className="form-label fw-semibold text-sm mb-8">Monthly Living Cost</label>

                                                <div className="row gx-2">
                                                    {/* Currency Field */}
                                                    <div className="col-6">
                                                        <input
                                                            type="text"
                                                            name="monthly_living_cost_currency"
                                                            value={formData.monthly_living_cost_currency}
                                                            onChange={handleChange}
                                                            className="form-control radius-8"
                                                            placeholder="Currency"
                                                        />
                                                    </div>

                                                    {/* Number Field */}
                                                    <div className="col-6">
                                                        <input
                                                            type="number"
                                                            name="monthly_living_cost_amount"
                                                            value={formData.monthly_living_cost_amount}
                                                            onChange={handleChange}
                                                            className="form-control radius-8"
                                                            placeholder="Amount"
                                                        />
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Largest State */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Largest State</label>
                                        <Select
                                            options={stateListData.map((option) => ({
                                                value: option.uuid,
                                                label: option.name,
                                            }))}
                                            value={
                                                formData.largest_state
                                                    ? stateListData
                                                        .map((option) => ({
                                                            value: option.uuid,
                                                            label: option.name,
                                                        }))
                                                        .find((opt) => opt.value === formData.largest_state)
                                                    : null
                                            }
                                            onChange={(selectedOption) =>
                                                handleSelectChange(selectedOption, 'largest_state')
                                            }
                                            filterOption={customFilterOption}
                                            placeholder={!formData.country_name ? "Select country first" : "Select largest state"}
                                            isClearable
                                            isSearchable
                                            isDisabled={!formData.country_name || stateLoading}
                                            isLoading={stateLoading}
                                            loadingMessage={() => "Loading states..."}
                                            noOptionsMessage={() =>
                                                !formData.country_name
                                                    ? "Please select a country first"
                                                    : stateLoading
                                                        ? "Loading states..."
                                                        : "No states found"
                                            }
                                            className="custom-select-container"
                                            classNamePrefix="custom-select"
                                        />
                                    </div>

                                    {/* Smallest State */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Smallest State</label>
                                        <Select
                                            options={stateListData.map((option) => ({
                                                value: option.uuid,
                                                label: option.name,
                                            }))}
                                            value={
                                                formData.smallest_state
                                                    ? stateListData
                                                        .map((option) => ({
                                                            value: option.uuid,
                                                            label: option.name,
                                                        }))
                                                        .find((opt) => opt.value === formData.smallest_state)
                                                    : null
                                            }
                                            onChange={(selectedOption) =>
                                                handleSelectChange(selectedOption, 'smallest_state')
                                            }
                                            filterOption={customFilterOption}
                                            placeholder={!formData.country_name ? "Select country first" : "Select smallest state"}
                                            isClearable
                                            isSearchable
                                            isDisabled={!formData.country_name || stateLoading}
                                            isLoading={stateLoading}
                                            loadingMessage={() => "Loading states..."}
                                            noOptionsMessage={() =>
                                                !formData.country_name
                                                    ? "Please select a country first"
                                                    : stateLoading
                                                        ? "Loading states..."
                                                        : "No states found"
                                            }
                                            className="custom-select-container"
                                            classNamePrefix="custom-select"
                                        />
                                    </div>
                                    {/* Major Cities */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Major Cities</label>
                                        <input
                                            type="text"
                                            name="major_cities"
                                            value={formData.major_cities}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Comma separated list"
                                        />
                                    </div>

                                    {/* National Animal */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">National Animal</label>
                                        <input
                                            type="text"
                                            name="national_animal"
                                            value={formData.national_animal}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Enter national animal"
                                        />
                                    </div>

                                    {/* National Bird */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">National Bird</label>
                                        <input
                                            type="text"
                                            name="national_bird"
                                            value={formData.national_bird}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Enter national bird"
                                        />
                                    </div>

                                    {/* National Flower */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">National Flower</label>
                                        <input
                                            type="text"
                                            name="national_flower"
                                            value={formData.national_flower}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Enter national flower"
                                        />
                                    </div>

                                    {/* Unemployment */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Unemployment Rate (%)</label>
                                        <input
                                            type="number"
                                            name="unemployment"
                                            value={formData.unemployment}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Enter %"
                                        />
                                    </div>

                                    {/* Skilled Shortages */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Skilled Shortages</label>
                                        <input
                                            type="text"
                                            name="skilled_shortages"
                                            value={formData.skilled_shortages}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Enter sectors"
                                        />
                                    </div>

                                    {/* Border Countries */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">Border Countries</label>
                                        <input
                                            type="text"
                                            name="border_countries"
                                            value={formData.border_countries}
                                            onChange={handleChange}
                                            className="form-control radius-8"
                                            placeholder="Comma separated list"
                                        />
                                    </div>

                                    {/* National Flag */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">
                                            National Flag
                                        </label>
                                        <input
                                            type="file"
                                            accept="image/*"
                                            onChange={(e) => handleFileChange(e, 'national_flag')}
                                            className="form-control radius-8"
                                            style={{ padding: '6px' }}
                                        />

                                        {/* Show image preview for images, file name for PDFs */}
                                        {files.national_flag && (
                                            <div className="mt-2">
                                                {files.national_flag.type.startsWith('image/') ? (
                                                    <img
                                                        src={filePreviews.national_flag}
                                                        alt="National flag preview"
                                                        className="img-thumbnail"
                                                        style={{ maxWidth: '100px', maxHeight: '100px' }}
                                                    />
                                                ) : (
                                                    <div className="text-primary p-2 border rounded">
                                                        <i className="fas fa-file me-2"></i>
                                                        {files.national_flag.name}
                                                    </div>
                                                )}
                                            </div>
                                        )}

                                        {/* Show existing file in edit mode */}
                                        {mode === 'edit' && formData.national_flag && !files.national_flag && (
                                            <div className="mt-2">
                                                {formData.national_flag.toLowerCase().endsWith('.pdf') ? (
                                                    <div className="text-primary p-2 border rounded">
                                                        <i className="fas fa-file-pdf me-2"></i>
                                                        Current PDF File
                                                    </div>
                                                ) : (
                                                    <img
                                                        src={formData.national_flag}
                                                        alt="Current national flag"
                                                        className="img-thumbnail"
                                                        style={{ maxWidth: '100px', maxHeight: '100px' }}
                                                        onError={(e) => {
                                                            e.target.style.display = 'none';
                                                            e.target.nextSibling.style.display = 'block';
                                                        }}
                                                    />
                                                )}
                                            </div>
                                        )}
                                    </div>

                                    {/* Country Map */}
                                    <div className="col-md-6 mb-10">
                                        <label className="form-label fw-semibold text-sm mb-8">
                                            Country Map
                                        </label>
                                        <input
                                            type="file"
                                            accept="image/*,.pdf"
                                            onChange={(e) => handleFileChange(e, 'country_map')}
                                            className="form-control radius-8"
                                            style={{ padding: '6px' }}
                                        />

                                        {/* Show image preview for images, file name for PDFs */}
                                        {files.country_map && (
                                            <div className="mt-2">
                                                {files.country_map.type.startsWith('image/') ? (
                                                    <img
                                                        src={filePreviews.country_map}
                                                        alt="Country map preview"
                                                        className="img-thumbnail"
                                                        style={{ maxWidth: '100px', maxHeight: '100px' }}
                                                    />
                                                ) : (
                                                    <div className="text-primary p-2 border rounded">
                                                        <i className="fas fa-file-pdf me-2"></i>
                                                        {files.country_map.name}
                                                    </div>
                                                )}
                                            </div>
                                        )}

                                        {/* Show existing file in edit mode */}
                                        {mode === 'edit' && formData.country_map && !files.country_map && (
                                            <div className="mt-2">
                                                {formData.country_map.toLowerCase().endsWith('.pdf') ? (
                                                    <div className="text-primary p-2 border rounded">
                                                        <i className="fas fa-file-pdf me-2"></i>
                                                        Current PDF File
                                                    </div>
                                                ) : (
                                                    <img
                                                        src={formData.country_map}
                                                        alt="Current country map"
                                                        className="img-thumbnail"
                                                        style={{ maxWidth: '100px', maxHeight: '100px' }}
                                                        onError={(e) => {
                                                            e.target.style.display = 'none';
                                                            e.target.nextSibling.style.display = 'block';
                                                        }}
                                                    />
                                                )}
                                            </div>
                                        )}
                                    </div>

                                    {/* Description */}
                                    <div className="col-12 mb-10">
                                        <label className="form-label fw-semibold  text-sm mb-8">
                                            Description
                                        </label>
                                        <textarea
                                            className="form-control radius-8"
                                            name="description"
                                            value={formData.description}
                                            onChange={handleChange}
                                            rows={4}
                                            placeholder="Enter description"
                                        />
                                    </div>
                                </div>

                                {/* Buttons */}
                                <div className="d-flex align-items-center justify-content-center gap-3 mt-24">
                                    <button
                                        type="button"
                                        onClick={onClose}
                                        className="border border-danger-600 bg-hover-danger-200 text-danger-600 text-md px-16 py-6 radius-8"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="btn comman-btn-color border border-primary-600 text-md px-16 py-6 radius-8"
                                        disabled={loading}
                                    >
                                        {loading ? (
                                            <>
                                                <span
                                                    className="spinner-border spinner-border-sm me-2"
                                                    role="status"
                                                    aria-hidden="true"
                                                ></span>
                                                Saving...
                                            </>
                                        ) : (
                                            "Save"
                                        )}
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AddEditRepresentingCountryModal;