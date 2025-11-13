import React, { useEffect, useState } from "react";
import { Icon } from "@iconify/react/dist/iconify.js";
import { Link, NavLink, useLocation } from "react-router-dom";
import ThemeToggleButton from "../helper/ThemeToggleButton";
// import Header from "./Header";
import { useNavigate } from 'react-router-dom';
import { toast } from "react-toastify";
const MasterLayout = ({ children }) => {
  const navigate = useNavigate()
  let [sidebarActive, seSidebarActive] = useState(false);
  let [mobileMenu, setMobileMenu] = useState(false);
  const location = useLocation();
  const [selectedItemName, setSelectedItemName] = useState('Dashboard');
  const [openSubmenu, setOpenSubmenu] = useState(null);
  const [openChildMenu, setOpenChildMenu] = useState(null);
  const menuItems = [
    {
      name: 'Dashboard',
      path: '/',
      submenu: []
    },
    {
      name: 'Sales',
      path: '/',
      submenu: []
    },
    {
      name: 'Clients',
      path: '/',
      submenu: []
    },
    {
      name: 'Partners',
      path: '/',
      submenu: []
    },
    {
      name: 'Visa',
      path: '/',
      submenu: []
    },
    {
      name: 'Institutes',
      path: '/',
      submenu: []
    },
    {
      name: 'Layout',
      path: '/',
      submenu: []
    },
    {
      name: 'Masters',
      // path: '/department',
      submenu: [
        {
          name: 'General',
          children: [
            { name: 'Gender', path: '/gender-list' },
            { name: 'Marital Status', path: '/marital-status' },
            { name: 'Continents ', path: '/continent-list' },
            { name: "Country ", path: "/country-list" },
            { name: 'State', path: '/state-list' },
            { name: 'District', path: '/district-list' },
            { name: 'City', path: '/city-list' },
            { name: 'Time Zone', path: '/timezone-list' },
            { name: 'Relation', path: '/relation-list' },
            { name: 'Civil ID Name', path: '/civil-name-list' },
          ]
        },
        {
          // name: 'Admin',
          name: 'Company',
          // path: '/Department',
          children: [
            { name: 'Department', path: '/department' },
            { name: 'Employee Type', path: '/employeetype' },
            { name: 'Company Type', path: '/companylist' },
            { name: 'Ownership Type', path: '/ownership-type' },
            { name: 'Stakeholder Category', path: '/stakeholder-list' },
            { name: 'Stakeholder Type', path: '/stakeholder-type' },
            { name: 'Accrediation Category ', path: '/accrediation-category' },
            { name: 'Accrediation Name', path: '/accrediation-name' },
            { name: 'Bank Account Type', path: '/bank-ccount-type' },
            { name: 'License Name', path: '/license-name' },
          ]
        },
        {
          name: 'Sales',
          // path: '/priority-type',
          children: [
            { name: 'Lead Source', path: '/lead-source' },
            { name: 'Interest Level', path: '/interest-level' },
            { name: 'Priority', path: '/priority-type' },
            { name: 'Tags', path: '/tags-type' },
            { name: 'Activity Type', path: '/activity-type' },
            { name: 'Lost Reason (B2C)', path: '/lost-reason-B2C' },
            { name: 'Lost Reason (B2B)', path: '/lost-reason-B2B' },
          ]
        },
        {
          name: 'Education',
          // path: '/priority-type',
          children: [
            { name: 'Education Level Code', path: '/education-level-code' },
            { name: 'Education Level', path: '/education-level' },
            { name: 'Study Main Area', path: '/study-main-area' },
            { name: 'Education Duration', path: '/education-duration' },
            { name: 'Study Major Area', path: '/study-major-area' },
            { name: 'Academic Result Type', path: '/academic-result-type' },
            { name: 'Education Type', path: '/education-type' },
            { name: 'Study Specialisation', path: '/study-specialisation' },
            { name: 'Degree Awarded By', path: '/degree-awarded-by' },
            { name: 'Academic Result', path: '/academic-result' },
            { name: 'Degree Awarded Institute', path: '/degree-awarded-institute' },
            { name: 'Compare : Academic Result To Result', path: '/academic-result-to-result' },
            { name: 'ECA Awarding Body', path: '/eca-awarding-body' },
            { name: 'Medium of Education', path: '/medium-of-education' },
            { name: 'ECA For', path: '/eca-for' },

          ]
        },
        {
          name: 'Test',
          // path: '/priority-type',
          children: [
            { name: 'Language Name(Test)', path: '/language-name-test' },
            { name: 'Language Test Name', path: '/language-test-name' },
            { name: 'Language Test Module Name', path: '/language-test-module-name' },
            { name: 'Language Banchmark Level', path: '/language-banchmark-level' },
            { name: 'CLB Level', path: '/cbl-level' },
            { name: 'Entrance Test Name', path: '/entrance-test-name' },
            { name: 'Entrance Test Module Name', path: '/entrance-test-module-name' },
            { name: 'Entrance Test Result', path: '/entrance-test-result' },
            { name: 'Language Test Result', path: '/language-test-result' },
          ]
        },
        {
          name: 'Occupation',
          children: [
            { name: 'Job Type', path: '/job-type' },
            { name: 'Mode of Salary', path: '/mode-of-salary' },
            { name: 'IT Return Status', path: '/it-return-status' },
            { name: 'Occupation Type', path: '/occupation-type' },
            { name: 'Occupation Prospect', path: '/occupation-prospect' },
            { name: 'Occupation Version', path: '/occupation-version' }

          ]
        },
        {
          name: 'Institute',
          children: [
            { name: 'Institute Type', path: '/institute-type' },
            { name: 'Institute Group Name', path: '/institute-group-name' },
            { name: "Institute Status", path: '/institute-status' },
            { name: "Institute Priority", path: '/institute-priority' },
            { name: "Institute Department", path: '/institute-department' },


          ]
        },


        // { name: 'Education', path: '/' },
        // { name: 'Test', path: '/' },
        // { name: 'Occupation', path: '/' },
        // { name: 'General', path: '/' },
        // { name: 'Admin', path: '/' },
        // { name: 'Visa', path: '/' },
        // { name: 'Process', path: '/' },
        // { name: 'Institute', path: '/' },

      ]
    },
    {
      name: 'Packages',
      path: '/',
      submenu: []
    },
    {
      name: 'Subscribers',
      path: '/',
      submenu: []
    }
  ];


  const handleMenuClick = (item, parent = null, grandParent = null) => {
    if (item.children && item.children.length > 0) {
      return;
    }
    const menuName = item.name;
    setSelectedItemName(menuName);
  };

  const handleLogout = () => {
    toast.success('Logout successful');
    // // 1. Clear user data (localStorage / sessionStorage / Redux)
    // localStorage.removeItem('userToken') // or whatever you use
    localStorage.removeItem('authUser')

    // // 2. Optionally reset Redux state
    // // dispatch({ type: 'LOGOUT' }) 

    // // 3. Navigate to login page
    navigate('/sign-in');
  }

  useEffect(() => {
    // Current path के basis पर menu item ढूंढो
    const findMenuItemByPath = (items, currentPath) => {
      for (const item of items) {
        if (item.path === currentPath) {
          return item.name;
        }
        if (item.submenu && item.submenu.length > 0) {
          for (const subItem of item.submenu) {
            if (subItem.children) {
              for (const child of subItem.children) {
                if (child.path === currentPath) {
                  return child.name;
                }
              }
            }
          }
        }
      }
      return null;
    };

    const matchedName = findMenuItemByPath(menuItems, location.pathname);
    if (matchedName) {
      setSelectedItemName(matchedName);
    }

    const handleDropdownClick = (event) => {
      event.preventDefault();
      const clickedLink = event.currentTarget;
      const clickedDropdown = clickedLink.closest(".dropdown");

      if (!clickedDropdown) return;

      const isActive = clickedDropdown.classList.contains("open");

      const allDropdowns = document.querySelectorAll(".sidebar-menu .dropdown");
      allDropdowns.forEach((dropdown) => {
        dropdown.classList.remove("open");
        const submenu = dropdown.querySelector(".sidebar-submenu");
        if (submenu) {
          submenu.style.maxHeight = "0px";
        }
      });

      if (!isActive) {
        clickedDropdown.classList.add("open");
        const submenu = clickedDropdown.querySelector(".sidebar-submenu");
        if (submenu) {
          submenu.style.maxHeight = `${submenu.scrollHeight}px`;
        }
      }
    };

    const dropdownTriggers = document.querySelectorAll(
      ".sidebar-menu .dropdown > a, .sidebar-menu .dropdown > Link"
    );

    dropdownTriggers.forEach((trigger) => {
      trigger.addEventListener("click", handleDropdownClick);
    });

    const openActiveDropdown = () => {
      const allDropdowns = document.querySelectorAll(".sidebar-menu .dropdown");
      allDropdowns.forEach((dropdown) => {
        const submenuLinks = dropdown.querySelectorAll(".sidebar-submenu li a");
        submenuLinks.forEach((link) => {
          if (
            link.getAttribute("href") === location.pathname ||
            link.getAttribute("to") === location.pathname
          ) {
            dropdown.classList.add("open");
            const submenu = dropdown.querySelector(".sidebar-submenu");
            if (submenu) {
              submenu.style.maxHeight = `${submenu.scrollHeight}px`;
            }
          }
        });
      });
    };

    openActiveDropdown();

    return () => {
      dropdownTriggers.forEach((trigger) => {
        trigger.removeEventListener("click", handleDropdownClick);
      });
    };
  }, [location.pathname]);



  let sidebarControl = () => {
    seSidebarActive(!sidebarActive);
  };

  let mobileMenuControl = () => {
    setMobileMenu(!mobileMenu);
  };


  return (
    <section className={mobileMenu ? "overlay active" : "overlay "}>
      <aside
        className={
          sidebarActive
            ? "sidebar active "
            : mobileMenu
              ? "sidebar sidebar-open"
              : "sidebar"
        }
        style={{ display: "none" }}
      >
        <button
          onClick={mobileMenuControl}
          type='button'
          className='sidebar-close-btn'
        >
          <Icon icon='radix-icons:cross-2' />
        </button>
        <div>
          <Link to='/' className='sidebar-logo'>
            <img
              src='assets/images/logo-test1.png'
              alt='site logo'
              className='light-logo'
            />
            {/* <img
              src='assets/images/logo-test11.jpg'
              alt='site logo'
              className='light-logo'
            /> */}
            <img
              src='assets/images/logo-light.png'
              alt='site logo'
              className='dark-logo'
            />
            {/* <img
              src='assets/images/logo-icon.png'
              alt='site logo'
              className='logo-icon'
            /> */}
            <img
              src='assets/images/logo-test2.png'
              alt='site logo'
              className='logo-icon'
            />
          </Link>
        </div>
        <div className='sidebar-menu-area'>
          {/* <ul className='sidebar-menu' id='sidebar-menu'>
                    <li className='dropdown'>
                      <Link to='#'>
                        <Icon
                          icon='solar:home-smile-angle-outline'
                          className='menu-icon'
                        />
                        <span>Dashboard</span>
                      </Link>
                      <ul className='sidebar-submenu'>
                        <li>
                          <NavLink
                            to='/'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-primary-600 w-auto' />
                            AI
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/index-2'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />{" "}
                            CRM
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/index-3'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-info-main w-auto' />{" "}
                            eCommerce
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/index-4'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-danger-main w-auto' />
                            Cryptocurrency
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/index-5'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-success-main w-auto' />{" "}
                            Investment
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/index-6'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-purple w-auto' />{" "}
                            LMS
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/index-7'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-info-main w-auto' />{" "}
                            NFT &amp; Gaming
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/index-8'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-info-main w-auto' />{" "}
                            Medical
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/index-9'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-info-main w-auto' />{" "}
                            Analytics
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/index-10'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-info-main w-auto' />{" "}
                            POS & Inventory
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/index-11'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-info-main w-auto' />{" "}
                            Finance & Banking
                          </NavLink>
                        </li>
                      </ul>
                    </li>
        
                    <li className='sidebar-menu-group-title'>Application</li>
                    <li>
                      <NavLink
                        to='/email'
                        className={(navData) => (navData.isActive ? "active-page" : "")}
                      >
                        <Icon icon='mage:email' className='menu-icon' />
                        <span>Email</span>
                      </NavLink>
                    </li>
                    <li>
                      <NavLink
                        to='/chat-message'
                        className={(navData) => (navData.isActive ? "active-page" : "")}
                      >
                        <Icon icon='bi:chat-dots' className='menu-icon' />
                        <span>Chat</span>
                      </NavLink>
                    </li>
                    <li>
                      <NavLink
                        to='/calendar-main'
                        className={(navData) => (navData.isActive ? "active-page" : "")}
                      >
                        <Icon icon='solar:calendar-outline' className='menu-icon' />
                        <span>Calendar</span>
                      </NavLink>
                    </li>
                    <li>
                      <NavLink
                        to='/kanban'
                        className={(navData) => (navData.isActive ? "active-page" : "")}
                      >
                        <Icon
                          icon='material-symbols:map-outline'
                          className='menu-icon'
                        />
                        <span>Kanban</span>
                      </NavLink>
                    </li>
        
                  
                    <li className='dropdown'>
                      <Link to='#'>
                        <Icon icon='hugeicons:invoice-03' className='menu-icon' />
                        <span>Invoice</span>
                      </Link>
                      <ul className='sidebar-submenu'>
                        <li>
                          <NavLink
                            to='/invoice-list'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-primary-600 w-auto' />{" "}
                            List
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/invoice-preview'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />
                            Preview
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/invoice-add'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-info-main w-auto' />{" "}
                            Add new
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/invoice-edit'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-danger-main w-auto' />{" "}
                            Edit
                          </NavLink>
                        </li>
                      </ul>
                    </li>
        
                  
                    <li className='dropdown'>
                      <Link to='#'>
                        <i className='ri-robot-2-line mr-10' />
        
                        <span>Ai Application</span>
                      </Link>
                      <ul className='sidebar-submenu'>
                        <li>
                          <NavLink
                            to='/text-generator'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-primary-600 w-auto' />{" "}
                            Text Generator
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/code-generator'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />{" "}
                            Code Generator
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/image-generator'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-info-main w-auto' />{" "}
                            Image Generator
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/voice-generator'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-danger-main w-auto' />{" "}
                            Voice Generator
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/video-generator'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-success-main w-auto' />{" "}
                            Video Generator
                          </NavLink>
                        </li>
                      </ul>
                    </li>
        
                  
                    <li className='dropdown'>
                      <Link to='#'>
                        <i className='ri-btc-line mr-10' />
                        <span>Crypto Currency</span>
                      </Link>
                      <ul className='sidebar-submenu'>
                        <li>
                          <NavLink
                            to='/wallet'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-primary-600 w-auto' />{" "}
                            Wallet
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/marketplace'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />
                            Marketplace
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/marketplace-details'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />
                            Marketplace Details
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/portfolio'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />
                            Portfolios
                          </NavLink>
                        </li>
                      </ul>
                    </li>
        
                    <li className='sidebar-menu-group-title'>UI Elements</li>
        
                  
                    <li className='dropdown'>
                      <Link to='#'>
                        <Icon
                          icon='solar:document-text-outline'
                          className='menu-icon'
                        />
                        <span>Components</span>
                      </Link>
                      <ul className='sidebar-submenu'>
                        <li>
                          <NavLink
                            to='/typography'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-primary-600 w-auto' />
                            Typography
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/colors'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />{" "}
                            Colors
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/button'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-success-main w-auto' />{" "}
                            Button
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/dropdown'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-lilac-600 w-auto' />{" "}
                            Dropdown
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/alert'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />{" "}
                            Alerts
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/card'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-danger-main w-auto' />{" "}
                            Card
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/carousel'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-info-main w-auto' />{" "}
                            Carousel
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/avatar'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-success-main w-auto' />{" "}
                            Avatars
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/progress'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-primary-600 w-auto' />{" "}
                            Progress bar
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/tabs'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />{" "}
                            Tab &amp; Accordion
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/pagination'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-danger-main w-auto' />
                            Pagination
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/badges'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-info-main w-auto' />{" "}
                            Badges
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/tooltip'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-lilac-600 w-auto' />{" "}
                            Tooltip &amp; Popover
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/videos'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-cyan w-auto' />{" "}
                            Videos
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/star-rating'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-indigo w-auto' />{" "}
                            Star Ratings
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/tags'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-purple w-auto' />{" "}
                            Tags
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/list'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-red w-auto' />{" "}
                            List
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/calendar'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-yellow w-auto' />{" "}
                            Calendar
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/radio'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-orange w-auto' />{" "}
                            Radio
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/switch'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-pink w-auto' />{" "}
                            Switch
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/image-upload'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-primary-600 w-auto' />{" "}
                            Upload
                          </NavLink>
                        </li>
                      </ul>
                    </li>
        
                   
                    <li className='dropdown'>
                      <Link to='#'>
                        <Icon icon='heroicons:document' className='menu-icon' />
                        <span>Forms</span>
                      </Link>
                      <ul className='sidebar-submenu'>
                        <li>
                          <NavLink
                            to='/form'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-primary-600 w-auto' />{" "}
                            Input Forms
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/form-layout'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />{" "}
                            Input Layout
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/form-validation'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-success-main w-auto' />{" "}
                            Form Validation
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/wizard'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-danger-main w-auto' />{" "}
                            Form Wizard
                          </NavLink>
                        </li>
                      </ul>
                    </li>
        
               
                    <li className='dropdown'>
                      <Link to='#'>
                        <Icon icon='mingcute:storage-line' className='menu-icon' />
                        <span>Table</span>
                      </Link>
                      <ul className='sidebar-submenu'>
                        <li>
                          <NavLink
                            to='/table-basic'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-primary-600 w-auto' />{" "}
                            Basic Table
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/table-data'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />{" "}
                            Data Table
                          </NavLink>
                        </li>
                      </ul>
                    </li>
        
                   
                    <li className='dropdown'>
                      <Link to='#'>
                        <Icon icon='solar:pie-chart-outline' className='menu-icon' />
                        <span>Chart</span>
                      </Link>
                      <ul className='sidebar-submenu'>
                        <li>
                          <NavLink
                            to='/line-chart'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-danger-main w-auto' />{" "}
                            Line Chart
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/column-chart'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />{" "}
                            Column Chart
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/pie-chart'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-success-main w-auto' />{" "}
                            Pie Chart
                          </NavLink>
                        </li>
                      </ul>
                    </li>
        
                    <li>
                      <NavLink
                        to='/widgets'
                        className={(navData) => (navData.isActive ? "active-page" : "")}
                      >
                        <Icon icon='fe:vector' className='menu-icon' />
                        <span>Widgets</span>
                      </NavLink>
                    </li>
        
                   
                    <li className='dropdown'>
                      <Link to='#'>
                        <Icon
                          icon='flowbite:users-group-outline'
                          className='menu-icon'
                        />
                        <span>Users</span>
                      </Link>
                      <ul className='sidebar-submenu'>
                        <li>
                          <NavLink
                            to='/users-list'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-primary-600 w-auto' />{" "}
                            Users List
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/users-grid'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />{" "}
                            Users Grid
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/add-user'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-info-main w-auto' />{" "}
                            Add User
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/view-profile'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-danger-main w-auto' />{" "}
                            View Profile
                          </NavLink>
                        </li>
                      </ul>
                    </li>
        
                  
                    <li className='dropdown'>
                      <Link to='#'>
                        <i className='ri-user-settings-line' />
                        <span>Role &amp; Access</span>
                      </Link>
                      <ul className='sidebar-submenu'>
                        <li>
                          <NavLink
                            to='/role-access'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-primary-600 w-auto' />{" "}
                            Role &amp; Access
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/assign-role'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />{" "}
                            Assign Role
                          </NavLink>
                        </li>
                      </ul>
                    </li>
        
                    <li className='sidebar-menu-group-title'>Application</li>
        
                    
                    <li className='dropdown'>
                      <Link to='#'>
                        <Icon icon='simple-line-icons:vector' className='menu-icon' />
                        <span>Authentication</span>
                      </Link>
                      <ul className='sidebar-submenu'>
                        <li>
                          <NavLink
                            to='/sign-in'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-primary-600 w-auto' />{" "}
                            Sign In
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/sign-up'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />{" "}
                            Sign Up
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/forgot-password'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-info-main w-auto' />{" "}
                            Forgot Password
                          </NavLink>
                        </li>
                      </ul>
                    </li>
        
                 
        
                    <li className='dropdown'>
                      <Link to='#'>
                        <Icon
                          icon='flowbite:users-group-outline'
                          className='menu-icon'
                        />
                        <span>Gallery</span>
                      </Link>
                      <ul className='sidebar-submenu'>
                        <li>
                          <NavLink
                            to='/gallery-grid'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-primary-600 w-auto' />{" "}
                            Gallery Grid
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/gallery'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />{" "}
                            Gallery Grid Desc
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/gallery-masonry'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-info-main w-auto' />{" "}
                            Gallery Grid
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/gallery-hover'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-danger-main w-auto' />{" "}
                            Gallery Hover Effect
                          </NavLink>
                        </li>
                      </ul>
                    </li>
        
                    <li>
                      <NavLink
                        to='/pricing'
                        className={(navData) => (navData.isActive ? "active-page" : "")}
                      >
                        <Icon
                          icon='hugeicons:money-send-square'
                          className='menu-icon'
                        />
                        <span>Pricing</span>
                      </NavLink>
                    </li>
        
                   
        
                    <li className='dropdown'>
                      <Link to='#'>
                        <Icon
                          icon='flowbite:users-group-outline'
                          className='menu-icon'
                        />
                        <span>Blog</span>
                      </Link>
                      <ul className='sidebar-submenu'>
                        <li>
                          <NavLink
                            to='/blog'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-primary-600 w-auto' />{" "}
                            Blog
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/blog-details'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />{" "}
                            Blog Details
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/add-blog'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-info-main w-auto' />{" "}
                            Add Blog
                          </NavLink>
                        </li>
                      </ul>
                    </li>
        
                    <li>
                      <NavLink
                        to='/testimonials'
                        className={(navData) => (navData.isActive ? "active-page" : "")}
                      >
                        <Icon
                          icon='mage:message-question-mark-round'
                          className='menu-icon'
                        />
                        <span>Testimonials</span>
                      </NavLink>
                    </li>
                    <li>
                      <NavLink
                        to='/faq'
                        className={(navData) => (navData.isActive ? "active-page" : "")}
                      >
                        <Icon
                          icon='mage:message-question-mark-round'
                          className='menu-icon'
                        />
                        <span>FAQs.</span>
                      </NavLink>
                    </li>
                    <li>
                      <NavLink
                        to='/error'
                        className={(navData) => (navData.isActive ? "active-page" : "")}
                      >
                        <Icon icon='streamline:straight-face' className='menu-icon' />
                        <span>404</span>
                      </NavLink>
                    </li>
                    <li>
                      <NavLink
                        to='/terms-condition'
                        className={(navData) => (navData.isActive ? "active-page" : "")}
                      >
                        <Icon icon='octicon:info-24' className='menu-icon' />
                        <span>Terms &amp; Conditions</span>
                      </NavLink>
                    </li>
                    <li>
                      <NavLink
                        to='/coming-soon'
                        className={(navData) => (navData.isActive ? "active-page" : "")}
                      >
                        <i className='ri-rocket-line menu-icon'></i>
                        <span>Coming Soon</span>
                      </NavLink>
                    </li>
                    <li>
                      <NavLink
                        to='/access-denied'
                        className={(navData) => (navData.isActive ? "active-page" : "")}
                      >
                        <i className='ri-folder-lock-line menu-icon'></i>
                        <span>Access Denied</span>
                      </NavLink>
                    </li>
                    <li>
                      <NavLink
                        to='/maintenance'
                        className={(navData) => (navData.isActive ? "active-page" : "")}
                      >
                        <i className='ri-hammer-line menu-icon'></i>
                        <span>Maintenance</span>
                      </NavLink>
                    </li>
                    <li>
                      <NavLink
                        to='/blank-page'
                        className={(navData) => (navData.isActive ? "active-page" : "")}
                      >
                        <i className='ri-checkbox-multiple-blank-line menu-icon'></i>
                        <span>Blank Page</span>
                      </NavLink>
                    </li>
        
                   
                    <li className='dropdown'>
                      <Link to='#'>
                        <Icon
                          icon='icon-park-outline:setting-two'
                          className='menu-icon'
                        />
                        <span>Settings</span>
                      </Link>
                      <ul className='sidebar-submenu'>
                        <li>
                          <NavLink
                            to='/company'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-primary-600 w-auto' />{" "}
                            Company
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/notification'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-warning-main w-auto' />{" "}
                            Notification
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/notification-alert'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-info-main w-auto' />{" "}
                            Notification Alert
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/theme'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-danger-main w-auto' />{" "}
                            Theme
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/currencies'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-danger-main w-auto' />{" "}
                            Currencies
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/language'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-danger-main w-auto' />{" "}
                            Languages
                          </NavLink>
                        </li>
                        <li>
                          <NavLink
                            to='/payment-gateway'
                            className={(navData) =>
                              navData.isActive ? "active-page" : ""
                            }
                          >
                            <i className='ri-circle-fill circle-icon text-danger-main w-auto' />{" "}
                            Payment Gateway
                          </NavLink>
                        </li>
                      </ul>
                    </li>
                  </ul> */}
        </div>
      </aside>

      <main
        className={sidebarActive ? "dashboard-main active" : "dashboard-main"}
      >
        {/* <div className='navbar-header' >
          <div className='row align-items-center justify-content-between' style={{ margin: '0' }}>
            <div className='col-auto'>
              <div className='d-flex align-items-center gap-3'>
                <div>
                  <img
                    src='assets/images/logo-test1.png'
                    alt='site logo'
                    className='light-logo'
                    style={{ width: "100px" }}
                  />
                </div>

                <Header />

              </div>
            </div>
            <div className='col-auto'>
              <div className='d-flex flex-wrap align-items-center gap-3'>
            

                <div className='dropdown'>
                  <button
                    className='has-indicator w-40-px h-40-px bg-neutral-200 rounded-circle d-flex justify-content-center align-items-center'
                    type='button'
                    data-bs-toggle='dropdown'
                  >
                    <Icon
                      icon='iconoir:bell'
                      className='text-primary-light text-xl'
                    />
                  </button>
                  <div className='dropdown-menu to-top dropdown-menu-lg p-0'>
                    <div className='m-16 py-12 px-16 radius-8 bg-primary-50 mb-16 d-flex align-items-center justify-content-between gap-2'>
                      <div>
                        <h6 className='text-lg text-primary-light fw-semibold mb-0'>
                          Notifications
                        </h6>
                      </div>
                      <span className='text-primary-600 fw-semibold text-lg w-40-px h-40-px rounded-circle bg-base d-flex justify-content-center align-items-center'>
                        05
                      </span>
                    </div>
                  </div>
                </div>

                <div className='dropdown'>
                  <button
                    className='d-flex justify-content-center align-items-center rounded-circle'
                    type='button'
                    data-bs-toggle='dropdown'
                  >
                    <img
                      src='assets/images/users/avatar-4.jpg'
                      alt='image_user'
                      className='w-40-px h-40-px object-fit-cover rounded-circle'
                    />
                  </button>
                  <div className='dropdown-menu to-top dropdown-menu-sm'>
                    <div className='py-12 px-16 radius-8 bg-primary-50 mb-16 d-flex align-items-center justify-content-between gap-2'>
                      <div>
                        <h6 className='text-lg text-primary-light fw-semibold mb-2'>
                          Shaidul Islam
                        </h6>
                        <span className='text-secondary-light fw-medium text-sm'>
                          Admin
                        </span>
                      </div>
                      <button type='button' className='hover-text-danger'>
                        <Icon
                          icon='radix-icons:cross-1'
                          className='icon text-xl'
                        />
                      </button>
                    </div>
                    <ul className='to-top-list'>
                      <li>
                        <Link
                          className='dropdown-item text-black px-0 py-8 hover-bg-transparent hover-text-primary d-flex align-items-center gap-3'
                          to='/'
                        >
                          <Icon
                            icon='solar:user-linear'
                            className='icon text-xl'
                          />{" "}
                          My Profile
                        </Link>
                      </li>
                      <li>
                        <Link
                          className='dropdown-item text-black px-0 py-8 hover-bg-transparent hover-text-danger d-flex align-items-center gap-3'
                          to='/sign-in' onClick={handleLogout}
                        >
                          <Icon icon='lucide:power' className='icon text-xl' />{" "}
                          Log Out
                        </Link>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div> */}
        <div className="d-flex align-items-stretch main-header-container">
          <div className="logo-section">
            <img
              src="assets/images/logo-test1.png"
              alt="Logo"
              className="logo-image"
            />
          </div>

          <div className="flex-grow-1 d-flex flex-column">
            <div className="top-header-bar">
              {/* <Header onMenuItemClick={handleMenuClick} /> */}
              <nav className='d-none d-lg-flex align-items-center gap-2'>
                {menuItems.map((item, index) => (
                  <div
                    key={index}
                    className='position-relative'
                    onMouseEnter={() => setOpenSubmenu(index)}
                    onMouseLeave={() => {
                      setOpenSubmenu(null);
                      setOpenChildMenu(null);
                    }}
                  >
                    <Link
                      to={item.path}
                      onClick={() => handleMenuClick(item)}

                      className='text-white text-decoration-none d-flex align-items-center gap-1 main-menu-items'
                      style={{
                        backgroundColor: openSubmenu === index ? 'rgba(255, 255, 255, 0.1)' : 'transparent'
                      }}
                      onMouseEnter={(e) => {
                        if (openSubmenu !== index) {
                          e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.08)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (openSubmenu !== index) {
                          e.currentTarget.style.backgroundColor = 'transparent';
                        }
                      }}
                    >
                      {item.name}
                      {item.submenu && item.submenu.length > 0 && (
                        <Icon
                          icon='mingcute:down-line'
                          width='16'
                          height='16'
                          style={{
                            transition: 'transform 0.2s ease',
                            transform: openSubmenu === index ? 'rotate(180deg)' : 'rotate(0deg)'
                          }}
                        />
                      )}
                    </Link>

                    {/* Submenu Dropdown */}
                    {item.submenu && item.submenu.length > 0 && openSubmenu === index && (
                      <div
                        className='position-absolute main-submenu-items'
                      >
                        <style>
                          {`
                                              @keyframes slideDown {
                                                  from {
                                                      opacity: 0;
                                                      transform: translateY(-10px);
                                                  }
                                                  to {
                                                      opacity: 1;
                                                      transform: translateY(0);
                                                  }
                                              }
                                              @keyframes slideRight {
                                                  from {
                                                      opacity: 0;
                                                      transform: translateX(-10px);
                                                  }
                                                  to {
                                                      opacity: 1;
                                                      transform: translateX(0);
                                                  }
                                              }
                                          `}
                        </style>
                        {item.submenu.map((subItem, subIndex) => (
                          <div
                            key={subIndex}
                            className='position-relative'
                            onMouseEnter={() => setOpenChildMenu(subIndex)}
                            onMouseLeave={() => setOpenChildMenu(null)}
                          >
                            <Link
                              to={subItem.path}
                              onClick={() => handleMenuClick(subItem, item)}

                              className='d-flex align-items-center justify-content-between text-decoration-none main-submenu-items-link'
                              onMouseEnter={(e) => {
                                e.currentTarget.style.backgroundColor = '#f3f4f6';
                                e.currentTarget.style.color = '#111827';
                                e.currentTarget.style.paddingLeft = '18px';
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.backgroundColor = 'transparent';
                                e.currentTarget.style.color = '#374151';
                                e.currentTarget.style.paddingLeft = '14px';
                              }}
                            >
                              <span>{subItem.name}</span>
                              {subItem.children && subItem.children.length > 0 && (
                                <Icon
                                  icon='mingcute:right-line'
                                  width='16'
                                  height='16'
                                  style={{ opacity: 0.6 }}
                                />
                              )}
                            </Link>

                            {/* Child Menu (Third Level) */}
                            {subItem.children && subItem.children.length > 0 && openChildMenu === subIndex && (
                              <div
                                className='position-absolute main-submenu-children-items'
                              >
                                {subItem.children.map((childItem, childIndex) => (
                                  <Link
                                    key={childIndex}
                                    to={childItem.path}
                                    onClick={() => handleMenuClick(childItem, subItem, item)}

                                    className='d-block text-decoration-none main-submenu-children-items-link'

                                    onMouseEnter={(e) => {
                                      e.currentTarget.style.backgroundColor = '#f3f4f6';
                                      e.currentTarget.style.color = '#111827';
                                      e.currentTarget.style.paddingLeft = '18px';
                                    }}
                                    onMouseLeave={(e) => {
                                      e.currentTarget.style.backgroundColor = 'transparent';
                                      e.currentTarget.style.color = '#374151';
                                      e.currentTarget.style.paddingLeft = '14px';
                                    }}
                                  >
                                    {childItem.name}
                                  </Link>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </nav>

              <div className="col-auto">
                <div className="d-flex flex-wrap align-items-center gap-3">
                  {/* Alarm Icon */}
                  <div className="dropdown">
                    <button className="has-indicator w-32-px h-32-px bg-neutral-200 rounded-circle d-flex justify-content-center align-items-center">
                      <Icon icon="solar:alarm-linear" className="text-primary-light text-md" />
                    </button>
                  </div>

                  {/* Notification Icon */}
                  <div className="dropdown">
                    <button
                      className="has-indicator w-32-px h-32-px bg-neutral-200 rounded-circle d-flex justify-content-center align-items-center"
                      type="button"
                      data-bs-toggle="dropdown"
                    >
                      <Icon icon="iconoir:bell" className="text-primary-light text-md" />
                    </button>

                    <div className="dropdown-menu to-top dropdown-menu-lg p-0">
                      <div className="notification-header">
                        <div>
                          <h6 className="text-lg text-primary-light fw-semibold mb-0">Notifications</h6>
                        </div>
                        <span className="notification-count">05</span>
                      </div>
                    </div>
                  </div>

                  {/* User Dropdown */}
                  <div className="dropdown">
                    <button
                      className="d-flex justify-content-center align-items-center rounded-circle"
                      type="button"
                      data-bs-toggle="dropdown"
                    >
                      <img
                        src="assets/images/users/avatar-4.jpg"
                        alt="image_user"
                        className="w-32-px h-32-px object-fit-cover rounded-circle"
                      />
                    </button>
                    <div className="dropdown-menu to-top dropdown-menu-sm">
                      <div className="user-info-header">
                        <div>
                          <h6 className="text-lg text-primary-light fw-semibold mb-2">Shaidul Islam</h6>
                          <span className="text-secondary-light fw-medium text-sm">Admin</span>
                        </div>
                        <button type="button" className="hover-text-danger">
                          <Icon icon="radix-icons:cross-1" className="icon text-xl" />
                        </button>
                      </div>

                      <ul className="to-top-list">
                        <li>
                          <Link
                            className="dropdown-item text-black px-0 py-8 hover-bg-transparent hover-text-primary d-flex align-items-center gap-3"
                            to="/"
                          >
                            <Icon icon="solar:user-linear" className="icon text-xl" /> My Profile
                          </Link>
                        </li>
                        <li>
                          <Link
                            className="dropdown-item text-black px-0 py-8 hover-bg-transparent hover-text-danger d-flex align-items-center gap-3"
                            to="/sign-in"
                            onClick={handleLogout}
                          >
                            <Icon icon="lucide:power" className="icon text-xl" /> Log Out
                          </Link>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Sub Header */}
            <div className="sub-header-bar">
              <div className="sub-header-title">
                {selectedItemName}
              </div>
            </div>
          </div>
        </div>
        <div className='dashboard-main-body'>{children}</div>

        <footer className='d-footer main-footer'>
          <div className='row align-items-center justify-content-between'>
            <div className='col-auto'>
              <p className='mb-0'>© 2025 Abrova. All Rights Reserved.</p>
            </div>
            {/* <div className='col-auto'>
              <p className='mb-0'>
                Powered by <span className='text-primary-600'>Abrova</span>
              </p>
            </div> */}
            <div className='col-auto d-flex align-items-center gap-2 pe-5 pe-lg-6 flex-wrap justify-content-center justify-content-md-end'>
              <p className='mb-0'>
                Powered by
              </p>
              <img
                src='assets/images/logo-test1.png'
                alt='site logo'
                className='light-logo'
              />
            </div>
          </div>
        </footer>
      </main>
    </section>
  );
};

export default MasterLayout;