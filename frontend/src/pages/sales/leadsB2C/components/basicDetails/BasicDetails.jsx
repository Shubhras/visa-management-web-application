import React, { useEffect, useState } from "react";
import Select from "react-select";
import { maritalStatusList, countryList, stateListByCountry, districtListByState, cityList } from "../../../../../store/master/generalMasters/actions";
import { useDispatch } from "react-redux";
import { visaMainCategoryList } from "../../../../../store/master/visaConditionsMaster/action";
const BasicDetails = () => {
  const genderOptions = [
    { value: "master", label: "Master" },
    { value: "male", label: "Male" },
    { value: "female", label: "Female" },
    { value: "other", label: "Other" },
  ];

  const maritalOptions = [
    { value: "master", label: "Master" },
    { value: "single", label: "Single" },
    { value: "married", label: "Married" },
  ];

  const dispatch = useDispatch();
  const [gender, setGender] = useState(null);
  const [maritalStatus, setMaritalStatus] = useState([]);
  const [country, setCountry] = useState([]);
  const [visaMainCategory, setVisaMainCategory] = useState([]);
  const [state, setState] = useState([]);
  const [district, setDistrict] = useState([]);
  const [city, setCity] = useState([]);

  const [formData, setFormData] = useState({
    maritalStatus: '',
    alongWith: '',
    countryCitizen: '',
    countryResidency: '',
    mobileCode: '',
    mobileNumber: '',
    whatsappCode: '',
    whatsappNumber: '',
    residencyStatus: '',
    email: '',
    address1: '',
    address2: '',
    landmarkArea: '',
    country: '',
    state: '',
    district: '',
    city: '',
    village: '',
    pinCode: '',
  });
  useEffect(() => {
    fetchListData();
    fetchStateList("all");
    fetchDistrictList("all");
    fetchCityListByDistrict("all");
  }, [dispatch])

  const fetchListData = () => {
    const params = {
      page: 1,
      limit: 2000,
      search: '',
      status: '',
      sortBy: 'name',
      sortOrder: 'asc',
    };
    dispatch(maritalStatusList(params, (response, error) => {
      if (response?.statusCode === 200 && response?.status === true) {
        setMaritalStatus(response?.data || []);

      }
    }));
    dispatch(countryList(params, (response, error) => {
      if (response?.statusCode === 200 && response?.status === true) {
        setCountry(response?.data || []);

      }
    }));
    dispatch(visaMainCategoryList(params, (response, error) => {
      if (response?.statusCode === 200 && response?.status === true) {
        setVisaMainCategory(response?.data || []);

      }
    }));
  }

  const handleAddressCountryChange = (selectedOption) => {
    const value = selectedOption ? selectedOption.value : "";
    setFormData(prev => ({
      ...prev,
      country: value,
      state: "",
      district: "",
      city: ""
    }));
    fetchStateList(value || "all");
  };

  const handleStateChange = (selectedOption) => {
    const value = selectedOption ? selectedOption.value : "";
    setFormData(prev => ({
      ...prev,
      state: value,
      district: "",
      city: ""
    }));
    fetchDistrictList(value || "all");
  };

  const handleDistrictChange = (selectedOption) => {
    const value = selectedOption ? selectedOption.value : "";
    setFormData(prev => ({
      ...prev,
      district: value,
      city: ""
    }));

    fetchCityListByDistrict(value || "all");
  };

  const fetchStateList = (countryId) => {
    const params = {
      page: 1,
      limit: 2000,
      search: "",
      status: "",
      sortBy: "name",
      sortOrder: "asc",
      countryId: countryId,
    };

    dispatch(
      stateListByCountry(params, (response, error) => {
        if (response?.statusCode === 200 && response?.status === true) {
          setState(response?.data || []);
        } else {
          setState([]);
        }
      })
    );
  };
  const fetchDistrictList = (stateId) => {

    const params = {
      page: 1,
      limit: 2000,
      search: "",
      status: "",
      sortBy: "districtName",
      sortOrder: "asc",
      countryId: formData.country || null,
      stateId: stateId,
    };
    dispatch(
      districtListByState(params, (response, error) => {
        if (response?.statusCode === 200 && response?.status === true) {
          setDistrict(response?.data || []);
        } else {
          setDistrict([]);
        }
      })
    );
  };

  const fetchCityListByDistrict = (districtId) => {


    const params = {
      page: 1,
      limit: 2000,
      search: "",
      status: "",
      sortBy: "cityName",
      sortOrder: "asc",
      district: districtId,
      country: formData.country || null,
      state: formData.state || null,
    };
    dispatch(
      cityList(params, (response, error) => {
        if (response?.statusCode === 200 && response?.status === true) {
          setCity(response?.data || []);
        } else {
          setCity([]);
        }
      })
    );
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };


  const handleCountryResidencyChange = (selectedOption) => {
    const value = selectedOption ? selectedOption.value : "";
    const selectedCountry = country.find(c => c.uuid === value);

    let dialCode = "";
    if (selectedCountry?.dialCodes) {
      dialCode = Array.isArray(selectedCountry.dialCodes)
        ? selectedCountry.dialCodes[0]
        : selectedCountry.dialCodes;
    }

    setFormData(prev => ({
      ...prev,
      countryResidency: value,
      mobileCode: dialCode,
      whatsappCode: dialCode,
    }));
  };


  return (
    <div className="section-block no-overflow compact-inputs">
      <div className="row gx-5">
        {/* First row */}

        <div className="col-md-4">
          <div className="row g-2">
            <div className="col-6">
              <label className="form-label">
                First Name <span className="text-danger">*</span>
              </label>
              <input
                className="form-control form-control-sm "
                placeholder="Text"
              />
            </div>

            <div className="col-6">
              <label className="form-label">
                Last Name <span className="text-danger">*</span>
              </label>
              <input
                className="form-control form-control-sm"
                placeholder="Text"
              />
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="row g-2">
            <div className="col-6">
              <label className="form-label">
                Gender<span className="text-danger">*</span>
              </label>

              {/* React Select Added */}
              <Select
                options={genderOptions}
                value={genderOptions.find((o) => o.value === gender)}
                onChange={(opt) => setGender(opt?.value || null)}
                placeholder="Master"
                isClearable
                classNamePrefix="custom-select"
                className="custom-select-container"
              />
            </div>

            <div className="col-6">
              <label className="form-label">Date of Birth</label>
              <input type="date" className="form-control form-control-sm" />
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="row g-2">
            <div className="col-6">
              <label className="form-label">Marital Status</label>
              <Select
                options={maritalStatus.map((option) => ({
                  value: option.uuid,
                  label: option.name,
                }))}
                value={
                  formData.maritalStatus
                    ? maritalStatus
                      .map((option) => ({
                        value: option.uuid,
                        label: option.name,
                      }))
                      .find((opt) => opt.value === formData.maritalStatus)
                    : null
                }
                onChange={(selectedOption) => {
                  const value = selectedOption ? selectedOption.value : "";
                  const selectedName = maritalStatus.find(s => s.uuid === value)?.name;
                  const shouldBeYes = selectedName?.includes("Married") ||
                    selectedName === "Common Law Partner";

                  handleChange({
                    target: { name: "alongWith", value: shouldBeYes ? "yes" : "no" }
                  });

                  handleChange({
                    target: { name: "maritalStatus", value }
                  });
                }}
                placeholder="Select Marital Status"
                isClearable
                isSearchable
                classNamePrefix="custom-select"
                menuPortalTarget={document.body}
                menuPosition="fixed"
              />
            </div>

            <div className="col-6">
              <label className="form-label">Along with</label>
              <Select
                options={[
                  { value: 'yes', label: 'Yes' },
                  { value: 'no', label: 'No' }
                ]}
                value={
                  formData.alongWith === 'yes'
                    ? { value: 'yes', label: 'Yes' }
                    : formData.alongWith === 'no'
                      ? { value: 'no', label: 'No' }
                      : null
                }
                onChange={(selectedOption) =>
                  handleChange({
                    target: {
                      name: "alongWith",
                      value: selectedOption ? selectedOption.value : "",
                    },
                  })
                }
                placeholder="Yes / No"
                isClearable
                isSearchable
                classNamePrefix="custom-select"
                menuPortalTarget={document.body}
                menuPosition="fixed"
              />
            </div>
          </div>
        </div>

        {/* Second row */}
        <div className="col-md-4">
          <label className="form-label">Country of Citizen</label>
          <Select
            options={country.map((option) => ({
              value: option.uuid,
              label: option.name,
            }))}
            value={
              formData.countryCitizen
                ? country
                  .map((option) => ({
                    value: option.uuid,
                    label: option.name,
                  }))
                  .find((opt) => opt.value === formData.countryCitizen)
                : null
            }
            onChange={(selectedOption) =>
              handleChange({
                target: {
                  name: "countryCitizen",
                  value: selectedOption ? selectedOption.value : "",
                },
              })
            }
            placeholder="Select Country"
            isClearable
            isSearchable
            classNamePrefix="custom-select"
            menuPortalTarget={document.body}
            menuPosition="fixed"
          />
        </div>

        <div className="col-md-4">
          <label className="form-label">Country of Residency</label>
          <Select
            options={country.map((option) => ({
              value: option.uuid,
              label: option.name,
            }))}
            value={
              formData.countryResidency
                ? country
                  .map((option) => ({
                    value: option.uuid,
                    label: option.name,
                  }))
                  .find((opt) => opt.value === formData.countryResidency)
                : null
            }
            onChange={handleCountryResidencyChange}
            placeholder="Select Country"
            isClearable
            isSearchable
            classNamePrefix="custom-select"
            menuPortalTarget={document.body}
            menuPosition="fixed"
          />
        </div>

        <div className="col-md-4">
          <label className="form-label">Residency Status</label>
          <Select
            options={visaMainCategory.map((option) => ({
              value: option.uuid,
              label: option.name,
            }))}
            value={
              formData.residencyStatus
                ? visaMainCategory
                  .map((option) => ({
                    value: option.uuid,
                    label: option.name,
                  }))
                  .find((opt) => opt.value === formData.residencyStatus)
                : null
            }
            onChange={(selectedOption) =>
              handleChange({
                target: {
                  name: "residencyStatus",
                  value: selectedOption ? selectedOption.value : "",
                },
              })
            }
            placeholder="Select Visa Main Category"
            isClearable
            isSearchable
            classNamePrefix="custom-select"
            menuPortalTarget={document.body}
            menuPosition="fixed"
          />
        </div>

        {/* Third row */}
        <div className="col-md-4">
          <label className="form-label">
            Mobile No.<span className="text-danger">*</span>
          </label>
          <div className="d-flex gap-2">
            <input
              className="form-control form-control-sm"
              placeholder="Code"
              style={{ maxWidth: 84 }}
              name="mobileCode"
              value={formData.mobileCode || ""}
              onChange={handleChange}
            />
            <input
              className="form-control form-control-sm"
              placeholder="Number"
              name="mobileNumber"
              value={formData.mobileNumber || ""}
              onChange={handleChange}
            />
          </div>
        </div>

        <div className="col-md-4">
          <label className="form-label">
            WhatsApp No.<span className="text-danger">*</span>
          </label>
          <div className="d-flex gap-2">
            <input
              className="form-control form-control-sm"
              placeholder="Code"
              style={{ maxWidth: 84 }}
              name="whatsappCode"
              value={formData.whatsappCode || ""}
              onChange={handleChange}
            />
            <input
              className="form-control form-control-sm"
              placeholder="Number"
              name="whatsappNumber"
              value={formData.whatsappNumber || ""}
              onChange={handleChange}
            />
          </div>
        </div>

        <div className="col-md-4">
          <label className="form-label">
            Email ID<span className="text-danger">*</span>
          </label>
          <input
            type="email"
            className="form-control form-control-sm"
            placeholder="Text"
          />
        </div>

        {/* Fourth row */}
        <div className="col-md-4">
          <label className="form-label">Address Line - 01</label>
          <input className="form-control form-control-sm" placeholder="Text" />
        </div>

        <div className="col-md-4">
          <label className="form-label">Address Line - 02</label>
          <input className="form-control form-control-sm" placeholder="Text" />
        </div>

        <div className="col-md-4">
          <label className="form-label">Landmark / Area</label>
          <input className="form-control form-control-sm" placeholder="Text" />
        </div>

        {/* Fifth row */}
        <div className="col-md-4">
          <div className="row g-2">
            <div className="col-6">
              <label className="form-label">Country</label>
              <Select
                options={country.map((option) => ({
                  value: option.uuid,
                  label: option.name,
                }))}
                value={
                  formData.country
                    ? country
                      .map((option) => ({
                        value: option.uuid,
                        label: option.name,
                      }))
                      .find((opt) => opt.value === formData.country)
                    : null
                }
                onChange={handleAddressCountryChange}
                placeholder="Select Country"
                isClearable
                isSearchable
                classNamePrefix="custom-select"
                menuPortalTarget={document.body}
                menuPosition="fixed"
              />
            </div>
            <div className="col-6">
              <label className="form-label">State</label>
              <Select
                options={state.map((option) => ({
                  value: option.uuid,
                  label: option.name,
                }))}
                value={
                  formData.state
                    ? state
                      .map((option) => ({
                        value: option.uuid,
                        label: option.name,
                      }))
                      .find((opt) => opt.value === formData.state)
                    : null
                }
                onChange={handleStateChange}
                placeholder="Select State"
                isClearable
                isSearchable
                classNamePrefix="custom-select"
                menuPortalTarget={document.body}
                menuPosition="fixed"
              />
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="row g-2">
            <div className="col-6">
              <label className="form-label">District</label>
              <Select
                options={district.map((option) => ({
                  value: option.uuid,
                  label: option.districtName,
                }))}
                value={
                  formData.district
                    ? district
                      .map((option) => ({
                        value: option.uuid,
                        label: option.districtName,
                      }))
                      .find((opt) => opt.value === formData.district)
                    : null
                }
                onChange={handleDistrictChange}
                placeholder="Select District"
                isClearable
                isSearchable
                classNamePrefix="custom-select"
                menuPortalTarget={document.body}
                menuPosition="fixed"
              />
            </div>
            <div className="col-6">
              <label className="form-label">City / Taluka</label>
              <Select
                options={city.map((option) => ({
                  value: option.uuid,
                  label: option.cityName,
                }))}
                value={
                  formData.city
                    ? city
                      .map((option) => ({
                        value: option.uuid,
                        label: option.cityName,
                      }))
                      .find((opt) => opt.value === formData.city)
                    : null
                }
                onChange={(opt) => handleChange({ target: { name: "city", value: opt ? opt.value : "" } })}
                placeholder="Select City/ Taluka"
                isClearable
                isSearchable
                classNamePrefix="custom-select"
                menuPortalTarget={document.body}
                menuPosition="fixed"
              />
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="row g-2">
            <div className="col-6">
              <label className="form-label">Village</label>
              <input
                className="form-control form-control-sm"
                placeholder="Text"
              />
            </div>
            <div className="col-6">
              <label className="form-label">PIN / ZIP</label>
              <input
                className="form-control form-control-sm"
                placeholder="Text"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BasicDetails;
