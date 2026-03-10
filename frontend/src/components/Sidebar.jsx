import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import {
  HiOutlineCode, HiOutlineDatabase, HiOutlineHome,
  HiOutlineChevronLeft, HiOutlineChevronRight,
  HiOutlineSun, HiOutlineMoon,
} from 'react-icons/hi'
import { useTheme } from '../context/ThemeContext'
import './Sidebar.css'

const navItems = [
  { path: '/', label: 'Dashboard', icon: HiOutlineHome },
  { path: '/query-review', label: 'Query Review', icon: HiOutlineCode },
  { path: '/schema-review', label: 'Schema Review', icon: HiOutlineDatabase },
]

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const { theme, toggleTheme } = useTheme()

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      {/* Logo */}
      <div className="sidebar-header">
        <NavLink to="/" className="logo" style={{ textDecoration: 'none', color: 'inherit' }}>
          <img
            src="/logo.png"
            alt="AI Query Master"
            style={{
              width: collapsed ? 40 : 48,
              height: collapsed ? 40 : 48,
              borderRadius: 'var(--radius-md)',
              objectFit: 'cover',
              flexShrink: 0,
              background: 'var(--gradient-primary)',
              padding: 2,
            }}
          />
          {!collapsed && (
            <div className="logo-text">
              <span className="logo-title">AI Query Master</span>
              <span className="logo-subtitle">Database Assistant</span>
            </div>
          )}
        </NavLink>
        <button
          className="collapse-btn"
          onClick={() => setCollapsed(!collapsed)}
          title={collapsed ? 'Expand' : 'Collapse'}
        >
          {collapsed ? <HiOutlineChevronRight /> : <HiOutlineChevronLeft />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {navItems.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `nav-item ${isActive ? 'active' : ''}`
            }
            title={label}
          >
            <Icon className="nav-icon" />
            {!collapsed && <span className="nav-label">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        {/* Theme Toggle */}
        <button
          className="theme-toggle"
          onClick={toggleTheme}
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? <HiOutlineSun /> : <HiOutlineMoon />}
          {!collapsed && <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>}
        </button>
      </div>
    </aside>
  )
}
