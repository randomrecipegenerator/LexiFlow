import { Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import DashboardPage from './pages/DashboardPage'
import CaseViewPage from './pages/CaseViewPage'
import TrialPrepPage from './pages/TrialPrepPage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/case/:matterId" element={<CaseViewPage />} />
        <Route path="/trial-prep/:matterId" element={<TrialPrepPage />} />
      </Route>
    </Routes>
  )
}