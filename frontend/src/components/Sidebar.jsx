import { useState, useRef, useEffect } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import {
  HiOutlineCode, HiOutlineDatabase, HiOutlineChatAlt2,
  HiOutlineServer, HiOutlineClock, HiOutlineHome,
  HiOutlineChevronLeft, HiOutlineChevronRight,
  HiOutlineSun, HiOutlineMoon, HiOutlinePhotograph,
  HiOutlineLogout, HiOutlineUserCircle,
  HiOutlineChevronUp,
} from 'react-icons/hi'
import { useTheme } from '../context/ThemeContext'
import { useAuth } from '../context/AuthContext'
import './Sidebar.css'

const navItems = [
  { path: '/', label: 'Dashboard', icon: HiOutlineHome },
  { path: '/query-review', label: 'Query Review', icon: HiOutlineCode },
  { path: '/schema-review', label: 'Schema Review', icon: HiOutlineDatabase },
  { path: '/schema-builder', label: 'Schema Builder', icon: HiOutlinePhotograph },
  { path: '/nl-to-query', label: 'NL to Query', icon: HiOutlineChatAlt2 },
  { path: '/live-db', label: 'Live Database', icon: HiOutlineServer },
  { path: '/history', label: 'History', icon: HiOutlineClock },
]

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef(null)
  const location = useLocation()
  const { theme, toggleTheme } = useTheme()
  const { user, isAuthenticated, logout } = useAuth()

  // Close menu when clicking outside
  useEffect(() => {
    const handleClick = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const userName = user?.full_name || user?.email?.split('@')[0] || 'User'
  const userInitials = userName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()

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

        {/* Account Section */}
        {isAuthenticated ? (
          <div className="account-section" ref={menuRef}>
            {/* Account Menu Dropdown (opens upward) */}
            {menuOpen && !collapsed && (
              <div className="account-menu animate-fade-in">
                <div className="account-menu-header">
                  <div className="account-avatar-lg">
                    {userInitials}
                  </div>
                  <div className="account-info-lg">
                    <div className="account-name-lg">{userName}</div>
                    <div className="account-email-lg">{user?.email}</div>
                  </div>
                </div>
                <div className="account-menu-divider" />

                <div className="account-menu-section">
                  <div className="account-menu-label">AI Features</div>
                  <div className="account-menu-stats">
                    <div className="stat-item">
                      <span className="stat-icon">🧠</span>
                      <span className="stat-text">Multi-LLM Fallback</span>
                      <span className="stat-badge stat-active">Active</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-icon">📚</span>
                      <span className="stat-text">RAG Knowledge Base</span>
                      <span className="stat-badge stat-active">Active</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-icon">🔄</span>
                      <span className="stat-text">Self-Reflection</span>
                      <span className="stat-badge stat-active">Active</span>
                    </div>
                  </div>
                </div>

                <div className="account-menu-divider" />

                <button className="account-menu-item" onClick={toggleTheme}>
                  {theme === 'dark' ? <HiOutlineSun /> : <HiOutlineMoon />}
                  <span>Appearance: {theme === 'dark' ? 'Dark' : 'Light'}</span>
                </button>

                <div className="account-menu-divider" />

                <button className="account-menu-item logout-item" onClick={logout}>
                  <HiOutlineLogout />
                  <span>Log out</span>
                </button>
              </div>
            )}

            {/* Account trigger button */}
            <button
              className="account-trigger"
              onClick={() => setMenuOpen(!menuOpen)}
              title={`${userName} — ${user?.email}`}
            >
              <div className="account-avatar">{userInitials}</div>
              {!collapsed && (
                <>
                  <div className="account-details">
                    <span className="account-name">{userName}</span>
                    <span className="account-email">{user?.email}</span>
                  </div>
                  <HiOutlineChevronUp
                    className={`account-chevron ${menuOpen ? 'open' : ''}`}
                  />
                </>
              )}
            </button>
          </div>
        ) : (
          <NavLink to="/login" className="nav-item" title="Login">
            <HiOutlineUserCircle className="nav-icon" />
            {!collapsed && <span className="nav-label">Login</span>}
          </NavLink>
        )}
      </div>
    </aside>
  )
}
