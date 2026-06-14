import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import AIInsightsPanel from './AIInsightsPanel'

export default function AppLayout() {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-navy">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-hidden">
        <Outlet />
      </main>
      <AIInsightsPanel />
    </div>
  )
}