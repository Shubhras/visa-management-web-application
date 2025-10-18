import React, { useState } from 'react';
import { Icon } from '@iconify/react/dist/iconify.js';
import { Link, NavLink } from 'react-router-dom';

const Header = () => {
    const [openSubmenu, setOpenSubmenu] = useState(null);

    const menuItems = [
        {
            name: 'Dashboard',
            path: '/',
            submenu: [
                { name: 'Leads', path: '/leads' },
            ]
        },
        {
            name: 'Sales',
            path: '/sales',
            submenu: [
                { name: 'All Sales', path: '/sales/all' },
                // { name: 'Add Sale', path: '/sales/add' },
                // { name: 'Reports', path: '/sales/reports' }
            ]
        },
        {
            name: 'Clients',
            path: '/clients',
            submenu: [
                { name: 'All Clients', path: '/clients/all' },
                // { name: 'Add Client', path: '/clients/add' },
                // { name: 'Active Clients', path: '/clients/active' }
            ]
        },
        {
            name: 'Stockholders',
            path: '/stockholders',
            submenu: [
                { name: 'All Stockholders', path: '/stockholders/all' },
                // { name: 'Add Stockholder', path: '/stockholders/add' }
            ]
        },
        {
            name: 'Visa',
            path: '/visa',
            submenu: [
                { name: 'Visa Applications', path: '/visa/applications' },
                // { name: 'Approved Visas', path: '/visa/approved' },
                // { name: 'Pending Visas', path: '/visa/pending' }
            ]
        },
        {
            name: 'Package',
            path: '/package',
            submenu: [
                { name: 'All Packages', path: '/package/all' },
                // { name: 'Add Package', path: '/package/add' },
                // { name: 'Package Types', path: '/package/types' }
            ]
        },
        {
            name: 'Subscriber',
            path: '/subscriber',
            submenu: [
                { name: 'All Subscribers', path: '/subscriber/all' },
                // { name: 'Active Plans', path: '/subscriber/active' },
                // { name: 'Expired Plans', path: '/subscriber/expired' }
            ]
        },
        {
            name: 'Masters',
            path: '/masters',
            submenu: [
                { name: 'Department', path: '/department' },
                { name: 'Employee type', path: '/employeetype' },
                {name:'country',path:'/country'},
                {name:'State',path:'/state'},

                // { name: 'Roles', path: '/masters/roles' }
            ]
        }
    ];

    return (
        <nav className='d-none d-lg-flex align-items-center gap-2'>
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

                    {/* Submenu Dropdown */}
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
        </nav>
    );
};

export default Header;