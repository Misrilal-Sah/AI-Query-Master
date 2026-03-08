import { Routes, Route, useLocation } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import { AuthProvider } from './context/AuthContext'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import QueryReview from './pages/QueryReview'
import SchemaReview from './pages/SchemaReview'
import SchemaBuilder from './pages/SchemaBuilder'
import NLToQuery from './pages/NLToQuery'
import LiveDatabase from './pages/LiveDatabase'
import History from './pages/History'
import HistoryDetail from './pages/HistoryDetail'
import Login from './pages/Login'
import Signup from './pages/Signup'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import AuthCallback from './pages/AuthCallback'

function AppContent() {
  const location = useLocation()
  const isAuthPage = ['/login', '/signup', '/forgot-password', '/reset-password', '/auth/callback'].includes(location.pathname)

  if (isAuthPage) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
      </Routes>
    )
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/query-review" element={<QueryReview />} />
          <Route path="/schema-review" element={<SchemaReview />} />
          <Route path="/schema-builder" element={<SchemaBuilder />} />
          <Route path="/nl-to-query" element={<NLToQuery />} />
          <Route path="/live-db" element={<LiveDatabase />} />
          <Route path="/history" element={<History />} />
          <Route path="/history/:id" element={<HistoryDetail />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  )
}
