import React, { useState } from 'react';
import { Icon } from '@iconify/react/dist/iconify.js';
import { Link, NavLink } from 'react-router-dom';

const Header = () => {
    const [openSubmenu, setOpenSubmenu] = useState(null);
    const [openChildMenu, setOpenChildMenu] = useState(null);
    const menuItems = [
        {
            name: 'Dashboard',
            path: '/',
            submenu: [

            ]
        },
        {
            name: 'Sales',
            path: '/',
            submenu: [

            ]
        },
        {
            name: 'Clients',
            path: '/',
            submenu: [

            ]
        },
        {
            name: 'Stockholders',
            path: '/',
            submenu: [

            ]
        },
        {
            name: 'Visa',
            path: '/',
            submenu: [

            ]
        },
        {
            name: 'Package',
            path: '/',
            submenu: [

            ]
        },
        {
            name: 'Subscriber',
            path: '/',
            submenu: [

            ]
        },
        {
            name: 'Masters',
            path: '/department',
            submenu: [
                {
                    name: 'Admin',
                    path: '/Department',
                    children: [
                        { name: 'Department', path: '/department' },
                        { name: 'Employee type', path: '/employeetype' },
                        { name: 'Company type', path: '/companylist' },
                        { name: 'Stakeholder categories', path: '/stakeholder-list' },
                    ]
                },
                {
                    name: 'Sales',
                    path: '/priority-type',
                    children: [
                        { name: 'Priority type', path: '/priority-type' },
                        { name: 'Tags type', path: '/tags-type' },
                        { name: 'Activity Type', path: '/activity-type' },
                    ]
                },

                { name: 'Education', path: '/' },
                { name: 'Test', path: '/' },
                { name: 'Occupation', path: '/' },
                { name: 'General', path: '/' },
                { name: 'Admin', path: '/' },
                // { name: 'Visa', path: '/' },
                // { name: 'Process', path: '/' },
                // { name: 'Institute', path: '/' },

            ]
        },
    ];

    return (
        <>
            {/* <nav className='d-none d-lg-flex align-items-center gap-2'>
            {menuItems.map((item, index) => (
                <div
                    key={index}
                    className='position-relative'
                    onMouseEnter={() => setOpenSubmenu(index)}
                    onMouseLeave={() => setOpenSubmenu(null)}
                >
                    <Link
                        to={item.path}
                        className='text-white text-decoration-none d-flex align-items-center gap-1'
                        style={{
                            fontSize: '15px',
                            fontWeight: '500',
                            padding: '8px 16px',
                            borderRadius: '6px',
                            transition: 'all 0.2s ease',
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
                        {item.submenu && (
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

                
                    {item.submenu && openSubmenu === index && (
                        <div
                            className='position-absolute'
                            style={{
                                top: '100%',
                                left: '0',
                                minWidth: '220px',
                                backgroundColor: '#fff',
                                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
                                borderRadius: '8px',
                                zIndex: 1000,
                                marginTop: '2px',
                                padding: '8px',
                                animation: 'slideDown 0.2s ease'
                            }}
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
                                `}
                            </style>
                            {item.submenu.map((subItem, subIndex) => (
                                <Link
                                    key={subIndex}
                                    to={subItem.path}
                                    className='d-block text-decoration-none'
                                    style={{
                                        fontSize: '14px',
                                        fontWeight: '400',
                                        color: '#374151',
                                        padding: '10px 14px',
                                        borderRadius: '6px',
                                        transition: 'all 0.2s ease',
                                        margin: '2px 0'
                                    }}
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
                                    {subItem.name}
                                </Link>
                            ))}
                        </div>
                    )}
                </div>
            ))}
        </nav> */}
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
                            className='text-white text-decoration-none d-flex align-items-center gap-1'
                            style={{
                                fontSize: '15px',
                                fontWeight: '500',
                                padding: '8px 16px',
                                borderRadius: '6px',
                                transition: 'all 0.2s ease',
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
                                className='position-absolute'
                                style={{
                                    top: '100%',
                                    left: '0',
                                    minWidth: '220px',
                                    backgroundColor: '#fff',
                                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
                                    borderRadius: '8px',
                                    zIndex: 1000,
                                    marginTop: '1px',
                                    padding: '8px',
                                    animation: 'slideDown 0.2s ease'
                                }}
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
                                            className='d-flex align-items-center justify-content-between text-decoration-none'
                                            style={{
                                                fontSize: '14px',
                                                fontWeight: '400',
                                                color: '#374151',
                                                padding: '10px 14px',
                                                borderRadius: '6px',
                                                transition: 'all 0.2s ease',
                                                margin: '2px 0'
                                            }}
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
                                                className='position-absolute'
                                                style={{
                                                    top: '0',
                                                    left: '100%',
                                                    minWidth: '200px',
                                                    backgroundColor: '#fff',
                                                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
                                                    borderRadius: '8px',
                                                    zIndex: 1001,
                                                    marginLeft: '2px',
                                                    padding: '8px',
                                                    animation: 'slideRight 0.2s ease'
                                                }}
                                            >
                                                {subItem.children.map((childItem, childIndex) => (
                                                    <Link
                                                        key={childIndex}
                                                        to={childItem.path}
                                                        className='d-block text-decoration-none'
                                                        style={{
                                                            fontSize: '13px',
                                                            fontWeight: '400',
                                                            color: '#374151',
                                                            padding: '10px 14px',
                                                            borderRadius: '6px',
                                                            transition: 'all 0.2s ease',
                                                            margin: '2px 0'
                                                        }}
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
        </>

    );
};

export default Header;