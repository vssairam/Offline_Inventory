import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { ProtectedRoute } from '@/components/layout/ProtectedRoute'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { ForgotPasswordPage } from '@/pages/ForgotPasswordPage'
import { ProfilePage } from '@/pages/ProfilePage'
import { StockPage } from '@/pages/StockPage'
import { AlertsPage } from '@/pages/AlertsPage'
import { ProductListPage } from '@/pages/ProductListPage'
import { ProductCreatePage } from '@/pages/ProductCreatePage'
import { ProductEditPage } from '@/pages/ProductEditPage'
import { SalesListPage } from '@/pages/SalesListPage'
import { SaleCreatePage } from '@/pages/SaleCreatePage'
import { SaleDetailPage } from '@/pages/SaleDetailPage'
import { ReportsPage } from '@/pages/ReportsPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { SettingsPage } from '@/pages/SettingsPage'
import { AdminDashboardPage } from '@/pages/AdminDashboardPage'
import { AdminUsersPage } from '@/pages/AdminUsersPage'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/products" element={<ProductListPage />} />
          <Route path="/products/new" element={<ProductCreatePage />} />
          <Route path="/products/:id/edit" element={<ProductEditPage />} />
          <Route path="/stock" element={<StockPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/sales" element={<SalesListPage />} />
          <Route path="/sales/new" element={<SaleCreatePage />} />
          <Route path="/sales/:id" element={<SaleDetailPage />} />
          <Route path="/reports" element={<ReportsPage />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute adminOnly />}>
        <Route element={<AppLayout />}>
          <Route path="/admin" element={<AdminDashboardPage />} />
          <Route path="/admin/users" element={<AdminUsersPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
